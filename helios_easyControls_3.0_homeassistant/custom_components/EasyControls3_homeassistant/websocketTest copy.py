
import asyncio
from websockets.sync.client import connect
import datetime
from dateutil.relativedelta import relativedelta

from deviceList import deviceInfo
from KWLStates import KWLState

url = 'ws://10.0.0.31:80'





async def readCurrentData():
    with connect(url) as websocket:
        print("connected")
        now = datetime.datetime.now()
        print(now.time())

        #request current data package
        data = bytes.fromhex('0300f6000000f900')
        websocket.send(data)
        print("sent")

        message = websocket.recv()
        # print(f"Received: {message}")
        parseData(message)


def parseData(data):
    #device info
    deviceModel = deviceInfo["device_model_data"][data[17 * 2 + 1]]
    deviceType  = deviceInfo["device_type_data"][data[16 * 2 + 1]]
    setSerialNR =  data[14 * 2] * 16777216 + data[14 * 2 + 1] * 65536 + data[15 * 2] * 256 + data[15 * 2 + 1]

    #state
	#current device state - we need A_CYC_STATE (Y), A_CYC_FIREPLACE_TIMER (u), A_CYC_BOOST_TIMER (v)
	#offsets: 107, 111, 110
	#the status is calculated:
	#IF fireplace timer is 0 and boost timer is 0 and state is 0 => 0
	#IF fireplace timer is not 0 => 3
	#IF boost timer is not 0 => 2
	#IF state is not 0 => 1
	#eq: a = 0 == u ? 0 == v ? 0 == Y ? 0 : 1 : 2 : 3
    state = data[107 * 2 + 1]
    fire  = data[111 * 2 + 1]
    boost = data[110 * 2 + 1]
    devState = 'Zuhause'
    devState = 'Unterwegs' if state != 0 else devState
    devState = 'Intensivlüftung' if boost != 0 else devState
    devState = 'Individuell' if fire != 0 else devState
    
    #fan
    FanSpeed = data[129]

    #temperaturs
    OutTemp= dataToCelsius(data, 67)
    SupTemp= dataToCelsius(data, 69)
    IndTemp= dataToCelsius(data, 65)
    ExhTemp= dataToCelsius(data, 66)

    #humidity
    AirRH = data[74 * 2 + 1]

    #filter
    filterInterval = data[239 * 2 + 1] #a month at helios has 30 days
    lastFilterChangedYear = 2000+ data[250 * 2 + 1]
    lastFilterChangedMonth = data[249 * 2 + 1]
    lastFilterChangedDay = data[248 * 2 + 1]
    filterChanged = datetime.date(lastFilterChangedYear, lastFilterChangedMonth, lastFilterChangedDay)
    filterDue = filterChanged + relativedelta(days=+int(filterInterval))

    print("data")
    print(devState)
    print(deviceModel)
    print(deviceType)    
    print(setSerialNR)
    print(FanSpeed )
    print(OutTemp)
    print(SupTemp)
    print(IndTemp)
    print(ExhTemp)
    print(state)
    print(fire )
    print(boost)
    print(AirRH)
    print(filterInterval)
    print(filterChanged)
    print(filterDue)
    print("data end\n\n")

async def switchMode(wantedKWLState):
    if wantedKWLState is KWLState.AtHome:
        payload = '0800f9000112000004120000051200000b37'
    elif wantedKWLState is KWLState.Away:
        payload = '0800f9000112010004120000051200000c37'
    elif wantedKWLState is KWLState.Intensive:
        payload = '0600f9000412b40005120000bc25'
    elif wantedKWLState is KWLState.Individual:
        payload = '0600f90004120000051296009e25'
    else:
        raise TypeError('direction must be an instance of Direction Enum')

    with connect(url) as websocket:
        print("connected")

        #send change request
        data = bytes.fromhex(payload)
        websocket.send(data)
        print("sent")

        message = websocket.recv()
        if bytes.fromhex("0200f500f700") == message:
            print("expected response")
        else:
            print("unexpected response")


def dataToCelsius(data, offsetPosition):
    outTemp = data[offsetPosition * 2] * 256 + data[offsetPosition * 2 + 1]
    outTemp = outTemp / 100 - 273.15
    outTemp = round(outTemp, 1)
    return(outTemp)   


# print("status before change")
# asyncio.run(readCurrentData())
# asyncio.run(asyncio.sleep(60))

# print("change to intensiv")
# asyncio.run(switchMode(KWLState.Intensive))
# asyncio.run(asyncio.sleep(20))
# print("status after change")
# asyncio.run(readCurrentData())
# asyncio.run(asyncio.sleep(40))

# print("change to away")
# asyncio.run(switchMode(KWLState.Away))
# asyncio.run(asyncio.sleep(60))
# asyncio.run(asyncio.sleep(20))
# print("status after change")
# asyncio.run(readCurrentData())
# asyncio.run(asyncio.sleep(40))

# print("change to individual")
# asyncio.run(switchMode(KWLState.Individual))
# asyncio.run(asyncio.sleep(20))
# print("status after change")
# asyncio.run(readCurrentData())
# asyncio.run(asyncio.sleep(40))

print("change to athome")
asyncio.run(switchMode(KWLState.AtHome))
asyncio.run(asyncio.sleep(20))
# print("status after change")
# asyncio.run(readCurrentData())
# asyncio.run(asyncio.sleep(40))









