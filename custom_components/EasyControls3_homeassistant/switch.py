from datetime import timedelta

from homeassistant.components.switch import SwitchEntity

from .const import DOMAIN
from .KWLStates import KWLState

SCAN_INTERVAL = timedelta(seconds=60)
MIN_TIME_BETWEEN_SCANS = timedelta(seconds=30)


async def async_setup_entry(hass, config_entry, async_add_entities):
    easyConnector = hass.data[DOMAIN][config_entry.entry_id]

    if easyConnector.serialNR is None:
        await easyConnector.readCurrentData()

    async_add_entities([KWLOnOffSwitch(easyConnector)])


class KWLOnOffSwitch(SwitchEntity):
    def __init__(self, easyConnector):
        self._easyConnector = easyConnector

        self._attr_unique_id = f"{self._easyConnector.serialNR}_OnOffSwitch"
        # The name of the entity
        self._attr_name = f"{self._easyConnector.deviceModel} On Off Switch"


    async def async_turn_on(self, **kwargs):
        await self._easyConnector.turnOffOn(requestTurnOff=False)
        self.IsOn = False

    async def async_turn_off(self, **kwargs):
        await self._easyConnector.turnOffOn(requestTurnOff=True)
        self.IsOn = True

    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {"identifiers": {(DOMAIN, self._easyConnector.serialNR)}}

    @property
    def available(self) -> bool:
        return self._easyConnector.IsAvailable

    async def async_update(self):
        await self._easyConnector.readCurrentData()
        # self.is_on = self._easyConnector.IsOn

    @property
    def name(self):
        return "KWL on off switch"

    @property
    def is_on(self):
        """Return true if the switch is on."""
        return self._easyConnector.IsOn

    @property
    def device_class(self):
        """Return the class of this device, from SwitchDeviceClass."""
        return "switch"