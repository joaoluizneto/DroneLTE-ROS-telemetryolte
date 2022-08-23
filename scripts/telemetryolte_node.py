#! /usr/bin/env python
# Import ROS.
import time
import rospy
import json
import websocket
# Import the API.
from iq_gnc.py_gnc_functions import *
# To print colours (optional).
from iq_gnc.PrintColours import *

import platform
import subprocess
import re
 
def get_rssi():
        if platform.system() == 'Linux':
                p = subprocess.Popen("iwconfig", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        elif platform.system() == 'Windows':
                p = subprocess.Popen("netsh wlan show interfaces", stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        else:
                raise Exception('reached else of if statement')
        out = p.stdout.read().decode()
 
        if platform.system() == 'Linux':
                m = re.findall('(wl.*?[0-9]+).*?Signal level=(-[0-9]+) dBm', out, re.DOTALL)
        elif platform.system() == 'Windows':
                m = re.findall('Name.*?:.*?([A-z0-9 ]*).*?Signal.*?:.*?([0-9]*)%', out, re.DOTALL)
        else:
                raise Exception('reached else of if statement')
 
        p.communicate()
 
        return m


def send_to_django(utm_pos, gps_pos, theta, rssi):
    global ws
    #rospy.loginfo(rospy.get_caller_id() + 'x: %s', data.x)
    position = {
        'x': utm_pos.x,
        'y': utm_pos.y,
        'z': utm_pos.z,
        'theta': theta,

        'long':gps_pos.longitude,
        'lat' :gps_pos.latitude
    }
    message = json.dumps({ 'message' : position })
    ws.send('%s' % message)

def main():
    # Initializing ROS node.
    rospy.init_node("drone_telemetry_over_network")

    # Create an object for the API.
    drone = gnc_api()
    # Wait for FCU connection.
    drone.wait4connect()
    # Wait for the mode to be switched.
    #drone.wait4start()

    # Create local reference frame.
    drone.initialize_local_frame()
    # Specify control loop rate. We recommend a low frequency to not over load the FCU with messages. Too many messages will cause the drone to be sluggish.
    rate = rospy.Rate(3)
    rospy.loginfo(CGREEN2 + "Begin to transmit data." + CEND)


    while True:
        #get telemetry info
        rospy.sleep(1)
        rssi = get_rssi()[0][1]
        utm_pos = drone.get_current_location()
        theta = drone.get_current_heading()
        gps_pos = drone.gps_position()
        send_to_django(utm_pos, gps_pos, theta, rssi)
        rospy.loginfo(CGREEN2 + f"Dispatching telemetry info x={utm_pos.x}, y={utm_pos.y}, z={utm_pos.z}, theta={theta}| long={gps_pos.longitude}, lat={gps_pos.latitude}, rssi={rssi}dbm" + CEND)


if __name__ == '__main__':
    while True:
        try:
            ws = websocket.WebSocket()
            ws.connect("ws://localhost:8000/ws/robot/guy/")
            main()
        except KeyboardInterrupt:
            print("Crtl-C getting out...")
        except ConnectionRefusedError:
            print("Connection Refused at server, retrying in 3 seconds...")
            rospy.sleep(3)
            continue
        except BrokenPipeError:
            print("Broken Pipe, retying...")
            rospy.sleep(0.5)
            continue
    exit()

