#! /usr/bin/env python
# Import ROS.
import rospy
import json
import websocket
# Import the API.
from iq_gnc.py_gnc_functions import *
# To print colours (optional).
from iq_gnc.PrintColours import *


#ws = websocket.WebSocket()
#ws.connect("ws://localhost:8000/ws/robot/guy/")



def main():
    # Initializing ROS node.
    rospy.init_node("telemetryolte")

    # Create an object for the API.
    drone = gnc_api()
    # Wait for FCU connection.
    #drone.wait4connect()
    # Wait for the mode to be switched.
    #drone.wait4start()

    # Create local reference frame.
    #drone.initialize_local_frame()
    # Specify control loop rate. We recommend a low frequency to not over load the FCU with messages. Too many messages will cause the drone to be sluggish.
    rate = rospy.Rate(3)
    rospy.loginfo(CGREEN2 + "Begin to transmit data." + CEND)


    while True:
        #get telemetry info
        rospy.sleep(1)
        coord = drone.get_current_location()
        #send_position(coord)
        gps_pos = drone.gps_position()
        rospy.loginfo(CGREEN2 + f"Dispatching telemetry info x={coord.x}, y={coord.y}, z={coord.z} | lat={gps_pos.latitude}, lon={gps_pos.longitude}" + CEND)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        exit()

