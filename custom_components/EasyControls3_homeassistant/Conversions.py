def dataToCelsius(data, offsetPosition):
    OutsideTemperature = data[offsetPosition * 2] * 256 + data[offsetPosition * 2 + 1]
    OutsideTemperature = OutsideTemperature / 100 - 273.15
    OutsideTemperature = round(OutsideTemperature, 1)
    return OutsideTemperature
