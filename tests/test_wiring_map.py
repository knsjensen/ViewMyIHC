"""The wiring map's data, and LK's product pictures fetched from the controller's report pages."""

from __future__ import annotations

import base64
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import threading
from types import SimpleNamespace

import pytest

from conftest import load_module

parser = load_module("project_parser")
wm = load_module("wiring_map")
pi = load_module("product_images")

PROJECT = (
    '<utcs_project version_major="4" version_minor="0"><documentation_modules id="_0x1">'
    '<dataline_input_modules id="_0x2"><dataline_input_module id="_0x3" module_type="Input 230" dataline="1" location="Tavle 1"/></dataline_input_modules>'
    '<dataline_output_modules id="_0x4"><dataline_output_module id="_0x5" module_type="Output 24" dataline="1" location="Tavle 3"/></dataline_output_modules>'
    "</documentation_modules>"
    '<group id="_0x10" name="Køkken">'
    '<product_dataline id="_0x11" name="Tryk 4 tast 2 dioder" product_identifier="_0x2105" position="Ved døren" cabletype="NOPOVIC" cablenumber="K7">'
    '<dataline_input id="_0x12" name="Øverst" address_dataline="_0x2" cable_colour="Grøn (0V = Sort)"/><dataline_input id="_0x13" name="Nederst" address_dataline="_0x9"/>'
    '<dataline_output id="_0x14" name="LED" address_dataline="_0x3"/></product_dataline>'
    '<product_dataline id="_0x15" name="Temperatur sensor" product_identifier="_0x2124"/>'
    '<product_dataline id="_0x18" name="Temperatur sensor" product_identifier="_0x2124"><settings id="_0x19" name="Indstillinger">'
    '<dataline_input id="_0x1a" name="Temperatur sensor indgang" address_dataline="_0x5" cable_colour="K1: Violet, K2: Hvid"/>'
    '</settings></product_dataline>'
    '<product_airlink id="_0x16" name="Fjernbetjening" product_identifier="_0x4104">'
    '<airlink_input id="_0x17" name="Tast 1" address_channel="_0x1"/></product_airlink>'
    "</group></utcs_project>"
)


def test_products_are_found_through_the_terminals_they_are_wired_to():
    result = wm.wiring(parser.Project(PROJECT))
    line = result["inputs"][0]
    assert (line["type"], line["capacity"], len(line["slots"])) == ("Input 230", 8, 9)  # position 9 is used: shown outside
    used = {s["position"]: (s["product_id"], s["name"]) for s in line["slots"] if "name" in s}
    assert used == {2: (0x11, "Øverst"), 5: (0x18, "Temperatur sensor indgang"), 9: (0x11, "Nederst")}
    assert [s["product_id"] for s in result["outputs"][0]["slots"] if "name" in s] == [0x11]  # the LED: same product, other side
    products = {p["id"]: p for p in result["products"]}
    assert products[0x11] == {"id": 0x11, "name": "Tryk 4 tast 2 dioder", "identifier": "_0x2105", "kind": "product_dataline",
                              "location": "Køkken", "position": "Ved døren", "cable_type": "NOPOVIC", "cable_number": "K7"}
    assert products[0x18]["name"] == "Temperatur sensor"  # not its section "Indstillinger"
    colours = {s["position"]: (s["colour"], s["colours"]) for s in line["slots"] if "name" in s}
    assert colours == {2: ("Grøn (0V = Sort)", ["#388e3c"]), 5: ("K1: Violet, K2: Hvid", ["#7b1fa2", "#f4f4f4"]), 9: ("", [])}
    assert result["airlink"]["inputs"] == [{"id": 0x17, "name": "Tast 1", "kind": "bool", "product_id": 0x16, "channel": "_0x1", "links": 0}]
    assert [p["name"] for p in result["unwired"]] == ["Temperatur sensor"]


JPEG = b"\xff\xd8\xff\xe0fake-jpeg"


@pytest.fixture
def controller_site():
    hits: list[str] = []

    class Handler(BaseHTTPRequestHandler):
        def log_message(self, *args):
            pass

        def do_GET(self):  # noqa: N802
            hits.append(self.path)
            if self.path == "/":
                body, kind = b'<a href="/reports/LK_da/entry_page.html?FILE=/bin/IHCFile">r</a>', "text/html"
            elif self.path == "/reports/LK_da/rep_gen_files/eur/products/_0x2105.jpg":
                body, kind = JPEG, "image/jpeg;charset=ISO-8859-1"
            elif self.path.endswith("_0x2106.jpg"):
                body, kind = b"<html>not a picture</html>", "text/html"
            else:
                self.send_response(404)
                self.end_headers()
                return
            self.send_response(200)
            self.send_header("Content-Type", kind)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

    server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    yield SimpleNamespace(client=SimpleNamespace(url=f"http://127.0.0.1:{server.server_address[1]}")), hits
    server.shutdown()


def test_pictures_are_fetched_once_and_kept(controller_site, tmp_path):
    controller, hits = controller_site
    images = pi.ProductImages(tmp_path)
    got = images.get(controller, ["_0x2105", "_0x2201", "_0x2106", "../etc/passwd", "_0x2105"])
    assert got["_0x2105"] == "data:image/jpeg;base64," + base64.b64encode(JPEG).decode()
    assert got["_0x2201"] is None and got["_0x2106"] is None  # missing, and not a picture
    assert "../etc/passwd" not in got
    assert (tmp_path / "_0x2105.jpg").read_bytes() == JPEG
    before = len(hits)
    again = images.get(controller, ["_0x2105", "_0x2201"])
    assert again["_0x2105"] == got["_0x2105"] and len(hits) == before  # from disk / remembered as missing
    fresh = pi.ProductImages(tmp_path)  # after a restart the picture is still on disk
    assert fresh.get(controller, ["_0x2105"])["_0x2105"] == got["_0x2105"]


def test_every_connector_of_the_controller_is_listed_the_unused_as_free():
    result = wm.wiring(parser.Project(PROJECT))
    assert [(line["line"], bool(line.get("free"))) for line in result["inputs"]] == [(1, False)] + [(n, True) for n in range(2, 9)]
    assert len(result["outputs"]) == 16 and not result["outputs"][0].get("free") and result["outputs"][15]["free"]


@pytest.mark.parametrize(("text", "expected"), [
    ("Orange", ["#f57c00"]),
    ("Grøn (0V = Sort, 24V = Rød)", ["#388e3c"]),
    ("Blå (sort = 0v)", ["#1976d2"]),
    ("Orange+Grøn", ["#f57c00", "#388e3c"]),
    ("Grå + Grå", ["#8c8c8c"]),
    ("K3: Rød, K2: Rød", ["#d32f2f"]),
    ("ukendt", []),
    ("", []),
])
def test_wire_colours_from_free_text(text, expected):
    assert wm.wire_colours(text) == expected
