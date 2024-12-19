from datetime import timedelta

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    UnitOfTemperature,
    CONCENTRATION_PARTS_PER_MILLION,
)

from .const import DOMAIN

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    new_devices = []

    new_devices.append(HumiditySensor(easyConnector))
    new_devices.append(OutsideTemperatureSensor(easyConnector))
    new_devices.append(SupplyTemperatureSensor(easyConnector))
    new_devices.append(IndoorTemperatureSensor(easyConnector))
    new_devices.append(ExhaustTemperatureSensor(easyConnector))
    new_devices.append(CurrentFanSpeed(easyConnector))
    new_devices.append(FilterChanged(easyConnector))
    new_devices.append(FilterDue(easyConnector))

    if easyConnector.CO2Value != 0xFFFF:  # only add CO2 sensor if it is available
        new_devices.append(CO2Sensor(easyConnector))

    if new_devices:
        async_add_entities(new_devices)


class SensorBase(SensorEntity):
    """Base representation of a Sensor."""

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        self._easyConnector = easyConnector

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._easyConnector.serialNR)}}

    # This property is important to let HA know if this entity is online or not.
    # If an entity is offline (return False), the UI will refelect this.
    @property
    def available(self) -> bool:
        return self._easyConnector.IsAvailable


class HumiditySensor(SensorBase):
    device_class = SensorDeviceClass.HUMIDITY

    native_unit_of_measurement = PERCENTAGE
    unit_of_measurement = PERCENTAGE
    native_value = int
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_AirRH"
        self._attr_name = f"{self._easyConnector.deviceModel} Air Relativ Humidity"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.AirRH

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.AirRH


class OutsideTemperatureSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_OutsideTemperature"
        self._attr_name = f"{self._easyConnector.deviceModel} Outside Temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.OutsideTemperature

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.OutsideTemperature


class SupplyTemperatureSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_SupplyTemperature"
        self._attr_name = f"{self._easyConnector.deviceModel} Supply Temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.SupplyTemperature

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.SupplyTemperature


class IndoorTemperatureSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_IndoorTemperature"
        self._attr_name = f"{self._easyConnector.deviceModel} Indoor Temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.IndoorTemperature

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.IndoorTemperature


class ExhaustTemperatureSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._easyConnector.serialNR}_ExhaustTemperature"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Exhaust Temperature"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.ExhaustTemperature

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.ExhaustTemperature


class CO2Sensor(SensorBase):
    device_class = SensorDeviceClass.CO2
    native_unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    unit_of_measurement = CONCENTRATION_PARTS_PER_MILLION
    native_value = int
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._easyConnector.serialNR}_CO2Value"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} CO2 Value"

    @property
    def state(self):
        """Return the state of the sensor."""
        if self._easyConnector.CO2Value == 0xFFFF:
            return 0
        else:
            return self._easyConnector.CO2Value

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        if self._easyConnector.CO2Value == 0xFFFF:
            self.native_value = 0
        else:
            self.native_value = self._easyConnector.CO2Value

    # If the sensor is not available the KWL reports FF FF, so this is used to set the sensor to be not available
    @property
    def available(self) -> bool:
        return (
            self._easyConnector.IsAvailable and self._easyConnector.CO2Value != 0xFFFF
        )


class CurrentFanSpeed(SensorBase):
    device_class = SensorDeviceClass.POWER_FACTOR

    native_unit_of_measurement = PERCENTAGE
    unit_of_measurement = PERCENTAGE
    native_value = int
    state_class = SensorStateClass.MEASUREMENT
    suggested_display_precision = 1

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_CurrentFanSpeed"
        self._attr_name = f"{self._easyConnector.deviceModel} current Fan Speed"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.CurrentFanSpeed

    @property
    def icon(self):
        return "mdi:fan"

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.CurrentFanSpeed


class FilterChanged(SensorBase):
    device_class = SensorDeviceClass.DATE

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_filterChanged"
        self._attr_name = f"{self._easyConnector.deviceModel} last filter change"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.filterChanged

    @property
    def icon(self):
        return "mdi:calendar-sync-outline"

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.filterChanged


class FilterDue(SensorBase):
    device_class = SensorDeviceClass.DATE

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_filterDue"
        self._attr_name = f"{self._easyConnector.deviceModel} next filter change"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.filterDue

    @property
    def icon(self):
        return "mdi:calendar-alert-outline"

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        self.native_value = self._easyConnector.filterDue
