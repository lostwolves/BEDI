import shapely.geometry as sg
import numpy as np

from tools.utils import extract_json
from task_examples.prompt_exapmles.prompt4Delivery import PROMPT_S2S

## Search for Ship Task
# ------------------------------------------------------
# 1. task name
name = "SearchForShip"

# ------------------------------------------------------
# 2. task description
desc = "Controlling the drone to search for a ship in Bruce Port"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_S2S["search_for_ship"]

# ------------------------------------------------------
# 4. task force prompt
force_prompt = "\n\nNOTE: The cargo ship is currently NOT within the drone's view, which means the task is NOT completed yet."

# ------------------------------------------------------
# 5. initial pose
initial_position = (-2400, 400, -120)
initial_orientation = (0, 0, 1, 0)

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
def checker(seg_mask, **kwargs):
    if np.sum(seg_mask) > 100:
        return True
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
task_complete_actions = ["task_complete"]
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
