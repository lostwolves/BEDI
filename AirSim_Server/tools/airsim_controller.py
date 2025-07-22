import time
import airsim
import cv2
import numpy as np
import functools
from copy import deepcopy
import base64
import math
import pyautogui
import re
from flask import Flask, request, jsonify
import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import *

class AirSimController():
    def __init__(self, logger:logging.Logger, config_file:str=None) -> None:
        self.logger = logger

        self.cfg = get_default_config()
        if config_file:
            self.cfg.defrost()
            self.cfg.merge_from_file(config_file)
            self.cfg.freeze()

        self.cur_view = self.cfg.view

        # some basic info
        self.status = {
            "initPose" : airsim.Pose(airsim.Vector3r(*self.cfg.init_pose.position), airsim.Quaternionr(*self.cfg.init_pose.orientation)),
            "curPose": None,
        }

        # color map
        self.color_map = []
        with open(self.cfg.color_file, "r") as f:
            lines = f.read()
            pattern = re.compile(r"\d+\t\[(\d+), (\d+), (\d+)\]")
            for match in pattern.findall(lines):
                color = [int(i) for i in match]
                self.color_map.append(color[::-1])

        # supported actions
        self.supported_actions = [
            # turn
            "turn_left",
            "turn_right",
            # move
            "move_forward",
            "move_backward",
            "move_left",
            "move_right",
            "move_up",
            "move_down",
            "move_upleft",
            "move_upright",
            "move_downleft",
            "move_downright",
            "fly_to",
            # switch view
            "switch_view",
            # hover and land
            "land",
            "hover",
            # get image
            "get_image",
            # reset
            "reset"
            # others
            "get_position",
            "set_pose",
        ]

        # init
        self.setup()

    def setup(self) -> None:
        # connect to airsim server
        self.client=airsim.MultirotorClient()
        self.client.confirmConnection()
        self.client.enableApiControl(True)
        self.client.armDisarm(True)
        self.client.takeoffAsync().join()
        self.client.hoverAsync().join()
        self.logger.info(f"AirSim Controller: Connected to server")


        # set init pose
        self.client.simSetVehiclePose(self.status["initPose"], True)
        self.status["curPose"] = self.client.simGetVehiclePose()
        self.logger.info(f"AirSim Controller: Init pose set to {self.status['initPose']}")

        # set ship id
        success = self.client.simSetSegmentationObjectID("BPA_West_Carrier_CVN76_9", self.cfg.ship_id)
        # success = self.client.simSetSegmentationObjectID("HL_Combine_12", self.cfg.ship_id)
        if not success:
            raise Exception(f"Failed to set object id for ship")
        self.ship_color = self.color_map[self.cfg.ship_id]
        
    def isShipInView(self) -> bool:
        ship_color = self.color_map[self.cfg.ship_id]
        view = self.client.simGetImages([airsim.ImageRequest(0, airsim.ImageType.Segmentation, False, False)])[0]
        view_np = np.frombuffer(view.image_data_uint8, dtype=np.uint8).reshape(view.height, view.width, 3)
        mask = np.all(view_np == ship_color, axis=-1)
        pixels_num = np.sum(mask).item()
        return pixels_num > self.cfg.task.ship_visible_threshold * view.height * view.width
    
    def fly_to(self,
        x:int,
        y:int,
        z:int,
    ):
        cur_position = self.client.simGetVehiclePose().position
        cur_x,cur_y,cur_z = cur_position.x_val,cur_position.y_val,cur_position.z_val

        self.client.moveToPositionAsync(cur_x,cur_y,self.cfg.control.cruise_altitude,self.cfg.control.cruise_velocity).join()
        self.client.moveToPositionAsync(x,y,self.cfg.control.cruise_altitude,self.cfg.control.cruise_velocity).join()
        self.client.moveToZAsync(z,self.cfg.control.cruise_velocity).join()
        # self.client.hoverAsync().join()
        self.client.moveByVelocityAsync(0, 0, 0, 1).join()

    def set_pose(self, position:tuple=None, quaternion:tuple=None):
        pose=self.client.simGetVehiclePose()
        if position is None:
            position = (pose.position.x_val, pose.position.y_val, pose.position.z_val)
        if quaternion is None:
            quaternion = (pose.orientation.x_val, pose.orientation.y_val, pose.orientation.z_val, pose.orientation.w_val)
        self.client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(*position), airsim.Quaternionr(*quaternion)), True)

        self.client.moveByVelocityAsync(0,0,0,1).join()

    def set_position(
        self,
        x:int,
        y:int,
        z:int,
    ):
        self.client.simSetVehiclePose(airsim.Pose(airsim.Vector3r(x, y, z), airsim.to_quaternion(0, 0, 0)), True)
        self.client.moveByVelocityAsync(0, 0, 0, 1).join()
        # self.client.hoverAsync().join()
        self.status["curPose"] = self.client.simGetVehiclePose()

        
    def get_image(self) -> str:
        camera_id = 0 if self.cur_view == FRONT else 3
        image = self.client.simGetImage(camera_id,airsim.ImageType.Scene)

        img = cv2.imdecode(airsim.string_to_uint8_array(image), cv2.IMREAD_COLOR)
        os.makedirs(os.path.join(self.cfg.cache,"images"),exist_ok=True)
        img_path = os.path.join(self.cfg.cache,"images",f"{time.strftime('%Y%m%d%H%M%S')}.png")
        cv2.imwrite(img_path,img)

        return img_path

    def get_segmentation(self) -> str:
        camera_id = 0 if self.cur_view == FRONT else 3
        ship_color = self.color_map[self.cfg.ship_id]

        view = self.client.simGetImages([airsim.ImageRequest(camera_id, airsim.ImageType.Segmentation, False, False)])[0]
        view_np = np.frombuffer(view.image_data_uint8, dtype=np.uint8).reshape(view.height, view.width, 3)
        mask = np.all(view_np == ship_color, axis=-1)

        mask = mask.astype(np.uint8)

        # save the mask
        os.makedirs(os.path.join(self.cfg.cache,"segmentation"),exist_ok=True)
        mask_path = os.path.join(self.cfg.cache,"segmentation",f"{time.strftime('%Y%m%d%H%M%S')}.png")
        cv2.imwrite(mask_path, mask * 255)

        return mask_path

    def move(self, action_name:str) -> None :
        if action_name == "move_up" or action_name == "move_down":
            if action_name == "move_up":
                step_y = -self.cfg.control.step_dist
            else:
                step_y = self.cfg.control.step_dist
            self.client.moveByVelocityAsync(0,0,step_y,step_y,self.cfg.control.base_speed).join()
            return
        elif action_name in [
            "move_forward",
            "move_backward",
            "move_left",
            "move_right",
            "move_upleft",
            "move_upright",
            "move_downleft",
            "move_downright",
        ]:
            pose = self.client.simGetVehiclePose()
            position = pose.position
            yaw = airsim.to_eularian_angles(pose.orientation)[2]

            cur_x,cur_y,cur_z = position.x_val,position.y_val,position.z_val
            dist = self.cfg.control.step_dist

            if action_name == "move_forward":
                step_x = dist*math.cos(yaw)
                step_y = dist*math.sin(yaw)
            elif action_name == "move_backward":
                step_x = -dist*math.cos(yaw)
                step_y = -dist*math.sin(yaw)
            elif action_name == "move_left":
                step_x = dist*math.sin(yaw)
                step_y = -dist*math.cos(yaw)
            elif action_name == "move_right":
                step_x = -dist*math.sin(yaw)
                step_y = dist*math.cos(yaw)
            elif action_name == "move_upleft":
                step_x = dist*math.cos(yaw-math.pi/4)
                step_y = dist*math.sin(yaw+math.pi/4)
            elif action_name == "move_upright":
                step_x = dist*math.cos(yaw+math.pi/4)
                step_y = dist*math.sin(yaw+math.pi/4)
            elif action_name == "move_downleft":
                step_x = -dist*math.cos(yaw+math.pi/4)
                step_y = -dist*math.sin(yaw+math.pi/4)
            elif action_name == "move_downright":
                step_x = -dist*math.cos(yaw-math.pi/4)
                step_y = -dist*math.sin(yaw-math.pi/4)

            self.client.moveToPositionAsync(cur_x+step_x,cur_y+step_y,cur_z,self.cfg.control.base_speed).join()
            # self.client.hoverAsync().join()
            self.client.moveByVelocityAsync(0, 0, 0, 1).join()
            return

        else:
            print(f"action_name {action_name} not supported")
            return

    def turn(self,action_name:str) -> None:
        if action_name == "turn_left":
            yaw_rate = -self.cfg.control.yaw_rate
        elif action_name == "turn_right":
            yaw_rate = self.cfg.control.yaw_rate
        else:
            print(f"action_name {action_name} not supported")
            return
        self.client.moveByVelocityBodyFrameAsync(0,0,0,yaw_rate,self.cfg.control.rotate_step).join()

        # self.client.hoverAsync().join()
        self.client.moveByVelocityAsync(0, 0, 0, 1).join()
        return

    def land(self) -> None:
        self.client.landAsync().join()
        return

    def switch_view(self):
        if self.cur_view == FRONT:
            self.cur_view = BOTTOM
        else:
            self.cur_view = FRONT
        return

    def spray_water(self) -> None:
        self.status["isSpraying"] = not self.status["isSpraying"]
        screen,height = pyautogui.size()
        pyautogui.moveTo(screen/2,height/2,duration=1)
        pyautogui.click()
        pyautogui.press('P')

    def get_position_and_view(self) -> dict:
        position = self.client.simGetVehiclePose().position
        return {
            "x":int(position.x_val),
            "y":int(position.y_val),
            "z":int(position.z_val),
            "view":self.cur_view,
        }

    def reset(self) -> None:
        self.client.simSetVehiclePose(self.status["init_pose"], True)
        self.client.moveByVelocityAsync(0,0,0,1).join()
        self.cur_view = self.cfg.view
        self.status["isSpraying"] = False
        return

    

    def exec_action(self, action) -> dict :
        self.logger.info(f"AirSim Controller: exec action {action["action_name"]} with params {action['action_params']}")
        if "move" in action["action_name"]:
            self.move(action["action_name"])
            return None
        elif action["action_name"] == "set_pose":
            position = action["action_params"].get("position", None)
            quaternion = action["action_params"].get("quaternion", None)
            self.set_pose(position, quaternion)
            return None
        elif action["action_name"] == "get_segmentation":
            mask_path = self.get_segmentation()
            return {"seg_mask": mask_path}
        elif "turn" in action["action_name"]:
            self.turn(action["action_name"])
            return None
        elif action["action_name"] == "land":
            self.land()
            return None
        elif action["action_name"] == "switch_view":
            self.switch_view()
            return None
        elif action["action_name"] == "get_image":
            image_path = self.get_image()
            return {"image_path":image_path}
        elif action["action_name"] == "reset":
            self.reset()
        elif action["action_name"] == "spray_water":
            self.spray_water()
        elif action["action_name"] == "stop_spray":
            self.stop_spray()
        elif action["action_name"] == "get_position_and_view":
            info = self.get_position_and_view()
            return info
        elif action["action_name"] == "fly_to":
            x,y = action["action_params"]["x"], action["action_params"]["y"]
            z = action["action_params"]["z"] if "z" in action["action_params"] else self.cfg.init_pose.position[2]
            self.client.moveToPositionAsync(x,y,z,self.cfg.control.base_speed).join()
            return None
        elif action["action_name"] == "set_position":
            x,y,z = action["action_params"]["x"], action["action_params"]["y"], action["action_params"]["z"]
            self.set_position(x,y,z)
            return None
        else:
            print(f"action_name {action['action_name']} not supported")
            return None

    def start_server(self):
        app = Flask(__name__)


        @app.route('/test',methods=['GET','POST'])
        def test():
            return jsonify({'status': 'success'})


        @app.route('/control', methods=['POST'])
        def control():
            action = request.get_json()
            result = self.exec_action(action)
            if result:
                return jsonify(result)
            return jsonify({'status': 'success'})
        
        app.run(host='0.0.0.0', port=self.cfg.server.airsim_port)


if __name__ == "__main__":
    pass
