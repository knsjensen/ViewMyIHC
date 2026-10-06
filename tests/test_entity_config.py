from __future__ import annotations

import pytest
import yaml

from conftest import load_module


@pytest.fixture(scope="module")
def ec():
    return load_module("entity_config")


def detail(sample, parser, hex_id):
    return sample.detail(parser.parse_id(hex_id))


# ------------------------------------------------------------------ suggestions


def test_output_suggests_switch_input_suggests_binary_sensor(ec, sample, parser):
    assert ec.suggest(detail(sample, parser, "_0x111"))["default_platform"] == "switch"  # dataline_output "On"
    assert ec.suggest(detail(sample, parser, "_0x101"))["default_platform"] == "binary_sensor"  # dataline_input


def test_temperature_suggests_sensor_with_unit(ec, sample, parser):
    s = ec.suggest(detail(sample, parser, "_0x20a"))
    assert s["default_platform"] == "sensor" and s["option_defaults"]["unit_of_measurement"] == "°C"
    avail = {p["platform"]: p["available"] for p in s["platforms"]}
    assert avail == {"binary_sensor": False, "light": True, "sensor": True, "switch": False}


def test_time_enum_resources_have_no_entity_type_in_the_integration_yet(ec, sample, parser):
    for hex_id in ("_0x207", "_0x208", "_0x209"):
        s = ec.suggest(detail(sample, parser, hex_id))
        assert s["supported"] is False and s["default_platform"] is None
        assert not any(p["available"] for p in s["platforms"])


def test_defaults_use_locality_as_position_and_offer_name_alternatives(ec, sample, parser):
    s = ec.suggest(detail(sample, parser, "_0x111"))
    assert s["defaults"]["position"] == "Køkken"
    assert s["defaults"]["name"] == "Lampeudtag On"  # short generic names get their product prepended
    assert "On" in s["name_suggestions"]


# ------------------------------------------------------------------ validation


def good(**over):
    entry = {"platform": "switch", "id": 514, "name": "Lampe", "options": {}}
    entry.update(over)
    return entry


def test_validate_trims_text(ec):
    e = ec.validate_entry(good(name="  Lampe  ", note=" n ", position=" Køkken "))
    assert (e["name"], e["note"], e["position"]) == ("Lampe", "n", "Køkken")


def test_only_the_id_is_required(ec):
    """The integration itself only requires `id`; the name then defaults to ihc_<id>."""
    e = ec.validate_entry({"platform": "switch", "id": 7})
    assert e["name"] == "" and e["options"] == {}
    assert ec.render_entry(e) == "- id: 7"


@pytest.mark.parametrize(
    "bad, field",
    [
        (good(platform="climate"), "platform"),
        (good(id=0), "id"),
        (good(id="abc"), "id"),
        (good(id=-5), "id"),
        (good(options={"on_id": "x"}), "options.on_id"),
        (good(options={"off_id": -1}), "options.off_id"),
        (good(platform="binary_sensor", options={"type": "nonsense"}), "options.type"),
    ],
)
def test_validate_rejects(ec, bad, field):
    with pytest.raises(ec.EntityConfigError) as err:
        ec.validate_entry(bad, device_classes={"door", "motion"})
    assert field in err.value.errors


def test_validate_keeps_only_the_options_of_the_platform(ec):
    e = ec.validate_entry(good(platform="sensor", options={"unit_of_measurement": "°C", "on_id": 5, "dimmable": True}))
    assert e["options"] == {"unit_of_measurement": "°C"}
    light = ec.validate_entry(good(platform="light", options={"dimmable": True, "on_id": "7", "off_id": ""}))
    assert light["options"] == {"dimmable": True, "on_id": 7}


# ------------------------------------------------------------------ rendering


def entry(ec, **raw):
    return ec.validate_entry(raw, device_classes={"door", "motion"})


def test_minimal_output_only_values_that_differ_from_the_defaults(ec):
    assert ec.render_entry(entry(ec, platform="binary_sensor", id=1, name="Dør", options={"inverting": False})) == '- id: 1\n  name: "Dør"'
    assert ec.render_entry(entry(ec, platform="binary_sensor", id=1, options={"inverting": True, "type": "door"})) == (
        "- id: 1\n  inverting: true\n  type: \"door\""
    )
    assert ec.render_entry(entry(ec, platform="light", id=2, options={"dimmable": False})) == "- id: 2"


