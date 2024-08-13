def dataToCelsius(data, offsetPosition):
    OutsideTemperatur = data[offsetPosition * 2] * 256 + data[offsetPosition * 2 + 1]
    OutsideTemperatur = OutsideTemperatur / 100 - 273.15
    OutsideTemperatur = round(OutsideTemperatur, 1)
    return OutsideTemperatur
