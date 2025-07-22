import requests
import asyncio
import websockets
import json
import threading
import time
import queue
import logging

import logging

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from configs import get_default_config
from tools.utils import draw_box, extract_json
from taskInfo import TASK_INFO, TASK_MAPPING

class TaskHelper:
    def __init__(self,
                 logger: logging.Logger,
                 config_file: str = None):
        self.logger = logger
        self.cfg = get_default_config()
        if config_file:
            self.logger.info(f"Loading config from {config_file}")
            self.cfg.merge_from_file(config_file)

        self.message_queue = queue.Queue()
        self.client_connections = set()
        self.client_lock = threading.Lock()
        self.send_thread = threading.Thread(target=self.send_worker, daemon=True)
        self.send_thread.start()

        self.task_start = False
        self.task_complete = False

        if "ollama" in self.cfg.agent.model_name.lower():
            from agents.ollama_models import OllamaModel
            model_name = self.cfg.agent.model_name.split("__")[1]
            self.agent = OllamaModel(
                model_name=model_name,
                max_tokens=self.cfg.agent.max_tokens
            )
        elif "qwen" in self.cfg.agent.model_name.lower():
            from agents.qwenvl import QwenVL
            self.agent = QwenVL(
                model_name=self.cfg.agent.model_name,
                api_key=self.cfg.agent.api_key,
                max_tokens=self.cfg.agent.max_tokens
            )
        elif "gpt" in self.cfg.agent.model_name.lower():
            from agents.gpt import GPTs
            self.agent = GPTs(
                model_name=self.cfg.agent.model_name,
                api_key=self.cfg.agent.api_key,
                max_tokens=self.cfg.agent.max_tokens
            )
        else:
            raise NotImplementedError(
                f"Model {self.cfg.agent.model_name} is not supported yet."
            )
        
        self.cur_step = 0
        self.prompt_template = None

        self.last_goal = "none(currently the first step)"
        self.task_complete_actions = []

        self.needEnforcement = False

        self.taskInfoInitialized = False

    def init_task_info(self, task_type:str):
        task_type = TASK_MAPPING.get(task_type, None)
        if not task_type:
            raise ValueError(f"Unknown task type: {task_type}")
        task_info = TASK_INFO.get(task_type, None)
        if not task_info:
            raise ValueError(f"Unknown task info for type: {task_type}")
        
        self.task_name = task_info["name"]
        self.task_desc = task_info["desc"]
        self.get_prompt_func = task_info["get_prompt_func"]
        self.force_prompt = task_info["force_prompt"]
        self.chat_func = task_info["chat_func"]
        self.checker_func = task_info["checker_func"]
        self.response_formatter = task_info["response_formatter"]

        self.cur_step = 0
        self.view = self.cfg.view
        self.last_goal = "none(currently the first step)"

        self.task_complete_actions = task_info["task_complete_actions"]

        if "position" or "quaternion" in task_info:
            position = task_info.get("position", None)
            quaternion = task_info.get("quaternion", None)
            self.airsim_control(
                {
                    "action_name": "set_pose",
                    "action_params": {
                        "position": position,
                        "quaternion": quaternion
                    }
                }
            )

        self.taskInfoInitialized = True
        self.logger.info(f"Initialized task info for {task_type}")
        self.task_complete = False
        self.task_start = True

    def airsim_control(self, payload:dict):
        response = requests.post(
            f"http://localhost:{self.cfg.server.airsim_port}/control",
            json=payload
        )

        if response.status_code == 200:
            return response.json()
        else:
            self.logger.error(f"Failed to control AirSim: {response.status_code}")
            raise Exception(
                f"Failed to control AirSim: {response.status_code}"
            )

    def get_prompt(self):
        pos_and_view = self.airsim_control({"action_name": "get_position_and_view", "action_params": {}})

        self.pos = (pos_and_view["x"], pos_and_view["y"], pos_and_view["z"])
        self.view = pos_and_view["view"]

        prompt = self.get_prompt_func(
            task_name=self.task_name,
            task_desc=self.task_desc,
            position=self.pos,
            view=self.view,
            last_goal=self.last_goal
        )

        if self.needEnforcement:
            prompt += self.force_prompt
            self.needEnforcement = False

        self.logger.info(f"Generated prompt: {prompt}")
        return prompt
    
    def chat(self, frame:str):
        prompt = self.get_prompt()

        self.logger.info(f"Chatting with model: {self.cfg.agent.model_name}")

        response = self.chat_func(
            prompt=prompt,
            frame=frame,
            agent=self.agent,
            pos=self.pos,
            view=self.view,
            task_name=self.task_name,
            task_desc=self.task_desc,
            cur_step=self.cur_step
        )

        return response
    
    def checker(self):
        self.logger.info("Checking task completion...")

        pos_and_view = self.airsim_control({"action_name": "get_position_and_view", "action_params": {}})
        pos = (pos_and_view["x"], pos_and_view["y"], pos_and_view["z"])
        view = pos_and_view["view"]
        seg_mask = self.airsim_control({"action_name": "get_segmentation", "action_params": {}})["seg_mask"]

        frame = self.airsim_control({"action_name": "get_image", "action_params": {}})["image_path"]

        return self.checker_func(
            pos=pos,
            view=view,
            frame=frame,
            task_name=self.task_name,
            task_desc=self.task_desc,
            seg_mask=seg_mask,
        )
    
    async def start_task(self):
        while True:
            while not self.task_start:
                time.sleep(1)
            while not self.task_complete:
                try:
                    if not self.taskInfoInitialized:
                        self.task_start = False
                        self.task_complete = True
                        self.logger.info("Task info not initialized, skipping task.")
                        self.send(
                            json.dumps({
                                "role": "system",
                                "response": "任务信息未成功初始化，跳过任务执行。"
                            })
                        )
                        break
                    
                    self.cur_step += 1
                    self.logger.info(f"Current step: {self.cur_step}")
                    if self.cur_step > self.cfg.task.max_steps:
                        self.logger.info("Reached max steps, stopping task.")
                        self.task_start = False
                        self.task_complete = True
                        if not self.checker():
                            self.logger.info("Task not completed.")
                            self.send(
                                json.dumps({
                                    "role": "system",
                                    "response": "任务执行超过最大步数，任务失败。"
                                })
                            )
                        else:
                            self.logger.info("Task completed successfully despite max steps.")
                            self.send(
                                json.dumps({
                                    "role": "system",
                                    "response": "任务执行超过最大步数，但任务完成。"
                                })
                            )
                        self.taskInfoInitialized = False
                        break

                    
                    frame = self.airsim_control({
                        "action_name": "get_image",
                        "action_params": {}
                    })["image_path"]
                    self.logger.info(f"Frame captured: {frame}")

                    # send the frame to the frontend for visualization
                    self.send(
                        json.dumps({
                            "role": "model",
                            "image": os.path.basename(frame),
                        })
                    )

                    response = self.chat(frame)
                    self.logger.info(f"Model response: {response}")

                    self.last_goal = response.get("current_goal", "none")

                    content = self.response_formatter(response)
                    self.logger.info(f"Formatted response: {content}")

                    self.send(
                        json.dumps({
                            "role": "model",
                            "response": content,
                        })
                    )

                    if response['action_name'] in self.task_complete_actions:
                        # check if the task is complete
                        if not self.checker():
                            self.logger.info("Task not complete, force execution.")
                            self.needEnforcement = True
                            self.send(
                                json.dumps({
                                    "role": "system",
                                    "response": "任务未完成，继续执行。"
                                })
                            )
                            continue
                        else:
                            self.logger.info("Task completed successfully.")
                            self.task_start = False
                            self.task_complete = True
                            self.send(
                                json.dumps({
                                    "role": "system",
                                    "response": "task_done"
                                })
                            )
                            self.taskInfoInitialized = False
                    else:
                        self.logger.info(f"Executing action: {response['action_name']} with params: {response.get('params', {})}")
                        self.airsim_control({
                            "action_name": response["action_name"],
                            "action_params": response.get("params", {})
                        })
                        
                        time.sleep(self.cfg.control.rotate_step)

                except Exception as e:
                    self.logger.error(f"Error during task execution: {str(e)}")
                    self.send(
                        json.dumps({
                            "role": "system",
                            "response": f"任务执行过程中发生错误: {str(e)}"
                        })
                    )
                    self.taskInfoInitialized = False
                    self.task_start = False
                    self.task_complete = True
                    break



    def send_worker(self):
        while True:
            message = self.message_queue.get()
            with self.client_lock:
                clients = list(self.client_connections)
            for client in clients:
                try:
                    future = asyncio.run_coroutine_threadsafe(
                        client.send(message), 
                        self.loop
                    )
                    future.result(timeout=1.0)
                except Exception as e:
                    print(f"Failed to send message: {str(e)}")
                    with self.client_lock:
                        if client in self.client_connections:
                            self.client_connections.remove(client)
            self.message_queue.task_done()

    def send(self, message: str):
        self.message_queue.put(message)

    
    async def connect(self):
        self.logger.info("Connecting to WebSocket server...")
        self.loop = asyncio.get_event_loop()
        async def reply(websocket):
            client_addr = websocket.remote_address
            with self.client_lock:
                self.client_connections.add(websocket)
            self.logger.info(f"Client connected: {client_addr}")
            try:
                async for message in websocket:
                    self.logger.info(f"Received message from {client_addr}: {message}")
                    data = json.loads(message)
                    if data["type"] == "message":
                        question = data["content"]
                        frame = self.airsim_control({
                            "action_name": "get_image",
                            "action_params": {}
                        })["image_path"]
                        self.logger.info(f"Frame for question: {frame}")
                        await websocket.send(
                            json.dumps({
                                "role": "system",
                                "image": os.path.basename(frame),
                            })
                        )
                        response = self.agent(
                            question=question,
                            image_file=frame
                        )
                        self.logger.info(f"Response from agent: {response}")
                        await websocket.send(
                            json.dumps({
                                "role": "model",
                                "response": response
                            })
                        )
                    elif data["type"] == "task":
                        self.init_task_info(data["content"])
                        self.logger.info(f"Task started: {data['content']}")
                    else:
                        raise ValueError(f"Unknown message type: {data['type']}")
            except Exception as e:
                self.logger.error(f"Error in client {client_addr}: {str(e)}")
                await websocket.send(
                    json.dumps({
                        "role": "system",
                        "response": f"遇到错误: {str(e)}"
                    })
                )

        server = await websockets.serve(
            reply, 
            "localhost", 
            self.cfg.server.ws_port,
            ping_interval=30,       
            ping_timeout=120,       
            max_size=2**20,         
            max_queue=100,          
            close_timeout=10        
        )

        self.logger.info(f"WebSocket server started on ws://127.0.0.1:{self.cfg.server.ws_port}")
        await asyncio.Future()

    async def run(self):
        self.logger.info("Starting task helper...")
        threading.Thread(target=asyncio.run, args=(self.connect(),), daemon=True).start()
        await self.start_task()

                   
