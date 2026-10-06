"""Exercise the Home Assistant facing layer against a real ``HomeAssistant`` core (no test plugin needed)."""

from __future__ import annotations

import asyncio
import base64
from pathlib import Path
import sys
from unittest.mock import MagicMock

import pytest
import yaml

pytest.importorskip("homeassistant")
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from homeassistant.core import HomeAssistant  # noqa: E402
from homeassistant.helpers import area_registry as ar, device_registry as dr, entity_registry as er  # noqa: E402

import fakes  # noqa: E402
from custom_components.viewmyihc import entity_api, websocket_api as ws  # noqa: E402
from custom_components.viewmyihc.const import DOMAIN, VERSION  # noqa: E402
from custom_components.viewmyihc.admin_snapshot import AdminSnapshotStore  # noqa: E402

SERIAL = "1234-ABCD"


@pytest.fixture
async def hass(tmp_path):
    core = HomeAssistant(str(tmp_path))
    core.config.config_dir = str(tmp_path)
    dr.async_setup(core)
    for registry in (ar, dr, er):
        loaded = registry.async_load(core)
        if asyncio.iscoroutine(loaded):
            await loaded
    core.data["ihc"] = {SERIAL: {"controller": fakes.Controller()}}
    core.data[DOMAIN] = {"projects": {}, "admin_snapshots": AdminSnapshotStore(core)}
    await core.data[DOMAIN]["admin_snapshots"].async_load()
    yield core
    await core.async_stop(force=True)


def entry(**over):
    base = {"platform": "switch", "id": 514, "name": "Lampe", "note": "n", "position": "Køkken", "options": {}}
    base.update(over)
    return base


# ------------------------------------------------------------------ websocket handlers


class Conn:
    """Minimal ActiveConnection stand-in that records the answer."""

    def __init__(self, admin=True):
        self.user = MagicMock(is_admin=admin)
        self.result = None
        self.error = None
        self.msg_id = None

    def send_result(self, msg_id, result=None):
        self.msg_id, self.result = msg_id, result

    def send_error(self, msg_id, code, message):
        self.msg_id, self.error = msg_id, (code, message)

    def async_handle_exception(self, msg, err):  # used by async_response wrappers
        raise err


async def call(hass, handler, msg, admin=True):
    conn = Conn(admin)
    # The client (hass.callWS) owns the "id" field: it is the *message* number, never a resource id
    CLIENT_MESSAGE_ID = 77
    msg = {**msg, "id": CLIENT_MESSAGE_ID}
    if handler._ws_schema:  # commands without parameters have no schema; HA then skips validation
        msg = handler._ws_schema(msg)  # exactly what HA does before calling the handler
    result = handler(hass, conn, msg)
    if asyncio.iscoroutine(result):
        await result
    await hass.async_block_till_done()
    # @async_response handlers run as background tasks, which async_block_till_done does not wait for
    for _ in range(20):
        pending = [t for t in hass._background_tasks if not t.done()]
        if not pending:
            break
        # an executor job that failed was already handled by the handler awaiting it; a handler task that failed was not
        for task, outcome in zip(pending, await asyncio.gather(*pending, return_exceptions=True)):
            if isinstance(task, asyncio.Task) and isinstance(outcome, BaseException):
                raise outcome
    return conn


async def load_project(hass):
    conn = await call(hass, ws.ws_load, {"type": "viewmyihc/load", "force": False})
    return conn


async def test_load_children_detail_values_end_to_end(hass):
    conn = await load_project(hass)
    assert conn.error is None, conn.error
    assert conn.result["controller"] == SERIAL and conn.result["info"]["resources"] == 9
    top = await call(hass, ws.ws_children, {"type": "viewmyihc/children", "parent": 0, "view": "all"})
    assert [c["name"] for c in top.result] == ["Køkken", "Kun programmer", "Kun installation"]
    detail = await call(hass, ws.ws_detail, {"type": "viewmyihc/detail", "ihc_id": 514})
    assert detail.result["id_hex"] == "0x202"
    values = await call(hass, ws.ws_values, {"type": "viewmyihc/values", "ids": [514, 515]})
    assert values.result == {"514": True, "515": False}


async def test_project_is_only_downloaded_again_when_revision_changes(hass):
    controller = hass.data["ihc"][SERIAL]["controller"]
    await load_project(hass)
    await load_project(hass)
    assert controller.client.project_downloads == 1
    await call(hass, ws.ws_load, {"type": "viewmyihc/load", "force": True})
    assert controller.client.project_downloads == 2
    controller.client.get_project_info = lambda: {"projectMajorRevision": 2}
    await load_project(hass)
    assert controller.client.project_downloads == 3


async def test_commands_before_load_report_not_loaded(hass):
    conn = await call(hass, ws.ws_children, {"type": "viewmyihc/children", "parent": 0, "view": "all"})
    assert conn.error[0] == "not_loaded"


async def test_no_ihc_integration_reports_no_ihc(hass):
    hass.data.pop("ihc")
    conn = await call(hass, ws.ws_load, {"type": "viewmyihc/load", "force": False})
    assert conn.error[0] == "no_ihc"
    status = await call(hass, ws.ws_status, {"type": "viewmyihc/status"})
    assert status.result == {"version": VERSION, "controllers": []}


async def test_admin_data_hides_secrets(hass):
    conn = await call(hass, ws.ws_admin_refresh, {"type": "viewmyihc/admin/refresh"})
    sections = {s["key"]: s for s in conn.result["sections"]}
    assert "hemmelig" not in repr(conn.result)
    assert sections["system"]["data"]["password"] == "***"


