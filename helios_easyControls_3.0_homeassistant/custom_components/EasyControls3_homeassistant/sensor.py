from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import PERCENTAGE, UnitOfTemperature
from homeassistant.helpers.entity import Entity

from .const import DOMAIN

SCAN_INTERVAL = timedelta(minutes=60)


async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    new_devices = []

    new_devices.append(HumiditySensor(easyConnector))
    new_devices.append(OutsideTemperaturSensor(easyConnector))
    new_devices.append(SupplyTemperaturSensor(easyConnector))
    new_devices.append(IndoorTepmeraturSensor(easyConnector))
    new_devices.append(ExhaustTepmeraturSensor(easyConnector))
    new_devices.append(CurrentFanSpeed(easyConnector))
    new_devices.append(FilterChanged(easyConnector))
    new_devices.append(FilterDue(easyConnector))

    if new_devices:
        async_add_entities(new_devices)


class SensorBase(Entity):
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
        """Return True if roller and hub is available."""
        return True

    async def async_update(self):
        await self._easyConnector.readCurrentData()


class HumiditySensor(SensorBase):
    device_class = SensorDeviceClass.HUMIDITY

    native_unit_of_measurement = PERCENTAGE
    unit_of_measurement = PERCENTAGE
    native_value = int
    state_class = "measurement"
    suggested_display_precision = 2

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_AirRH"
        self._attr_name = f"{self._easyConnector.deviceModel} Air Relativ Humidity"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.AirRH


class OutsideTemperaturSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = "measurement"
    suggested_display_precision = 3

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_OutsideTemperatur"
        self._attr_name = f"{self._easyConnector.deviceModel} Outside Temperatur"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.OutsideTemperatur


class SupplyTemperaturSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = "measurement"
    suggested_display_precision = 3

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_SupplyTemperatur"
        self._attr_name = f"{self._easyConnector.deviceModel} Supply Temperatur"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.SupplyTemperatur


class IndoorTepmeraturSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = "measurement"
    suggested_display_precision = 3

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)

        self._attr_unique_id = f"{self._easyConnector.serialNR}_IndoorTepmeratur"
        self._attr_name = f"{self._easyConnector.deviceModel} Indoor Tepmeratur"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.IndoorTepmeratur


class ExhaustTepmeraturSensor(SensorBase):
    device_class = SensorDeviceClass.TEMPERATURE
    native_unit_of_measurement = UnitOfTemperature.CELSIUS
    unit_of_measurement = UnitOfTemperature.CELSIUS
    native_value = float
    state_class = "measurement"
    suggested_display_precision = 3

    def __init__(self, easyConnector):
        """Initialize the sensor."""
        super().__init__(easyConnector)
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._easyConnector.serialNR}_ExhaustTepmeratur"

        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} Exhaust Tepmeratur"

    @property
    def state(self):
        """Return the state of the sensor."""
        return self._easyConnector.ExhaustTepmeratur


class CurrentFanSpeed(SensorBase):
    device_class = SensorDeviceClass.POWER_FACTOR

    native_unit_of_measurement = PERCENTAGE
    unit_of_measurement = PERCENTAGE
    native_value = int
    state_class = "measurement"
    suggested_display_precision = 2

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
