from __future__ import annotations

import datetime
import xml.etree.ElementTree as ET

import pytest


class FakeConnection:
    def __init__(self, answers):
        self.answers = list(answers)
        self.calls = []

    def soap_action(self, service, action, body, wait=None):
        self.calls.append((service, action))
        return self.answers.pop(0)


class FakeClient:
    def __init__(self, connection, state="text.ctrl.state.ready", info=None, project="<xml/>"):
        self.connection = connection
        self._state = state
        self._info = {"projectMajorRevision": 1} if info is None else info
        self._project = project

    def get_state(self):
        return self._state

    def get_project_info(self):
        return self._info

    def get_project_in_segments(self, info):
        return self._project


class FakeController:
    def __init__(self, client, values=None):
        self.client = client
        self.reauth = 0
        self._values = values

    def re_authenticate(self, notify=False):
        self.reauth += 1

    def get_runtime_values(self, ids):
        return self._values


def test_find_controllers_ignores_foreign_entries(bridge):
    data = {"ihc": {"123": {"controller": "C1", "info": True}, "weird": 5, "x": {"no": 1}}, "other": {}}
    assert bridge.find_controllers(data) == {"123": "C1"}
    assert bridge.find_controllers({}) == {}
    assert bridge.find_controllers({"ihc": "nope"}) == {}


def test_json_value_converts_temporal_types(bridge):
    assert bridge.json_value(datetime.time(7, 5, 9)) == "07:05:09"
    assert bridge.json_value(datetime.date(2026, 10, 31)) == "2026-10-31"
    assert bridge.json_value(datetime.timedelta(seconds=2, milliseconds=250)) == 2250
    assert bridge.json_value(True) is True
    assert bridge.json_value(1.5) == 1.5
    assert bridge.json_value(object).startswith("<class")


def test_soap_action_retries_once_after_reauthentication(bridge):
    doc = ET.fromstring("<a/>")
    conn = FakeConnection([False, doc])
    ctrl = FakeController(FakeClient(conn))
    assert bridge.soap_action(ctrl, "/ws/X", "op") is doc
    assert ctrl.reauth == 1
    assert len(conn.calls) == 2


def test_soap_action_raises_when_still_failing(bridge):
    ctrl = FakeController(FakeClient(FakeConnection([False, False])))
    with pytest.raises(bridge.BridgeError):
        bridge.soap_action(ctrl, "/ws/X", "op")


def test_fetch_project_requires_ready_controller(bridge):
    ctrl = FakeController(FakeClient(FakeConnection([]), state="text.ctrl.state.initialize"))
    with pytest.raises(bridge.BridgeError, match="not ready"):
        bridge.fetch_project_xml(ctrl)
    ok = FakeController(FakeClient(FakeConnection([]), project="<utcs_project/>"))
    assert bridge.fetch_project_xml(ok) == "<utcs_project/>"


def test_project_signature_changes_with_revision(bridge):
    a = FakeController(FakeClient(FakeConnection([]), info={"major": 1, "minor": 2}))
    b = FakeController(FakeClient(FakeConnection([]), info={"major": 1, "minor": 3}))
    assert bridge.project_signature(a) != bridge.project_signature(b)
    with pytest.raises(bridge.BridgeError):
        bridge.project_signature(FakeController(FakeClient(FakeConnection([]), info=False)))


def test_runtime_values_maps_ids_and_raises_on_failure(bridge):
    ctrl = FakeController(FakeClient(FakeConnection([])), values={5: True, 6: datetime.time(1, 2, 3)})
    assert bridge.runtime_values(ctrl, [5, 6]) == {5: True, 6: "01:02:03"}
    assert bridge.runtime_values(ctrl, []) == {}
    with pytest.raises(bridge.BridgeError):
        bridge.runtime_values(FakeController(FakeClient(FakeConnection([])), values=False), [1])


USERS_RESPONSE = """<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/">
<SOAP-ENV:Body><ns1:getUsers2 xmlns:ns1="utcs">
  <ns1:arrayItem><ns1:username>admin</ns1:username><ns1:password>hemmelig</ns1:password><ns1:group>Admin</ns1:group></ns1:arrayItem>
  <ns1:arrayItem><ns1:username>anna</ns1:username><ns1:password>pw</ns1:password><ns1:group>User</ns1:group></ns1:arrayItem>
</ns1:getUsers2></SOAP-ENV:Body></SOAP-ENV:Envelope>"""


def test_admin_conversion_strips_namespaces_and_removes_secrets(admin):
    payload = admin._body_payload(ET.fromstring(USERS_RESPONSE))
    users = payload  # the single wrapper element ("arrayItem") is unwrapped into a plain list
    assert isinstance(users, list)
    assert [u["username"] for u in users] == ["admin", "anna"]
    assert all(u["password"] == "***" for u in users)
    assert "hemmelig" not in repr(payload)


def test_admin_single_value_and_empty_elements(admin):
    doc = ET.fromstring(
        '<e:Envelope xmlns:e="x"><e:Body><r><uptime>12</uptime><empty/></r></e:Body></e:Envelope>'
    )
    assert admin._body_payload(doc) == {"uptime": "12", "empty": None}


@pytest.mark.parametrize("key", ["smtpPassword", "pwd", "pincode", "pin", "secretKey", "authToken"])
def test_admin_secret_keys_detected(admin, key):
    el = ET.fromstring(f"<r><{key}>topsecret</{key}></r>")
    assert admin.element_to_py(el) == {key: "***"}


def test_read_admin_isolates_failing_sections(admin, bridge, monkeypatch):
    doc = ET.fromstring(USERS_RESPONSE)

    def fake(controller, service, operation, body=""):
        if operation == "getUsers":
            return doc
        raise bridge.BridgeError("boom")

    monkeypatch.setattr(admin, "soap_action", fake)
    sections = {s["key"]: s for s in admin.read_admin(object())}
    assert "data" in sections["users"] and "error" not in sections["users"]
    assert sections["system"]["error"] == "boom"
    assert len(sections) == len(admin.SECTIONS)


def test_only_read_operations_are_called(admin):
    assert all(op.startswith("get") for _, _, _, op in admin.SECTIONS)


def test_soap_action_does_not_hold_the_ihc_lock_while_reauthenticating(bridge):
    """Regression: ihcsdk's authenticate() takes a non-reentrant class lock; holding it deadlocks."""
    import threading

    class LockingController(FakeController):
        _mutex = threading.Lock()

        def re_authenticate(self, notify=False):
            if not self._mutex.acquire(timeout=1):  # would hang forever in production
                raise AssertionError("deadlock: lock was held while re-authenticating")
            self._mutex.release()
            self.reauth += 1

    doc = ET.fromstring("<a/>")
    ctrl = LockingController(FakeClient(FakeConnection([False, doc])))
    assert bridge.soap_action(ctrl, "/ws/X", "op") is doc
    assert ctrl.reauth == 1


def test_project_download_takes_and_releases_the_ihc_lock(bridge):
    import threading

    class LockingController(FakeController):
        _mutex = threading.Lock()

    ctrl = LockingController(FakeClient(FakeConnection([]), project="<utcs_project/>"))
    assert bridge.fetch_project_xml(ctrl) == "<utcs_project/>"
    assert LockingController._mutex.acquire(timeout=1)  # released again
    LockingController._mutex.release()
