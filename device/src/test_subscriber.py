#!/usr/bin/env python

import paho.mqtt.client as mqtt
import ssl

ROOT_CA = "/home/blitz/certs/robotcerts/root-CA.crt"
CERTIFICATE = "/home/blitz/certs/robotcerts/certificate.pem.crt"
PRIVATE_KEY = "/home/blitz/certs/robotcerts/private.pem.key"
AWS_IOT_TOPIC = "$aws/things/awsiotdemo/shadow/update"
AWS_IOT_ENDPOINT = "a1j88xr8j1m132.iot.us-west-2.amazonaws.com"

def on_connect(client, userdata, flags, rc):
	print("Connected with result code "+str(rc))
	client.subscribe(AWS_IOT_TOPIC)

def on_message(client, userdata, msg):
	print(msg.topic+" "+str(msg.payload))

client = mqtt.Client()
client.on_connect = on_connect
client.tls_set(ROOT_CA,
			   CERTIFICATE,
			   PRIVATE_KEY,
				tls_version=ssl.PROTOCOL_TLSv1_2)

client.on_message = on_message

client.connect(AWS_IOT_ENDPOINT, 8883, 10)

client.loop_forever()
