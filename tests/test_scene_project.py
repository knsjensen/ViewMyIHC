"""SceneDesign's project: downloaded in segments as a ZIP, and its message lists read from project.icw."""

from __future__ import annotations

import base64
import io
import xml.etree.ElementTree as ET
import zipfile

import pytest

import fakes
from conftest import load_module

sp = load_module("scene_project")

ICW = """<?xml version="1.0" encoding="UTF-8"?>
<icwproject version="2" name="Hus">
  <description>Scener</description>
  <scenes><scene name="Stue" type="pc"/><scene name="Mobil" type="web"/></scenes>
  <notifications>
    <notification event="text.inactive_to_active_event"><resource rid="202"/>
      <message recipient="a@x.dk; b@y.dk" sender="Unknown"><subject>Alarm</subject><body>Døren er åbnet</body></message>
    </notification>
  </notifications>
  <smsnotifications>
    <smsnotification event="text.active_to_inactive_event"><resource rid="0x203"/>
      <message recipient="100010000000000000000000000000" sender="Unknown"><subject/><body>Varmen er slukket</body></message>
    </smsnotification>
  </smsnotifications>
  <emailcontrols>
    <emailcontrol><resource rid="204"/><action type="text.emailcontrol.off_to_on_action"/>
      <executionconfirmation><body>Tændt</body><subject>OK</subject></executionconfirmation>
      <authorization type="text.emailcontrol.authorization.three_way"><triggersubject>VARME TIL</triggersubject>
        <confirmationaddress>me@x.dk</confirmationaddress><confirmationmessage>Bekræft</confirmationmessage></authorization>
    </emailcontrol>
  </emailcontrols>
  <smscontrols>
    <smscontrol><resource rid="205"/><action type="text.emailcontrol.pulse_action"/>
      <authorization type="text.emailcontrol.authorization.sender_based"><triggersubject>PORT</triggersubject>
        <acceptsenderaddress>010000000000000000000000000001</acceptsenderaddress></authorization>
    </smscontrol>
  </smscontrols>
</icwproject>""".encode("utf-8")


def icz(icw: bytes = ICW) -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("project.icw", icw)
        archive.writestr("images/a.png", b"png")
    return buffer.getvalue()


def envelope(inner: str) -> ET.Element:
    return ET.fromstring(
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
        f'<ns1:r xmlns:ns1="utcs">{inner}</ns1:r></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    )


class SceneController(fakes.Controller):
    """Serves an .icz in two segments, like the controller's ModuleService."""

    def __init__(self, data: bytes, crc: str = "42"):
        super().__init__()
        self.data, self.crc, self.segment_calls = data, crc, 0
        conn = self.client.connection
        original = conn.soap_action

        def soap_action(service, action, body=""):
            if action == "getSceneProjectInfo":
                return envelope(f"<ns1:name>Hus</ns1:name><ns1:size>{len(self.data)}</ns1:size>"
                                f"<ns1:filepath>C:\\\\x\\\\Hus.icz</ns1:filepath><ns1:crc>{self.crc}</ns1:crc>")
            if action == "getSceneProjectSegmentationSize":
                return envelope(f"{(len(self.data) + 1) // 2}")
            if action == "getSceneProjectSegment":
                self.segment_calls += 1
                doc = ET.fromstring(f"<r>{body}</r>")
                name, index = doc[0].text, int(doc[1].text)
                assert name == "Hus"  # the file name without .icz, as SceneDesign asks
                half = (len(self.data) + 1) // 2
                chunk = self.data[index * half:(index + 1) * half]
                return envelope(f"<ns1:filename>Hus</ns1:filename><ns1:data>{base64.b64encode(chunk).decode()}</ns1:data>" if chunk else "")
            return original(service, action, body)

        conn.soap_action = soap_action


def test_download_joins_the_segments_into_the_zip():
    data = icz()
    controller = SceneController(data)
    assert sp.download(controller) == data and controller.segment_calls == 2


def test_parse_reads_messages_and_controls():
    result = sp.parse(icz())
    assert (result["name"], result["scenes"]) == ("Hus", 2)
    email, sms = result["notifications"]
    assert email == {"key": "notifications:0", "channel": "email", "resource": 0x202, "event": "inactive_to_active_event", "recipients": ["a@x.dk", "b@y.dk"],
                     "slots": [], "subject": "Alarm", "body": "Døren er åbnet"}
    assert (sms["channel"], sms["resource"], sms["event"], sms["slots"]) == ("sms", 0x203, "active_to_inactive_event", [1, 5])
    mail_control, sms_control = result["controls"]
    assert mail_control == {"key": "emailcontrols:0", "channel": "email", "resource": 0x204, "action": "off_to_on_action", "authorization": "three_way",
                            "trigger": "VARME TIL", "senders": [], "confirmation_address": "me@x.dk", "confirmation": "Tændt",
                            "confirmation_message": "Bekræft"}
    assert (sms_control["action"], sms_control["authorization"], sms_control["senders"]) == ("pulse_action", "sender_based", [2, 30])


def test_read_downloads_again_only_when_the_checksum_changes():
    controller = SceneController(icz())
    first = sp.read(controller, None)
    again = sp.read(controller, first)
    assert again is first and controller.segment_calls == 2
    controller.crc = "43"
    assert sp.read(controller, first)["crc"] == "43" and controller.segment_calls == 4


@pytest.mark.parametrize("data", [b"not a zip", icz(b"<other/>"), icz(b"<icwproject><broken")])
def test_unreadable_projects_raise(data):
    with pytest.raises(sp.SceneProjectError):
        sp.parse(data)


def test_sms_numbers_come_from_the_ihc_project():
    parser = load_module("project_parser")
    project = parser.Project(
        '<utcs_project version_major="4" version_minor="0"><group id="_0x1" name="Teknik">'
        '<product_rs485_sms_modem id="_0x2" name="SMS modem">'
        '<sms_modem_settings id="_0x3" name="Anna"><sms_modem_phonenumber id="_0x4" address="1" phonenumber="+4512345678"/></sms_modem_settings>'
        '<sms_modem_settings id="_0x5" name="Bo"><sms_modem_phonenumber id="_0x6" address="5" phonenumber="+4587654321"/></sms_modem_settings>'
        "</product_rs485_sms_modem></group></utcs_project>"
    )
    assert project.sms_numbers == {1: {"number": "+4512345678", "label": "Anna"}, 5: {"number": "+4587654321", "label": "Bo"}}
