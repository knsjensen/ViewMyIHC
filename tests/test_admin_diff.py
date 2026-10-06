from __future__ import annotations

import pytest

from conftest import load_module


@pytest.fixture(scope="module")
def d():
    return load_module("admin_diff")


def test_flatten_addresses_users_by_username_and_other_lists_by_index(d):
    flat = d.flatten(
        {"users": [{"username": "anna", "email": "k"}, {"username": "ann", "email": "a"}], "dns": ["1.1.1.1", "8.8.8.8"]}
    )
    assert flat[("users", "[anna]", "email")] == "k"
    assert flat[("users", "[ann]", "email")] == "a"
    assert flat[("dns", "[0]")] == "1.1.1.1" and flat[("dns", "[1]")] == "8.8.8.8"


def test_no_difference_means_no_changes(d):
    data = {"a": "1", "b": {"c": "2"}}
    assert d.diff_section("network", data, {"a": "1", "b": {"c": "2"}}) == []


def test_changed_added_and_removed(d):
    out = d.diff_section("network", {"a": "1", "gone": "x"}, {"a": "2", "new": "y"})
    assert {(c["type"], tuple(c["path"])) for c in out} == {
        ("changed", ("a",)),
        ("removed", ("gone",)),
        ("added", ("new",)),
    }
    changed = next(c for c in out if c["type"] == "changed")
    assert (changed["old"], changed["new"]) == ("1", "2")


def test_reordering_users_is_not_a_change(d):
    a = [{"username": "a", "x": "1"}, {"username": "b", "x": "2"}]
    assert d.diff_section("users", a, list(reversed(a))) == []


def test_volatile_sections_and_keys_are_ignored(d):
    assert d.diff_section("uptime", "1", "2") == []
    assert d.diff_section("local_time", {"h": 1}, {"h": 2}) == []
    same = d.diff_section(
        "system", {"uptime": "1", "realtimeclock": "a", "brand": "LK"}, {"uptime": "2", "realtimeclock": "b", "brand": "LK"}
    )
    assert same == []
    assert len(d.diff_section("system", {"uptime": "1", "brand": "LK"}, {"uptime": "2", "brand": "ELKO"})) == 1


def test_the_controller_clock_inside_the_time_settings_is_never_a_change(d):
    def settings(minutes, server="dk.pool.ntp.org"):
        clock = {"monthWithJanuaryAsOne": "10", "day": "6", "hours": "12", "year": "2026", "seconds": "9", "minutes": minutes}
        return {"synchroniseTimeAgainstServer": "true", "serverName": server, "timeAndDateInUTC": clock}

    assert d.diff_section("time", settings("1"), settings("2")) == []
    changed = d.diff_section("time", settings("1"), settings("2", server="pool.ntp.org"))
    assert [c["path"] for c in changed] == [["serverName"]]


def test_merge_first_read_has_no_changes(d):
    fresh = [{"key": "network", "title": "N", "data": {"ip": "1"}}]
    show, keep, changes = d.merge_refresh({}, fresh)
    assert changes == [] and keep == {"network": fresh[0]} and show == fresh


def test_merge_keeps_last_good_data_when_a_section_fails(d):
    saved = {"network": {"key": "network", "title": "N", "data": {"ip": "1"}}}
    show, keep, changes = d.merge_refresh(saved, [{"key": "network", "title": "N", "error": "boom"}])
    assert changes == [] and keep == saved
    assert show[0]["data"] == {"ip": "1"} and show[0]["error"] == "boom" and show[0]["stale"] is True


def test_merge_failing_section_without_history_is_shown_as_error(d):
    show, keep, _ = d.merge_refresh({}, [{"key": "dns", "title": "D", "error": "boom"}])
    assert keep == {} and show[0]["error"] == "boom" and "data" not in show[0]
