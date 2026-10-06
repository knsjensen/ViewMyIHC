"""Send a saved project back to the controller (blocking: run in the executor).

IHC project – the way IHC Visual (and the open-source IHCClientSDK) does it: the controller must be ready; enter
project change mode; send the whole project once with ``storeIHCProject`` (gzip of the ISO-8859-1 XML, base64);
always leave project change mode again; wait until the controller reports ready. The controller restarts its
program: runtime values (output states, counters) start again from their initial values.

SceneDesign project – the way SceneDesign does it: the ``.icz`` bytes in segments of the controller's segment size
with ``storeSceneProjectSegment`` (first/last flags), under the project's name; then fetched back and compared.
"""

from __future__ import annotations

import base64
import gzip
import logging
import time
from typing import Any
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from . import scene_project
from .admin_reader import _body_payload, _local
from .ihc_bridge import BridgeError, soap_action

_LOGGER = logging.getLogger(__name__)

CONTROLLER = "/ws/ControllerService"
READY = "text.ctrl.state.ready"
INITIALIZE = "text.ctrl.state.initialize"
READY_TIMEOUT = 180  # seconds the controller gets to start the restored project


class RestoreError(Exception):
    """The restore was refused or did not complete; the message is shown in the panel."""


def _answer(document: Any, name: str) -> str:
    element = next((e for e in document.iter() if _local(e.tag) == name), None)
    return (element.text or "").strip() if element is not None else ""


def state(controller: Any) -> str:
    return _answer(soap_action(controller, CONTROLLER, "getState"), "state")


def _wait_for(controller: Any, wanted: str, seconds: float) -> str:
    """Long-poll ``waitForControllerStateChange`` until ``wanted`` or the time is up. Returns the last state."""
    deadline = time.monotonic() + seconds
    current = ""
    while time.monotonic() < deadline:
        body = (f'<waitForControllerStateChange1 xmlns="utcs"><state>{wanted}</state></waitForControllerStateChange1>'
                '<waitForControllerStateChange2 xmlns="utcs">10</waitForControllerStateChange2>')
        try:
            current = _answer(soap_action(controller, CONTROLLER, "waitForControllerStateChange", body), "state")
        except BridgeError:
            time.sleep(2)  # the controller may not answer while it restarts
            continue
        if current == wanted:
            return current
    return current


def check_project(xml: str) -> bytes:
    """The bytes to send, after checking the XML is a complete IHC project that survives the round trip."""
    raw = xml.encode("iso-8859-1")
    if raw.decode("iso-8859-1") != xml:  # pragma: no cover - ISO-8859-1 maps every byte
        raise RestoreError("The saved project does not survive encoding")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError as err:
        raise RestoreError(f"The saved project is not valid XML: {err}") from err
    if root.tag != "utcs_project":
        raise RestoreError("The saved file is not an IHC project")
    return raw


def restore_project(controller: Any, xml: str, filename: str = "project.vis") -> str:
    """Store ``xml`` as the controller's project. Returns the controller's state afterwards."""
    raw = check_project(xml)
    if (current := state(controller)) != READY:
        raise RestoreError(f"The controller is not ready ({current or 'no answer'})")
    data = base64.b64encode(gzip.compress(raw)).decode()
    if _answer(soap_action(controller, CONTROLLER, "enterProjectChangeMode"), "enterProjectChangeMode1") != "true":
        raise RestoreError("The controller refused to enter project change mode")
    _LOGGER.warning("ViewMyIHC: restoring a saved project on the controller (%s bytes)", len(raw))
    stored = False
    try:
        _wait_for(controller, INITIALIZE, 15)
        body = (f'<storeIHCProject1 xmlns="utcs"><filename>{escape(filename)}</filename>'
                f"<data>{data}</data></storeIHCProject1>")
        stored = _answer(soap_action(controller, CONTROLLER, "storeIHCProject", body), "storeIHCProject2") == "true"
    finally:
        # never leave the controller in project change mode, whatever happened above
        try:
            soap_action(controller, CONTROLLER, "exitProjectChangeMode")
        except BridgeError:
            _LOGGER.exception("ViewMyIHC: exitProjectChangeMode failed")
    final = _wait_for(controller, READY, READY_TIMEOUT)
    if not stored:
        raise RestoreError(f"The controller did not accept the project (state now: {final or 'unknown'})")
    if final != READY:
        raise RestoreError(f"The project was sent, but the controller is not ready yet (state: {final or 'unknown'})")
    return final


def restore_scene(controller: Any, icz: bytes) -> None:
    """Store a SceneDesign project and check it by fetching it back."""
    scene_project.parse(icz)  # must be a readable SceneDesign project
    info = scene_project.project_info(controller)
    name = scene_project._file_name(info)  # noqa: SLF001 - the same name SceneDesign uses
    if not name:
        raise RestoreError("The controller has no scene project to replace")
    size = int(_body_payload(soap_action(controller, scene_project.MODULE, "getSceneProjectSegmentationSize")) or 0)
    if size <= 0:
        raise RestoreError("The controller did not give a segment size")
    chunks = [icz[i:i + size] for i in range(0, len(icz), size)]
    _LOGGER.warning("ViewMyIHC: restoring a saved SceneDesign project (%s bytes in %s parts)", len(icz), len(chunks))
    for index, chunk in enumerate(chunks):
        body = (f'<storeSceneProjectSegment1 xmlns="utcs"><filename>{escape(name)}</filename>'
                f"<data>{base64.b64encode(chunk).decode()}</data></storeSceneProjectSegment1>"
                f'<storeSceneProjectSegment2 xmlns="utcs">{"true" if index == 0 else "false"}</storeSceneProjectSegment2>'
                f'<storeSceneProjectSegment3 xmlns="utcs">{"true" if index == len(chunks) - 1 else "false"}</storeSceneProjectSegment3>')
        answer = _answer(soap_action(controller, scene_project.MODULE, "storeSceneProjectSegment", body), "storeSceneProjectSegment4")
        if answer == "false":
            raise RestoreError(f"The controller refused part {index + 1} of {len(chunks)} of the scene project")
    if scene_project.download(controller) != icz:
        raise RestoreError("The scene project on the controller differs from the one sent")