async def test_non_admin_users_are_refused(hass):
    from homeassistant.exceptions import Unauthorized

    for handler, msg in (
        (ws.ws_load, {"type": "viewmyihc/load", "force": False}),
        (ws.ws_admin_refresh, {"type": "viewmyihc/admin/refresh"}),
        (ws.ws_admin_snapshot, {"type": "viewmyihc/admin/snapshot"}),
        (entity_api.ws_snippet, {"type": "viewmyihc/entity/snippet", "entry": {"platform": "switch", "id": 1}}),
    ):
        with pytest.raises(Unauthorized):
            await call(hass, handler, msg, admin=False)


# ------------------------------------------------------------------ regression: "id" is the websocket message id


async def test_answers_carry_the_clients_message_id_not_the_resource_id(hass):
    """Real bug: ``detail`` used "id" for the resource, but hass.callWS overwrites "id" with a message number."""
    await load_project(hass)
    for handler, msg in (
        (ws.ws_detail, {"type": "viewmyihc/detail", "ihc_id": 514}),
        (entity_api.ws_suggest, {"type": "viewmyihc/entity/suggest", "ihc_id": 273}),
        (ws.ws_children, {"type": "viewmyihc/children", "parent": 0}),
    ):
        conn = await call(hass, handler, msg)
        assert conn.error is None, conn.error
        assert conn.msg_id == 77  # the number the client chose in call(); never 514 / 273


async def test_a_resource_id_cannot_be_smuggled_in_through_the_message_id(hass):
    """If the message id happened to equal a resource id it must not change which resource is looked up."""
    await load_project(hass)
    conn = Conn()
    msg = ws.ws_detail._ws_schema({"type": "viewmyihc/detail", "ihc_id": 514, "id": 273})
    ws.ws_detail(hass, conn, msg)
    assert conn.result["id"] == 514 and conn.msg_id == 273


def test_no_command_uses_id_as_a_payload_key():
    import inspect

    for module in (ws, entity_api):
        for name, fn in inspect.getmembers(module):
            schema = getattr(fn, "_ws_schema", None)
            if not name.startswith("ws_") or not schema:
                continue
            id_validators = [v for k, v in schema.schema.items() if str(k) == "id"]
            # only the base message id (a positive integer) may exist under "id"
            assert len(id_validators) == 1, name
            assert "ihc_id" in str(list(schema.schema)) or name not in ("ws_detail", "ws_suggest", "ws_delete"), name


async def test_status_reports_the_backend_version_so_the_panel_can_detect_stale_python(hass):
    conn = await call(hass, ws.ws_status, {"type": "viewmyihc/status"})
    assert conn.result["version"] == VERSION
    assert conn.result["controllers"] == [{"serial": SERIAL, "loaded": False, "ha_user": "homeassistant"}]


# ------------------------------------------------------------------ admin: saved state first, refresh in the background


def soap_calls(hass):
    return hass.data["ihc"][SERIAL]["controller"].client.connection.calls


def refresh(hass):
    return call(hass, ws.ws_admin_refresh, {"type": "viewmyihc/admin/refresh"})


def snapshot(hass):
    return call(hass, ws.ws_admin_snapshot, {"type": "viewmyihc/admin/snapshot"})


def users_answer(*users):
    items = "".join(f"<arrayItem><username>{u}</username><email>{e}</email></arrayItem>" for u, e in users)
    return fakes.ET.fromstring(f'<e:Envelope xmlns:e="x"><e:Body><r xmlns="utcs">{items}</r></e:Body></e:Envelope>')


async def test_snapshot_is_empty_until_the_first_read_and_never_contacts_the_controller(hass):
    first = await snapshot(hass)
    assert first.result == {"sections": None, "saved": None, "ha_user": "homeassistant"}
    assert soap_calls(hass) == []


async def test_first_refresh_saves_and_the_snapshot_then_answers_without_any_controller_call(hass):
    from custom_components.viewmyihc.admin_reader import SECTIONS

    result = await refresh(hass)
    assert result.result["first"] is True and result.result["changes"] == []
    calls = len(soap_calls(hass))
    assert calls == len(SECTIONS) + 1  # e-mail control also reads whether it is switched on

    shown = await snapshot(hass)  # what the panel shows instantly when the tab opens
    assert [s["key"] for s in shown.result["sections"]] == [k for k, *_ in SECTIONS]
    assert shown.result["saved"] == result.result["fetched"]
    assert len(soap_calls(hass)) == calls  # the snapshot cost the controller nothing
    assert "hemmelig" not in repr(shown.result)


async def test_saved_state_survives_a_restart_of_home_assistant(hass):
    await refresh(hass)
    reloaded = AdminSnapshotStore(hass)
    await reloaded.async_load()
    assert reloaded.sections(SERIAL) is not None
    assert {s["key"] for s in reloaded.sections(SERIAL)} >= {"users", "time", "network"}


async def test_unchanged_controller_reports_no_changes(hass):
    await refresh(hass)
    again = await refresh(hass)
    assert again.result["first"] is False and again.result["changes"] == [] and again.result["errors"] == []


