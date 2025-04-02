"""Platform for light integration."""
from __future__ import annotations

import logging
from typing import Any

from nanoleafapi import Nanoleaf
import voluptuous as vol

# Import the device class from the component that you want to support
import homeassistant.helpers.config_validation as cv
from homeassistant.components.light import (ATTR_BRIGHTNESS, ATTR_HS_COLOR, ATTR_COLOR_TEMP_KELVIN, PLATFORM_SCHEMA, LightEntity, ColorMode)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType

_LOGGER = logging.getLogger(__name__)

# Validation of the user's configuration
PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend({
    vol.Required("title"): cv.string,
    vol.Required("addr"): cv.string,
    vol.Required("token"): cv.string,
    vol.Optional("brightness_only", default=False): cv.boolean,
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
    brightness_only = config["brightness_only"]

    # Add devices
    add_entities([NanoLight(hass, title, addr, token, brightness_only)])


class NanoLight(LightEntity):
    def __init__(self, hass, entity_name, addr, token, brightness_only=False) -> None:
        self._hass = hass
        self._entity_name = entity_name
        self._nl: Nanoleaf|None = None
        self._addr = addr
        self._token = token
        self._name = "Nanoleaf Light"
        self.brightness_only = brightness_only

        self._attr_min_color_temp_kelvin = 2500
        self._attr_max_color_temp_kelvin = 6500

        self._attr_is_on = False
        self._attr_brightness = 0
        self._attr_color_temp_kelvin = self._attr_max_color_temp_kelvin
        self._attr_hs_color = (0, 0)

        if self.brightness_only:
            self._attr_color_mode = ColorMode.BRIGHTNESS
            self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        else:
            self._attr_color_mode = ColorMode.HS
            self._attr_supported_color_modes = {ColorMode.COLOR_TEMP, ColorMode.HS}
        
    @property
    def name(self) -> str:
        """Return the display name of this light."""
        return self._entity_name

    async def init_nl(self):
        if self._nl is not None:
            try:
                await self._hass.async_add_executor_job(self._nl.check_connection)
            except:
                self._nl = None

        if self._nl is None:
            self._nl = await self._hass.async_add_executor_job(Nanoleaf, self._addr, self._token)


    async def async_turn_on(self, **kwargs: Any) -> None:
        """
        Instruct the light to turn on.
        """
        await self.init_nl()
        await self._hass.async_add_executor_job(self._nl.power_on)

        if ATTR_BRIGHTNESS in kwargs:
            await self._hass.async_add_executor_job(self._nl.set_brightness, round(kwargs.get(ATTR_BRIGHTNESS) / 2.55))

        if ATTR_HS_COLOR in kwargs:
            hue_sat = kwargs.get(ATTR_HS_COLOR)
            await self._hass.async_add_executor_job(self._nl.set_hue, round(hue_sat[0]))
            await self._hass.async_add_executor_job(self._nl.set_saturation, round(hue_sat[1]))
        elif ATTR_COLOR_TEMP_KELVIN in kwargs:
            await self._hass.async_add_executor_job(self._nl.set_color_temp, kwargs.get(ATTR_COLOR_TEMP_KELVIN))


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

        if self.brightness_only:
            return

        colour_mode = await self._hass.async_add_executor_job(self._nl.get_color_mode)
        if colour_mode == "ct":
            # Color temperature
            self._attr_color_mode = ColorMode.COLOR_TEMP
            self._attr_color_temp_kelvin = await self._hass.async_add_executor_job(self._nl.get_color_temp)

        else:
            # "hs" for hue-saturation, but we'll also include "effect" here
            self._attr_color_mode = ColorMode.HS

        # Always update hue/sat - even if in color temp mode
        hue = await self._hass.async_add_executor_job(self._nl.get_hue)
        sat = await self._hass.async_add_executor_job(self._nl.get_saturation)
        self._attr_hs_color = (hue, sat)
