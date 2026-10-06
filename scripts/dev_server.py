"""Local development harness: run the panel in a normal browser against a project file.

    python scripts/dev_server.py [path/to/project.vis] [--port 8765]

It speaks the same websocket-style commands as ``websocket_api.py`` (over ``POST /ws``) using the real
parser, but invents live values and admin data, so the real controller is never contacted.
"""

from __future__ import annotations

import argparse
import hashlib
import importlib.util
import json
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COMPONENT = ROOT / "custom_components" / "viewmyihc"

spec = importlib.util.spec_from_file_location("project_parser", COMPONENT / "project_parser.py")
parser = importlib.util.module_from_spec(spec)
sys.modules["project_parser"] = parser
spec.loader.exec_module(parser)

spec2 = importlib.util.spec_from_file_location("entity_config", COMPONENT / "entity_config.py")
ec = importlib.util.module_from_spec(spec2)
sys.modules["entity_config"] = ec
spec2.loader.exec_module(ec)

import os
import re

_VERSION = re.search(r'VERSION = "([^"]+)"', (COMPONENT / "const.py").read_text(encoding="utf-8")).group(1)
# VMI_FAKE_BACKEND_VERSION=0.1.0 or =none imitates an old backend, to try the panel's version warning
_FAKE = os.environ.get("VMI_FAKE_BACKEND_VERSION")

PROJECT: parser.Project | None = None
SNAPSHOT: dict | None = None          # {"saved": epoch, "sections": {key: section}} - the "saved state"
DEV = {"mutate": False, "fail": False, "delay": 1.5}  # toggled through /ws (viewmyihc/dev/*) to try the panel
# the setup check runs for real, against a small sample configuration (scripts/dev_config); nothing is written
_pkg = __import__("types").ModuleType("vmi")
_pkg.__path__ = [str(COMPONENT)]
sys.modules["vmi"] = _pkg
cl = importlib.import_module("vmi.config_locator")
vparser = importlib.import_module("vmi.project_parser")
vdiff = importlib.import_module("vmi.project_diff")
vpress = importlib.import_module("vmi.press_automation")
vlayout = importlib.import_module("vmi.dataline_layout")
vreport = importlib.import_module("vmi.report_builder")
vwiring = importlib.import_module("vmi.wiring_map")
vscene = importlib.import_module("vmi.scene_project")
import io
import zipfile
import base64
import gzip
import random
DEV_CONFIG = ROOT / "scripts" / "dev_config"
spec3 = importlib.util.spec_from_file_location("admin_diff", COMPONENT / "admin_diff.py")
ad = importlib.util.module_from_spec(spec3)
sys.modules["admin_diff"] = ad
spec3.loader.exec_module(ad)
SERIAL = "DEV-0001"
FAKE_REGISTRY = [
    {"id": 22337626, "platform": "binary_sensor", "entity_id": "binary_sensor.stue_tryk", "name": "Stue tryk", "disabled": False},
    {"id": 22338394, "platform": "light", "entity_id": "light.koekken_loft", "name": "Køkken loft", "disabled": True},
]
AREAS = [{"id": "kitchen", "name": "Køkken"}, {"id": "living", "name": "Stue"}, {"id": "bath", "name": "Bad"}]
CLASSES = ["door", "garage_door", "window", "motion", "occupancy", "smoke", "moisture", "opening", "light", "problem"]