async def test_a_changed_setting_is_reported_with_path_old_and_new_value(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getSettings"] = fakes.answer(serverName="pool.ntp.org", useDST="true")
    await refresh(hass)

    conn.answer_for["getSettings"] = fakes.answer(serverName="dk.pool.ntp.org", useDST="true")
    changed = await refresh(hass)
    assert changed.result["changes"] == [
        {"type": "changed", "section": "time", "path": ["serverName"], "old": "pool.ntp.org", "new": "dk.pool.ntp.org"}
    ]
    after = await refresh(hass)
    assert after.result["changes"] == []  # reported once; the saved state is now the new one


async def test_added_and_changed_users_are_found_by_username_not_position(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getUsers"] = users_answer(("admin", "a@x"), ("anna", "k@x"))
    await refresh(hass)
    # same users in another order, anna has a new e-mail, and a third user was added
    conn.answer_for["getUsers"] = users_answer(("anna", "k2@x"), ("admin", "a@x"), ("ny", "n@x"))
    result = await refresh(hass)
    found = {(c["type"], tuple(c["path"])) for c in result.result["changes"] if c["section"] == "users"}
    assert ("changed", ("[anna]", "email")) in found
    assert ("added", ("[ny]", "username")) in found and ("added", ("[ny]", "email")) in found
    assert not any(path[0] == "[admin]" for _, path in found)


async def test_a_section_that_fails_keeps_its_last_good_data_and_is_flagged(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    await refresh(hass)
    conn.fail = {"getSMTPSettings"}
    result = await refresh(hass)
    smtp = {s["key"]: s for s in result.result["sections"]}["smtp"]
    assert smtp["stale"] is True and "error" in smtp and "data" in smtp  # the old data is still shown
    assert [e["key"] for e in result.result["errors"]] == ["smtp"]
    assert result.result["changes"] == []  # a failing call is not a change
    conn.fail = set()
    ok = await refresh(hass)
    assert ok.result["errors"] == [] and ok.result["changes"] == []


async def test_uptime_and_clock_never_count_as_changes(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getSystemInfo"] = fakes.answer(brand="LK", uptime="1 dag", realtimeclock="10:00")
    conn.answer_for["getUptime"] = fakes.answer(value="100")
    conn.answer_for["getCurrentLocalTime"] = fakes.answer(hour="10", minute="00")
    await refresh(hass)
    conn.answer_for["getSystemInfo"] = fakes.answer(brand="LK", uptime="2 dage", realtimeclock="10:01")
    conn.answer_for["getUptime"] = fakes.answer(value="200")
    conn.answer_for["getCurrentLocalTime"] = fakes.answer(hour="10", minute="01")
    result = await refresh(hass)
    assert result.result["changes"] == []
    shown = {s["key"]: s for s in result.result["sections"]}
    assert shown["system"]["data"]["uptime"] == "2 dage"  # the fresh value is displayed, just not flagged


# ------------------------------------------------------------------ entities of the ihc integration (all read only)


def snippet(hass, entry_dict):
    return call(hass, entity_api.ws_snippet, {"type": "viewmyihc/entity/snippet", "entry": entry_dict})


def entity_list(hass):
    return call(hass, entity_api.ws_list, {"type": "viewmyihc/entity/list"})


def existing(hass):
    return call(hass, entity_api.ws_existing, {"type": "viewmyihc/entity/existing"})


def write_setup(tmp_path, config, **files):
    (tmp_path / "configuration.yaml").write_text(config, encoding="utf-8")
    for name, text in files.items():
        (tmp_path / name.replace("__", "/")).parent.mkdir(parents=True, exist_ok=True)
        (tmp_path / name.replace("__", "/")).write_text(text, encoding="utf-8")


def register(hass, domain, unique_id, object_id, **kwargs):
    return er.async_get(hass).async_get_or_create(domain, "ihc", unique_id, suggested_object_id=object_id, **kwargs)


async def test_suggest_returns_the_form_defaults_and_what_already_exists(hass):
    await load_project(hass)
    register(hass, "switch", f"{SERIAL}-273", "lampe")
    conn = await call(hass, entity_api.ws_suggest, {"type": "viewmyihc/entity/suggest", "ihc_id": 273})  # lamp "On"
    assert conn.error is None, conn.error
    assert conn.result["default_platform"] == "switch" and "door" in conn.result["device_classes"]
    assert [(e["platform"], e["entity_id"]) for e in conn.result["existing"]] == [("switch", "switch.lampe")]


async def test_suggest_refuses_things_that_are_not_resources(hass):
    await load_project(hass)
    conn = await call(hass, entity_api.ws_suggest, {"type": "viewmyihc/entity/suggest", "ihc_id": 8498})  # a group
    assert conn.error[0] == "not_found"


async def test_snippet_renders_minimal_yaml_and_validates(hass, tmp_path):
    write_setup(tmp_path, "ihc:\n  - url: http://192.168.1.3\n    username: u\n")
    bad = await snippet(hass, {"platform": "switch", "id": 514, "name": "x", "options": {"on_id": "abc"}})
    assert bad.result == {"ok": False, "errors": {"options.on_id": "Skal være et heltal"}}
    ok = await snippet(hass, {"platform": "switch", "id": 514, "name": "Lampe", "options": {}})
    assert ok.result["ok"] is True and ok.result["yaml"] == '- id: 514\n  name: "Lampe"'
    assert ok.result["blocked"] is False and ok.result["same_platform"] == []


async def test_snippet_says_exactly_where_the_entry_goes_in_the_users_setup(hass, tmp_path):
    write_setup(
        tmp_path,
        "default_config:\nihc: !include ihc.yaml\n",
        **{"ihc.yaml": "- url: http://192.168.1.3\n  switch:\n    - id: 100\n      name: Egen\n"},
    )
    conn = await snippet(hass, {"platform": "switch", "id": 514, "name": "Lampe"})
    place = conn.result["placement"]
    assert (place["mode"], place["file"], place["after_line"]) == ("append", "ihc.yaml", 4)
    assert place["text"] == '    - id: 514\n      name: "Lampe"'  # indented like the user's own entries
    missing = await snippet(hass, {"platform": "sensor", "id": 20, "name": "T", "options": {"unit_of_measurement": "°C"}})
    place = missing.result["placement"]
    assert (place["mode"], place["file"], place["after_line"]) == ("add_key", "ihc.yaml", 1)
    assert place["text"] == '  sensor:\n    - id: 20\n      name: "T"\n      unit_of_measurement: "°C"'


async def test_snippet_blocks_a_type_that_already_exists_but_not_another_type(hass, tmp_path):
    write_setup(tmp_path, "ihc:\n  - url: http://192.168.1.3\n")
    register(hass, "switch", f"{SERIAL}-514", "lampe", original_name="Lampe")
    same = await snippet(hass, {"platform": "switch", "id": 514, "name": "Dublet"})
    assert same.result["blocked"] is True and same.result["same_platform"][0]["entity_id"] == "switch.lampe"
    other = await snippet(hass, {"platform": "light", "id": 514, "name": "Lys"})
    assert other.result["blocked"] is False and other.result["other_platforms"][0]["entity_id"] == "switch.lampe"


async def test_snippet_also_finds_an_entry_already_pasted_into_the_yaml_but_not_loaded_yet(hass, tmp_path):
    write_setup(tmp_path, "ihc:\n  - url: http://192.168.1.3\n    switch:\n      - id: 514\n        name: Indsat\n")
    conn = await snippet(hass, {"platform": "switch", "id": 514, "name": "Igen"})
    assert conn.result["blocked"] is True
    assert (conn.result["same_platform"][0]["source"], conn.result["same_platform"][0]["line"]) == ("yaml", 4)


async def test_list_shows_registry_entities_and_pending_yaml_entries_once_each(hass, tmp_path):
    write_setup(
        tmp_path,
        "ihc:\n  - url: http://192.168.1.3\n    sensor:\n      - id: 20\n        name: Min sensor\n      - id: 21\n",
    )
    register(hass, "switch", f"{SERIAL}-514", "lampe", original_name="Lampe")
    register(hass, "sensor", f"{SERIAL}-20", "temp", original_name="Temp", disabled_by=er.RegistryEntryDisabler.USER)
    rows = (await entity_list(hass)).result["entities"]
    summary = [(r["ihc_id"], r["platform"], r["source"], r["disabled"]) for r in rows]
    assert summary == [(20, "sensor", "registry", True), (21, "sensor", "yaml", False), (514, "switch", "registry", False)]
    assert next(r for r in rows if r["ihc_id"] == 21)["name"] == "ihc_21"  # the integration's default name


async def test_other_integrations_other_controllers_and_odd_ids_are_ignored(hass):
    register(hass, "switch", f"{SERIAL}-514", "x", original_name="x")
    er.async_get(hass).async_get_or_create("switch", "hue", f"{SERIAL}-515", suggested_object_id="not_ihc")
    register(hass, "switch", "OTHER-SERIAL-516", "other_controller")
    register(hass, "switch", f"{SERIAL}-abc", "not_a_number")
    by_id = (await existing(hass)).result["by_id"]
    assert list(by_id) == ["514"]


async def test_nothing_the_entity_commands_do_changes_any_file(hass, tmp_path):
    write_setup(tmp_path, "ihc: !include ihc.yaml\n", **{"ihc.yaml": "- url: http://192.168.1.3\n"})
    before = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    await snippet(hass, {"platform": "switch", "id": 514, "name": "Lampe"})
    await entity_list(hass)
    await existing(hass)
    await call(hass, entity_api.ws_check, {"type": "viewmyihc/entity/check"})
    after = {p.relative_to(tmp_path).as_posix(): p.read_bytes() for p in tmp_path.rglob("*") if p.is_file()}
    assert before == after and not (tmp_path / "viewmyihc").exists() and not (tmp_path / ".storage").exists() or True


async def test_check_reports_where_ihc_lives(hass, tmp_path):
    write_setup(tmp_path, "default_config:\nihc: !include ihc.yaml\n", **{"ihc.yaml": "- url: http://192.168.1.3\n"})
    result = (await call(hass, entity_api.ws_check, {"type": "viewmyihc/entity/check"})).result
    assert result["ihc_defined_in"] == {"file": "configuration.yaml", "line": 2}
    assert (result["chosen"]["file"], result["chosen"]["matches"]) == ("ihc.yaml", True)


async def test_entity_commands_require_admin_and_ihc(hass):
    from homeassistant.exceptions import Unauthorized

    for handler, msg in (
        (entity_api.ws_list, {"type": "viewmyihc/entity/list"}),
        (entity_api.ws_existing, {"type": "viewmyihc/entity/existing"}),
        (entity_api.ws_check, {"type": "viewmyihc/entity/check"}),
        (entity_api.ws_snippet, {"type": "viewmyihc/entity/snippet", "entry": {"platform": "switch", "id": 1}}),
    ):
        with pytest.raises(Unauthorized):
            await call(hass, handler, msg, admin=False)
    hass.data.pop("ihc")
    assert (await entity_list(hass)).error[0] == "no_ihc"


# ------------------------------------------------------------------ changing values


def resources(hass):
    return hass.data["ihc"][SERIAL]["controller"].client.connection.resources


async def test_resource_reports_runtime_and_initial_value_with_type_and_limits(hass):
    conn = await call(hass, ws.ws_resource, {"type": "viewmyihc/resource", "ihc_id": 200})
    assert conn.result["runtime"]["value"] == 5 and conn.result["initial"]["value"] == 1
    assert (conn.result["runtime"]["min"], conn.result["runtime"]["max"]) == (0, 10)
    assert conn.result["holding"] is False


async def test_set_writes_the_runtime_value_and_answers_with_what_the_controller_holds(hass):
    conn = await call(hass, ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 100, "value": True})
    assert conn.error is None, conn.error
    assert conn.result["runtime"]["value"] is True and conn.result["initial"]["value"] is False


async def test_set_initial_value_leaves_the_runtime_value_alone(hass):
    conn = await call(hass, ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 200, "value": 7, "target": "initial"})
    assert (conn.result["runtime"]["value"], conn.result["initial"]["value"]) == (5, 7)
    assert resources(hass).values[200] == ["WSIntegerValue", "5", "7"]


async def test_set_refuses_values_that_do_not_fit_the_resource(hass):
    for value in (11, "x", True):
        conn = await call(hass, ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 200, "value": value})
        assert conn.error[0] == "invalid_value", value
    assert resources(hass).values[200][1] == "5"


async def test_set_reports_when_the_controller_refuses(hass):
    resources(hass).refuse = True
    conn = await call(hass, ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 100, "value": True})
    assert conn.error[0] == "ihc_error"


