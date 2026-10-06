"""Sending a saved version back: the IHC project like IHC Visual does it, the scene project like SceneDesign."""

from __future__ import annotations

import base64
import gzip
import xml.etree.ElementTree as ET

import pytest

import fakes
from conftest import load_module

pr = load_module("project_restore")
bridge = load_module("ihc_bridge")

XML = fakes.sample_xml_as_ihcsdk_returns_it()


def envelope(wrapper: str, inner: str) -> ET.Element:
    return ET.fromstring(
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
        f'<ns1:{wrapper} xmlns:ns1="utcs">{inner}</ns1:{wrapper}></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    )


class RestoringController(fakes.Controller):
    """ControllerService as far as a restore needs it; records the order of the calls."""

    def __init__(self, state="text.ctrl.state.ready", accept="true", store_error=False):
        super().__init__()
        self.state, self.accept, self.store_error = state, accept, store_error
        self.order: list[str] = []
        self.stored: bytes | None = None
        conn = self.client.connection
        fallback = conn.soap_action

        def soap_action(service, action, body=""):
            if service != pr.CONTROLLER:
                return fallback(service, action, body)
            self.order.append(action)
            if action == "getState":
                return envelope("getState1", f"<ns1:state>{self.state}</ns1:state>")
            if action == "enterProjectChangeMode":
                self.state = "text.ctrl.state.initialize"
                return envelope("enterProjectChangeMode1", "true")
            if action == "waitForControllerStateChange":
                return envelope("waitForControllerStateChange3", f"<ns1:state>{self.state}</ns1:state>")
            if action == "storeIHCProject":
                if self.store_error:
                    return False  # no answer: soap_action raises after its retry
                data = next(e.text for e in ET.fromstring(f"<r>{body}</r>").iter() if e.tag.endswith("data"))
                self.stored = gzip.decompress(base64.b64decode(data))
                return envelope("storeIHCProject2", self.accept)
            if action == "exitProjectChangeMode":
                self.state = "text.ctrl.state.ready"
                return envelope("exitProjectChangeMode1", "true")
            raise AssertionError(action)

        conn.soap_action = soap_action


def test_a_project_is_stored_in_project_change_mode_and_the_controller_is_ready_again():
    controller = RestoringController()
    assert pr.restore_project(controller, XML, "x.vis") == "text.ctrl.state.ready"
    assert controller.stored == XML.encode("iso-8859-1")  # the very bytes of the saved project
    order = [a for a in controller.order if a != "waitForControllerStateChange"]
    assert order == ["getState", "enterProjectChangeMode", "storeIHCProject", "exitProjectChangeMode"]


def test_nothing_is_sent_when_the_controller_is_not_ready():
    controller = RestoringController(state="text.ctrl.state.initialize")
    with pytest.raises(pr.RestoreError, match="not ready"):
        pr.restore_project(controller, XML)
    assert controller.order == ["getState"]


@pytest.mark.parametrize("kwargs", [{"accept": "false"}, {"store_error": True}])
def test_project_change_mode_is_always_left_again(kwargs):
    controller = RestoringController(**kwargs)
    with pytest.raises((pr.RestoreError, bridge.BridgeError)):
        pr.restore_project(controller, XML)
    assert "exitProjectChangeMode" in controller.order and controller.state == "text.ctrl.state.ready"


@pytest.mark.parametrize("bad", ["<html/>", "not xml at all", "<utcs_project><broken"])
def test_only_complete_ihc_projects_are_sent(bad):
    controller = RestoringController()
    with pytest.raises(pr.RestoreError):
        pr.restore_project(controller, bad)
    assert controller.order == []


def test_a_scene_project_is_sent_in_segments_and_checked_afterwards():
    from test_scene_project import SceneController, icz

    old = icz()
    new = icz(b'<icwproject version="2" name="Hus"><description>' + bytes(range(65, 91)) * 400 + b"</description></icwproject>")
    assert len(new) > (len(old) + 1) // 2  # bigger than one segment: it goes in two parts
    controller = SceneController(old)
    sent: list[tuple[bytes, str, str]] = []
    conn = controller.client.connection
    serve = conn.soap_action

    def soap_action(service, action, body=""):
        if action == "storeSceneProjectSegment":
            doc = ET.fromstring(f'<r xmlns:u="utcs">{body}</r>')
            leaves = {e.tag.rsplit("}", 1)[-1]: e.text for e in doc.iter()}
            sent.append((base64.b64decode(leaves["data"]), leaves["storeSceneProjectSegment2"], leaves["storeSceneProjectSegment3"]))
            if leaves["storeSceneProjectSegment3"] == "true":
                controller.data = b"".join(chunk for chunk, *_ in sent)
            return envelope("storeSceneProjectSegment4", "true")
        return serve(service, action, body)

    conn.soap_action = soap_action
    pr.restore_scene(controller, new)
    assert controller.data == new
    flags = [(first, last) for _, first, last in sent]
    assert flags[0] == ("true", "false") and flags[-1] == ("false", "true") and len(flags) >= 2


def test_a_scene_project_that_does_not_come_back_identical_is_reported():
    from test_scene_project import SceneController, icz

    controller = SceneController(icz())
    conn = controller.client.connection
    serve = conn.soap_action
    conn.soap_action = lambda s, a, b="": envelope("storeSceneProjectSegment4", "true") if a == "storeSceneProjectSegment" else serve(s, a, b)
    with pytest.raises(pr.RestoreError, match="differs"):
        pr.restore_scene(controller, icz(b'<icwproject version="2" name="Andet"/>'))
