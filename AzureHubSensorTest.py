import os
import math
import time
import json
import random
import asyncio
import numpy as np
from gpiozero import MCP3008
from azure.iot.device.aio import IoTHubDeviceClient

adc0 = MCP3008(channel=0)
adc1 = MCP3008(channel=1)
adc2 = MCP3008(channel=2)
adc3 = MCP3008(channel=3)
adc4 = MCP3008(channel=4)
adc5 = MCP3008(channel=5)

temp0 = temp1 = temp2 = temp3 = temp4 = temp5 = 0.0

resistance = 100000
num_readings = 50
v_ref = 3.3


def steinhart_temperature_C(r, Ro=100000.0, To=25.0, beta=3950.0):
	steinhart = math.log(r / Ro, 10) / beta
	steinhart += 1.0 / (To + 273.15)
	steinhart = (1.0 / steinhart) - 273.15
	return steinhart


def calculate_temperature(volts):
	volts = volts / num_readings
	ohms = ((1/volts) * (v_ref * resistance)) - resistance

	return steinhart_temperature_C(ohms)


def main():
	global temp0, temp1, temp2, temp3, temp4, temp5
	while (True):
		volts0 = volts1 = volts2 = volts3 = volts4 = volts5 = 0.0
		for i in range(num_readings):
			volts0 += adc0.value * v_ref
			volts1 += adc1.value * v_ref
			volts2 += adc2.value * v_ref
			volts3 += adc3.value * v_ref
			volts4 += adc4.value * v_ref
			volts5 += adc5.value * v_ref
			time.sleep(0.025)

		[temp0,temp1,temp2,temp3,temp4,temp5] = [volts0,volts1,volts2,volts3,volts4,volts5] * calculate_temperature(test)

		# temp0 = calculate_temperature(volts0)
		# temp1 = calculate_temperature(volts1)
		# temp2 = calculate_temperature(volts2)
		# temp3 = calculate_temperature(volts3)
		# temp4 = calculate_temperature(volts4)
		# temp5 = calculate_temperature(volts5)

		asyncio.run(push_telemetry_to_twin())
		time.sleep(4)


async def push_telemetry_to_twin():
	conn_str = "HostName=XpediteIoTHub.azure-devices.net;DeviceId=RaspberryPi0;SharedAccessKey=7DkJ020eIpkWELF21/IMuCmKokhGJBGqZ3a0muQG5uM="
	device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)
	await device_client.connect()

	data = [{
		"sensorContext" : "Printer1",
		"sensorPath": "/HotEndTemperature",
		"value": temp0
	}, {
		"sensorContext" : "Printer1",
		"sensorPath": "/BedTemperature",
		"value": temp1
	}, {
		"sensorContext" : "Printer1",
		"sensorPath": "/AmbientTemperature",
		"value": temp2
	}]

	print("Sending message...")
	print(json.dumps(data))
	await device_client.send_message(json.dumps(data))
	print("Message successfully sent!")

	await device_client.shutdown()


if __name__ == "__main__":
	asyncio.run(main())
