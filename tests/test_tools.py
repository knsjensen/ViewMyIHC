"""Diagnostic tools without Home Assistant: controller log/messages/dataline, backups, diff, press YAML, monitor."""

from __future__ import annotations

import base64
import xml.etree.ElementTree as ET

import pytest
import yaml

import fakes
from conftest import load_module

info = load_module("controller_info")
backup = load_module("project_backup")
project_diff = load_module("project_diff")
press = load_module("press_automation")
monitor_mod = load_module("event_monitor")
parser = load_module("project_parser")


def envelope(inner: str) -> ET.Element:
    return ET.fromstring(
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
        f'<ns1:r1 xmlns:ns1="utcs">{inner}</ns1:r1></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    )


# ------------------------------------------------------------------ controller info


def test_user_log_is_decoded_into_lines():
    controller = fakes.Controller()
    text = "2026-10-06 10:00 Login fejlede\n\n2026-10-06 10:05 Lavt batteri: Tryk køkken\n"
    data = base64.b64encode(text.encode()).decode()
    controller.client.connection.answer_for["getUserLog"] = envelope(f"<ns1:data>{data}</ns1:data>")
    assert info.user_log(controller, "da") == ["2026-10-06 10:00 Login fejlede", "2026-10-06 10:05 Lavt batteri: Tryk køkken"]
    assert "<getUserLog3 xmlns=\"utcs\">da</getUserLog3>" in controller.client.connection.bodies[-1]


def test_user_log_language_cannot_inject_xml():
    controller = fakes.Controller()
    controller.client.connection.answer_for["getUserLog"] = envelope("")
    assert info.user_log(controller, "<x/>") == []
    assert "<x/>" not in controller.client.connection.bodies[-1]


def test_notifications_one_or_many_become_a_list():
    controller = fakes.Controller()
    item = "<ns1:arrayItem><ns1:subject>Alarm</ns1:subject><ns1:delivered>true</ns1:delivered></ns1:arrayItem>"
    controller.client.connection.answer_for["getMessages"] = envelope(item)
    assert info.notifications(controller) == [{"subject": "Alarm", "delivered": "true"}]
    controller.client.connection.answer_for["getMessages"] = envelope(item * 2)
    assert len(info.notifications(controller)) == 2
    controller.client.connection.answer_for["getMessages"] = envelope("")
    assert info.notifications(controller) == []


def test_dataline_lists_addresses_with_resource_ids():
    controller = fakes.Controller()
    conn = controller.client.connection

    def items(*pairs):
        return envelope("".join(
            f"<ns1:arrayItem><ns1:datalineNumber>{a}</ns1:datalineNumber><ns1:resourceID>{r}</ns1:resourceID></ns1:arrayItem>"
            for a, r in pairs))

    conn.answer_for.update({
        "getAllDatalineInputs": items((2, 258), (1, 257)), "getExtraDatalineInputs": envelope(""),
        "getAllDatalineOutputs": items((1, 273)), "getExtraDatalineOutputs": items((9, 900)),
    })
    result = info.dataline(controller)
    assert [(e["address"], e["id"]) for e in result["inputs"]] == [(1, 257), (2, 258)]
    assert [(e["address"], e["extra"]) for e in result["outputs"]] == [(1, False), (9, True)]


# ------------------------------------------------------------------ backups


def sample_xml() -> str:
    return fakes.sample_xml_as_ihcsdk_returns_it()


def test_backup_is_stored_once_per_distinct_project_and_reads_back(tmp_path):
    xml = sample_xml()
    first = backup.save(tmp_path, "S1", xml, {"modified": "x"}, now=1000)
    assert first and first["modified"] == "x"
    assert backup.save(tmp_path, "S1", xml, {}, now=2000) is None
    changed = xml.replace("Lampeudtag", "Stikkontakt")
    assert backup.save(tmp_path, "S1", changed, {}, now=3000)
    names = [e["name"] for e in backup.list_backups(tmp_path, "S1")]
    assert len(names) == 2 and backup.read(tmp_path, "S1", names[0]) == changed
    assert backup.list_backups(tmp_path, "OTHER") == []


def test_backups_are_pruned_to_the_newest(tmp_path, monkeypatch):
    monkeypatch.setattr(backup, "KEEP", 3)
    for n in range(5):
        backup.save(tmp_path, "S1", f"<utcs_project n='{n}'/>", {}, now=1000 + n)
    entries = backup.list_backups(tmp_path, "S1")
    assert len(entries) == 3 and len(list((tmp_path / "S1").glob("*.vis.gz"))) == 3


def test_only_listed_backups_can_be_read(tmp_path):
    backup.save(tmp_path, "S1", sample_xml(), {}, now=1000)
    for name in ("../index.json", "index.json", "20260101-000000-deadbeef.vis.gz"):
        with pytest.raises(backup.BackupError):
            backup.read(tmp_path, "S1", name)


# ------------------------------------------------------------------ diff


def test_diff_finds_added_removed_renamed_moved_and_changed_values():
    xml = sample_xml()
    old = parser.Project(xml)
    new_xml = (
        xml.replace('name="Lampeudtag"', 'name="Stikkontakt"')
        .replace('name="Køkken"', 'name="Køkken alrum"')  # a renamed location is one change, not one per child
    )
    new = parser.Project(new_xml)
    result = project_diff.diff(old, new)
    assert result["counts"] == {"added": 0, "removed": 0, "changed": 2}
    names = {c["name"]: [x["field"] for x in c["changes"]] for c in result["changed"]}
    assert names == {"Stikkontakt": ["name"], "Køkken alrum": ["name"]}
    assert project_diff.diff(old, old)["counts"] == {"added": 0, "removed": 0, "changed": 0}


def test_diff_reports_additions_removals_and_ignores_programs():
    base = '<utcs_project version_major="4" version_minor="0"><group id="_0x1" name="Rum">{}</group></utcs_project>'
    old = parser.Project(base.format(
        '<functionblock id="_0x10" name="Blok"><inputs id="_0x11"><resource_input id="_0x12" name="A" inivalue="0"/></inputs>'
        '<programs id="_0x30"><program_simple id="_0x31" name="P1"/></programs></functionblock>'))
    new = parser.Project(base.format(
        '<functionblock id="_0x10" name="Blok"><inputs id="_0x11"><resource_input id="_0x13" name="B"/></inputs>'
        '<programs id="_0x30"><program_simple id="_0x31" name="P2"/></programs></functionblock>'))
    result = project_diff.diff(old, new)
    assert [a["name"] for a in result["added"]] == ["B"] and [r["name"] for r in result["removed"]] == ["A"]
    assert result["changed"] == []


# ------------------------------------------------------------------ press automation


def test_press_automation_is_valid_yaml_with_three_branches():
    text = press.press_automation("binary_sensor.tryk_koekken", "Tryk køkken", long_ms=800, double_ms=400)
    doc = yaml.safe_load(text)
    assert doc["mode"] == "single" and doc["triggers"][0]["entity_id"] == "binary_sensor.tryk_koekken"
    assert doc["actions"][0]["timeout"] == "00:00:00.800"
    choose = doc["actions"][1]
    assert choose["choose"][0]["alias"] == "Long press"
    danish = yaml.safe_load(press.press_automation("binary_sensor.x", "Tryk", language="da"))
    assert danish["actions"][1]["choose"][0]["alias"] == "Langt tryk" and danish["alias"] == "Tryk – tryk"
    assert choose["default"][0]["timeout"] == "00:00:00.400"
    assert {"then", "else"} <= set(choose["default"][1])


@pytest.mark.parametrize(("entity", "long_ms"), [("light.x", 800), ("binary_sensor.x\nmode: queued", 800), ("binary_sensor.x", 50)])
def test_press_automation_refuses_bad_input(entity, long_ms):
    with pytest.raises(ValueError):
        press.press_automation(entity, "x", long_ms=long_ms)


# ------------------------------------------------------------------ monitor


def test_monitor_records_only_real_changes_from_ihc_notifications():
    controller = fakes.Controller()  # fake runtime values: even ids are on
    mon = monitor_mod.EventMonitor()
    assert mon.start(controller, [514, 515]) == 2
    assert set(controller.notify) == {514, 515}
    controller.change(514, True)  # the value the controller reports right after enabling: same as the baseline
    controller.change(515, True)
    controller.change(515, False)
    events = mon.events()
    assert [(e["id"], e["old"], e["new"]) for e in events] == [(515, False, True), (515, True, False)]
    assert mon.events(events[0]["seq"]) == events[1:]
    assert mon.start(controller, [514, 516]) == 1 and len(controller.notify[514]) == 1
    mon.clear()
    assert mon.events() == []


# ------------------------------------------------------------------ dataline layout

layout_mod = load_module("dataline_layout")

MODULES = (
    '<utcs_project version_major="4" version_minor="0"><documentation_modules id="_0x1">'
    '<dataline_input_modules id="_0x2">'
    '<dataline_input_module id="_0x3" module_type="Input 230" dataline="1" location="Tavle 1"/>'
    '<dataline_input_module id="_0x4" module_type="Input 24" dataline="2" location="Tavle 3"/></dataline_input_modules>'
    '<dataline_output_modules id="_0x5"><dataline_output_module id="_0x6" module_type="Output 230/10" dataline="1" location="Tavle 1"/>'
    "</dataline_output_modules></documentation_modules>"
    '<group id="_0x10" name="Rum"><product_dataline id="_0x11" name="Tryk" position="Køkken">'
    '<dataline_input id="_0x20" name="A" address_dataline="_0x1"/>'
    '<dataline_input id="_0x21" name="B" address_dataline="_0x9"/>'   # position 9 on a 230 V module: does not exist
    '<dataline_input id="_0x22" name="C" address_dataline="_0x11"/>'  # line 2, position 1
    '<dataline_input id="_0x23" name="D" address_dataline="_0x31"/>'  # line 4: no module entered
    '<dataline_output id="_0x24" name="Lys" address_dataline="_0x2"/>'
    '<dataline_output id="_0x25" name="Ubrugt" address_dataline="_0x0"/>'
    "</product_dataline></group></utcs_project>"
)


def test_modules_are_read_per_line():
    project = parser.Project(MODULES)
    assert project.modules["inputs"][1] == {"type": "Input 230", "location": "Tavle 1"}
    assert project.modules["outputs"] == {1: {"type": "Output 230/10", "location": "Tavle 1"}}


def test_lines_follow_the_module_on_them():
    result = layout_mod.layout(parser.Project(MODULES))
    lines = {line["line"]: line for line in result["inputs"]}
    assert sorted(lines) == [1, 2, 4]
    one = lines[1]
    assert (one["type"], one["location"], one["capacity"], one["used"], one["outside"]) == ("Input 230", "Tavle 1", 8, 2, 1)
    # the 8 slots of the 230 V module, plus address 9 that is used although the module has no 9th input
    assert [s["address"] for s in one["slots"]] == [1, 2, 3, 4, 5, 6, 7, 8, 9]
    assert one["slots"][8] == {**one["slots"][8], "name": "B", "usable": False}
    assert lines[2]["capacity"] == 16 and lines[2]["slots"][0]["name"] == "C"
    assert lines[4]["type"] is None and lines[4]["capacity"] == 16 and lines[4]["slots"][0]["name"] == "D"
    out = result["outputs"]
    assert [(o["line"], o["capacity"], o["used"]) for o in out] == [(1, 8, 1)]
    assert out[0]["slots"][1]["name"] == "Lys"


def test_free_slots_get_the_controllers_resource_id_even_if_it_counts_from_zero():
    project = parser.Project(MODULES)
    # the controller numbers addresses from 0 here: learn that from the addresses both know
    controller = {"inputs": [{"address": 0, "id": 0x20, "extra": False}, {"address": 2, "id": 9003, "extra": False}],
                  "outputs": []}
    slots = {s["address"]: s for s in layout_mod.layout(project, controller)["inputs"][0]["slots"]}
    assert slots[3] == {"address": 3, "position": 3, "usable": True, "id": 9003}
