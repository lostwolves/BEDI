import shapely.geometry as sg

from tools.utils import extract_json
from task_examples.prompt_exapmles.prompt4Delivery import PROMPT_S2S

## Fly to Bruce Port Task
# ------------------------------------------------------
# 1. task name
name = "FlyToBrucePort"

# ------------------------------------------------------
# 2. task description
desc = "Controlling the drone to fly to Bruce Port"

# ------------------------------------------------------
# 3. task prompt template
prompt_template = PROMPT_S2S["fly_to_bruce_port"]

# ------------------------------------------------------
# 4. task force prompt
force_prompt = "\n\nNOTE: The drone is currently NOT within Bruce Port, which means the task is NOT completed yet."

# ------------------------------------------------------
# 5. initial pose
initial_position = (0, 0, -2)
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
port = sg.Polygon(
    [
        (-2100,810),
        (-2100,90),
        (-2800,90),
        (-2800,810)
    ]
)
def checker(pos, **kwargs):
    pos = sg.Point(pos[0], pos[1])
    return pos.within(port)

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
