import shapely.geometry as sg

from tools.utils import draw_box, extract_json
from task_examples.prompt_exapmles.prompt4Delivery import PROMPT_E2E


## Delivery Task
# 1. task name
name = "DeliveryCargo"

# 2. task description
desc = "Controlling a drone to deliver cargo to a red cargo ship with many containers of goods docked in the Bruce Port"

# 3. task prompt template
prompt_template = PROMPT_E2E

# 4. task force prompt
# This prompt is used to force the agent to not choose landing when the drone is not directly above the target cargo ship.
force_prompt = "\n\nNOTE:The drone is NOT currently directly above the target cargo ship, do NOT choose to perform a landing operation!!!"

# 5. initial pose
initial_position = (0, 0, -2)
initial_orientation = (0, 0, 1, 0)


# 6. function to get the prompt
def get_prompt(task_desc, position, view, last_goal, **kwargs):
    prompt = prompt_template.format(
        desc=task_desc,
        pos=position,
        view=view,
        goal=last_goal,
    )
    return prompt

# 7. function to get the next action from the agent
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
def checker(pos,view,frame,task_name,task_desc,**kwargs):
    if view == "downward-looking":
        pos = sg.Point(pos[0], pos[1])
        return pos.within(ship_area)
    return False

# 9. function to format the response for frontend display
def format_response(response, **kwargs):
    content = f"步数: {response['cur_step']}\n"
    content += f"当前位置: {response['position']}\n"
    content += f"当前视角: {response['view']}\n"
    content += f"动作命令: {response['action_name']}\n"
    content += f"动作参数: {response['params']}\n"
    content += f"决策依据: {response['analysis']}\n"
    return content

# 10. task complete actions
task_complete_actions = ["task_complete", "land"]


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