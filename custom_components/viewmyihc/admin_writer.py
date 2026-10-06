"""Change the controller settings IHC Administrator can change: users, network, DNS, web access, time, e-mail.

Blocking (run in the executor). Every change starts from a fresh read of the controller's own answer: only the
fields the panel changed are replaced, everything else (also fields this module does not know) is sent back exactly
as the controller gave it. Passwords never leave this module: an empty password from the panel means "keep it".

Guards keep Home Assistant connected: the ihc integration logs in as a user of the "treeview" program, so that user
cannot be removed or get a new password here, and LAN access for treeview/Administrator cannot be switched off.
Changing the controller's address or ports needs an explicit confirmation from the panel.
"""

from __future__ import annotations

import datetime
import ipaddress
import logging
import re
from dataclasses import dataclass, field
from typing import Any, Callable
from xml.etree.ElementTree import Element
from xml.sax.saxutils import escape

from .admin_reader import _local
from .ihc_bridge import BridgeError, soap_action

_LOGGER = logging.getLogger(__name__)

XSI = "http://www.w3.org/2001/XMLSchema-instance"
_NIL = f"{{{XSI}}}nil"
CONFIG, USERS, TIME = "/ws/ConfigurationService", "/ws/UserManagerService", "/ws/TimeManagerService"
ADMIN_GROUP = "text.usermanager.group_administrators"


class AdminWriteError(Exception):
    """A change that is not allowed or not valid; the message is shown in the panel."""


class NeedsConfirmation(AdminWriteError):
    """The change can cut the connection; the panel must ask and send ``confirm``."""


# ------------------------------------------------------------------ field types


def _text(limit: int = 255, required: bool = False) -> Callable[[Any], str]:
    def check(value: Any) -> str:
        text = str(value if value is not None else "").strip()
        if len(text) > limit or any(ord(c) < 32 for c in text):
            raise AdminWriteError(f"Text too long or invalid (max {limit})")
        if required and not text:
            raise AdminWriteError("Required")
        return text
    return check


def _int(low: int, high: int) -> Callable[[Any], str]:
    def check(value: Any) -> str:
        try:
            number = int(str(value).strip())
        except ValueError as err:
            raise AdminWriteError(f"Expected a whole number between {low} and {high}") from err
        if not low <= number <= high:
            raise AdminWriteError(f"Expected a whole number between {low} and {high}")
        return str(number)
    return check


