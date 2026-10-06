"""Stand-ins for the objects the built-in ihc integration puts in ``hass.data['ihc']``."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import requests
from pathlib import Path

SAMPLE = Path(__file__).parent / "fixtures" / "sample_project.vis"


def sample_xml_as_ihcsdk_returns_it() -> str:
    """ihcsdk hands back the project already decoded to ``str`` (still with the XML declaration)."""
    return SAMPLE.read_bytes().decode("iso-8859-1")


ANSWER = ET.fromstring(
    '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
    '<ns1:getSomething xmlns:ns1="utcs"><ns1:name>x</ns1:name><ns1:password>hemmelig</ns1:password>'
    "</ns1:getSomething></SOAP-ENV:Body></SOAP-ENV:Envelope>"
)


class Connection:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []
        self.fail: set[str] = set()  # operations that "get no answer from the controller"
        self.answer_for: dict[str, ET.Element] = {}  # per operation; default ANSWER
        self.bodies: list[str] = []
        self.resources = Resources()
        self.session = requests.Session()  # like ihcsdk's IHCConnection (only the timeout guard touches it)

    def soap_action(self, service, action, body):
        self.calls.append((service, action))
        self.bodies.append(body)
        if action in self.fail:
            return False
        if action in self.answer_for:
            return self.answer_for[action]
        if service == "/ws/ResourceInteractionService":
            return self.resources.answer(action, body)
        return ANSWER


class Resources:
    """A controller's resources with a runtime and an initial value each: ``{id: [type, runtime, initial]}``."""

    FIELD = {"WSBooleanValue": "value", "WSIntegerValue": "integer"}

    def __init__(self):
        self.values = {100: ["WSBooleanValue", "false", "false"], 200: ["WSIntegerValue", "5", "1"]}
        self.refuse = False

    def _envelope(self, wrapper, rid, slot):
        ws_type, *vals = self.values[rid]
        field = self.FIELD[ws_type]
        limits = "<ns2:maximumValue>10</ns2:maximumValue><ns2:minimumValue>0</ns2:minimumValue>" if ws_type == "WSIntegerValue" else ""
        return ET.fromstring(
            '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
            f'<ns1:{wrapper} xmlns:ns1="utcs" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="utcs.values">'
            f'<ns1:value xsi:type="ns2:{ws_type}"><ns2:{field}>{vals[slot]}</ns2:{field}>{limits}</ns1:value>'
            f"<ns1:resourceID>{rid}</ns1:resourceID></ns1:{wrapper}></SOAP-ENV:Body></SOAP-ENV:Envelope>"
        )

    def answer(self, action, body):
        if action in ("getRuntimeValue", "getInitialValue"):
            rid = int(ET.fromstring(body).text)
            return self._envelope(f"{action}2", rid, 0 if action == "getRuntimeValue" else 1)
        if action == "setResourceValue":
            doc = ET.fromstring(body)
            leaf = {el.tag.rsplit("}", 1)[-1]: el.text for el in doc.iter()}
            rid, slot = int(leaf["resourceID"]), 0 if leaf["isValueRuntime"] == "true" else 1
            if not self.refuse:
                self.values[rid][1 + slot] = leaf[self.FIELD[self.values[rid][0]]]
            return ET.fromstring(
                '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
                f'<ns1:setResourceValue2 xmlns:ns1="utcs">{"false" if self.refuse else "true"}</ns1:setResourceValue2>'
                "</SOAP-ENV:Body></SOAP-ENV:Envelope>"
            )
        return ANSWER


class Client:
    def __init__(self):
        self.connection = Connection()
        self.url = "http://192.168.1.3"
        self.project_downloads = 0
        self.username, self.password = "homeassistant", "hemmeligt"  # ihcsdk keeps the login like this

    def get_state(self):
        return "text.ctrl.state.ready"

    def get_project_info(self):
        return {"projectMajorRevision": 1, "projectMinorRevision": 7}

    def get_project_in_segments(self, info=None):
        self.project_downloads += 1
        return sample_xml_as_ihcsdk_returns_it()


class Controller:
    def __init__(self):
        self.client = Client()
        self.notify: dict[int, list] = {}  # what add_notify_event registered, like ihcsdk's _ihcevents

    def add_notify_event(self, resourceid, callback, delayed=False):
        self.notify.setdefault(resourceid, []).append(callback)
        return True

    def change(self, resourceid, value):
        """What ihcsdk's notify thread does when the controller reports a change."""
        for callback in self.notify.get(resourceid, []):
            callback(resourceid, value)

    def re_authenticate(self, notify=False):
        return True

    def get_runtime_values(self, ids):
        return {i: (i % 2 == 0) for i in ids}


def answer(**fields) -> ET.Element:
    """A SOAP response whose body holds the given fields."""
    inner = "".join(f"<ns1:{k}>{v}</ns1:{k}>" for k, v in fields.items())
    return ET.fromstring(
        '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>'
        f'<ns1:r xmlns:ns1="utcs">{inner}</ns1:r></SOAP-ENV:Body></SOAP-ENV:Envelope>'
    )
