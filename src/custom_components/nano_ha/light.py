"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

from nanoleafapi import Nanoleaf
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("addr"): cv.string,
    vol.Required("token"): cv.string,
})


def setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    # Assign configuration variables.
    # The configuration check takes care they are present.
    addr = config["addr"]
    token = config["token"]

    # Add devices
    add_entities([NanoLight(Nanoleaf(addr, token, print_errors=True))])


class NanoLight(LightEntity):
    """Representation of an Awesome Light."""

    def __init__(self, nl: Nanoleaf) -> None:
        """Initialize an AwesomeLight."""
        self._nl: Nanoleaf = nl
        self._state = None
        self._brightness = None

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._nl.get_name()

    @property
    def brightness(self):
        """Return the brightness of the light.

        This method is optional. Removing it indicates to Home Assistant
        that brightness is not supported for this light.
        """
        return self._nl.get_brightness() * 2.55

    @property
    def is_on(self) -> bool | None:
        """
        Return true if light is on.
        """
        return self._nl.get_power()

    def turn_on(self, **kwargs: Any) -> None:
        """
        Instruct the light to turn on.
        """
        self._nl.set_brightness(kwargs.get(ATTR_BRIGHTNESS, 255) / 2.55)
        self._nl.power_on()

    def turn_off(self, **kwargs: Any) -> None:
        """
        Instruct the light to turn off.
        """
        self._nl.power_off()

    def update(self) -> None:
        """
        Fetch new state data for this light.
        """
        self._state = self._nl.get_power()
        self._brightness = self._nl.get_brightness() * 2.55