def _bool(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if str(value).lower() in ("true", "false"):
        return str(value).lower()
    raise AdminWriteError("Expected on/off")


def _ipv4(value: Any) -> str:
    try:
        return str(ipaddress.IPv4Address(str(value).strip()))
    except ValueError as err:
        raise AdminWriteError(f"Not an IPv4 address: {value}") from err


_HOST = re.compile(r"^[A-Za-z0-9.-]{0,253}$")


def _host(value: Any) -> str:
    text = str(value or "").strip()
    if not _HOST.match(text):
        raise AdminWriteError(f"Not a host name or address: {value}")
    return text


_PORT = _int(1, 65535)
SECRET = "secret"


@dataclass(frozen=True)
class Spec:
    service: str
    read: str
    write: str
    fields: dict[str, Any] = field(default_factory=dict)  # name -> checker, or SECRET
    login: str = ""  # the user name that goes with the SECRET field
    confirm: frozenset[str] = frozenset()  # fields that can cut the connection
    must_stay_on: frozenset[str] = frozenset()


_ACCESS = [f"m_{program}_{where}" for program in (
    "administrator", "treeview", "sceneview", "scenedesign", "serverstatus", "ihcvisual", "onlinedocumentation",
    "websceneview", "openapi") for where in ("usb", "internal", "external")]

SPECS: dict[str, Spec] = {
    "network": Spec(CONFIG, "getNetworkSettings", "setNetworkSettings",
                    {"ipAddress": _ipv4, "netmask": _ipv4, "gateway": _ipv4, "httpPort": _PORT, "httpsPort": _PORT},
                    confirm=frozenset({"ipAddress", "netmask", "gateway", "httpPort", "httpsPort"})),
    "smtp": Spec(CONFIG, "getSMTPSettings", "setSMTPSettings",
                 {"hostname": _host, "hostport": _PORT, "username": _text(), "password": SECRET}, login="username"),
    "email_control": Spec(CONFIG, "getEmailControlSettings", "setEmailControlSettings",
                          {"serverIPAddress": _host, "serverPortNumber": _PORT, "pop3Username": _text(),
                           "pop3Password": SECRET, "emailAddress": _text(), "pollInterval": _int(1, 1440),
                           "removeEmailsAfterUsage": _bool}, login="pop3Username"),
    "web_access": Spec(CONFIG, "getWebAccessControl", "setWebAccessControl",
                       {name: _bool for name in [*_ACCESS, "m_usbLoginRequired_usb", "m_openapi_used"]},
                       must_stay_on=frozenset({"m_treeview_internal", "m_administrator_internal"})),
    "time": Spec(TIME, "getSettings", "setSettings",
                 {"synchroniseTimeAgainstServer": _bool, "useDST": _bool, "gmtOffsetInHours": _int(-12, 14),
                  "serverName": _host, "syncIntervalInHours": _int(1, 8760)}),
}


# ------------------------------------------------------------------ XML helpers


def _holder(document: Element, name: str) -> Element:
    found = next((e for e in document.iter() if _local(e.tag) == name), None)
    if found is None:
        raise BridgeError(f"The controller's answer has no {name}")
    return found


def _child_text(element: Element, name: str) -> str:
    child = next((c for c in element if _local(c.tag) == name), None)
    return (child.text or "").strip() if child is not None else ""


def _serialize(element: Element, name: str | None = None) -> str:
    """An answer element as request XML: local names only (everything is in the default namespace utcs)."""
    name = name or _local(element.tag)
    if element.get(_NIL) == "true":
        return f'<{name} xsi:nil="true"/>'
    children = list(element)
    if children:
        return f"<{name}>{''.join(_serialize(child) for child in children)}</{name}>"
    return f"<{name}>{escape(element.text or '')}</{name}>"


def _wrap(operation: str, inner: str, suffix: str = "1") -> str:
    return f'<{operation}{suffix} xmlns="utcs" xmlns:xsi="{XSI}">{inner}</{operation}{suffix}>'


def _accepted(document: Element, operation: str) -> None:
    answer = next((e for e in document.iter() if _local(e.tag) == f"{operation}2"), None)
    if answer is not None and (answer.text or "").strip() == "false":
        raise AdminWriteError(f"The controller refused the change ({operation})")


def _wsdate(when: datetime.datetime) -> str:
    when = when.astimezone(datetime.timezone.utc)
    parts = {"monthWithJanuaryAsOne": when.month, "day": when.day, "hours": when.hour, "year": when.year,
             "seconds": when.second, "minutes": when.minute}
    return "".join(f"<{k}>{v}</{k}>" for k, v in parts.items())


# ------------------------------------------------------------------ settings sections


def write_section(controller: Any, key: str, changes: dict[str, Any], *, confirm: bool = False,
                  set_clock: datetime.datetime | None = None) -> list[str]:
    """Change some fields of one settings section. Returns the names of the fields that really changed."""
    spec = SPECS.get(key)
    if spec is None:
        raise AdminWriteError(f"{key} cannot be changed here")
    unknown = set(changes) - set(spec.fields)
    if unknown:
        raise AdminWriteError(f"Unknown fields: {', '.join(sorted(unknown))}")
    current = _holder(soap_action(controller, spec.service, spec.read), f"{spec.read}1")
    new_text: dict[str, str] = {}
    for name, value in changes.items():
        checker = spec.fields[name]
        if checker == SECRET:
            if value in (None, ""):
                continue  # keep the password the controller has (checked below)
            new_text[name] = _text()(value)
        else:
            new_text[name] = checker(value)
    changed = [name for name, text in new_text.items() if text != _child_text(current, name)]
    for name in spec.must_stay_on:
        if new_text.get(name) == "false":
            raise AdminWriteError(f"{name} must stay on: Home Assistant and IHC Administrator use it")
    if spec.confirm.intersection(changed) and not confirm:
        raise NeedsConfirmation("This change can cut the connection to the controller")
    if not changed and set_clock is None:
        return []
    for name, checker in spec.fields.items():
        login = new_text.get(spec.login, _child_text(current, spec.login)) if spec.login else ""
        if checker == SECRET and name not in new_text and login and not _child_text(current, name):
            # the controller gave out no password although there is a user name: sending it back empty would erase it
            raise AdminWriteError("The controller does not give out the password: enter it again to save")
    parts = []
    for child in current:
        name = _local(child.tag)
        if name in new_text:
            parts.append(f"<{name}>{escape(new_text[name])}</{name}>")
        elif name == "timeAndDateInUTC":
            # left out (nil) the controller keeps its clock; only set when the panel asks for it
            parts.append(f"<{name}>{_wsdate(set_clock)}</{name}>" if set_clock else f'<{name} xsi:nil="true"/>')
        else:
            parts.append(_serialize(child))
    _accepted(soap_action(controller, spec.service, spec.write, _wrap(spec.write, "".join(parts))), spec.write)
    _LOGGER.info("ViewMyIHC: changed %s on the controller: %s", key, ", ".join(changed) or "clock")
    return changed or ["timeAndDateInUTC"]


def set_email_control_enabled(controller: Any, enabled: bool) -> None:
    body = _wrap("setEmailControlEnabled", _bool(enabled))
    _accepted(soap_action(controller, CONFIG, "setEmailControlEnabled", body), "setEmailControlEnabled")


def set_dns(controller: Any, primary: str, secondary: str) -> None:
    """Both DNS servers (the controller stores an address as a signed 32-bit number)."""
    def number(value: str) -> int:
        if not str(value or "").strip():
            return 0
        raw = int(ipaddress.IPv4Address(_ipv4(value)))
        return raw - (1 << 32) if raw >= 1 << 31 else raw

    body = (_wrap("setDNSServers", f"<ipAddress>{number(primary)}</ipAddress>")
            + _wrap("setDNSServers", f"<ipAddress>{number(secondary)}</ipAddress>", "2"))
    soap_action(controller, CONFIG, "setDNSServers", body)
    _LOGGER.info("ViewMyIHC: changed the DNS servers on the controller")


# ------------------------------------------------------------------ users

USER_FIELDS = {"email": _text(100), "firstname": _text(100), "lastname": _text(100), "phone": _text(40)}
_USERNAME = re.compile(r"^[A-Za-z0-9._@-]{1,40}$")


def _ha_username(controller: Any) -> str:
    return str(getattr(controller.client, "username", "") or getattr(controller, "_username", "") or "")


def _users(controller: Any) -> list[Element]:
    holder = _holder(soap_action(controller, USERS, "getUsers"), "getUsers1")
    return [item for item in holder if _child_text(item, "username")]


def _user_xml(fields: dict[str, str], original: Element | None) -> str:
    """WSUser in schema order; dates, group and project come from the controller's own record."""
    def keep(name: str, fallback: str) -> str:
        child = next((c for c in original if _local(c.tag) == name), None) if original is not None else None
        return _serialize(child) if child is not None else fallback

    return (
        keep("createdDate", '<createdDate xsi:nil="true"/>') + keep("loginDate", '<loginDate xsi:nil="true"/>')
        + "".join(f"<{name}>{escape(fields[name])}</{name}>" for name in
                  ("username", "password", "email", "firstname", "lastname", "phone"))
        + keep("group", f"<group><type>{ADMIN_GROUP}</type></group>") + keep("project", "<project></project>")
    )


def add_user(controller: Any, username: str, password: str, details: dict[str, Any]) -> None:
    if not _USERNAME.match(username or ""):
        raise AdminWriteError("Username: 1–40 letters, digits or . _ @ -")
    if any(_child_text(u, "username").lower() == username.lower() for u in _users(controller)):
        raise AdminWriteError(f"The user {username} already exists")
    fields = {"username": username, "password": _text(64, required=True)(password)}
    fields.update({name: check(details.get(name, "")) for name, check in USER_FIELDS.items()})
    body = _wrap("addUser", _user_xml(fields, None))
    _accepted(soap_action(controller, USERS, "addUser", body), "addUser")
    _LOGGER.info("ViewMyIHC: added the controller user %s", username)


def update_user(controller: Any, username: str, password: str | None, details: dict[str, Any]) -> None:
    original = next((u for u in _users(controller) if _child_text(u, "username") == username), None)
    if original is None:
        raise AdminWriteError(f"Unknown user {username}")
    fields = {name: _child_text(original, name) for name in ("username", "password", *USER_FIELDS)}
    fields.update({name: check(details[name]) for name, check in USER_FIELDS.items() if name in details})
    if password:
        if username == _ha_username(controller):
            raise AdminWriteError("This is the user Home Assistant logs in with: change its password in IHC "
                                  "Administrator and in the ihc setup together, or Home Assistant loses the connection")
        fields["password"] = _text(64, required=True)(password)
    elif not fields["password"]:
        if username == _ha_username(controller):
            raise AdminWriteError("The controller does not give out passwords, and the password of the user Home "
                                  "Assistant logs in with cannot be set here: change this user in IHC Administrator")
        raise AdminWriteError("The controller does not give out passwords: enter the password again to save")
    _accepted(soap_action(controller, USERS, "updateUser", _wrap("updateUser", _user_xml(fields, original))), "updateUser")
    _LOGGER.info("ViewMyIHC: updated the controller user %s", username)


def remove_user(controller: Any, username: str) -> None:
    users = [_child_text(u, "username") for u in _users(controller)]
    if username not in users:
        raise AdminWriteError(f"Unknown user {username}")
    if username == _ha_username(controller):
        raise AdminWriteError("This is the user Home Assistant logs in with and cannot be removed here")
    if len(users) == 1:
        raise AdminWriteError("The last user cannot be removed")
    _accepted(soap_action(controller, USERS, "removeUser", _wrap("removeUser", escape(username))), "removeUser")
    _LOGGER.info("ViewMyIHC: removed the controller user %s", username)
