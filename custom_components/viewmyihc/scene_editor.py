"""Change the message lists of a SceneDesign project (pure Python).

Only the four lists in ``project.icw`` change: ``notifications``, ``smsnotifications``, ``emailcontrols`` and
``smscontrols``. Everything else – scenes, images, the XML outside those lists, the other files in the ``.icz`` – is
copied byte for byte. Within the lists, an entry that was not changed is copied byte for byte too; only new and changed
entries are written, in the form SceneDesign itself writes them. Validation follows SceneDesign's own dialogs.
"""

from __future__ import annotations

import datetime
import io
import re
from typing import Any
from xml.sax.saxutils import escape, quoteattr
import zipfile

from .scene_project import SMS_SLOTS, SceneProjectError, parse

# list element, item element, channel, kind – in the order SceneDesign writes them
LISTS = (
    ("notifications", "notification", "email", "notification"),
    ("smsnotifications", "smsnotification", "sms", "notification"),
    ("emailcontrols", "emailcontrol", "email", "control"),
    ("smscontrols", "smscontrol", "sms", "control"),
)
_AFTER = ("description", "ihcproject", "created", "lastmodified", "images", "scenes")  # what comes before the lists
EVENTS = ("inactive_to_active_event", "active_to_inactive_event")
ACTIONS = ("off_to_on_action", "on_to_off_action", "pulse_action")
AUTH_EMAIL = ("direct_control", "sender_based", "three_way")
AUTH_SMS = ("direct_control", "sender_based")
_EMAIL = re.compile(r"^[^@\s;,<>]+@[^@\s;,<>]+\.[^@\s;,<>]+$")
TEXT_MAX, SMS_MAX, TRIGGER_MAX = 500, 60, 60


class SceneEditError(Exception):
    """Invalid input; the message is shown in the panel."""


# ------------------------------------------------------------------ locating the lists in the XML text


def _span(text: str, tag: str) -> tuple[int, int] | None:
    match = re.search(rf"<{tag}(?:\s[^>]*)?/>|<{tag}(?:\s[^>]*)?>.*?</{tag}>", text, re.S)
    return (match.start(), match.end()) if match else None


def _items(block: str, item: str) -> list[str]:
    return re.findall(rf"<{item}(?:\s[^>]*)?/>|<{item}(?:\s[^>]*)?>.*?</{item}>", block, re.S)


def _split(icz: bytes) -> tuple[zipfile.ZipFile, str, str]:
    try:
        archive = zipfile.ZipFile(io.BytesIO(icz))
    except zipfile.BadZipFile as err:
        raise SceneProjectError(f"The scene project is not a zip file: {err}") from err
    name = next((n for n in archive.namelist() if n.lower().endswith(".icw")), None)
    if name is None:
        raise SceneProjectError("No project.icw in the scene project")
    return archive, name, archive.read(name).decode("utf-8")


# ------------------------------------------------------------------ checking and writing one entry


def _hex(resource: Any) -> str:
    try:
        value = int(resource)
    except (TypeError, ValueError) as err:
        raise SceneEditError("Choose a resource") from err
    if value <= 0:
        raise SceneEditError("Choose a resource")
    return f"{value:x}"


def _mask(slots: Any) -> str:
    chosen = {int(s) for s in (slots or [])}
    if not chosen or not all(1 <= s <= SMS_SLOTS for s in chosen):
        raise SceneEditError(f"Choose at least one of the SMS numbers 1–{SMS_SLOTS}")
    return "".join("1" if i + 1 in chosen else "0" for i in range(SMS_SLOTS))


def _emails(value: Any, single: bool = False) -> list[str]:
    items = value if isinstance(value, list) else re.split(r"[;,\s]+", str(value or ""))
    addresses = [a.strip() for a in items if a and a.strip()]
    if not addresses:
        raise SceneEditError("Enter an e-mail address")
    bad = [a for a in addresses if not _EMAIL.match(a)]
    if bad:
        raise SceneEditError(f"Not an e-mail address: {bad[0]}")
    if single and len(addresses) > 1:
        raise SceneEditError("Enter only one e-mail address")
    return addresses


def _text(value: Any, limit: int, name: str, required: bool = False) -> str:
    text = str(value or "").strip()
    if required and not text:
        raise SceneEditError(f"{name} is required")
    if len(text) > limit:
        raise SceneEditError(f"{name}: at most {limit} characters")
    if any(ord(c) < 32 and c not in "\r\n\t" for c in text):
        raise SceneEditError(f"{name} contains invalid characters")
    return text


def _date(now: datetime.datetime) -> str:
    return (f'<date year="{now.year}" month="{now.month}" day="{now.day}" hour="{now.hour}" '
            f'min="{now.minute}" sec="{now.second}"/>')


def notification_xml(entry: dict[str, Any], now: datetime.datetime) -> str:
    sms = entry.get("channel") == "sms"
    event = entry.get("event")
    if event not in EVENTS:
        raise SceneEditError("Choose when the message is sent")
    body = _text(entry.get("body"), SMS_MAX if sms else TEXT_MAX, "Message", required=sms)
    subject = "" if sms else _text(entry.get("subject"), TEXT_MAX, "Subject", required=True)
    recipient = _mask(entry.get("slots")) if sms else ";".join(_emails(entry.get("recipients")))
    tag = "smsnotification" if sms else "notification"
    return (f'<{tag} event="text.{event}"><resource rid="{_hex(entry.get("resource"))}"/>'
            f'<message recipient={quoteattr(recipient)} sender="Unknown">{_date(now)}'
            f"<subject>{escape(subject)}</subject><body>{escape(body)}</body></message></{tag}>")