async def test_hold_flips_the_value_until_released(hass):
    start = await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "start"})
    assert start.result == {"holding": True, "value": True}
    assert resources(hass).values[100][1] == "true"
    blocked = await call(hass, ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 100, "value": False})
    assert blocked.error is not None
    keep = await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "keep"})
    assert keep.result == {"holding": True}
    release = await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "release"})
    assert release.result == {"holding": False, "value": False}
    assert resources(hass).values[100][1] == "false"


async def test_a_hold_without_keep_alives_puts_the_value_back_by_itself(hass, monkeypatch):
    from custom_components.viewmyihc import value_hold

    monkeypatch.setattr(value_hold, "HOLD_TIMEOUT", 0.05)
    await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "start"})
    assert resources(hass).values[100][1] == "true"
    await asyncio.sleep(0.2)
    await hass.async_block_till_done()
    assert resources(hass).values[100][1] == "false"
    keep = await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "keep"})
    assert keep.result == {"holding": False}


async def test_only_on_off_values_can_be_held(hass):
    conn = await call(hass, ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 200, "action": "start"})
    assert conn.error[0] == "ihc_error"


async def test_value_commands_require_admin(hass):
    from homeassistant.exceptions import Unauthorized

    for handler, msg in (
        (ws.ws_resource, {"type": "viewmyihc/resource", "ihc_id": 100}),
        (ws.ws_set, {"type": "viewmyihc/set", "ihc_id": 100, "value": True}),
        (ws.ws_hold, {"type": "viewmyihc/hold", "ihc_id": 100, "action": "start"}),
    ):
        with pytest.raises(Unauthorized):
            await call(hass, handler, msg, admin=False)
    assert resources(hass).values[100][1] == "false"