def test_every_yaml_field_of_every_platform_can_be_rendered(ec):
    full = {
        "binary_sensor": {"inverting": True, "type": "motion"},
        "light": {"dimmable": True, "on_id": 11, "off_id": 12},
        "sensor": {"unit_of_measurement": "°C"},
        "switch": {"on_id": 21, "off_id": 22},
    }
    for platform, options in full.items():
        text = ec.render_entry(entry(ec, platform=platform, id=5, name="N", note="K", position="P", options=options))
        data = yaml.safe_load(text)[0]
        assert set(data) == {"id", "name", "note", "position", *options}, platform


def test_rendered_yaml_round_trips_special_characters(ec):
    text = ec.render_entry(entry(ec, platform="switch", id=30, name='Lampe "køkken"', note="linje1\nlinje2", position="Køkken"))
    assert yaml.safe_load(text) == [{"id": 30, "name": 'Lampe "køkken"', "note": "linje1\nlinje2", "position": "Køkken"}]


def test_indentation_moves_the_whole_item(ec):
    text = ec.render_entry(entry(ec, platform="switch", id=1, name="A", options={"on_id": 2}), indent=4)
    assert text.splitlines() == ['    - id: 1', '      name: "A"', "      on_id: 2"]
    assert yaml.safe_load("x:\n" + text) == {"x": [{"id": 1, "name": "A", "on_id": 2}]}


def test_generated_entries_pass_the_builtin_ihc_schema(ec):
    """The strongest check: Home Assistant's own ihc manual-setup schema must accept what we generate."""
    pytest.importorskip("homeassistant.components.ihc.manual_setup")
    from homeassistant.components.ihc.manual_setup import IHC_SCHEMA

    full = {
        "binary_sensor": {"inverting": True, "type": "door"},
        "light": {"dimmable": True, "on_id": 11, "off_id": 12},
        "sensor": {"unit_of_measurement": "°C"},
        "switch": {"on_id": 21, "off_id": 22},
    }
    config = {"url": "http://192.168.1.3", "username": "u", "password": "p"}
    for platform, options in full.items():
        config[platform] = yaml.safe_load(ec.render_entry(entry(ec, platform=platform, id=5, name="N", note="K", position="P", options=options)))
    validated = IHC_SCHEMA(config)
    assert validated["binary_sensor"][0]["type"] == "door" and validated["binary_sensor"][0]["inverting"] is True
    assert validated["light"][0]["dimmable"] is True and validated["switch"][0]["on_id"] == 21
    assert validated["sensor"][0]["unit_of_measurement"] == "°C"


def test_the_minimal_entry_without_a_name_gets_the_integrations_default_name(ec):
    pytest.importorskip("homeassistant.components.ihc.manual_setup")
    from homeassistant.components.ihc.manual_setup import IHC_SCHEMA

    config = {"url": "x", "username": "u", "password": "p", "switch": yaml.safe_load(ec.render_entry(entry(ec, platform="switch", id=514)))}
    assert IHC_SCHEMA(config)["switch"][0]["name"] == "ihc_514"


def test_the_options_we_offer_match_the_integrations_schema(ec):
    """If Home Assistant adds or renames an option, this test shows it."""
    pytest.importorskip("homeassistant.components.ihc.manual_setup")
    from homeassistant.components.ihc import manual_setup

    schemas = {
        "binary_sensor": manual_setup.BINARY_SENSOR_SCHEMA,
        "light": manual_setup.LIGHT_SCHEMA,
        "sensor": manual_setup.SENSOR_SCHEMA,
        "switch": manual_setup.SWITCH_SCHEMA,
    }
    common = {"id", "name", "note", "position"}
    for platform, schema in schemas.items():
        keys = {str(k) for k in schema.schema}
        assert keys == common | set(ec.PLATFORM_OPTIONS[platform]), platform


def test_device_classes_offered_exist_in_home_assistant():
    pytest.importorskip("homeassistant.components.binary_sensor")
    from homeassistant.components.binary_sensor import BinarySensorDeviceClass

    assert {"door", "motion", "window", "smoke"} <= {c.value for c in BinarySensorDeviceClass}
