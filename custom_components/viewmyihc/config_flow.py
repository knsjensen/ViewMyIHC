"""Config flow: one click, no settings – the connection is borrowed from the ihc integration.

The only field is the acceptance of the disclaimer: ViewMyIHC can change the controller, and that is at the user's own
risk.
"""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult

from .const import DOMAIN

SCHEMA = vol.Schema({vol.Required("accept", default=False): bool})


class ViewMyIHCConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle the (only) setup step."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> ConfigFlowResult:
        if self._async_current_entries():
            return self.async_abort(reason="single_instance_allowed")
        errors: dict[str, str] = {}
        if user_input is not None:
            if user_input.get("accept") is True:
                return self.async_create_entry(title="ViewMyIHC", data={"disclaimer_accepted": datetime.now(UTC).isoformat()})
            errors["accept"] = "must_accept"
        return self.async_show_form(step_id="user", data_schema=SCHEMA, errors=errors)
