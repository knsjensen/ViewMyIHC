"""The timeout on the ihc integration's session: a call that would hang forever ends with an error instead."""

from __future__ import annotations

import socket
import threading
import time
from types import SimpleNamespace

import pytest
import requests

from conftest import load_module

guard = load_module("connection_guard")


def controller_with(session):
    return SimpleNamespace(client=SimpleNamespace(connection=SimpleNamespace(session=session)))


class Recorder(requests.adapters.HTTPAdapter):
    def __init__(self):
        super().__init__()
        self.timeouts = []

    def send(self, request, timeout=None, **kwargs):
        self.timeouts.append(timeout)
        response = requests.Response()
        response.status_code, response._content = 200, b"<ok/>"
        return response


def test_requests_without_a_timeout_get_one_and_explicit_ones_are_kept():
    session = requests.Session()
    recorder = Recorder()
    session.mount("http://", recorder)
    controller = controller_with(session)
    assert guard.apply(controller, 30) is True and guard.active_timeout(controller) == 30
    session.post("http://ihc/ws/x", data=b"")
    session.post("http://ihc/ws/x", data=b"", timeout=5)
    assert recorder.timeouts == [(guard.CONNECT_TIMEOUT, 30), 5]


def test_reapplying_changes_the_value_and_remove_restores_ihcsdks_behaviour():
    session = requests.Session()
    recorder = Recorder()
    session.mount("http://", recorder)
    controller = controller_with(session)
    guard.apply(controller, 30)
    guard.apply(controller, 60)  # not wrapped twice
    session.post("http://ihc/ws/x")
    assert recorder.timeouts[-1] == (guard.CONNECT_TIMEOUT, 60)
    guard.remove(controller)
    assert guard.active_timeout(controller) is None and "request" not in vars(session)
    session.post("http://ihc/ws/x")
    assert recorder.timeouts[-1] is None


def test_values_are_kept_above_the_controllers_long_poll():
    controller = controller_with(requests.Session())
    guard.apply(controller, 1)
    assert guard.active_timeout(controller) == guard.MIN_SECONDS


def test_no_session_is_handled():
    controller = controller_with(None)
    assert guard.apply(controller, 30) is False
    guard.remove(controller)
    assert guard.active_timeout(controller) is None


@pytest.fixture
def silent_server():
    """Accepts connections and never answers, like a controller that restarted in the middle of a call."""
    server = socket.socket()
    server.bind(("127.0.0.1", 0))
    server.listen()
    held = []
    stop = threading.Event()

    def accept():
        server.settimeout(0.2)
        while not stop.is_set():
            try:
                held.append(server.accept()[0])
            except OSError:
                continue

    thread = threading.Thread(target=accept, daemon=True)
    thread.start()
    yield f"http://127.0.0.1:{server.getsockname()[1]}"
    stop.set()
    thread.join()
    for conn in held:
        conn.close()
    server.close()


def test_ihcsdks_own_call_ends_with_an_error_instead_of_hanging(silent_server, monkeypatch):
    ihcsdk = pytest.importorskip("ihcsdk.ihcconnection")
    connection = ihcsdk.IHCConnection(silent_server)
    controller = controller_with(connection.session)
    controller.client.connection = connection
    monkeypatch.setattr(guard, "MIN_SECONDS", 1)
    guard.apply(controller, 1)
    started = time.monotonic()
    # what the notification thread calls; without the timeout this never returns
    assert connection.soap_action("/ws/ResourceInteractionService", "getResourceValue", "<x/>") is False
    assert time.monotonic() - started < 10
