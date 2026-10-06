"""Editing the message lists of a SceneDesign project: only what changes is written, the rest stays byte for byte."""

from __future__ import annotations

import datetime
import io
import zipfile

import pytest

from conftest import load_module
from test_scene_project import ICW, icz

se = load_module("scene_editor")
sp = load_module("scene_project")
NOW = datetime.datetime(2026, 10, 7, 12, 30, 0)


def project_with_extras() -> bytes:
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w") as archive:
        archive.writestr("project.icw", ICW)
        archive.writestr("images/a.png", b"\x89PNG-picture-bytes")
        archive.writestr("ihcproject.ihc", b"stored", compress_type=zipfile.ZIP_STORED)
    return buffer.getvalue()


def entries(data: bytes):
    parsed = sp.parse(data)
    return parsed["notifications"], parsed["controls"]


def icw(data: bytes) -> str:
    return zipfile.ZipFile(io.BytesIO(data)).read("project.icw").decode("utf-8")


def test_nothing_changed_gives_the_very_same_file():
    data = project_with_extras()
    assert se.apply(data, *entries(data), now=NOW) == data


def test_only_the_changed_entry_is_rewritten_everything_else_stays_byte_for_byte():
    data = project_with_extras()
    notes, controls = entries(data)
    notes[0] = {**notes[0], "body": "Hoveddøren er åbnet"}
    out = se.apply(data, notes, controls, now=NOW)
    before, after = icw(data), icw(out)
    for tag in ("smsnotifications", "emailcontrols", "smscontrols", "scenes", "description"):
        assert before[slice(*se._span(before, tag))] == after[slice(*se._span(after, tag))], tag
    assert sp.parse(out)["notifications"][0]["body"] == "Hoveddøren er åbnet"
    old_zip, new_zip = zipfile.ZipFile(io.BytesIO(data)), zipfile.ZipFile(io.BytesIO(out))
    assert old_zip.namelist() == new_zip.namelist()
    for name in ("images/a.png", "ihcproject.ihc"):
        assert old_zip.read(name) == new_zip.read(name)
        assert old_zip.getinfo(name).compress_type == new_zip.getinfo(name).compress_type


def test_new_and_removed_entries():
    data = icz()
    notes, controls = entries(data)
    notes.append({"channel": "sms", "resource": 0x2AB, "event": "inactive_to_active_event", "slots": [1, 30], "body": "Røg i køkkenet"})
    controls = [c for c in controls if c["channel"] != "sms"]  # remove the SMS control
    controls.append({"channel": "email", "resource": 0x2AC, "action": "on_to_off_action", "authorization": "sender_based",
                     "trigger": "LYS FRA", "senders": ["anna@example.org"], "confirmation": "Slukket"})
    result = sp.parse(se.apply(data, notes, controls, now=NOW))
    added = result["notifications"][-1]
    assert (added["channel"], added["resource"], added["slots"], added["body"]) == ("sms", 0x2AB, [1, 30], "Røg i køkkenet")
    assert [c["channel"] for c in result["controls"]] == ["email", "email"]
    new = result["controls"][-1]
    assert (new["trigger"], new["action"], new["authorization"], new["senders"], new["confirmation"]) == (
        "LYS FRA", "on_to_off_action", "sender_based", ["anna@example.org"], "Slukket")


def test_a_list_that_did_not_exist_is_added_in_scenedesigns_order():
    data = icz(b'<?xml version="1.0" encoding="UTF-8"?><icwproject version="2" name="Ny"><scenes/></icwproject>')
    note = {"channel": "email", "resource": 0x10, "event": "active_to_inactive_event", "recipients": ["a@b.dk"],
            "subject": "Varme", "body": "Slukket <&>"}
    out = se.apply(data, [note], [], now=NOW)
    text = icw(out)
    assert text.index("<scenes/>") < text.index("<notifications>")
    assert sp.parse(out)["notifications"][0]["body"] == "Slukket <&>"  # escaped and back


@pytest.mark.parametrize(("kind", "entry"), [
    ("n", {"channel": "email", "resource": 1, "event": "inactive_to_active_event", "recipients": ["ikke en adresse"], "subject": "x"}),
    ("n", {"channel": "email", "resource": 1, "event": "inactive_to_active_event", "recipients": ["a@b.dk"], "subject": ""}),
    ("n", {"channel": "sms", "resource": 1, "event": "inactive_to_active_event", "slots": [31], "body": "x"}),
    ("n", {"channel": "sms", "resource": 1, "event": "inactive_to_active_event", "slots": [1], "body": "x" * 61}),
    ("n", {"channel": "sms", "resource": 1, "event": "sometimes", "slots": [1], "body": "x"}),
    ("n", {"channel": "sms", "resource": 0, "event": "inactive_to_active_event", "slots": [1], "body": "x"}),
    ("c", {"channel": "sms", "resource": 1, "action": "pulse_action", "authorization": "three_way", "trigger": "X"}),
    ("c", {"channel": "email", "resource": 1, "action": "pulse_action", "authorization": "direct_control", "trigger": ""}),
    ("c", {"channel": "email", "resource": 1, "action": "pulse_action", "authorization": "direct_control", "trigger": "x" * 61}),
    ("c", {"channel": "email", "resource": 1, "action": "pulse_action", "authorization": "three_way", "trigger": "X",
           "confirmation_address": "a@b.dk c@d.dk"}),
    ("c", {"channel": "email", "resource": 1, "action": "explode", "authorization": "direct_control", "trigger": "X"}),
])
def test_scenedesigns_rules_are_enforced(kind, entry):
    data = icz()
    notes, controls = entries(data)
    with pytest.raises(se.SceneEditError):
        se.apply(data, notes + [entry] if kind == "n" else notes, controls + [entry] if kind == "c" else controls, now=NOW)
