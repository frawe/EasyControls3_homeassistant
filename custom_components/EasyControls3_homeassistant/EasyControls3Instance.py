import datetime
import logging
import math

from dateutil.relativedelta import relativedelta
from websockets.asyncio.client import connect

from .Conversions import dataToCelsius
from .deviceList import deviceInfo
from .KWLStates import KWLState

LOGGER = logging.getLogger(__name__)


class EasyControls3Instance:
    def __init__(self, url: str) -> None:
        self._url = "ws://" + url + ":80"
        self._deviceModel = None
        self._deviceType = None
        self._SerialNR = None
        self._instanceState = None
        self._CurrentFanSpeed = None
        self._intensivFanSpeed = None
        self._atHomeFanSpeed = None
        self._awayFanSpeed = None
        self._intensivDuration = None
        self._OutsideTemperature = None
        self._SupplyTemperature = None
        self._IndoorTemperature = None
        self._ExhaustTemperature = None
        self._AirRH = None
        self._filterInterval = None
        self._filterChanged = None
        self._filterDue = None
        self._sthModified = False
        self._lastUpdate = None
        self._minSecondsBetweenRead = 60
        self._isAvailable = True
        self._offlineAfter = datetime.timedelta(minutes=10)
        self._isOn = True
        self._CO2Value = None

    async def _exchangeData(self, request):
        async with connect(self._url) as websocket:
            LOGGER.debug("connected")
            # request current data package
            await websocket.send(request)
            LOGGER.debug("sent")
            response = await websocket.recv()
            return response

    async def readCurrentData(self):
        if (
            self._lastUpdate is None
            or (datetime.datetime.now() - self._lastUpdate).total_seconds()
            > self._minSecondsBetweenRead
            or self._sthModified
        ):
            try:
                request = bytes.fromhex("0300f6000000f900")
                response = await self._exchangeData(request)
                self._parseData(response)
                self._isAvailable = True
                self._lastUpdate = datetime.datetime.now()
                self._sthModified = False
            except Exception as exception:
                LOGGER.error(f"error in reading ({exception})")
                if datetime.datetime.now() - self._lastUpdate > self._offlineAfter:
                    self._isAvailable = False

    def _parseData(self, data):
        # device info
        self._deviceModel = deviceInfo["device_model_data"][data[17 * 2 + 1]]
        self._deviceType = deviceInfo["device_type_data"][data[16 * 2 + 1]]
        self._SerialNR = (
            data[14 * 2] * 16777216
            + data[14 * 2 + 1] * 65536
            + data[15 * 2] * 256
            + data[15 * 2 + 1]
        )

        # state
        # current device state - we need A_CYC_STATE (Y), A_CYC_FIREPLACE_TIMER (u), A_CYC_BOOST_TIMER (v)
        # offsets: 107, 111, 110
        # the status is calculated:
        # IF fireplace timer is 0 and boost timer is 0 and state is 0 => 0
        # IF fireplace timer is not 0 => 3
        # IF boost timer is not 0 => 2
        # IF state is not 0 => 1
        # eq: a = 0 == u ? 0 == v ? 0 == Y ? 0 : 1 : 2 : 3
        state = data[107 * 2 + 1]
        fire = data[111 * 2 + 1]
        boost = data[110 * 2 + 1]
        tmpState = KWLState.AtHome
        tmpState = KWLState.Away if state != 0 else tmpState
        tmpState = KWLState.Intensive if boost != 0 else tmpState
        tmpState = KWLState.Individual if fire != 0 else tmpState
        self._instanceState = tmpState

        # fan
        self._CurrentFanSpeed = data[129]
        self._intensivFanSpeed = data[431]
        self._atHomeFanSpeed = data[419]
        self._awayFanSpeed = data[407]

        # temperatures
        self._OutsideTemperature = dataToCelsius(data, 67)
        self._SupplyTemperature = dataToCelsius(data, 69)
        self._IndoorTemperature = dataToCelsius(data, 65)
        self._ExhaustTemperature = dataToCelsius(data, 66)

        # humidity
        self._AirRH = data[74 * 2 + 1]

        # filter
        self._filterInterval = data[239 * 2 + 1]  # a month at helios has 30 days
        lastFilterChangedYear = 2000 + data[250 * 2 + 1]
        lastFilterChangedMonth = data[249 * 2 + 1]
        lastFilterChangedDay = data[248 * 2 + 1]
        self._filterChanged = datetime.date(
            lastFilterChangedYear, lastFilterChangedMonth, lastFilterChangedDay
        )
        self._filterDue = self._filterChanged + relativedelta(
            days=+int(self._filterInterval)
        )

        # duration
        intensivDurationInMinutes = data[493]
        intensivDurationHours = math.floor(intensivDurationInMinutes / 60)
        intensivDurationMinutes = intensivDurationInMinutes - 60 * intensivDurationHours

        self._intensivDuration = datetime.time(
            intensivDurationHours, intensivDurationMinutes
        )

        # on off state
        # value_if_true if condition else value_if_false
        self._isOn = bool(data[217] == 0)

        # CO2 value
        self._CO2Value = int(data[182]) << 8 | int(data[183])

    async def switchMode(self, wantedKWLState):
        if wantedKWLState is KWLState.AtHome:
            requestData = "0800f9000112000004120000051200000b37"
        elif wantedKWLState is KWLState.Away:
            requestData = "0800f9000112010004120000051200000c37"
        elif wantedKWLState is KWLState.Intensive:
            requestedDuration = (
                self.IntensivDuration.hour * 60 + self.IntensivDuration.minute
            )
            requestData = (
                "0600f9000412"
                + (requestedDuration).to_bytes(2, byteorder="little").hex()
                + "05120000"
                + (requestedDuration + 0x2508).to_bytes(2, byteorder="little").hex()
            )


        elif wantedKWLState is KWLState.Individual:
            requestData = "0600f90004120000051296009e25"
        else:
            raise TypeError("direction must be an instance of Direction Enum")

        request = bytes.fromhex(requestData)
        response = await self._exchangeData(request)

        if bytes.fromhex("0200f500f700") == response:
            LOGGER.debug("expected response")
        else:
            LOGGER.debug("unexpected response")

        self._sthModified = True

    def checkFanSpeedLimit(self, requestedFanSpeed: int):
        if requestedFanSpeed < 1:
            requestedFanSpeed = 1
        elif requestedFanSpeed > 100:
            requestedFanSpeed = 100
        else:
            requestedFanSpeed = round(requestedFanSpeed)
        return requestedFanSpeed

    def createFanSpeedPlainRequestString(self, requestedFanSpeed: int):
        return (
            f"{requestedFanSpeed:x}"
            if len(f"{requestedFanSpeed:x}") == 2
            else ("0" + f"{requestedFanSpeed:x}")
        )  # needs to be 1byte, 2 nibble long

    def createFanSpeedModdedRequestString(self, requestedFanSpeed: int, mode: KWLState):
        offset = 30  # Intensive

        if mode is KWLState.AtHome:
            offset = 24
        elif mode is KWLState.Away:
            offset = 18
        elif mode is KWLState.Intensive:
            offset = 30
        else:  # Individual/Fireplace should not be changed from here
            LOGGER.debug("Individual/Fireplace is not supported")

        return (
            f"{requestedFanSpeed + offset :x}"
            if len(f"{requestedFanSpeed + offset :x}") == 2
            else ("0" + f"{requestedFanSpeed + offset :x}")
        )  # needs to be 1byte, 2 nibble long

    async def setFanSpeed(self, requestedFanSpeed: int, mode: KWLState):
        requestedFanSpeed = self.checkFanSpeedLimit(requestedFanSpeed)
        requestedSpeedPlainString = self.createFanSpeedPlainRequestString(
            requestedFanSpeed
        )
        requestedSpeedModdedString = self.createFanSpeedModdedRequestString(
            requestedFanSpeed, mode
        )

        modeIdentifier = "21"  # Intensive

        if mode is KWLState.AtHome:
            modeIdentifier = "1B"
        elif mode is KWLState.Away:
            modeIdentifier = "15"
        elif mode is KWLState.Intensive:
            modeIdentifier = "21"
        else:  # Individual/Fireplace should not be changed from here
            LOGGER.debug("Individual/Fireplace is not supported")
            return

        requestData = (
            "04 00 f9 00"
            + modeIdentifier
            + "50"
            + requestedSpeedPlainString
            + "00"
            + requestedSpeedModdedString
            + "51"
        )

        request = bytes.fromhex(requestData)
        response = await self._exchangeData(request)
        if bytes.fromhex("0200f500f700") == response:
            LOGGER.debug("expected response")
        else:
            LOGGER.debug("unexpected response")

        self._sthModified = True

    async def setIntensiveFanSpeed(self, requestedFanSpeed: int):
        await self.setFanSpeed(requestedFanSpeed, KWLState.Intensive)

    async def setAtHomeFanSpeed(self, requestedFanSpeed: int):
        await self.setFanSpeed(requestedFanSpeed, KWLState.AtHome)

    async def setAwayFanSpeed(self, requestedFanSpeed: int):
        await self.setFanSpeed(requestedFanSpeed, KWLState.Away)

    async def setIntensiveDuration(self, requestedDurationTime: datetime.time):
        requestedDuration = (
            requestedDurationTime.hour * 60 + requestedDurationTime.minute
        )
        if requestedDuration < 1:
            requestedDuration = 1
        elif (
            requestedDuration > 0x5A0
        ):  # if the time should be more than 0x5A0 (24*60min = 1 day it doesn't make sense anymore)
            requestedDuration = 0x5A0
        else:
            requestedDuration = round(requestedDuration)

        requestData = (
            "0400f9004050"
            + (requestedDuration).to_bytes(2, byteorder="little").hex()
            + (requestedDuration + 0x513D).to_bytes(2, byteorder="little").hex()
        )

        request = bytes.fromhex(requestData)
        response = await self._exchangeData(request)
        if bytes.fromhex("0200f500f700") == response:
            LOGGER.debug("expected response")
        else:
            LOGGER.debug("unexpected response")

        self._sthModified = True

    async def test_connection(self) -> bool:
        # """Test connectivity by doing a read."""
        request = bytes.fromhex("0300f6000000f900")
        response = await self._exchangeData(request)
        self._parseData(response)
        return bool(response is not None)

    async def turnOffOn(self, requestTurnOff: bool):
        if requestTurnOff is True:
            requestData = "0400f900021205000413"
        else:
            requestData = "0400f90002120000ff12"

        request = bytes.fromhex(requestData)
        response = await self._exchangeData(request)
        if bytes.fromhex("0200f500f700") == response:
            LOGGER.debug("expected response")
        else:
            LOGGER.debug("unexpected response")

        self._sthModified = True

    @property
    def url(self):
        return self._url

    @property
    def deviceModel(self):
        return self._deviceModel

    @property
    def deviceType(self):
        return self._deviceType

    @property
    def serialNR(self):
        return self._SerialNR

    @property
    def instanceState(self):
        return self._instanceState

    @property
    def CurrentFanSpeed(self):
        return self._CurrentFanSpeed

    @property
    def AtHomeFanSpeed(self):
        return self._atHomeFanSpeed

    @property
    def AwayFanSpeed(self):
        return self._awayFanSpeed

    @property
    def IntensivFanSpeed(self):
        return self._intensivFanSpeed

    @property
    def IntensivDuration(self):
        return self._intensivDuration

    @property
    def OutsideTemperature(self):
        return self._OutsideTemperature

    @property
    def SupplyTemperature(self):
        return self._SupplyTemperature

    @property
    def IndoorTemperature(self):
        return self._IndoorTemperature

    @property
    def ExhaustTemperature(self):
        return self._ExhaustTemperature

    @property
    def AirRH(self):
        return self._AirRH

    @property
    def filterInterval(self):
        return self._filterInterval

    @property
    def filterChanged(self):
        return self._filterChanged

    @property
    def filterDue(self):
        return self._filterDue

    @property
    def sthModified(self):
        return self._sthModified

    @property
    def IsAvailable(self):
        return self._isAvailable

    @property
    def IsOn(self):
        return self._isOn

    @property
    def CO2Value(self):
        return self._CO2Value
