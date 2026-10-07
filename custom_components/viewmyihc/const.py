"""Constants for ViewMyIHC."""

DOMAIN = "viewmyihc"
# Must equal "version" in manifest.json and PANEL_VERSION in frontend/viewmyihc-panel.js (a test checks this)
VERSION = "0.16.0"
IHC_DOMAIN = "ihc"
# Key under hass.data["ihc"][serial] that holds the IHCController (see homeassistant/components/ihc/const.py)
IHC_CONTROLLER_KEY = "controller"

PANEL_URL_PATH = "viewmyihc"
PANEL_COMPONENT = "viewmyihc-panel"
STATIC_URL = "/viewmyihc_static"

# Maximum number of resource ids the panel may ask live values for in one request
MAX_VALUE_IDS = 250
