from datetime import time, timedelta

from homeassistant.components.time import TimeEntity

from .const import DOMAIN
from .KWLStates import KWLState

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    async_add_entities([IntensiveDuration(easyConnector)])


class IntensiveDuration(TimeEntity):
    def __init__(self, easyConnector):
        self._easyConnector = easyConnector

        self._attr_unique_id = f"{self._easyConnector.serialNR}_intensiveDuration"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Intensive Mode Duration"
        self.native_value = self._easyConnector.IntensivDuration
        fuu = 2

    async def async_set_value(self, value: time) -> None:
        """Update the current value."""
        await self._easyConnector.setIntensiveDuration(value)

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._easyConnector.serialNR)}}

    @property
    def available(self) -> bool:
        return self._easyConnector.IsAvailable

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.IntensivDuration

    @property
    def name(self):
        return "Time for the intensive mode"
