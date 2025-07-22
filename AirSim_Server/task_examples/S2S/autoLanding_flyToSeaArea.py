import shapely.geometry as sg

from tools.utils import extract_json
from task_examples.prompt_exapmles.prompt4LandOnShip import PROMPT_S2S

## Task configuration for flying to Sea Area X1
# ------------------------------------------------------
# 1. task name
name = "FlyToSeaAreaX1"

# ------------------------------------------------------
# 2. task description
desc = "Controlling the drone to fly to Sea Area X1"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_S2S["fly_to_sea_area"]

# ------------------------------------------------------
# 4. task force prompt
force_prompt = "\n\nNOTE: The drone is currently NOT within Sea Area X1, which means the task is not completed yet."

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
def checker(pos, **kwargs):
    sea_area_X1 = sg.Point(1100, 2500).buffer(50)
    pos = sg.Point(pos[0], pos[1])
    return pos.within(sea_area_X1)

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
