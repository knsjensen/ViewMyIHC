"""An invented IHC project at the scale of a real house, for trying the panel (python scripts/dev_server.py --demo).

Module types per line and the product mix follow a typical LK IHC installation; all names and rooms are made up.
"""

from __future__ import annotations

import itertools
from xml.sax.saxutils import quoteattr

ROOMS = ["Entré", "Køkken", "Stue", "Alrum", "Bryggers", "Bad", "Gæstetoilet", "Soveværelse", "Børneværelse 1",
         "Børneværelse 2", "Kontor", "Gang", "Carport", "Have", "Teknikrum", "Loft"]

# identifier, LK name, inputs, outputs (dataline), count
PRODUCTS = [
    ("_0x2105", "LK FUGA Tryk 4 tast 2 dioder", 4, 2, 11), ("_0x2104", "LK FUGA Tryk 2 tast 1 diode", 2, 1, 4),
    ("_0x2102", "LK FUGA Tryk 4 tast", 4, 0, 2), ("_0x2109", "Magnetkontaktsæt", 1, 0, 10), ("_0x210a", "Røgsensor", 1, 1, 1),
    ("_0x210e", "PIR", 1, 0, 4), ("_0x210f", "PIR alarm", 1, 0, 9), ("_0x2110", "Skumringsrelæ", 1, 0, 1),
    ("_0x2111", "Kodetastatur", 3, 1, 1), ("_0x2112", "Sabotagekreds", 1, 0, 1), ("_0x2113", "Ringetryk", 1, 0, 1),
    ("_0x2115", "Backup modul", 2, 0, 1), ("_0x2701", "Havedørslås magnetkontakt", 1, 0, 2),
    ("_0x2201", "Stikkontakt", 0, 1, 9), ("_0x2202", "Lampeudtag", 0, 1, 29), ("_0x2203", "Lydgiver intern", 0, 2, 1),
    ("_0x2204", "Lydgiver ekstern", 0, 1, 1), ("_0x2209", "Ringeklokke", 0, 1, 1), ("_0x220a", "Telestat", 0, 1, 8),
    ("_0x220b", "Cirkulationspumpe", 0, 1, 1), ("_0x220c", "Ventilator", 0, 1, 2), ("_0x2703", "Havedørslås relæ", 0, 1, 1),
]
INPUT_MODULES = {1: ("Input 230", "Tavle 1"), 2: ("Input 24/3", ""), 3: ("Input 24/3", ""), 4: ("Input 24", "Tavle 3"),
                 5: ("Input 24", "Tavle 3"), 6: ("Input 24", "Tavle 3"), 7: ("Input 24/3", "Tavle 3"), 8: ("Input 24/3", "Tavle 3")}
OUTPUT_MODULES = {1: ("Output 230/10", "Tavle 1"), 2: ("Output 230/10", "Tavle 1"), 3: ("Output 230/10", "Tavle 1"),
                  4: ("Output 230/10", "Tavle 2"), 5: ("Output 230/10", "Tavle 2"), 6: ("Output 24", "Tavle 3"),
                  7: ("Output 24", "Tavle 4"), 8: ("Output 24", "Tavle 3"), 9: ("Output 24", "Tavle 3"),
                  10: ("Output 230/10", "Tavle 2"), 11: ("Output 24", "Tavle 3")}
CAPACITY = {"Input 230": 8, "Input 24": 16, "Input 24/3": 16, "Output 230/10": 8, "Output 24": 8}


def _addresses(modules: dict[int, tuple[str, str]], size: int, skip_first: int = 0):
    """Free addresses line by line, only on positions the module has (line 1 keeps most free, like a 230 V module)."""
    for line, (kind, _) in sorted(modules.items()):
        for position in range(1, CAPACITY[kind] + 1):
            if line == 1 and position > skip_first:
                continue
            yield (line - 1) * size + position


def demo_project() -> str:
    ids = itertools.count(0x1000)
    inputs = _addresses(INPUT_MODULES, 16, skip_first=2)
    outputs = _addresses(OUTPUT_MODULES, 8, skip_first=8)
    rooms: dict[str, list[str]] = {room: [] for room in ROOMS}
    room_cycle = itertools.cycle(ROOMS)
    # the wire colours of a 5x2 cable as installers write them in IHC Visual ("Ledningsfarve"), now and then left out
    colours = itertools.cycle(["Orange", "Hvid", "Brun", "Rød", "Grå", "Gul", "", "Blå (0V = Sort)", "Grøn", "Hvid+Lilla"])
    # buttons first so that each one's inputs sit next to each other, like a real installation
    for identifier, name, n_in, n_out, count in PRODUCTS:
        for _ in range(count):
            room = next(room_cycle)
            children = []
            for i in range(n_in):
                address = next(inputs, 0)
                children.append(f'<dataline_input id="_0x{next(ids):x}" name="Tast {i + 1}" address_dataline="_0x{address:x}" cable_colour="{next(colours)}"/>')
            for i in range(n_out):
                address = next(outputs, 0)
                label = "Diode" if n_in else name
                children.append(f'<dataline_output id="_0x{next(ids):x}" name="{label} {i + 1}" address_dataline="_0x{address:x}" cable_colour="{next(colours)}"/>')
            rooms[room].append(
                f'<product_dataline id="_0x{next(ids):x}" name={quoteattr(name)} product_identifier="{identifier}" '
                f'position={quoteattr(f"{room} ved døren")} cabletype="5x1,5mm2 NOIKJ" cablenumber="Kabel {next(ids) % 40 + 1}" power_group="Gruppe {len(rooms[room]) % 4 + 1}"'
                f' enduser_report="{"yes" if n_in >= 2 else "no"}">{"".join(children)}</product_dataline>'
            )
    remote = "".join(f'<airlink_input id="_0x{next(ids):x}" name="Tast {i + 1}" address_channel="_0x{i + 1:x}"/>' for i in range(8))
    rooms["Stue"].append(f'<product_airlink id="_0x{next(ids):x}" name="Fjernbetjening" product_identifier="_0x4104">{remote}</product_airlink>')
    for room in ROOMS[:8]:
        rooms[room].append(f'<product_dataline id="_0x{next(ids):x}" name="Temperatur sensor" product_identifier="_0x2124"/>')
    modules = (
        '<documentation_modules id="_0x10"><dataline_input_modules id="_0x11">'
        + "".join(f'<dataline_input_module id="_0x{next(ids):x}" module_type="{k}" dataline="{n}" location="{loc}"/>' for n, (k, loc) in INPUT_MODULES.items())
        + '</dataline_input_modules><dataline_output_modules id="_0x12">'
        + "".join(f'<dataline_output_module id="_0x{next(ids):x}" module_type="{k}" dataline="{n}" location="{loc}"/>' for n, (k, loc) in OUTPUT_MODULES.items())
        + "</dataline_output_modules></documentation_modules>"
    )
    groups = "".join(f'<group id="_0x{next(ids):x}" name={quoteattr(room)}>{"".join(items)}</group>' for room, items in rooms.items())
    return (
        '<utcs_project version_major="4" version_minor="0"><project_info description="Demohus"/>'
        '<modified year="2026" month="10" day="1" hour="12" minute="0"/>'
        f"{modules}{groups}</utcs_project>"
    )