def fake_value(node_id: int, kind: str):
    """Deterministic pseudo-random value that changes every ~10 seconds."""
    tick = int(time.time() // 10)
    h = int(hashlib.md5(f"{node_id}:{tick}".encode()).hexdigest(), 16)
    if kind == "bool":
        return h % 3 == 0
    if kind == "temperature":
        return 17 + (h % 800) / 100
    if kind in ("time", "timertime"):
        return f"{h % 24:02d}:{h // 24 % 60:02d}:00"
    if kind == "timer":
        return (h % 600) * 1000
    if kind == "integer":
        return h % 100
    if kind == "enum":
        return ("Ur 1", "Ur 2", "Ingen Ur funktion")[h % 3]
    if kind == "weekday":
        return ("Mandag", "Tirsdag", "Onsdag", "Torsdag", "Fredag", "Lørdag", "Søndag")[h % 7]
    if kind == "date":
        return "2026-10-31"
    return h % 2


# Values changed in the panel (set / hold), per resource id: {"runtime": info, "initial": info}
CHANGED: dict[int, dict] = {}
HELD: dict[int, bool] = {}
_WS_TYPE = {"bool": "WSBooleanValue", "temperature": "WSFloatingPointValue", "integer": "WSIntegerValue",
            "timer": "WSTimerValue", "timertime": "WSTimerValue", "time": "WSTimeValue", "enum": "WSEnumValue"}


def _info(node_id: int, kind: str, value) -> dict:
    ws_type = _WS_TYPE.get(kind, "WSWeekdayValue")
    info = {"type": ws_type, "editable": kind in _WS_TYPE, "value": value}
    if kind == "temperature":
        info.update(min=-50.0, max=100.0)
    if kind == "integer":
        info.update(min=0, max=255)
    if kind == "enum":
        values = (PROJECT.detail(node_id).get("enum") or {}).get("values", [])
        hit = next((v for v in values if v["name"] == value), values[0] if values else None)
        info.update(value=hit and hit["id"], name=hit and hit["name"], definition=1)
    return info


def dev_state(node_id: int) -> dict:
    kind = PROJECT.kinds([node_id]).get(node_id)
    if kind is None:
        raise KeyError("Not a resource")
    if node_id not in CHANGED:
        CHANGED[node_id] = {"runtime": _info(node_id, kind, fake_value(node_id, kind)),
                            "initial": _info(node_id, kind, fake_value(node_id + 1, kind))}
    return CHANGED[node_id]


def poll_value(info: dict):
    return info["name"] if info["type"] == "WSEnumValue" else info["value"]


ADMIN = [
    {"key": "system", "title": "System", "operation": "getSystemInfo", "data": {
        "brand": "LK", "version": "3.9.1", "serialNumber": "1234567890", "hwRevision": "2.0", "swDate": "2019-04-01",
        "uptime": "2114820000"}},
    {"key": "time", "title": "Tid og sommertid", "operation": "getSettings", "data": {
        "synchroniseTimeAgainstServer": "true", "useDST": "true", "gmtOffsetInHours": "1", "serverName": "dk.pool.ntp.org",
        "syncIntervalInHours": "24", "timeAndDateInUTC": {"monthWithJanuaryAsOne": "10", "day": "6", "hours": "9",
        "year": "2026", "seconds": "0", "minutes": "0"}}},
    {"key": "local_time", "title": "Lokal tid", "operation": "getCurrentLocalTime", "data": {
        "monthWithJanuaryAsOne": "10", "day": "6", "hours": "11", "year": "2026", "seconds": "0", "minutes": "0"}},
    {"key": "uptime", "title": "Oppetid", "operation": "getUptime", "data": "2114820000"},
    {"key": "users", "title": "Brugere", "operation": "getUsers", "data": [
        {"username": "admin", "password": "***", "email": "", "firstname": "Administrator", "lastname": "", "phone": "",
         "group": {"type": "text.usermanager.group_administrators"}},
        {"username": "anna", "password": "***", "email": "anna@example.org", "firstname": "Anna", "lastname": "Hansen", "phone": "12345678",
         "group": {"type": "text.usermanager.group_administrators"}}]},
    {"key": "network", "title": "Netværk", "operation": "getNetworkSettings", "data": {
        "ipAddress": "192.168.1.3", "netmask": "255.255.255.0", "gateway": "192.168.1.1", "httpPort": "80", "httpsPort": "443"}},
    {"key": "dns", "title": "DNS", "operation": "getDNSServers", "data": [{"ipAddress": "134744072"}, {"ipAddress": "-1062731519"}]},
    {"key": "web_access", "title": "Webadgang", "operation": "getWebAccessControl", "data": {
        "m_usbLoginRequired_usb": "false", "m_administrator_usb": "true", "m_administrator_internal": "true", "m_administrator_external": "false", "m_treeview_usb": "true", "m_treeview_internal": "true", "m_treeview_external": "false", "m_sceneview_usb": "true", "m_sceneview_internal": "true", "m_sceneview_external": "false", "m_scenedesign_usb": "true", "m_scenedesign_internal": "true", "m_scenedesign_external": "false", "m_serverstatus_usb": "true", "m_serverstatus_internal": "true", "m_serverstatus_external": "false", "m_ihcvisual_usb": "true", "m_ihcvisual_internal": "true", "m_ihcvisual_external": "false", "m_onlinedocumentation_usb": "true", "m_onlinedocumentation_internal": "true", "m_onlinedocumentation_external": "false", "m_websceneview_usb": "true", "m_websceneview_internal": "true", "m_websceneview_external": "false", "m_openapi_usb": "true", "m_openapi_internal": "true", "m_openapi_external": "false", "m_openapi_used": "false"}},
    {"key": "smtp", "title": "E-mail (SMTP)", "operation": "getSMTPSettings", "data": {
        "hostname": "smtp.example.org", "hostport": "25", "username": "ihc", "password": "***"}},
    {"key": "email_control", "title": "E-mail kontrol", "operation": "getEmailControlSettings", "data": {
        "enabled": "false", "serverIPAddress": "", "serverPortNumber": "110", "pop3Username": "", "pop3Password": "***",
        "emailAddress": "", "pollInterval": "10", "removeEmailsAfterUsage": "true"}},
    {"key": "sms_modem", "title": "SMS-modem", "operation": "getSMSModemSettings", "data": {
        "m_powerupMessage": "false", "m_powerdownMessage": "false", "m_relaySMS": "true"}},
    {"key": "sms_status", "title": "SMS-modem: status", "operation": "getSMSModemStatus", "data": {
        "modemStatus": "text.sms_modem.ok", "mobileNumber": "N.A.", "antennaCoverage": "text.sms_modem.antenna_coverage.high",
        "mobileOperator": "TELMORE"}},
]


def existing(setup: dict) -> dict:
    """Registry stand-in plus the user's YAML entries, like entity_api.existing_entities()."""
    found: dict = {}
    for item in FAKE_REGISTRY:
        found.setdefault(item["id"], []).append({k: v for k, v in item.items() if k != "id"} | {"source": "registry", "area_id": None})
    for platform, info in setup.get("platforms", {}).items():
        for entry in info["entries"]:
            known = found.setdefault(entry["id"], [])
            if not any(k["platform"] == platform for k in known):
                known.append({"source": "yaml", "entity_id": None, "platform": platform, "name": entry["name"] or f"ihc_{entry['id']}",
                              "disabled": False, "area_id": None, "file": entry["file"], "line": entry["line"]})
    return found


def handle(msg: dict):
    global PROJECT, SNAPSHOT
    kind = msg["type"].split("/", 1)[1]
    if kind == "status":
        result = {"controllers": [{"serial": "DEV-0001", "loaded": PROJECT is not None, "ha_user": "admin"}]}
        if _FAKE != "none":
            result["version"] = _FAKE or _VERSION
        return result
    if kind == "load":
        return {"controller": "DEV-0001", "info": PROJECT.info}
    if kind == "children":
        return PROJECT.children(msg["parent"], msg.get("view", "all"))
    if kind == "detail":
        detail = PROJECT.detail(msg["ihc_id"])
        if detail is None:
            raise KeyError("Unknown node")
        return detail
    if kind == "search":
        return PROJECT.search(msg["query"], msg.get("view", "all"))
    if kind == "values":
        kinds = PROJECT.kinds(msg["ids"])
        return {str(i): poll_value(CHANGED[i]["runtime"]) if i in CHANGED else fake_value(i, k) for i, k in kinds.items()}
    if kind == "resource":
        return {**dev_state(msg["ihc_id"]), "holding": msg["ihc_id"] in HELD}
    if kind == "set":
        state, target, value = dev_state(msg["ihc_id"]), msg.get("target", "runtime"), msg["value"]
        info = state[target]
        if info["type"] == "WSEnumValue":
            values = PROJECT.detail(msg["ihc_id"])["enum"]["values"]
            info["name"] = next(v["name"] for v in values if v["id"] == value)
        if info.get("max") is not None and not info["min"] <= value <= info["max"]:
            raise ValueError(f"The value must be between {info['min']} and {info['max']}")
        info["value"] = value
        return {**state, "holding": False}
    if kind == "hold":
        state, rid = dev_state(msg["ihc_id"]), msg["ihc_id"]
        if msg["action"] == "start":
            HELD.setdefault(rid, state["runtime"]["value"])
            state["runtime"]["value"] = not HELD[rid]
            return {"holding": True, "value": state["runtime"]["value"]}
        if msg["action"] == "keep":
            return {"holding": rid in HELD}
        original = HELD.pop(rid, None)
        if original is not None:
            state["runtime"]["value"] = original
        return {"holding": False, "value": original}
    if kind == "admin/snapshot":
        if SNAPSHOT is None:
            return {"sections": None, "saved": None, "ha_user": "admin"}
        return {"sections": [dict(v, fetched=SNAPSHOT["saved"]) for v in SNAPSHOT["sections"].values()], "saved": SNAPSHOT["saved"],
                "ha_user": "admin"}
    if kind == "admin/refresh":
        time.sleep(DEV["delay"])  # the real controller needs a few seconds for 11 calls
        if DEV["fail"]:
            raise RuntimeError("getUsers failed (no answer from the controller)")
        fresh = json.loads(json.dumps(ADMIN))
        for section in fresh:
            if section["key"] == "time":
                section["data"]["timeAndDateInUTC"]["seconds"] = str(int(time.time()) % 60)  # volatile clock
            if section["key"] == "system":
                section["data"]["uptime"] = f"{int(time.time()) % 50} dage"  # volatile: must never count as a change
            if DEV["mutate"] and section["key"] == "time":
                section["data"]["timeServer"] = "ntp.example.org"
                section["data"]["useDaylightSaving"] = "false"
            if DEV["mutate"] and section["key"] == "users":
                section["data"][1]["firstname"] = "Anna Hansen"
                section["data"].append({"username": "gæst", "firstname": "Gæst", "password": "***", "group": "Bruger"})
        first = SNAPSHOT is None
        show, keep, changes = ad.merge_refresh({} if first else SNAPSHOT["sections"], fresh)
        now = time.time()
        SNAPSHOT = {"saved": now, "sections": keep}
        return {"first": first, "changes": changes, "sections": [dict(v, fetched=now) for v in show],
                "errors": [{"key": v["key"], "error": v["error"]} for v in show if "error" in v], "fetched": now}
    if kind == "dev/mutate":
        DEV["mutate"] = not DEV["mutate"]
        return dict(DEV)
    if kind == "dev/fail":
        DEV["fail"] = not DEV["fail"]
        return dict(DEV)
    if kind == "dev/reset":
        SNAPSHOT = None
        return {}
    if kind in ("entity/list", "entity/existing", "entity/suggest", "entity/snippet", "entity/check"):
        setup = cl.check_setup(DEV_CONFIG, "http://192.168.1.3")
        found = existing(setup)
        if kind == "entity/check":
            return setup
        if kind == "entity/existing":
            return {"by_id": {str(i): v for i, v in found.items()}, "count": len(found)}
        if kind == "entity/list":
            rows = [dict(item, ihc_id=i) for i, items in found.items() for item in items]
            rows.sort(key=lambda r: (r["platform"], r["ihc_id"]))
            return {"entities": rows, "count": len(rows)}
        if kind == "entity/suggest":
            detail = PROJECT.detail(msg["ihc_id"])
            if detail is None or not detail.get("kind"):
                raise KeyError("Not a resource")
            result = ec.suggest(detail)
            result["device_classes"] = CLASSES
            result["existing"] = found.get(msg["ihc_id"], [])
            return result
        try:
            entry = ec.validate_entry(msg["entry"], set(CLASSES))
        except ec.EntityConfigError as err:
            return {"ok": False, "errors": err.errors}
        same = [e for e in found.get(entry["id"], []) if e["platform"] == entry["platform"]]
        return {"ok": True, "yaml": ec.render_entry(entry), "placement": cl.placement(setup, entry["platform"], entry),
                "same_platform": same, "other_platforms": [e for e in found.get(entry["id"], []) if e["platform"] != entry["platform"]],
                "blocked": bool(same)}
    # ---- changing admin settings (password "dev"; changes go into the invented data)
    if kind.startswith("admin/") and kind not in ("admin/snapshot", "admin/refresh"):
        if msg.get("auth") != "dev":
            raise DevError("wrong_password", "Wrong password")
        section_key = {"admin/dns": "dns", "admin/user": "users", "admin/email_control_enabled": "email_control"}.get(kind, msg.get("section"))
        section = next(x for x in ADMIN if x["key"] == section_key)
        data = section["data"]
        if kind == "admin/write":
            if section_key == "network" and not msg.get("confirm") and any(str(v) != str(data.get(k)) for k, v in msg["changes"].items()):
                raise DevError("needs_confirm", "This change can cut the connection to the controller")
            for k, v in msg["changes"].items():
                data[k] = "***" if k in ("password", "pop3Password") else ("true" if v is True else "false" if v is False else str(v))
        elif kind == "admin/dns":
            def number(ip):
                a, b, c, d = (int(x) for x in ip.split(".")) if ip else (0, 0, 0, 0)
                n = (a << 24) | (b << 16) | (c << 8) | d
                return str(n - (1 << 32) if n >= 1 << 31 else n)
            section["data"] = [{"ipAddress": number(msg["primary"])}, {"ipAddress": number(msg.get("secondary", ""))}]
        elif kind == "admin/email_control_enabled":
            data["enabled"] = "true" if msg["enabled"] else "false"
        elif kind == "admin/user":
            if msg["action"] == "remove":
                if msg["username"] == "admin":
                    raise DevError("invalid_value", "This is the user Home Assistant logs in with and cannot be removed here")
                section["data"] = [u for u in data if u["username"] != msg["username"]]
            elif msg["action"] == "add":
                if not msg.get("password"):
                    raise DevError("invalid_value", "Required")
                data.append({"username": msg["username"], "password": "***", **{k: "" for k in ("email", "firstname", "lastname", "phone")},
                             **msg.get("details", {}), "group": {"type": "text.usermanager.group_administrators"}})
            else:
                next(u for u in data if u["username"] == msg["username"]).update(msg.get("details", {}))
        if SNAPSHOT is not None:
            SNAPSHOT["sections"][section_key] = dict(section)
        return {"changed": [], "sections": [dict(section, fetched=time.time())]}
    # ---- tools (all invented; the real controller is never contacted)
    if kind == "log":
        return {"lines": [f"2026-10-0{d} 0{h}:1{h}:00  " + text for d, h, text in (
            (5, 7, "Bruger admin logget ind fra 192.168.1.20"), (5, 8, "Lavt batteri: Trådløs tryk, Køkken (sn 1234)"),
            (6, 1, "Tast ikke tilknyttet: indgang 0x31"), (6, 2, "Controller startet"), (6, 3, "Login fejlede: bruger anna"))]}
    if kind == "messages":
        return {"errors": {}, "notifications": [
            {"date": {"year": "2026", "monthWithJanuaryAsOne": "10", "day": "5", "hours": "21", "minutes": "4", "seconds": "0"},
             "notificationType": "text.control.sms_type", "recipient": "+45 ** ** ** 12", "sender": "IHC", "subject": "Alarm: Bevægelse i stue",
             "body": "Alarmen er udløst", "delivered": "true"},
            {"date": {"year": "2026", "monthWithJanuaryAsOne": "10", "day": "6", "hours": "7", "minutes": "30", "seconds": "0"},
             "notificationType": "text.control.email_type", "recipient": "anna@example.org", "sender": "ihc@example.org", "subject": "Varme slukket",
             "body": "", "delivered": "false"}],
            "control": [{"date": {"year": "2026", "monthWithJanuaryAsOne": "10", "day": "4", "hours": "18", "minutes": "0", "seconds": "0"},
                         "controlType": "text.control.sms_type", "logEntryType": "1", "senderAddress": {"address": "+45 ** ** ** 12"},
                         "triggerString": "VARME TIL", "authenticationTypeAsString": "text.emailcontrol.authorization.sender_based", "actionTypeAsString": "text.control_log.executed_event"}], "control_disabled": False}
    if kind in ("settings/get", "settings/set"):
        for key in ("ihc_timeout", "ihc_timeout_seconds"):
            if key in msg:
                SETTINGS[key] = msg[key]
        return {"settings": dict(SETTINGS), "active": {"DEV-0001": SETTINGS["ihc_timeout_seconds"] if SETTINGS["ihc_timeout"] else None},
                "limits": {"min": 15, "max": 300}}
    if kind == "scene/messages":
        rids = [f"{n.id:x}" for n in PROJECT.nodes.values() if n.is_resource and not n.hidden][:4] + ["0"] * 4
        icw = f"""<icwproject version="2" name="Demo"><scenes><scene name="Stue"/></scenes>
          <notifications><notification event="text.inactive_to_active_event"><resource rid="{rids[0]}"/>
            <message recipient="anna@example.org;bo@example.org"><subject>Alarm</subject><body>Døren er åbnet</body></message></notification></notifications>
          <smsnotifications><smsnotification event="text.active_to_inactive_event"><resource rid="{rids[1]}"/>
            <message recipient="110000000000000000000000000000"><subject/><body>Varmen er slukket</body></message></smsnotification></smsnotifications>
          <emailcontrols><emailcontrol><resource rid="{rids[2]}"/><action type="text.emailcontrol.off_to_on_action"/>
            <executionconfirmation><body>Varmen er tændt</body></executionconfirmation>
            <authorization type="text.emailcontrol.authorization.three_way"><triggersubject>VARME TIL</triggersubject>
            <confirmationaddress>anna@example.org</confirmationaddress></authorization></emailcontrol></emailcontrols>
          <smscontrols><smscontrol><resource rid="{rids[3]}"/><action type="text.emailcontrol.pulse_action"/>
            <authorization type="text.emailcontrol.authorization.sender_based"><triggersubject>PORT</triggersubject>
            <acceptsenderaddress>100000000000000000000000000000</acceptsenderaddress></authorization></smscontrol></smscontrols></icwproject>"""
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("project.icw", icw.encode("utf-8"))
        parsed = vscene.parse(buffer.getvalue())
        book = {1: {"number": "+45 11 22 33 44", "label": "Anna"}, 2: {"number": "+45 55 66 77 88", "label": "Bo"}}
        def res(rid):
            node = PROJECT.nodes.get(rid)
            return {"id": rid, "name": node.name if node else None, "label": PROJECT.label(rid) if node else None}
        slots = lambda ns: [{"slot": n, **book.get(n, {"number": "", "label": ""})} for n in ns]  # noqa: E731
        return {**{k: v for k, v in parsed.items() if k not in ("notifications", "controls")},
                "notifications": [{**n, "resource": res(n["resource"]), "slots": slots(n["slots"])} for n in parsed["notifications"]],
                "controls": [{**c, "resource": res(c["resource"]), "senders": slots(c["senders"]) if c["channel"] == "sms" else c["senders"]}
                             for c in parsed["controls"]]}
    if kind == "map":
        return {**vwiring.wiring(PROJECT), "info": PROJECT.info, "serial": "DEV-0001"}
    if kind == "map/images":
        folder = DEV.get("images")
        out = {}
        for identifier in msg["identifiers"]:
            path = folder / f"{identifier.lower()}.jpg" if folder else None
            out[identifier] = ("data:image/jpeg;base64," + base64.b64encode(path.read_bytes()).decode()) if path and path.exists() else None
        return {"images": out}
    if kind == "report":
        if not any(PROJECT.modules.values()):
            PROJECT.modules = {"inputs": {4: {"type": "Input 24", "location": "Tavle 3"}}, "outputs": {}}
        builder = vreport.REPORTS[msg["report"]]
        result = builder(PROJECT, msg.get("only_marked", True)) if msg["report"] == "function" else builder(PROJECT)
        return {**result, "info": PROJECT.info}
    if kind == "backup/restore":
        if msg.get("auth") != "dev":
            raise DevError("wrong_password", "Wrong password")
        time.sleep(DEV["delay"] * 2)  # the controller restarts its program
        return {"kind": msg.get("kind", "ihc"), "state": "text.ctrl.state.ready", "info": PROJECT.info}
    if kind == "log/clear":
        if msg.get("auth") != "dev":
            raise DevError("wrong_password", "Wrong password")
        return {"cleared": msg["what"]}
    if kind == "dataline":
        # the sample project has no modules entered: invent a few, like a real installation has them
        if not any(PROJECT.modules.values()):
            PROJECT.modules = {"inputs": {1: {"type": "Input 230", "location": "Tavle 1"}, 4: {"type": "Input 24", "location": "Tavle 3"}},
                               "outputs": {1: {"type": "Output 230/10", "location": "Tavle 1"}, 2: {"type": "Output 24", "location": ""}}}
        if msg.get("refresh"):
            time.sleep(DEV["delay"])  # reading the controller takes a while
            first = DL["saved"] is None
            DL["saved"] = time.time()
            return {**vlayout.layout(PROJECT), "controller_error": None, "changed": first, "saved": DL["saved"]}
        return {**vlayout.layout(PROJECT), "controller_error": None, "changed": False, "saved": DL["saved"]}
    if kind == "coverage":
        return {"resources": PROJECT.resources()}
    if kind == "press":
        return {"yaml": vpress.press_automation(msg["entity_id"], msg.get("name", ""), msg.get("long_ms", 800), msg.get("double_ms", 400), msg.get("language", "en"))}
    if kind == "backups":
        if msg.get("kind") == "scene":
            return {"error": None, "backups": [{"name": "20261006-221500-cccccccc.icz", "saved": time.time() - 7200, "size": 18432,
                                                "scene_name": "Demo", "scenes": 3, "notifications": 2, "controls": 2}]}
        return {"error": None, "backups": [{k: v for k, v in b.items() if k != "xml"} for b in BACKUPS]}
    if kind == "backup/diff":
        by = {b["name"]: b["xml"] for b in BACKUPS}
        return vdiff.diff(vparser.Project(by[msg["old"]]), vparser.Project(by[msg["new"]]))
    if kind == "backup/download" and msg.get("kind") == "scene":
        buffer = io.BytesIO()
        with zipfile.ZipFile(buffer, "w") as archive:
            archive.writestr("project.icw", '<icwproject version="2" name="Demo"/>')
        return {"name": msg["name"], "data": base64.b64encode(buffer.getvalue()).decode()}
    if kind == "backup/download":
        xml = next(b["xml"] for b in BACKUPS if b["name"] == msg["name"])
        return {"name": msg["name"].removesuffix(".gz"), "gzip": base64.b64encode(gzip.compress(xml.encode("iso-8859-1"))).decode()}
    if kind == "monitor/start":
        MONITOR["started"] = MONITOR["started"] or time.time()
        return {"started": MONITOR["started"], "watching": len(PROJECT.resources())}
    if kind == "monitor/events":
        if MONITOR["started"]:
            resources = PROJECT.resources()
            while MONITOR["next"] < time.time():  # one invented change every ~1.5 s
                r = random.choice(resources)
                old, new = fake_value(r["id"], r["kind"]), fake_value(r["id"] + 7, r["kind"])
                if old != new:
                    MONITOR["seq"] += 1
                    MONITOR["events"].append({"seq": MONITOR["seq"], "time": MONITOR["next"], "id": r["id"], "old": old, "new": new,
                                              "name": r["name"], "label": r["label"], "kind": r["kind"]})
                MONITOR["next"] += 1.5
        return {"started": MONITOR["started"], "watching": len(PROJECT.resources()),
                "events": [e for e in MONITOR["events"] if e["seq"] > msg.get("after", 0)]}
    if kind == "monitor/clear":
        MONITOR["events"] = []
        return {"started": MONITOR["started"], "watching": len(PROJECT.resources())}
    raise KeyError(kind)


class DevError(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code


DL = {"saved": None}
SETTINGS = {"ihc_timeout": False, "ihc_timeout_seconds": 30}
MONITOR = {"started": None, "events": [], "seq": 0, "next": time.time()}
BACKUPS: list = []


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):  # keep the console quiet
        pass

    def _send(self, code: int, body: bytes, ctype: str) -> None:
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):  # noqa: N802
        path = self.path.split("?")[0]
        if path in ("/", "/index.html"):
            self._send(200, (ROOT / "scripts" / "dev_harness.html").read_bytes(), "text/html; charset=utf-8")
        elif path == "/viewmyihc-panel.js":
            self._send(200, (COMPONENT / "frontend" / "viewmyihc-panel.js").read_bytes(), "text/javascript; charset=utf-8")
        else:
            self._send(404, b"not found", "text/plain")

    def do_POST(self):  # noqa: N802
        length = int(self.headers.get("Content-Length", 0))
        msg = json.loads(self.rfile.read(length))
        try:
            payload = {"result": handle(msg)}
        except Exception as err:  # noqa: BLE001
            payload = {"error": {"code": getattr(err, "code", "not_found"), "message": str(err)}}
        self._send(200, json.dumps(payload).encode(), "application/json")


