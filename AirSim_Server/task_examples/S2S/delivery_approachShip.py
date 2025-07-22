import shapely.geometry as sg

from tools.utils import extract_json
from task_examples.prompt_exapmles.prompt4Delivery import PROMPT_S2S

## Approach Ship Task
# ------------------------------------------------------
# 1. task name
name = "ApproachShip"

# ------------------------------------------------------
# 2. task description 
desc = "Controlling the drone to fly directly above the ship in Bruce Port"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_S2S["approach_ship"]

# ------------------------------------------------------
# 4. task force prompt
force_prompt = "\n\nNOTE: The drone is currently NOT above the ship, which means the task is not completed yet. Do NOT choose to perform a landing operation!!!"

# ------------------------------------------------------
# 5. initial pose
initial_position = (-2400, 380, -120)
initial_orientation = (0, 0, 1, 1)

# ------------------------------------------------------
# 6. function to get the prompt
def get_prompt(task_desc, position, view, **kwargs):
    prompt = prompt_template.format(
        desc=task_desc,
        pos=position,
        view=view,
    )
    return prompt

# ------------------------------------------------------
# 7. function to get the next action from the agent
def chat(prompt, frame, agent, pos, view, task_name, task_desc, cur_step, **kwargs):
    response = agent(
        question=prompt,
        image_file=frame,
    )
    response = extract_json(response)
    response["prompt"] = prompt
    response["frame"] = frame
    response["agent"] = agent.model_name
    response["position"] = pos
    response["view"] = view
    response["task_name"] = task_name
    response["task_desc"] = task_desc
    response["cur_step"] = cur_step
    return response

# ------------------------------------------------------
# 8. function to check if the task is completed
ship_area =sg.Polygon(
    [
        (-2145,935),
        (-2620,935),
        (-2680,945),
        (-2710,980),
        (-2680,1015),
        (-2620,1035),
        (-2145,1035),
    ]
)
def checker(pos, view, **kwargs):
    if view == "downward-looking":
        pos = sg.Point(pos[0], pos[1])
        return pos.within(ship_area)
    return False

# ------------------------------------------------------
# 9. function to format the response for frontend display
def format_response(response):
    content = f"步数: {response['cur_step']}\n"
    content += f"当前位置: {response['position']}\n"
    content += f"当前视角: {response['view']}\n"
    content += f"动作命令: {response['action_name']}\n"
    content += f"动作参数: {response['params']}\n"
    content += f"决策依据: {response['analysis']}\n"
    return content
# ------------------------------------------------------
# 10. task complete actions
task_complete_actions = ["task_complete", "land"]
# ------------------------------------------------------


INFO = {
    "name": name,
    "desc": desc,
    "position": initial_position,
    "orientation": initial_orientation,
    "get_prompt_func": get_prompt,
    "chat_func": chat,
    "checker_func": checker,
    "response_formatter": format_response,
    "force_prompt": force_prompt,
    "task_complete_actions": task_complete_actions,
}
