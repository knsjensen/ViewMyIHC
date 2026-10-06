"""Give the ihc integration's HTTP session a timeout.

ihcsdk sends every request without a timeout. Its notification thread long-polls the controller
(``waitForResourceValueChanges``, answered within about 10 s); when the controller restarts in the middle of that
call without closing the connection, the call never returns. Commands keep working (each is its own request) but
states stop updating until Home Assistant restarts, because ihcsdk only recovers after an error.

With a timeout the hanging call ends with an error, and ihcsdk's own recovery takes over: it logs in again and
re-enables the notifications. Only this one ``requests.Session`` object is changed (no global patching), and the
change can be removed again. A call that already hangs when this is switched on keeps hanging; it needs a restart.
"""

from __future__ import annotations

from typing import Any

CONNECT_TIMEOUT = 10
DEFAULT_SECONDS = 30
MIN_SECONDS, MAX_SECONDS = 15, 300  # above the controller's 10 s long-poll, so normal waiting never times out

_MARK = "_viewmyihc_timeout"
_ORIGINAL = "_viewmyihc_original_request"


def _session(controller: Any) -> Any | None:
    connection = getattr(getattr(controller, "client", None), "connection", None)
    return getattr(connection, "session", None)


def active_timeout(controller: Any) -> int | None:
    """The read timeout ViewMyIHC put on this controller's session, or None."""
    session = _session(controller)
    return vars(session).get(_MARK) if session is not None else None


def apply(controller: Any, seconds: int) -> bool:
    """Requests without their own timeout get ``(connect, seconds)``. Returns False if there is no session."""
    seconds = max(MIN_SECONDS, min(MAX_SECONDS, int(seconds)))
    session = _session(controller)
    if session is None:
        return False
    original = vars(session).get(_ORIGINAL) or session.request

    def request(method: str, url: str, **kwargs: Any) -> Any:
        if kwargs.get("timeout") is None:
            kwargs["timeout"] = (CONNECT_TIMEOUT, seconds)
        return original(method, url, **kwargs)

    session.request = request
    vars(session)[_ORIGINAL] = original
    vars(session)[_MARK] = seconds
    return True


def remove(controller: Any) -> None:
    """Back to ihcsdk's own behaviour (no timeout)."""
    session = _session(controller)
    if session is None or _ORIGINAL not in vars(session):
        return
    for name in ("request", _ORIGINAL, _MARK):
        vars(session).pop(name, None)