def main() -> None:
    global PROJECT
    ap = argparse.ArgumentParser()
    ap.add_argument("project", nargs="?", default=str(ROOT / "tests" / "fixtures" / "sample_project.vis"))
    ap.add_argument("--port", type=int, default=8765)
    ap.add_argument("--demo", action="store_true", help="an invented project at the scale of a real house")
    ap.add_argument("--images", help="folder with LK product pictures (<identifier>.jpg) for the wiring map")
    args = ap.parse_args()
    if args.demo:
        sys.path.insert(0, str(ROOT / "scripts"))
        from demo_project import demo_project
        xml = demo_project()
        PROJECT = parser.Project(xml)
    else:
        PROJECT = parser.Project(Path(args.project).read_bytes())
        xml = Path(args.project).read_bytes().decode("iso-8859-1")
    if args.images:
        DEV["images"] = Path(args.images)
    older = xml.replace('name="Lampeudtag"', 'name="Stikkontakt"').replace('inivalue="_0x20b"', "")
    now = time.time()
    BACKUPS.extend([
        {"name": "20261006-090000-bbbbbbbb.vis.gz", "saved": now - 3600, "size": len(xml), "modified": PROJECT.info["modified"],
         "description": "Testprojekt", "resources": PROJECT.info["resources"], "xml": xml},
        {"name": "20261001-120000-aaaaaaaa.vis.gz", "saved": now - 5 * 86400, "size": len(older), "modified": "2026-08-01 10:00",
         "description": "Testprojekt", "resources": PROJECT.info["resources"], "xml": older},
    ])
    print(f"Loaded {args.project}: {PROJECT.info['resources']} resources")
    print(f"Open http://127.0.0.1:{args.port}/")
    ThreadingHTTPServer(("127.0.0.1", args.port), Handler).serve_forever()


if __name__ == "__main__":
    main()
