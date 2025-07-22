PROMPT_E2E = '''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}. You should complete the task step by step as follows:
1. Fly over Bruce Port.
2. Search for a red cargo ship in the port.
3. Fly directly above the red cargo ship.
4. Land on the red cargo ship.

The known information is as follows:  
1. The current position of the drone is {pos}.  
2. The approximate coordinates of Bruce Port are (-2400, 400).  Note: Bruce Harbour is an area, so even if it is slightly off by a few hundred metres, the drone could still be within range of the harbour!
3. The goal of the previous action was {goal}.  

You can control the drone to perform the following actions:  
1. Turn (left/right) 90 degrees:  
   "action_name"="turn_left"/"turn_right", "params"=[] 
2. Fly in a specific direction (left/right/forward/backward/up/down/upleft/upright/downleft/downright):  
   "action_name"="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", "params"=[]
3. Fly to specified coordinates:  
   "action_name"="fly_to", "params"=["x":float, "y":float]
4. Switch camera view (toggle between front view and downward view):  
   "action_name"="switch_view", "params"=[]  
5. Land:  
   "action_name"="land", "params"=[]  

Tips (Important!!!):  
1. When executing the "Fly over Bruce Port" task, if the target destination is known and the distance is far (over 200m), it is recommended to use the "fly_to" action to quickly navigate to the specified coordinates.  
2. For the "Search for the red cargo ship in the port" task:  
   2.1 If the red cargo ship is not visible in the front view, try turning left and searching again.  
   2.2 If the ship is still not found after rotating a full circle, consider ascending to search from a higher altitude and try again.
3. For the "Fly directly above the red cargo ship" task:  
   3.1 If the red cargo ship is still visible in the front view, the drone has NOT yet flown directly above it and needs to continue to approach the red cargo ship. 
   3.2 If the red cargo ship is NOT visible in the front view, it indicates that the drone is likely close to the ship. In this case, switch to the downward view and continue the task.
   ** Remember: do NOT switch the view if the ship is still visible in the front view!!!
   3.3 In the downward view, if the center of the image shows a cargo ship loaded with containers (specifically indicated by the pixels within the red box corresponding to the target cargo ship, likely containers), the drone has reached the position directly above the ship and can attempt to land. Otherwise, continue flying toward the ship until it is centered in the image.  
4. For the "Land on the red cargo ship" task:  
   If the red cargo ship appears at the center of the image in the downward view, the drone has reached the position directly above the ship and can attempt to land.

Instructions:  
First, determine whether the previous action achieved its goal. If not, continue executing actions to achieve the previous goal. If the goal has been achieved, plan the next task and corresponding action.  

Note:  
Your response should be in JSON format and include the following information:  
1. Whether the previous action achieved its goal ("last_goal_reached").  
2. The current task goal (affected by whether the previous goal was completed).  
3. The next action to take (if all steps are completed, the next action is "task_complete").  
4. The parameters for the action.  
5. The reasoning/analysis for selecting this action (keep it concise!).  

Here is an example:  
{{
    "last_goal_reached": true,
    "current_goal": "Pick up the cup on the table",
    "action_name": "xxx",
    "params": {{
        "duration": 1.0
    }},
    "analysis": "xxx"
}}
'''

