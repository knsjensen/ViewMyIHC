"""Changing controller settings: only changed fields are replaced, guards keep Home Assistant connected."""

from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET

import pytest

import fakes
from conftest import load_module

w = load_module("admin_writer")


def answer(wrapper: str, inner: str) -> ET.Element:
    return ET.fromstring(
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/" '
        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"><SOAP-ENV:Body>'
        f'<ns1:{wrapper} xmlns:ns1="utcs">{inner}</ns1:{wrapper}></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    )


def fields(**values) -> str:
    return "".join(f"<ns1:{k}>{v}</ns1:{k}>" for k, v in values.items())


def sent(controller, action: str) -> ET.Element:
    conn = controller.client.connection
    body = next(b for (svc, a), b in zip(reversed(conn.calls), reversed(conn.bodies)) if a == action)
    return ET.fromstring(f"<root>{body}</root>")


def leaves(element: ET.Element) -> dict[str, str]:
    return {e.tag.rsplit("}", 1)[-1]: (e.text or "") for e in element.iter() if len(e) == 0}


@pytest.fixture
def controller():
    c = fakes.Controller()
    c.client.username = "homeassistant"
    a = c.client.connection.answer_for
    a["getNetworkSettings"] = answer("getNetworkSettings1", fields(
        ipAddress="192.168.1.3", netmask="255.255.255.0", gateway="192.168.1.1", httpPort=80, httpsPort=443, futureField="x"))
    a["getWebAccessControl"] = answer("getWebAccessControl1", "".join(
        f"<ns1:{name}>true</ns1:{name}>" for name in ["m_usbLoginRequired_usb", *w._ACCESS, "m_openapi_used"]))
    a["getSMTPSettings"] = answer("getSMTPSettings1", fields(hostname="smtp.x.dk", hostport=25, username="anna", password=""))
    a["getSettings"] = answer("getSettings1", fields(
        synchroniseTimeAgainstServer="true", useDST="true", gmtOffsetInHours=1, serverName="dk.pool.ntp.org",
        syncIntervalInHours=24) + "<ns1:timeAndDateInUTC><ns1:year>2026</ns1:year></ns1:timeAndDateInUTC>")
    user = lambda name, pw: ("<ns1:arrayItem><ns1:createdDate><ns1:year>2021</ns1:year></ns1:createdDate>"  # noqa: E731
                             f"<ns1:loginDate xsi:nil=\"true\"/><ns1:username>{name}</ns1:username><ns1:password>{pw}</ns1:password>"
                             "<ns1:email>a@b.dk</ns1:email><ns1:firstname>Anna</ns1:firstname><ns1:lastname>J</ns1:lastname>"
                             "<ns1:phone>1</ns1:phone><ns1:group><ns1:type>text.usermanager.group_administrators</ns1:type></ns1:group>"
                             "<ns1:project/></ns1:arrayItem>")
    a["getUsers"] = answer("getUsers1", user("homeassistant", "hapw") + user("anna", "annapw") + user("gæst", ""))
    return c


def test_network_change_needs_confirmation_and_keeps_unknown_fields(controller):
    with pytest.raises(w.NeedsConfirmation):
        w.write_section(controller, "network", {"netmask": "255.255.0.0"})
    assert w.write_section(controller, "network", {"netmask": "255.255.0.0", "httpPort": 80}, confirm=True) == ["netmask"]
    body = leaves(sent(controller, "setNetworkSettings"))
    assert body["netmask"] == "255.255.0.0" and body["ipAddress"] == "192.168.1.3" and body["futureField"] == "x"


def test_nothing_is_sent_when_nothing_changed(controller):
    assert w.write_section(controller, "network", {"httpPort": "80"}) == []
    assert "setNetworkSettings" not in [a for _, a in controller.client.connection.calls]


@pytest.mark.parametrize(("section", "changes"), [
    ("network", {"ipAddress": "192.168.1.300"}), ("network", {"httpPort": 0}), ("smtp", {"hostname": "a b"}),
    ("time", {"gmtOffsetInHours": 20}), ("web_access", {"m_sceneview_usb": "maybe"}), ("network", {"bogus": 1}),
])
def test_invalid_values_are_refused(controller, section, changes):
    with pytest.raises(w.AdminWriteError):
        w.write_section(controller, section, changes, confirm=True)


def test_web_access_cannot_cut_off_home_assistant_or_administrator(controller):
    for name in ("m_treeview_internal", "m_administrator_internal"):
        with pytest.raises(w.AdminWriteError):
            w.write_section(controller, "web_access", {name: False})
    w.write_section(controller, "web_access", {"m_sceneview_external": False})
    body = leaves(sent(controller, "setWebAccessControl"))
    assert body["m_sceneview_external"] == "false" and body["m_treeview_internal"] == "true"


def test_a_password_the_controller_does_not_give_out_is_never_erased(controller):
    with pytest.raises(w.AdminWriteError, match="enter it again"):
        w.write_section(controller, "smtp", {"hostport": 587})
    w.write_section(controller, "smtp", {"hostport": 587, "password": "ny"})
    assert leaves(sent(controller, "setSMTPSettings"))["password"] == "ny"


def test_time_settings_leave_the_clock_alone_unless_asked(controller):
    w.write_section(controller, "time", {"syncIntervalInHours": 12})
    body = sent(controller, "setSettings")
    clock = next(e for e in body.iter() if e.tag.endswith("timeAndDateInUTC"))
    assert clock.get("{http://www.w3.org/2001/XMLSchema-instance}nil") == "true"
    when = datetime.datetime(2026, 10, 6, 12, 30, 5, tzinfo=datetime.timezone.utc)
    assert w.write_section(controller, "time", {}, set_clock=when) == ["timeAndDateInUTC"]
    clock = leaves(next(e for e in sent(controller, "setSettings").iter() if e.tag.endswith("timeAndDateInUTC")))
    assert (clock["year"], clock["hours"], clock["minutes"]) == ("2026", "12", "30")


def test_a_refused_change_is_reported(controller):
    controller.client.connection.answer_for["setNetworkSettings"] = answer("setNetworkSettings2", "false")
    with pytest.raises(w.AdminWriteError, match="refused"):
        w.write_section(controller, "network", {"gateway": "192.168.1.254"}, confirm=True)


def test_dns_servers_are_sent_as_signed_32_bit_numbers(controller):
    w.set_dns(controller, "8.8.8.8", "192.168.1.1")
    numbers = [e.text for e in sent(controller, "setDNSServers").iter() if e.tag.endswith("ipAddress")]
    assert numbers == ["134744072", "-1062731519"]
    with pytest.raises(w.AdminWriteError):
        w.set_dns(controller, "8.8.8", "")


def test_add_user_with_the_admin_group_and_no_dates(controller):
    w.add_user(controller, "ny", "hemmelig", {"firstname": "Ny"})
    body = sent(controller, "addUser")
    values = leaves(body)
    assert values["username"] == "ny" and values["password"] == "hemmelig" and values["type"] == "text.usermanager.group_administrators"
    with pytest.raises(w.AdminWriteError):
        w.add_user(controller, "ANNA", "x", {})  # exists (case-insensitive)
    with pytest.raises(w.AdminWriteError):
        w.add_user(controller, "ny2", "", {})  # a password is required


def test_update_user_keeps_password_dates_and_group(controller):
    w.update_user(controller, "anna", None, {"phone": "11223344"})
    values = leaves(sent(controller, "updateUser"))
    assert values["password"] == "annapw" and values["phone"] == "11223344" and values["year"] == "2021"
    with pytest.raises(w.AdminWriteError, match="enter the password"):
        w.update_user(controller, "gæst", None, {"phone": "1"})


def test_home_assistants_own_user_is_protected(controller):
    with pytest.raises(w.AdminWriteError):
        w.remove_user(controller, "homeassistant")
    with pytest.raises(w.AdminWriteError):
        w.update_user(controller, "homeassistant", "nyt", {})
    w.update_user(controller, "homeassistant", None, {"phone": "2"})  # details are fine
    w.remove_user(controller, "anna")
    assert "anna" in "".join(controller.client.connection.bodies[-1:])


def test_special_characters_are_escaped(controller):
    w.update_user(controller, "anna", "p<&>", {"firstname": "K&<"})
    values = leaves(sent(controller, "updateUser"))
    assert (values["password"], values["firstname"]) == ("p<&>", "K&<")
