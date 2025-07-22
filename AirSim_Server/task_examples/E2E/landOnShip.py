import shapely.geometry as sg

from tools.utils import draw_box, extract_json
from task_examples.prompt_exapmles.prompt4LandOnShip import PROMPT_E2E


## Task configuration for landing on a ship
# ------------------------------------------------------
# 1. task name
name = "LandOnShip"

# ------------------------------------------------------
# 2. task description
desc = "Controlling the drone to land on the aircraft carrier at Sea Area X1"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_E2E

# ------------------------------------------------------
# 4. task force prompt
# This prompt is used to force the agent to not choose landing when the drone is not directly above the aircraft carrier.
force_prompt = "\n\nNOTE: The drone is currently NOT directly above the aircraft carrier, do NOT choose to perform a landing operation!!!"

# ------------------------------------------------------
# 5. function to get the prompt
def get_prompt(task_desc, position, view, last_goal, **kwargs):
    prompt = prompt_template.format(
        desc=task_desc,
        pos=position,
        view=view,
        goal=last_goal,
    )
    return prompt

# ------------------------------------------------------
# 6. function to get the next action from the agent
def chat(prompt, frame, agent, pos, view, task_name, task_desc, cur_step, **kwargs):
    if view == "downward-looking":
        frame = draw_box(frame)
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
ship_area = sg.Polygon([
    (723,2475),
    (706,2491),
    (647,2441),
    (619,2436),
    (495,2310),
    (474,2267),
    (495,2241),
    (524,2264),
    (541,2235),
    (636,2352),
    (653,2361),
    (672,2378),
    (672,2417)
])

def checker(pos, view, frame, task_name, task_desc, **kwargs):
    pos = sg.Point(pos[0], pos[1])
    return pos.within(ship_area)

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
