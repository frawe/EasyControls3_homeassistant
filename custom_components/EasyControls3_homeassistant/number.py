from datetime import timedelta

from homeassistant.components.number import NumberDeviceClass, NumberEntity

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    async_add_entities(
        [
            FanSpeedNumberAtHome(easyConnector),
            FanSpeedNumberAway(easyConnector),
            FanSpeedNumberIntensive(easyConnector),
        ]
    )


class FanSpeedNumber(NumberEntity):
    device_class = NumberDeviceClass.POWER_FACTOR
    native_step = 1.0

    def __init__(self, easyConnector):
        self._easyConnector = easyConnector

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


class FanSpeedNumberAtHome(FanSpeedNumber):
    def __init__(self, easyConnector):
        super().__init__(easyConnector)
        self._attr_unique_id = f"{self._easyConnector.serialNR}_atHomeFanSpeed"

        # The name of the entity
        self._attr_name = (
            f"{self._easyConnector.deviceModel} Fan Speed for at home mode"
        )

        self.native_value = self._easyConnector.AtHomeFanSpeed

    @property
    def name(self):
        return "Set fan speed for at home mode"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.native_value = value
        await self._easyConnector.setAtHomeFanSpeed(value)

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.AtHomeFanSpeed


class FanSpeedNumberAway(FanSpeedNumber):
    def __init__(self, easyConnector):
        super().__init__(easyConnector)
        self._attr_unique_id = f"{self._easyConnector.serialNR}_awayFanSpeed"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Fan Speed for away mode"

        self.native_value = self._easyConnector.AwayFanSpeed

    @property
    def name(self):
        return "Set fan speed for away mode"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.native_value = value
        await self._easyConnector.setAwayFanSpeed(value)

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.AwayFanSpeed


class FanSpeedNumberIntensive(FanSpeedNumber):
    def __init__(self, easyConnector):
        super().__init__(easyConnector)
        self._attr_unique_id = f"{self._easyConnector.serialNR}_intensivFanSpeed"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Fan Speed for intensive"

        self.native_value = self._easyConnector.IntensivFanSpeed

    @property
    def name(self):
        return "Set fan speed for intensive mode"

    async def async_set_native_value(self, value: float) -> None:
        """Update the current value."""
        self.native_value = value
        await self._easyConnector.setIntensiveFanSpeed(value)

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.IntensivFanSpeed
