import os, math, time, json, random, asyncio
import numpy as np
from gpiozero import MCP3008
from azure.iot.device.aio import IoTHubDeviceClient

converters = np.array([MCP3008(channel=0),MCP3008(channel=1),MCP3008(channel=2)])
temps = np.zeros(len(converters))
vibration = 0.0

vib_adc = MCP3008(channel=3)

resistance = 100000
num_readings = 400
v_ref = 3.3

time_between_data = 0.025
time_between_push = 0

# Convert a resistance to a temperature using Steinhart method
def steinhart_temperature_C(r, Ro=100000.0, To=25.0, beta=3950.0):
	steinhart = np.log10(r / Ro) / beta
	steinhart += 1.0 / (To + 273.15)
	steinhart = (1.0 / steinhart) - 273.15
	return steinhart


# Convert a voltage to a temperature by using voltage divider
def calculate_temperature(volts):
	volts = volts / num_readings
	ohms = ((1/volts) * (v_ref * resistance)) - resistance

	return steinhart_temperature_C(ohms)


# Generate voltages over time from sensor readings
def main():
	global temps, time_between_data, time_between_push

	get_val = lambda adc: adc.value

	while (True):
		local_vibration = 0.0
		voltages = np.zeros(len(converters))
		for i in range(num_readings):
			local_vibration += get_val(vib_adc) * 100
			voltages += np.vectorize(get_val)(converters) * v_ref
			time.sleep(time_between_data)

		temps = calculate_temperature(voltages)
		vibration = local_vibration / num_readings

		asyncio.run(push_telemetry_to_twin())
		time.sleep(time_between_push)


# Push the readings to the digital twin
async def push_telemetry_to_twin():
	conn_str = "HostName=XpediteIoTHub.azure-devices.net;DeviceId=RaspberryPi0;SharedAccessKey=7DkJ020eIpkWELF21/IMuCmKokhGJBGqZ3a0muQG5uM="
	device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

	data = [{
		"sensorContext" : "Condenser0",
		"sensorPath": "/RefrigerantIn",
		"value": temps[0]
	}, {
		"sensorContext" : "Condenser0",
		"sensorPath": "/RefrigerantOut",
		"value": temps[1]
	}, {
		"sensorContext" : "Condenser0",
		"sensorPath": "/AmbientTemperature",
		"value": temps[2]
	}]

	print("Sending message...")
	print(json.dumps(data, indent=4))

	try:
		await device_client.connect()

		await device_client.send_message(json.dumps(data))
		print("Message successfully sent!")

		await device_client.shutdown()
	except:
		print("Failed to push update")


if __name__ == "__main__":
	asyncio.run(main())