def control_xml(entry: dict[str, Any]) -> str:
    sms = entry.get("channel") == "sms"
    action = entry.get("action")
    if action not in ACTIONS:
        raise SceneEditError("Choose what the command does")
    auth = entry.get("authorization")
    if auth not in (AUTH_SMS if sms else AUTH_EMAIL):
        raise SceneEditError("Choose how the command is authorised")
    trigger = _text(entry.get("trigger"), TRIGGER_MAX, "Command", required=True)
    parts = [f"<triggersubject>{escape(trigger)}</triggersubject>"]
    if auth == "sender_based":
        sender = _mask(entry.get("senders")) if sms else _emails(entry.get("senders"), single=True)[0]
        parts.append(f"<acceptsenderaddress>{escape(sender)}</acceptsenderaddress>")
    elif auth == "three_way":
        parts.append(f"<confirmationaddress>{escape(_emails(entry.get('confirmation_address'), single=True)[0])}</confirmationaddress>")
        parts.append(f"<confirmationmessage>{escape(_text(entry.get('confirmation_message'), TEXT_MAX, 'Confirmation'))}</confirmationmessage>")
    reply = _text(entry.get("confirmation"), SMS_MAX if sms else TEXT_MAX, "Reply")
    confirmation = f"<executionconfirmation><body>{escape(reply)}</body><subject></subject></executionconfirmation>" if reply else ""
    tag = "smscontrol" if sms else "emailcontrol"
    return (f'<{tag}><resource rid="{_hex(entry.get("resource"))}"/><action type="text.emailcontrol.{action}"/>'
            f'{confirmation}<authorization type="text.emailcontrol.authorization.{auth}">{"".join(parts)}</authorization></{tag}>')


# ------------------------------------------------------------------ the whole edit

_COMPARED = {
    "notification": ("channel", "resource", "event", "recipients", "slots", "subject", "body"),
    "control": ("channel", "resource", "action", "authorization", "trigger", "senders", "confirmation_address", "confirmation"),
}


def _same(kind: str, original: dict[str, Any], entry: dict[str, Any]) -> bool:
    def norm(v: Any) -> Any:
        return sorted(v) if isinstance(v, list) else ("" if v is None else v)
    return all(norm(original.get(k)) == norm(entry.get(k)) for k in _COMPARED[kind])


def apply(icz: bytes, notifications: list[dict[str, Any]], controls: list[dict[str, Any]],
          now: datetime.datetime | None = None) -> bytes:
    """A new ``.icz`` with these lists. Entries carry ``key`` (``"<list>:<index>"``) when they existed before."""
    now = now or datetime.datetime.now()
    archive, name, text = _split(icz)
    original_text = text
    current = parse(icz)
    originals = {"notification": current["notifications"], "control": current["controls"]}
    # each existing entry's own XML, in the same order parse() lists them
    raw: dict[str, list[tuple[str, str]]] = {"notification": [], "control": []}
    for list_tag, item_tag, _, kind in LISTS:
        span = _span(text, list_tag)
        block = text[span[0]:span[1]] if span else ""
        raw[kind] += [(f"{list_tag}:{i}", x) for i, x in enumerate(_items(block, item_tag))]
    if any(len(raw[k]) != len(originals[k]) for k in raw):
        raise SceneProjectError("The scene project's lists could not be matched up; it is left unchanged")

    by_key = {key: (xml, originals[kind][i]) for kind in raw for i, (key, xml) in enumerate(raw[kind])}
    new_lists: dict[str, list[str]] = {list_tag: [] for list_tag, *_ in LISTS}
    for kind, entries in (("notification", notifications), ("control", controls)):
        for entry in entries:
            channel = "sms" if entry.get("channel") == "sms" else "email"
            list_tag = next(t for t, _, c, k in LISTS if c == channel and k == kind)
            known = by_key.get(entry.get("key") or "")
            if known and _same(kind, known[1], {**entry, "channel": channel}):
                new_lists[list_tag].append(known[0])  # untouched: exactly as it was
            elif kind == "notification":
                new_lists[list_tag].append(notification_xml({**entry, "channel": channel}, now))
            else:
                new_lists[list_tag].append(control_xml({**entry, "channel": channel}))

    for list_tag, *_ in LISTS:
        before = [xml for key, xml in raw["notification"] + raw["control"] if key.startswith(f"{list_tag}:")]
        if new_lists[list_tag] == before:
            continue  # nothing changed in this list: it stays exactly as it was, whitespace included
        content = f"<{list_tag}>{''.join(new_lists[list_tag])}</{list_tag}>" if new_lists[list_tag] else f"<{list_tag}/>"
        span = _span(text, list_tag)
        text = text[:span[0]] + content + text[span[1]:] if span else _insert(text, list_tag, content)
    if text == original_text:
        return icz  # nothing changed at all: the very same file
    return _rezip(archive, name, text.encode("utf-8"))


def _insert(text: str, list_tag: str, content: str) -> str:
    """Put a list that did not exist after the element that comes before it in SceneDesign's order."""
    order = [*_AFTER, *(t for t, *_ in LISTS)]
    for previous in reversed(order[:order.index(list_tag)]):
        span = _span(text, previous)
        if span:
            return text[:span[1]] + content + text[span[1]:]
    end = text.rfind("</icwproject>")
    if end < 0:
        raise SceneProjectError("Not a SceneDesign project")
    return text[:end] + content + text[end:]


def _rezip(archive: zipfile.ZipFile, icw_name: str, icw: bytes) -> bytes:
    out = io.BytesIO()
    with zipfile.ZipFile(out, "w") as target:
        for info in archive.infolist():
            data = icw if info.filename == icw_name else archive.read(info.filename)
            target.writestr(info, data, compress_type=info.compress_type)
    return out.getvalue()