PROMPT_S2S ={
    "fly_to_bruce_port":'''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.

The known information is as follows:
1. The current position of the drone is {pos}.
2. The approximate coordinates of Bruce Port are (-2400, 400).

You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees:  
   "action_name"="turn_left"/"turn_right", "params"=[] 
2. Fly in a specific direction (left/right/forward/backward/up/down/upleft/upright/downleft/downright):  
   "action_name"="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", "params"=[]
3. Fly to specified coordinates:  
   "action_name"="fly_to", "params"=["x":float, "y":float]
4. Switch camera view (toggle between front view and downward view):  
   "action_name"="switch_view", "params"=[]  
5. Land:  
   "action_name"="land", "params"=[]

Tips (Important!!!):
1. When the target destination is known and the distance is far (over 500m), it is recommended to use the "fly_to" action to quickly navigate to the specified coordinates.
2. Note: Bruce Port is a large area, so even when the drone is less than 100 meters away from the target location, it may still be within the port!

Note: Your response should be in JSON format and include the following information:
1. The next action to take (if the task is completed, the next action should be "task_complete").
2. The parameters for the action.
3. The reasoning/analysis for selecting this action (keep it concise!).

Here is an example:
{{
    "action_name": "xxx",
    "params": {{
        "duration": 1.0
    }},
    "analysis": "xxx"
}}
''',

    "search_for_ship":'''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.


You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees:  
   "action_name"="turn_left"/"turn_right", "params"=[] 
2. Fly in a specific direction (left/right/forward/backward/up/down/upleft/upright/downleft/downright):  
   "action_name"="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", "params"=[]
3. Fly to specified coordinates:  
   "action_name"="fly_to", "params"=["x":float, "y":float]
4. Switch camera view (toggle between front view and downward view):  
   "action_name"="switch_view", "params"=[]  
5. Land:  
   "action_name"="land", "params"=[]

Tips (Important!!!):
1. When the red cargo ship is not visible in the front view, you can try turning left 90 degrees and searching again!
2. If the red cargo ship is still not found after a full left turn (i.e., turning left 3 times consecutively), you can try flying higher and search again!

Note: Your response should be in JSON format and include the following information:
1. The next action to take (if the task is completed, the next action should be "task_complete").
2. The parameters for the action.
3. The reasoning/analysis for selecting this action (keep it concise!).

Here is an example:
{{
    "action_name": "xxx",
    "params": {{
        "duration": 1.0
    }},
    "analysis": "xxx"
}}
''',

    "approach_ship":'''You are operating a drone, and this image is captured by the drone's {view} camera. Your overall mission objective is {desc}.

The known information is as follows:
1. The drone is already in the Bruce Port area.

You can control the drone to perform the following actions:
1. Turn (left/right) 90 degrees:  
   "action_name"="turn_left"/"turn_right", "params"=[] 
2. Fly in a specific direction (left/right/forward/backward/up/down/upleft/upright/downleft/downright):  
   "action_name"="move_left"/"move_right"/"move_forward"/"move_backward"/"move_up"/"move_down"/"move_upleft"/"move_upright"/"move_downleft"/"move_downright", "params"=[]
3. Fly to specified coordinates:  
   "action_name"="fly_to", "params"=["x":float, "y":float]
4. Switch camera view (toggle between forward-looking view and downward-looking view):  
   "action_name"="switch_view", "params"=[]  
5. Land:  
   "action_name"="land", "params"=[]

Tips (Important!!!):
1. When the red cargo ship is visible in the forward-looking view, it indicates that the drone is still relatively far from the ship. In this case, you need to determine the next action based on the position of the red cargo ship in the forward-looking view, and fly toward the red cargo ship to gradually approach it.
2. (Important) When the red cargo ship is NOT visible in the forward-looking view, it suggests that the drone is close to the red cargo ship. At this point, you MUST switch to the downward-looking view, and based on the position of the red cargo ship in the downward-looking view, determine the next action to fly directly above the ship!!!
3. In the downward view, if the center of the image shows a cargo ship loaded with containers (specifically indicated by the pixels within the red box corresponding to the target cargo ship, likely containers), the drone has reached the position directly above the ship. And it means that the task is completed.

Note: Your response should be in JSON format and include the following information:
1. The next action to take (if the task is completed, the next action should be "task_complete").
2. The parameters for the action.
3. The reasoning/analysis for selecting this action (keep it concise!).

Here is an example:
{{
    "action_name": "xxx",
    "params": {{
        "duration": 1.0
    }},
    "analysis": "xxx"
}}
'''
}