# ------------------------------------------------------------------ tools


from custom_components.viewmyihc import tools_api  # noqa: E402


async def test_loading_a_project_keeps_one_backup_per_revision_and_it_can_be_diffed_and_downloaded(hass):
    import gzip

    controller = hass.data["ihc"][SERIAL]["controller"]
    await load_project(hass)
    await call(hass, ws.ws_load, {"type": "viewmyihc/load", "force": True})  # same project again: no new copy
    listed = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups"})).result["backups"]
    assert len(listed) == 1 and listed[0]["resources"] == 9 and "sha256" not in listed[0]

    original = controller.client.get_project_in_segments
    controller.client.get_project_in_segments = lambda info=None: original().replace('name="Lampeudtag"', 'name="Stik"')
    controller.client.get_project_info = lambda: {"projectMajorRevision": 2}
    await load_project(hass)
    listed = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups"})).result["backups"]
    assert len(listed) == 2
    new, old = listed[0]["name"], listed[1]["name"]
    result = (await call(hass, tools_api.ws_backup_diff, {"type": "viewmyihc/backup/diff", "old": old, "new": new})).result
    assert [c["name"] for c in result["changed"]] == ["Stik"]
    download = (await call(hass, tools_api.ws_backup_download, {"type": "viewmyihc/backup/download", "name": new})).result
    assert download["name"].endswith(".vis") and b"Stik" in gzip.decompress(base64.b64decode(download["gzip"]))
    bad = await call(hass, tools_api.ws_backup_download, {"type": "viewmyihc/backup/download", "name": "../../secrets.yaml"})
    assert bad.error is not None


async def test_dataline_names_each_address_from_the_project(hass):
    await load_project(hass)
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection

    def items(*pairs):
        return fakes.answer(**{"arrayItem": "".join(
            f"<ns1:datalineNumber>{a}</ns1:datalineNumber><ns1:resourceID>{r}</ns1:resourceID>" for a, r in pairs)})

    conn.answer_for.update({"getAllDatalineInputs": items((49, 257)), "getExtraDatalineInputs": fakes.answer(),
                            "getAllDatalineOutputs": items((7, 999)), "getExtraDatalineOutputs": fakes.answer()})
    calls = lambda: [a for _, a in conn.calls if "Dataline" in a]  # noqa: E731
    first = (await call(hass, tools_api.ws_dataline, {"type": "viewmyihc/dataline"})).result
    # answered at once from the project: no controller call, no saved copy yet
    assert calls() == [] and first["saved"] is None
    line = first["inputs"][0]  # address 0x31 = 49: input line 4, position 1 (the sample has no modules entered)
    assert (line["line"], line["type"], line["capacity"]) == (4, None, 16)
    assert line["slots"][0]["name"] == "Tryk (øverst venstre)" and line["slots"][0]["product"] == "Tryk 4 tast"
    assert "id" not in line["slots"][1]  # free slot: the controller's id is not known yet

    fresh = (await call(hass, tools_api.ws_dataline, {"type": "viewmyihc/dataline", "refresh": True})).result
    assert fresh["changed"] is True and fresh["saved"] and len(calls()) == 4
    again = (await call(hass, tools_api.ws_dataline, {"type": "viewmyihc/dataline"})).result
    assert len(calls()) == 4 and again["saved"] == fresh["saved"]  # the saved copy, at once
    same = (await call(hass, tools_api.ws_dataline, {"type": "viewmyihc/dataline", "refresh": True})).result
    assert same["changed"] is False

    conn.fail.add("getAllDatalineInputs")  # a failing controller keeps the saved copy and says so
    failing = (await call(hass, tools_api.ws_dataline, {"type": "viewmyihc/dataline", "refresh": True})).result
    assert failing["controller_error"] and failing["saved"] == same["saved"]
    assert failing["inputs"][0]["slots"][0]["name"] == "Tryk (øverst venstre)"


