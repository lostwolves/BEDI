
PROMPT_E2E = '''Your are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}. You should complete the task step-by-step according to the following instructions:
1. Fly to the sea area where the target ship is located.
2. Search for the target ship within the target sea area.
3. Approach the target ship and fly directly above it.
4. Land on the target ship.

The known information is as follows:
1. The current position coordinates of the drone are {pos}.
2. The center coordinates of Sea Area X1 are (1100,2500).
3. The goal of the previous action was {goal}.

You can control the drone to perform the following actions:
1. Turn 90 degrees (turn left / turn right), where action_name="turn_left"/"turn_right", params=[]
2. Fly in a certain direction (left/right/forward/backward/up/down/up-left/up-right/down-left/down-right), where action_name="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", params=[]
3. Fly to specified coordinates, where action_name="fly_to", params=["x":int,"y":int]
4. Switch camera view (toggle between front view and downward view), where action_name="switch_view", params=[]
5. Land, where action_name="land", params=[]

Hints (Important!!!):
1. When performing the "Fly to the sea area where the target ship is located" task, if the destination coordinates are known and the distance is far (more than 200m), it is recommended to use the "fly_to" action.
2. When performing the "Search for the target ship within the target sea area" task:
   2.1 If the target ship cannot be seen in the front-view camera, try turning left and search again;
   2.2 If the target ship still cannot be found after a full rotation, try ascending higher and searching again.
3. When performing the "Approach the target ship and fly directly above it" task:
   3.1 If the target ship is visible in the front-view camera, attempt to fly toward the direction of the target ship to gradually approach;
   3.2 If the target ship is no longer visible in the front-view camera, it means the drone is already relatively close to the target ship. At this point, you should switch to the downward-view camera and continue the mission (do not switch views if the target ship is still visible in the front-view camera!!!);
   3.3 In the downward-view camera, if the center of the image is the main body of the target ship, it indicates that the drone has reached directly above the target ship and can attempt to land; otherwise, continue flying toward the target ship until it appears at the center of the image.
4. When performing the "Land on the target ship" task: if the main body of the target ship is centered in the downward-view camera, it indicates that the drone is already above the target ship and you can attempt to land.

Firstly, determine whether the previous action achieved its goal. If the goal was not achieved, continue executing actions with the same goal as before. If the goal was achieved, plan the next goal and corresponding action.
Note: Your response should be in JSON format and include the following information:
1. Whether the previous action achieved its goal;
2. The current mission goal (this may change depending on whether the previous goal was achieved);
3. The next action (when all steps are completed, the next action should be "task_complete");
4. Parameters for the action;
5. Reasoning/analysis for selecting this action (should be concise!).

Here is an example:
{{
    "last_goal_reached": true,
    "current_goal": "Pick up the cup on the table",
    "action_name": "xxx",
    "params": {{
        "xxx": 1.0
    }},
    "analysis": "xxx"
}}
'''


PROMPT_S2S = {
    "fly_to_sea_area":''' You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.

The known information is as follows:
1. The current position coordinates of the drone are {pos}.
2. The center coordinates of Area X1 are (1100, 2500).

You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees, where action_name="turn_left"/"turn_right", params=[]
2. Fly in a certain direction (left/right/forward/backward/up/down/up-left/up-right/down-left/down-right), where action_name="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", params=[]
3. Fly to specified coordinates, where action_name="fly_to", params=["x":int,"y":int]
4. Switch camera view (toggle between front and bottom views), where action_name="switch_view", params=[]
5. Land, where action_name="land", params=[]

Tips (Important!!!):
1. If the destination coordinates are known and the distance is far (more than 200m), it is recommended to use the "fly_to" action.

Note: Your response should be in JSON format, containing the following information:
1. The next action (when the mission objective is completed, the next action is "task_complete");
4. Action parameters;
5. Basis/analysis for selecting the action (should be brief and concise!).
The following is an example:
{{
    "action_name":"xxx",
    "params":{{
        "xxx":1.0
    }},
    "analysis":"xxx"
}}''',

    "search_for_ship": '''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.

The known information is as follows:
1. The current position coordinates of the drone are {pos}.

You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees, where action_name="turn_left"/"turn_right", params=[]
2. Fly in a certain direction (left/right/forward/backward/up/down/up-left/up-right/down-left/down-right), where action_name="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", params=[]
3. Fly to specified coordinates, where action_name="fly_to", params=["x":int,"y":int]
4. Switch camera view (toggle between front and bottom views), where action_name="switch_view", params=[]
5. Land, where action_name="land", params=[]

Tips (Important!!!):
1. If the target ship is not visible in the forward-looking camera view, try turning left and searching again;
2. If the target ship is still not found after a full rotation, try flying higher and searching again.

Note: Your response should be in JSON format, containing the following information:
1. The next action (when the mission objective is completed, i.e., the target carrier appears in the drone's view, the next action is "task_complete");
4. Action parameters;
5. Basis/analysis for selecting the action (should be brief and concise!).
The following is an example:
{{
    "action_name":"xxx",
    "params":{{
        "xxx":1.0
    }},
    "analysis":"xxx"
}}''',

    
    "approach_ship": '''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.

The known information is as follows:
1. The current position coordinates of the drone are {pos}.

You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees, where action_name="turn_left"/"turn_right", params=[]
2. Fly in a certain direction (left/right/forward/backward/up/down/up-left/up-right/down-left/down-right), where action_name="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", params=[]
3. Fly to specified coordinates, where action_name="fly_to", params=["x":int,"y":int]
4. Switch camera view (toggle between front and bottom views), where action_name="switch_view", params=[]
5. Land, where action_name="land", params=[]

Tips (Important!!!):
1. When the target ship appears in the drone's front camera view, it indicates that the drone is still far from the target. At this time, you should fly toward the direction of the target ship to approach gradually;
2. When the target ship disappears from the front camera view, it indicates that the drone is already relatively close to the target ship. At this point, you should switch to the bottom view and continue the mission (DO NOT switch to the bottom view if the target ship is still visible in the front view!!!);
3. In the bottom view, if the center of the image (within the red box) shows the main body of the target ship, it indicates that the drone has reached directly above the target ship, and you may attempt to land; otherwise, continue flying toward the direction of the target ship until the target appears in the center of the image (within the red box).

Note: Your response should be in JSON format, containing the following information:
1. The next action (when the mission objective is completed, i.e., the target carrier appears in the drone's view, the next action is "task_complete");
4. Action parameters;
5. Basis/analysis for selecting the action (should be brief and concise!).

The following is an example:
{{
    "action_name":"xxx",
    "params":{{
        "xxx":1.0
    }},
    "analysis":"xxx"
}}'''
}