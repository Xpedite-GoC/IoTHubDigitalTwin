import os
import json
import random
import asyncio
from azure.iot.device.aio import IoTHubDeviceClient

idCounter = 0

async def main():
	#conn_str = "HostName=XpediteDigitalTwinIoTHub.azure-devices.net;DeviceId=TestRaspberryPi;SharedAccessKey=WsVICj+3cYdLgus0lozyER9DAQOF0jk3FjbH1u0gAk4="
	conn_str = "HostName=XpediteIoTHub.azure-devices.net;DeviceId=RaspberryPi0;SharedAccessKey=7DkJ020eIpkWELF21/IMuCmKokhGJBGqZ3a0muQG5uM="

	device_client = IoTHubDeviceClient.create_from_connection_string(conn_str)

	await device_client.connect()

	global idCounter
	idCounter = idCounter + 1

	data = [{
		"sensorContext" : "Printer1",
		"sensorPath": "/HotEndTemperature",
		"value": random.randrange(190, 220)
	}, {
		"sensorContext" : "Printer1",
		"sensorPath": "/BedTemperature",
		"value": random.randrange(80,110)
	}, {
		"sensorContext" : "Printer1",
		"sensorPath": "/AmbientTemperature",
		"value": random.randrange(20, 25)
	}]

	print("Sending message...")
	print(json.dumps(data))
	await device_client.send_message(json.dumps(data))
	print("Message successfully sent!")

	await device_client.shutdown()

if __name__ == "__main__":
	asyncio.run(main())