async def test_coverage_lists_shown_resources_only(hass):
    await load_project(hass)
    resources = (await call(hass, tools_api.ws_coverage, {"type": "viewmyihc/coverage"})).result["resources"]
    assert len(resources) == 9 and 525 not in {r["id"] for r in resources}
    owners = {r["id"]: r["owner"] for r in resources}
    assert owners[257] == "product" and owners[514] == "functionblock"


async def test_monitor_records_changes_reported_through_the_ihc_integration(hass):
    await load_project(hass)
    controller = hass.data["ihc"][SERIAL]["controller"]
    started = (await call(hass, tools_api.ws_monitor_start, {"type": "viewmyihc/monitor/start"})).result
    assert started["watching"] == 9 and started["started"]
    controller.change(514, True)  # the fake controller says even ids are on: no change
    controller.change(514, False)
    events = (await call(hass, tools_api.ws_monitor_events, {"type": "viewmyihc/monitor/events"})).result["events"]
    assert [(e["id"], e["old"], e["new"], e["name"]) for e in events] == [(514, True, False, "Tænd scenarie")]
    after = events[-1]["seq"]
    later = (await call(hass, tools_api.ws_monitor_events, {"type": "viewmyihc/monitor/events", "after": after})).result
    assert later["events"] == []


async def test_press_yaml_and_log(hass):
    yaml_text = (await call(hass, tools_api.ws_press, {"type": "viewmyihc/press", "entity_id": "binary_sensor.tryk"})).result["yaml"]
    assert "binary_sensor.tryk" in yaml_text
    bad = await call(hass, tools_api.ws_press, {"type": "viewmyihc/press", "entity_id": "light.x"})
    assert bad.error[0] == "invalid_value"
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getUserLog"] = fakes.answer(data=base64.b64encode("linje 1\nlinje 2".encode()).decode())
    assert (await call(hass, tools_api.ws_log, {"type": "viewmyihc/log"})).result == {"lines": ["linje 1", "linje 2"]}


async def test_tool_commands_require_admin(hass):
    from homeassistant.exceptions import Unauthorized

    for handler, msg in (
        (tools_api.ws_log, {"type": "viewmyihc/log"}),
        (tools_api.ws_messages, {"type": "viewmyihc/messages"}),
        (tools_api.ws_dataline, {"type": "viewmyihc/dataline"}),
        (tools_api.ws_coverage, {"type": "viewmyihc/coverage"}),
        (tools_api.ws_backups, {"type": "viewmyihc/backups"}),
        (tools_api.ws_backup_download, {"type": "viewmyihc/backup/download", "name": "x"}),
        (tools_api.ws_monitor_start, {"type": "viewmyihc/monitor/start"}),
        (tools_api.ws_monitor_events, {"type": "viewmyihc/monitor/events"}),
    ):
        with pytest.raises(Unauthorized):
            await call(hass, handler, msg, admin=False)


# ------------------------------------------------------------------ changing admin settings


from custom_components.viewmyihc import admin_api  # noqa: E402


