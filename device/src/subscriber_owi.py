'''
Copyright 2014-2015 Amazon.com, Inc. or its affiliates. All Rights Reserved.

Licensed under the Apache License, Version 2.0 (the "License"). You may not use this file except in compliance with the License. A copy of the License is located at

    http://aws.amazon.com/apache2.0/

or in the "license" file accompanying this file. This file is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the License for the specific language governing permissions and limitations under the License.

Note: Other license terms may apply to certain, identified software files contained within or
distributed with the accompanying software if such terms are included in the directory containing
the accompanying software. Such other license terms will then apply in lieu of the terms of the
software license above.
'''

import paho.mqtt.client as paho
import ssl
import ast
import json
import schedule, time
from roboarm import Arm
from pygame import constants
import pygame

ROOT_CA = "/home/pi/awsiotrobot/robotcerts/root-CA.crt"
CERTIFICATE = "/home/pi/awsiotrobot/robotcerts/certificate.pem.crt"
PRIVATE_KEY = "/home/pi/awsiotrobot/robotcerts/private.pem.key"
AWS_IOT_TOPIC = "$aws/things/awsiotdemo/shadow/update"
AWS_IOT_ENDPOINT = "a1j88xr8j1m132.iot.us-west-2.amazonaws.com"

var_payload = ''

# Default active flag is false.
active = False

arm = Arm()
#self._init_pygame()
#self._init_actions()


'''
This function is invoked when the mqtt client makes a successful connection. It subscribes the client to the AWS IoT Topic.
@param client The MQTT Client
@param userdata
@param flags
@param rc The result code
'''
def on_connect(client, userdata, flags, rc):
    print("Connected with result code "+str(rc))
    client.subscribe(AWS_IOT_TOPIC)

'''
This function is invoked when a new message is received by the MQTT client. It sets the servo values to the values received from AWS IoT.
@param client The MQTT Client
@param userdata
@param msg The message that was recieved.
'''
deadzone = {
    "xRight": 360,
    "xLeft": 500,
    "yUp": 300,
    "yDown": 330
}

current_status = {
    "base": 0,
    "elbow": 0
    }

def on_message(client, userdata, msg):

    print(msg.topic+" "+str(msg.payload))

    # Message received! Wake up!
    active = True

    # The message is in JSON format
    tev_json_obj = json.loads(msg.payload)

    if (tev_json_obj["coordinates"]["xAxis"] < deadzone["xRight"]) and (current_status["base"] == 0):
        arm.base.rotate_counter(None)
        current_status["base"] = 1
    if tev_json_obj["coordinates"]["xAxis"] > deadzone["xLeft"] and (current_status["base"] == 0):
        arm.base.rotate_clock(None)
        current_status["base"] = -1
    if tev_json_obj["coordinates"]["yAxis"] < deadzone["yUp"] and (current_status["elbow"] == 0):
        arm.elbow.up(None)
        current_status["elbow"] = 1
    if tev_json_obj["coordinates"]["yAxis"] > deadzone["yDown"] and (current_status["elbow"] == 0):
        arm.elbow.down(None)
        current_status["elbow"] = -1

    if (tev_json_obj["coordinates"]["xAxis"] >= deadzone["xRight"]) and (tev_json_obj["coordinates"]["xAxis"] <= deadzone["xLeft"]):
        arm.base.stop()
        current_status["base"] = 0
    if (tev_json_obj["coordinates"]["yAxis"] >= deadzone["yUp"]) and (tev_json_obj["coordinates"]["yAxis"] <= deadzone["yDown"]):
        arm.elbow.stop()
        current_status["elbow"] = 0
    
def go_to_sleep(active):

    if (active):
        print("Still active... I'm Awake!");
        active = False
    else:
        print("Not active... Sleeping...");
        arm.grips.stop()
        arm.wrist.stop()
        arm.elbow.stop()
        arm.shoulder.stop()
        arm.base.stop()


# The main application runs the Paho MQTT Client
if __name__ == "__main__":

    arm.elbow.up(timeout=0.3)
    arm.elbow.down(timeout=0.3)
    
    mqttc = paho.Client()
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message
    mqttc.tls_set(ROOT_CA, CERTIFICATE, PRIVATE_KEY, tls_version=ssl.PROTOCOL_TLSv1_2)
    mqttc.connect(AWS_IOT_ENDPOINT, 8883, 10)
    mqttc.loop_start()

    schedule.every(0.1).minutes.do(lambda: go_to_sleep(active));

    while True:
        schedule.run_pending()
        time.sleep(1)
