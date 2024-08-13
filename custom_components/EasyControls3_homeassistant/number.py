from datetime import timedelta

from homeassistant.components.number import NumberDeviceClass, NumberEntity

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    async_add_entities([FanSpeedNumber(easyConnector)])


class FanSpeedNumber(NumberEntity):
    device_class = NumberDeviceClass.POWER_FACTOR
    native_step = 1.0

    def __init__(self, easyConnector):
        self._easyConnector = easyConnector

        self._attr_unique_id = f"{self._easyConnector.serialNR}_intensivFanSpeed"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Fan Speed for intensive"

        self.native_value = self._easyConnector.IntensivFanSpeed

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._easyConnector.serialNR)}}

    @property
    def available(self) -> bool:
        return self._easyConnector.IsAvailable

    @property
    def name(self):
        return "Set Speed for intensive Fan"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.native_value = value
        await self._easyConnector.setIntensiveFanSpeed(value)