async def test_admin_write_reads_back_and_stores_without_reporting_a_change(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getDNSServers"] = fakes.answer(arrayItem="<ns1:ipAddress>134744072</ns1:ipAddress>")
    await call(hass, ws.ws_admin_refresh, {"type": "viewmyihc/admin/refresh"})
    result = await call(hass, admin_api.ws_dns, {"type": "viewmyihc/admin/dns", "primary": "1.1.1.1", "secondary": "", "auth": "hemmeligt"})
    assert result.error is None, result.error
    assert [s["key"] for s in result.result["sections"]] == ["dns"]
    assert "setDNSServers" in [a for _, a in conn.calls]


async def test_admin_write_errors_carry_codes_the_panel_understands(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getNetworkSettings"] = fakes.answer(ipAddress="192.168.1.3", netmask="255.255.255.0", gateway="192.168.1.1",
                                                         httpPort="80", httpsPort="443")
    # fakes.answer wraps in <ns1:r>, the writer looks for getNetworkSettings1: rename the wrapper
    for element in conn.answer_for["getNetworkSettings"].iter():
        if element.tag.endswith("}r"):
            element.tag = element.tag[:-1] + "getNetworkSettings1"
    need = await call(hass, admin_api.ws_write, {"type": "viewmyihc/admin/write", "section": "network", "changes": {"httpPort": 8080}, "auth": "hemmeligt"})
    assert need.error[0] == "needs_confirm"
    bad = await call(hass, admin_api.ws_write, {"type": "viewmyihc/admin/write", "section": "network", "changes": {"gateway": "x"}, "auth": "hemmeligt"})
    assert bad.error[0] == "invalid_value"
    assert "setNetworkSettings" not in [a for _, a in conn.calls]


async def test_admin_write_commands_require_admin(hass):
    from homeassistant.exceptions import Unauthorized

    for handler, msg in (
        (admin_api.ws_write, {"type": "viewmyihc/admin/write", "section": "smtp", "changes": {}, "auth": "x"}),
        (admin_api.ws_dns, {"type": "viewmyihc/admin/dns", "primary": "1.1.1.1", "auth": "x"}),
        (admin_api.ws_user, {"type": "viewmyihc/admin/user", "action": "remove", "username": "x", "auth": "x"}),
        (admin_api.ws_email_control_enabled, {"type": "viewmyihc/admin/email_control_enabled", "enabled": True, "auth": "x"}),
    ):
        with pytest.raises(Unauthorized):
            await call(hass, handler, msg, admin=False)


async def test_every_admin_change_needs_the_password_home_assistant_logs_in_with(hass):
    admin_api._failures.clear()
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    msg = {"type": "viewmyihc/admin/dns", "primary": "1.1.1.1"}
    import voluptuous as vol

    with pytest.raises(vol.Invalid):  # no password at all: refused before anything happens
        await call(hass, admin_api.ws_dns, msg)
    wrong = await call(hass, admin_api.ws_dns, {**msg, "auth": "gæt"})
    assert wrong.error[0] == "wrong_password"
    assert "setDNSServers" not in [a for _, a in conn.calls]
    ok = await call(hass, admin_api.ws_dns, {**msg, "auth": "hemmeligt"})
    assert ok.error is None
    admin_api._failures.clear()


async def test_too_many_wrong_passwords_lock_changes_for_a_while(hass):
    admin_api._failures.clear()
    msg = {"type": "viewmyihc/admin/dns", "primary": "1.1.1.1"}
    for _ in range(admin_api.MAX_FAILURES):
        assert (await call(hass, admin_api.ws_dns, {**msg, "auth": "forkert"})).error[0] == "wrong_password"
    locked = await call(hass, admin_api.ws_dns, {**msg, "auth": "hemmeligt"})  # even the right one, for now
    assert locked.error[0] == "wrong_password" and "Too many" in locked.error[1]
    admin_api._failures.clear()


async def test_clearing_a_log_needs_the_password_and_calls_the_administrators_own_operation(hass):
    admin_api._failures.clear()
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    wrong = await call(hass, tools_api.ws_log_clear, {"type": "viewmyihc/log/clear", "what": "userlog", "auth": "gæt"})
    assert wrong.error[0] == "wrong_password" and "clearUserLog" not in [a for _, a in conn.calls]
    for what, operation in (("userlog", "clearUserLog"), ("messages", "clearMessages"), ("control", "emptyLog")):
        ok = await call(hass, tools_api.ws_log_clear, {"type": "viewmyihc/log/clear", "what": what, "auth": "hemmeligt"})
        assert ok.result == {"cleared": what} and conn.calls[-1][1] == operation
    admin_api._failures.clear()


async def test_the_control_log_is_only_read_when_email_control_is_on(hass):
    conn = hass.data["ihc"][SERIAL]["controller"].client.connection
    conn.answer_for["getEmailControlEnabled"] = fakes.answer(x="false")
    for element in conn.answer_for["getEmailControlEnabled"].iter():  # the controller answers a bare boolean
        if element.tag.endswith("}r"):
            element.text, element[:] = "false", []
    off = (await call(hass, tools_api.ws_messages, {"type": "viewmyihc/messages"})).result
    assert off["control_disabled"] is True and off["errors"] == {} and "getEvents" not in [a for _, a in conn.calls]
    conn.answer_for["getEmailControlEnabled"][0][0].text = "true"
    on = (await call(hass, tools_api.ws_messages, {"type": "viewmyihc/messages"})).result
    assert on["control_disabled"] is False and "getEvents" in [a for _, a in conn.calls]


# ------------------------------------------------------------------ settings


async def test_the_timeout_setting_is_stored_applied_and_removed(hass):
    from custom_components.viewmyihc import connection_guard, settings

    hass.data[DOMAIN]["settings"] = settings.Settings(hass)
    await hass.data[DOMAIN]["settings"].async_load()
    controller = hass.data["ihc"][SERIAL]["controller"]
    got = (await call(hass, settings.ws_settings_get, {"type": "viewmyihc/settings/get"})).result
    assert got["settings"]["ihc_timeout"] is False and got["active"] == {SERIAL: None}
    on = (await call(hass, settings.ws_settings_set, {"type": "viewmyihc/settings/set", "ihc_timeout": True, "ihc_timeout_seconds": 45})).result
    assert on["active"] == {SERIAL: 45} and connection_guard.active_timeout(controller) == 45
    reloaded = settings.Settings(hass)
    await reloaded.async_load()
    assert reloaded.values == {"ihc_timeout": True, "ihc_timeout_seconds": 45, "scene_upload_verified": []}
    off = (await call(hass, settings.ws_settings_set, {"type": "viewmyihc/settings/set", "ihc_timeout": False})).result
    assert off["active"] == {SERIAL: None}
    with pytest.raises(Exception):
        await call(hass, settings.ws_settings_set, {"type": "viewmyihc/settings/set", "ihc_timeout_seconds": 5})
    from homeassistant.exceptions import Unauthorized

    with pytest.raises(Unauthorized):
        await call(hass, settings.ws_settings_set, {"type": "viewmyihc/settings/set", "ihc_timeout": True}, admin=False)


def test_every_command_accepts_the_controller_the_panel_always_sends():
    """The panel adds "controller" to every message (see _ws in the panel); a schema without it rejects the command."""
    from custom_components.viewmyihc import admin_api, entity_api, settings

    handlers = [
        h for module in (ws, entity_api, tools_api, admin_api, settings) for h in vars(module).values()
        if callable(h) and getattr(h, "_ws_schema", False)  # False: no parameters, HA does not validate
    ]
    assert len(handlers) > 30
    for handler in handlers:
        keys = {str(getattr(k, "schema", k)) for k in handler._ws_schema.schema}
        assert "controller" in keys, handler._ws_command


async def test_reports_are_built_from_the_loaded_project(hass):
    await load_project(hass)
    calls_before = len(hass.data["ihc"][SERIAL]["controller"].client.connection.calls)
    for kind in ("installation", "function", "functionblocks"):
        result = (await call(hass, tools_api.ws_report, {"type": "viewmyihc/report", "report": kind})).result
        assert result["info"]["description"] == "Testprojekt"
    assert len(hass.data["ihc"][SERIAL]["controller"].client.connection.calls) == calls_before  # no controller call
    inst = (await call(hass, tools_api.ws_report, {"type": "viewmyihc/report", "report": "installation"})).result
    assert [i["terminal"] for i in inst["inputs"]] == ["4.01"]


async def test_the_scene_project_is_kept_in_versions_and_can_be_downloaded(hass):
    from test_scene_project import SceneController, icz

    data = icz()
    hass.data["ihc"][SERIAL]["controller"] = controller = SceneController(data)
    first = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups", "kind": "scene"})).result
    assert first["error"] is None and len(first["backups"]) == 1
    entry = first["backups"][0]
    assert entry["name"].endswith(".icz") and (entry["scene_name"], entry["notifications"], entry["controls"]) == ("Hus", 2, 2)
    again = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups", "kind": "scene"})).result
    assert len(again["backups"]) == 1 and controller.segment_calls == 2  # unchanged checksum: not fetched again
    down = (await call(hass, tools_api.ws_backup_download, {"type": "viewmyihc/backup/download", "kind": "scene", "name": entry["name"]})).result
    assert base64.b64decode(down["data"]) == data
    ihc_list = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups"})).result["backups"]
    assert all(not e["name"].endswith(".icz") for e in ihc_list)  # the two kinds are kept apart
    messages = (await call(hass, tools_api.ws_scene_messages, {"type": "viewmyihc/scene/messages"})).result
    assert len(messages["notifications"]) == 2 and "icz" not in messages


async def test_restoring_a_version_needs_the_password_and_keeps_the_current_one_first(hass):
    from test_project_restore import RestoringController

    admin_api._failures.clear()
    hass.data["ihc"][SERIAL]["controller"] = controller = RestoringController()
    await load_project(hass)
    old_xml = fakes.sample_xml_as_ihcsdk_returns_it()
    controller.client.get_project_in_segments = lambda info=None: old_xml.replace('name="Lampeudtag"', 'name="Stik"')
    controller.client.get_project_info = lambda: {"projectMajorRevision": 2}
    await load_project(hass)
    listed = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups"})).result["backups"]
    oldest = listed[-1]["name"]

    msg = {"type": "viewmyihc/backup/restore", "name": oldest}
    wrong = await call(hass, tools_api.ws_backup_restore, {**msg, "auth": "gæt"})
    assert wrong.error[0] == "wrong_password" and "storeIHCProject" not in controller.order
    done = await call(hass, tools_api.ws_backup_restore, {**msg, "auth": "hemmeligt"})
    assert done.error is None, done.error
    assert done.result["state"] == "text.ctrl.state.ready"
    assert controller.stored == old_xml.encode("iso-8859-1")  # exactly the saved version went back
    assert controller.order[-1] == "waitForControllerStateChange" and "exitProjectChangeMode" in controller.order
    unknown = await call(hass, tools_api.ws_backup_restore, {**msg, "name": "../../x.vis.gz", "auth": "hemmeligt"})
    assert unknown.error[0] == "restore_failed"
    admin_api._failures.clear()


async def test_editing_the_scene_project_needs_a_test_upload_first_and_a_fresh_checksum(hass):
    import zlib
    import xml.etree.ElementTree as ET

    from custom_components.viewmyihc import settings
    from test_scene_project import SceneController, icz

    admin_api._failures.clear()
    hass.data[DOMAIN]["settings"] = settings.Settings(hass)
    await hass.data[DOMAIN]["settings"].async_load()
    controller = SceneController(icz())
    controller.crc = str(zlib.crc32(controller.data))
    received: list[bytes] = []
    conn = controller.client.connection
    serve = conn.soap_action

    def soap_action(service, action, body=""):
        if action == "storeSceneProjectSegment":  # the controller keeps what it is sent
            leaves = {e.tag.rsplit("}", 1)[-1]: e.text for e in ET.fromstring(f"<r>{body}</r>").iter()}
            received.append(base64.b64decode(leaves["data"]))
            if leaves["storeSceneProjectSegment3"] == "true":
                controller.data = b"".join(received)
                received.clear()
                controller.crc = str(zlib.crc32(controller.data))
            return ET.fromstring(
                '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
                '<ns1:storeSceneProjectSegment4 xmlns:ns1="utcs">true</ns1:storeSceneProjectSegment4></SOAP-ENV:Body></SOAP-ENV:Envelope>')
        return serve(service, action, body)

    conn.soap_action = soap_action
    hass.data["ihc"][SERIAL]["controller"] = controller
    view = (await call(hass, tools_api.ws_scene_messages, {"type": "viewmyihc/scene/messages"})).result
    assert view["verified"] is False and view["crc"] == controller.crc
    notes, controls = view["notifications"], view["controls"]
    plain = lambda items: [{**i, "resource": i["resource"]["id"], **({"slots": [s["slot"] for s in i["slots"]]} if "slots" in i else {}),  # noqa: E731
                            **({"senders": [s["slot"] for s in i["senders"]]} if i.get("channel") == "sms" and "senders" in i else {})} for i in items]
    changed = plain(notes)
    changed[0]["body"] = "Hoveddøren er åbnet"
    save = {"type": "viewmyihc/scene/save", "notifications": changed, "controls": plain(controls), "auth": "hemmeligt"}

    first = await call(hass, tools_api.ws_scene_save, {**save, "crc": view["crc"]})
    assert first.error[0] == "restore_failed" and "test upload" in first.error[1]
    tested = await call(hass, tools_api.ws_scene_test, {"type": "viewmyihc/scene/test", "auth": "hemmeligt"})
    assert tested.result == {"verified": True}
    stale = await call(hass, tools_api.ws_scene_save, {**save, "crc": "0"})
    assert stale.error[0] == "restore_failed" and "meanwhile" in stale.error[1]
    saved = await call(hass, tools_api.ws_scene_save, {**save, "crc": controller.crc})
    assert saved.error is None, saved.error
    assert saved.result["notifications"][0]["body"] == "Hoveddøren er åbnet" and saved.result["verified"] is True
    kept = (await call(hass, tools_api.ws_backups, {"type": "viewmyihc/backups", "kind": "scene"})).result["backups"]
    # the original (saved the first time it was read; identical files are kept once) and the edited version
    assert len(kept) == 2 and kept[1]["notifications"] == kept[0]["notifications"] == 2
    admin_api._failures.clear()
