"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

from nanoleafapi import Nanoleaf
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, PLATFORM_SCHEMA, LightEntity, ColorMode)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("title"): cv.string,
    vol.Required("addr"): cv.string,
    vol.Required("token"): cv.string,
})


async def async_setup_platform(
        hass: HomeAssistant,
        config: ConfigType,
        add_entities: AddEntitiesCallback,
        discovery_info: DiscoveryInfoType | None = None
) -> None:
    # Assign configuration variables.
    # The configuration check takes care they are present.
    title = config["title"]
    addr = config["addr"]
    token = config["token"]

    # Add devices
    add_entities([NanoLight(hass, title, addr, token)])


class NanoLight(LightEntity):
    def __init__(self, hass, entity_name, addr, token) -> None:
        self._hass = hass
        self._entity_name = entity_name
        self._nl: Nanoleaf|None = None
        self._addr = addr
        self._token = token
        self._name = "Nanoleaf Light"

        self._attr_is_on = False
        self._attr_brightness = 0
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._entity_name

    async def init_nl(self):
        if self._nl is None:
            self._nl = await self._hass.async_add_executor_job(Nanoleaf, self._addr, self._token)


    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instruct the light to turn on.
        """
        await self.init_nl()
        await self._hass.async_add_executor_job(self._nl.power_on)
        await self._hass.async_add_executor_job(self._nl.set_brightness, round(kwargs.get(ATTR_BRIGHTNESS, 255) / 2.55))

    async def async_turn_off(self, **kwargs: Any) -> None:
        """
        Instruct the light to turn off.
        """
        await self.init_nl()
        await self._hass.async_add_executor_job(self._nl.power_off)

    async def async_update(self) -> None:
        """
        Fetch new state data for this light.
        """
        await self.init_nl()
        self._name = await self._hass.async_add_executor_job(self._nl.get_name)
        self._attr_is_on = await self._hass.async_add_executor_job(self._nl.get_power)
        self._attr_brightness = round(await self._hass.async_add_executor_job(self._nl.get_brightness) * 2.55)
