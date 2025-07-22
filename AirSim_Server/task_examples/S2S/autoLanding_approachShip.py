import shapely.geometry as sg
import cv2

from tools.utils import draw_box, extract_json
from task_examples.prompt_exapmles.prompt4LandOnShip import PROMPT_S2S
from configs.defaults import get_default_config
cfg = get_default_config()

## Task configuration for approaching a ship
# ------------------------------------------------------
# 1. task name
name = "ApproachShip"

# ------------------------------------------------------
# 2. task description
desc = "Controlling the drone to approach an aircraft carrier in Sea Area X1"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_S2S["approach_ship"]

# ------------------------------------------------------
# 4. task force prompt
force_prompt = "\n\nNOTE: The aircraft carrier is NOT within the current view, which means the task is not completed yet."

# ------------------------------------------------------
# 5. function to get the prompt
def get_prompt(task_desc, position, view, **kwargs):
    prompt = prompt_template.format(
        desc=task_desc,
        pos=position,
        view=view,
    )
    return prompt

# ------------------------------------------------------
# 6. function to get the next action from the agent
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
# 7. function to check if the task is completed
def checker(seg_mask, view, **kwargs):
    if view != "downward-looking":
        return False
    seg = cv2.imread(seg_mask, cv2.IMREAD_GRAYSCALE)
    # Check if the aircraft carrier is just in the center of the view
    height, width = seg.shape
    center_region = seg[height//2-50:height//2+50, width//2-50:width//2+50]
    return cv2.countNonZero(center_region) > cfg.task.ship_visible_threshold * center_region.size

# ------------------------------------------------------
# 8. function to format the response for frontend display
def format_response(response):
    content = f"步数: {response['cur_step']}\n"
    content += f"当前位置: {response['position']}\n"
    content += f"当前视角: {response['view']}\n"
    content += f"动作命令: {response['action_name']}\n"
    content += f"动作参数: {response['params']}\n"
    content += f"决策依据: {response['analysis']}\n"
    return content
# ------------------------------------------------------
# 9. task complete actions
task_complete_actions = ["task_complete", "land"]
# ------------------------------------------------------


INFO = {
    "name": name,
    "desc": desc,
    "get_prompt_func": get_prompt,
    "chat_func": chat,
    "checker_func": checker,
    "response_formatter": format_response,
    "force_prompt": force_prompt,
    "task_complete_actions": task_complete_actions,
}
