"""The controller's value format: read what it reports, check panel input, and build setResourceValue."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import pytest

from conftest import load_module

rv = load_module("resource_values")

ENV = '<SOAP-ENV:Envelope xmlns:SOAP-ENV="http://schemas.xmlsoap.org/soap/envelope/"><SOAP-ENV:Body>{}</SOAP-ENV:Body></SOAP-ENV:Envelope>'
XSI = 'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xmlns:ns2="utcs.values"'


def value(ws_type: str, fields: str) -> str:
    return f'<ns1:value {XSI} xsi:type="ns2:{ws_type}">{fields}</ns1:value>'


def single(wrapper: str, inner: str) -> ET.Element:
    return ET.fromstring(ENV.format(f'<ns1:{wrapper} xmlns:ns1="utcs">{inner}<ns1:resourceID>5</ns1:resourceID></ns1:{wrapper}>'))


def test_reads_each_editable_type_with_limits_and_enum_definition():
    cases = {
        value("WSBooleanValue", "<ns2:value>true</ns2:value>"): {"type": rv.BOOL, "value": True},
        value("WSIntegerValue", "<ns2:integer>7</ns2:integer><ns2:maximumValue>100</ns2:maximumValue><ns2:minimumValue>0</ns2:minimumValue>"):
            {"type": rv.INTEGER, "value": 7, "min": 0, "max": 100},
        value("WSFloatingPointValue", "<ns2:floatingPointValue>21.5</ns2:floatingPointValue>"): {"type": rv.FLOAT, "value": 21.5},
        value("WSTimerValue", "<ns2:milliseconds>1500</ns2:milliseconds>"): {"type": rv.TIMER, "value": 1500},
        value("WSTimeValue", "<ns2:hours>7</ns2:hours><ns2:seconds>0</ns2:seconds><ns2:minutes>5</ns2:minutes>"): {"type": rv.TIME, "value": "07:05:00"},
        value("WSEnumValue", "<ns2:definitionTypeID>99</ns2:definitionTypeID><ns2:enumValueID>101</ns2:enumValueID><ns2:enumName>Ur 2</ns2:enumName>"):
            {"type": rv.ENUM, "value": 101, "name": "Ur 2", "definition": 99},
    }
    for inner, expected in cases.items():
        info = rv.read_envelope(single("getRuntimeValue2", inner), "getRuntimeValue2")
        assert info["editable"] is True
        assert {k: info[k] for k in expected} == expected


def test_unknown_types_are_shown_but_not_editable():
    info = rv.read_envelope(single("getInitialValue2", value("WSWeekdayValue", "<ns2:weekdayNumber>2</ns2:weekdayNumber>")), "getInitialValue2")
    assert info["type"] == "WSWeekdayValue" and info["editable"] is False


def test_missing_answer_reads_as_none():
    assert rv.read_envelope(ET.fromstring(ENV.format("")), "getRuntimeValue2") is None


def test_list_answer_is_keyed_by_resource_id():
    items = "".join(
        f'<ns1:arrayItem>{value("WSBooleanValue", f"<ns2:value>{v}</ns2:value>")}<ns1:resourceID>{i}</ns1:resourceID></ns1:arrayItem>'
        for i, v in ((10, "true"), (11, "false"))
    )
    doc = ET.fromstring(ENV.format(f'<ns1:getInitialValues2 xmlns:ns1="utcs">{items}</ns1:getInitialValues2>'))
    assert {k: v["value"] for k, v in rv.read_envelopes(doc, "getInitialValues2").items()} == {10: True, 11: False}


@pytest.mark.parametrize(
    ("current", "raw", "expected"),
    [
        ({"type": rv.BOOL}, False, False),
        ({"type": rv.INTEGER, "min": 0, "max": 10}, 10, 10),
        ({"type": rv.INTEGER}, 3.0, 3),
        ({"type": rv.FLOAT, "min": -50.0, "max": 100.0}, 21, 21.0),
        ({"type": rv.TIMER}, 2500, 2500),
        ({"type": rv.TIME}, "7:05", (7, 5, 0)),
        ({"type": rv.ENUM, "definition": 1}, 101, 101),
    ],
)
def test_coerce_accepts_valid_input(current, raw, expected):
    assert rv.coerce(current, raw, {101}) == expected


@pytest.mark.parametrize(
    ("current", "raw"),
    [
        ({"type": rv.BOOL}, 1),
        ({"type": rv.INTEGER, "min": 0, "max": 10}, 11),
        ({"type": rv.INTEGER}, 2.5),
        ({"type": rv.INTEGER}, True),
        ({"type": rv.FLOAT, "min": 0.0, "max": 1.0}, -1),
        ({"type": rv.FLOAT}, "3"),
        ({"type": rv.TIMER}, -1),
        ({"type": rv.TIME}, "24:00"),
        ({"type": rv.TIME}, "<x>"),
        ({"type": rv.ENUM, "definition": 1}, 102),
        ({"type": "WSWeekdayValue"}, 1),
    ],
)
def test_coerce_refuses_invalid_input(current, raw):
    with pytest.raises(ValueError):
        rv.coerce(current, raw, {101})


def test_payload_targets_runtime_or_initial_value_and_matches_the_reported_type():
    run = rv.set_payload(5, {"type": rv.BOOL}, True, runtime=True)
    ini = rv.set_payload(5, {"type": rv.BOOL}, True, runtime=False)
    assert "<isValueRuntime>true</isValueRuntime>" in run and "<isValueRuntime>false</isValueRuntime>" in ini
    assert 'i:type="a:WSBooleanValue"' in run and "<resourceID>5</resourceID>" in run
    ET.fromstring(run)  # well formed


def test_enum_payload_escapes_the_name_and_carries_the_definition():
    body = rv.set_payload(5, {"type": rv.ENUM, "definition": 99}, 101, runtime=True, enum_name="A<&>B")
    doc = ET.fromstring(body)
    texts = {el.tag.rsplit("}", 1)[-1]: el.text for el in doc.iter()}
    assert texts["definitionTypeID"] == "99" and texts["enumValueID"] == "101" and texts["enumName"] == "A<&>B"


def test_time_payload_is_well_formed():
    body = rv.set_payload(5, {"type": rv.TIME}, (7, 5, 9), runtime=False)
    texts = {el.tag.rsplit("}", 1)[-1]: el.text for el in ET.fromstring(body).iter()}
    assert (texts["hours"], texts["minutes"], texts["seconds"]) == ("7", "5", "9")


def test_accepted_reads_the_controllers_answer():
    yes = ET.fromstring(ENV.format('<ns1:setResourceValue2 xmlns:ns1="utcs">true</ns1:setResourceValue2>'))
    no = ET.fromstring(ENV.format('<ns1:setResourceValue2 xmlns:ns1="utcs">false</ns1:setResourceValue2>'))
    assert rv.accepted(yes) and not rv.accepted(no)
