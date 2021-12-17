## Imports
import sys
import time
import logging, traceback
import paho.mqtt.client as mqtt
import json
import requests

sr="MyIOTHu.azure-devices.net%2Fdevices%2FApiDevice&sig=Dqa0FNd92Co7qLLwFLb5wNemR6r2VPdRXJHXsYyMoio%3D&se=44839744792"
# Set this to the IP of your MQTT broker
mqtt_broker = "MyIOTHu.azure-devices.net"

# Device auth token
device_token = "MyIOTHu.azure-devices.net/ApiDevice/?api-version=2018-06-30"

# Set MQTT topic.
topic = "devices/ApiDevice/messages/events/"

# Set latitude for weather data
lat = "59.190375"
# Set longiude
lon = "17.667006"

# Yr.no API URL
url = "https://api.met.no/weatherapi/locationforecast/2.0/compact?lat={}&lon={}".format(lat, lon)

# Yr.no headers, user-agent should point to where YR.no can contact you
headers = {
  'User-Agent': 'jojoaba94@gmail.com'
}

# Setup logger
logger = logging.getLogger() 
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
log_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(log_format)
logger.addHandler(handler)

if __name__ == '__main__':

    # Connect to Service domain MQTT
    try:
        mqttc = mqtt.Client(client_id="ApiDevice")
        # Set username to device token
        mqttc.username_pw_set(username=device_token, password=sr)
        logger.info("start connect")
        mqttc.connect(mqtt_broker, port=8883)
        logger.info("connect success")
        mqttc.loop_start()

        # Main Loop
        while True:
            ts = round(time.time()*1000)
            # Poll YR.no
            response = requests.request("GET", url, headers=headers, data={})

            yr_data = json.loads(response.text)
            temperature = yr_data['properties']['timeseries'][0]['data']['instant']['details']['air_temperature']
            humidity = yr_data['properties']['timeseries'][0]['data']['instant']['details']['relative_humidity']

            # Publish
            newPayload = {"ts" : ts, "values" : {"temperature" : str(temperature), "humidity" : str(humidity)}}
            mqttc.publish(topic, json.dumps(newPayload)) # Publish to broker
            logger.info("try to publish:{}".format(newPayload))

            # Set time between data points, 300 = 5 min
            time.sleep(300)

    except Exception as e:
        logger.error("exception main()")
        logger.error("e obj:{}".format(vars(e)))
        logger.error("message:{}".format(e.message))
        traceback.print_exc(file=sys.stdout)