"""LK's own product pictures, as the controller's report pages show them (``rep_gen_files/eur/products/<id>.jpg``).

The pictures are public files on the controller (no login). They are fetched once, kept in Home Assistant's
``.storage`` folder and handed to the panel as data URIs. The controller only has pictures for some products
(buttons, wireless products); a missing one is remembered so it is not asked for again until a restart.
"""

from __future__ import annotations

import base64
from pathlib import Path
import re
from typing import Any

import requests

_ID = re.compile(r"^_0x[0-9a-fA-F]{1,8}$")
_FOLDER = re.compile(r"/reports/([A-Za-z0-9_]+)/entry_page\.html")
MAX_BYTES = 300_000
TIMEOUT = (5, 10)


def identifiers(project: Any) -> list[str]:
    """The product types of a project, for fetching all their pictures at once."""
    return sorted({n.attrs.get("product_identifier", "") for n in project.nodes.values() if n.category == "product"} - {""})


class ProductImages:
    def __init__(self, folder: Path) -> None:
        self._folder = folder
        self._missing: set[str] = set()
        self._reports: str | None = None

    def _base(self, controller: Any) -> str:
        url = str(controller.client.url).rstrip("/")
        if self._reports is None:
            try:
                page = requests.get(f"{url}/", timeout=TIMEOUT, verify=False).text  # noqa: S501 - the controller's own certificate
                match = _FOLDER.search(page)
                self._reports = match.group(1) if match else "LK_da"
            except requests.RequestException:
                return f"{url}/reports/LK_da"
        return f"{url}/reports/{self._reports}"

    def get(self, controller: Any, identifiers: list[str]) -> dict[str, str | None]:
        """``{identifier: data URI or None}`` (blocking: run in the executor)."""
        result: dict[str, str | None] = {}
        base = None
        for identifier in dict.fromkeys(identifiers):
            if not _ID.match(identifier or ""):
                continue
            path = self._folder / f"{identifier.lower()}.jpg"
            if path.exists():
                data = path.read_bytes()
            elif identifier in self._missing:
                data = None
            else:
                base = base or self._base(controller)
                data = self._fetch(f"{base}/rep_gen_files/eur/products/{identifier}.jpg")
                if data is None:
                    self._missing.add(identifier)
                else:
                    self._folder.mkdir(parents=True, exist_ok=True)
                    path.write_bytes(data)
            result[identifier] = f"data:image/jpeg;base64,{base64.b64encode(data).decode()}" if data else None
        return result

    @staticmethod
    def _fetch(url: str) -> bytes | None:
        try:
            response = requests.get(url, timeout=TIMEOUT, verify=False)  # noqa: S501
        except requests.RequestException:
            return None
        if response.status_code != 200 or not response.headers.get("content-type", "").startswith("image/"):
            return None
        return response.content if len(response.content) <= MAX_BYTES else None
