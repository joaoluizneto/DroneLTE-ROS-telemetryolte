#! /usr/bin/env python
# Import ROS.
import rospy
from ccsclient import ccsWebsocketClient
import companion, os, requests

# Import the API.
from iq_gnc.py_gnc_functions import *
# To print colours (optional).
from iq_gnc.PrintColours import *

 

def main():
    # Initializing ROS node.
    rospy.init_node("drone_telemetry_over_network")

    # Create an object for the API.
    drone = gnc_api()

    ccscli = ccsWebsocketClient(
        api_url="ws://{}/ws/robot/zangado/".format(os.getenv(key='API_URL')), 
        #api_url="ws://192.168.0.12:8000/ws/robot/zangado/", 
        headers={'X-DroneApiKey':os.getenv(key='DRONE_API_KEY')},
        #headers={'X-DroneApiKey':'hOgtypH7.eQM8nQbEUNyQY5gPUQg0IG1WbuopENfz'},
        )

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
        utm_pos = drone.get_current_location()
        gps_pos = drone.gps_position()
        message={
                "companion":{
                        "system": companion.System.get_info(),
                        "connectivity":companion.Connectivity.get_info(),
                        },
                "state": drone.get_state(),
                "position": {
                        "location":{
                                'x': utm_pos.x,
                                'y': utm_pos.y,
                                'z': utm_pos.z,
                                'theta': drone.get_current_heading()
                        },
                        "gps":{
                                'long':gps_pos.longitude,
                                'lat' :gps_pos.latitude
                        },



                }
        }
        ccscli.send_telemetry(message)

        rospy.loginfo(CGREEN2 + f"Dispatching telemetry info:\n state:{message['state']} \nposition:{message['position']['location']}" + CEND)


if __name__ == '__main__':
    while True:
        try:
            main()
        except KeyboardInterrupt:
            print("Crtl-C getting out...")
            rospy.sleep(3)
            rospy.signal_shutdown("Crtl-C")
            exit()
        except ConnectionRefusedError:
            print("Connection Refused at server, retrying in 3 seconds...")
            rospy.sleep(3)
            continue
        except ConnectionResetError:
            print("Connection Reseted at server, retrying in 3 seconds...")
            rospy.sleep(3)
            continue           
        except BrokenPipeError:
            print("Broken Pipe, retying...")
            rospy.sleep(0.5)
            continue
        except requests.exceptions.ConnectionError:
            print("ConnectionError, retying...")
            rospy.sleep(0.5)
            continue

            
