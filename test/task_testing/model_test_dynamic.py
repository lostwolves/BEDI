from collections import Counter
import json
from pathlib import Path
from datetime import datetime
from zoneinfo import ZoneInfo

import ast
import json
import os
import base64
import time

import requests
from typing import Union, Dict
from mimetypes import guess_type

from tqdm import tqdm

os.environ['OPENAI_API_KEY'] = "XXXXXX" # replace with your API key

class GPTS:
    def __init__(self,
                 api_key:str=None,
                 model_name:str="gpt-4o",
                 temperature:float=0.5,
                 top_p:float=1.0,
                 max_tokens:int=2000):
        
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        
        assert self.api_key, "API Key is missing!"

        self.supported_model_names = ["gpt-3.5-turbo", 
                                      "gpt-4-turbo-preview", 
                                      "gpt-4-turbo", 
                                      "gpt-4-vision-preview", 
                                      "gpt-4-all", 
                                      "GPTS", 
                                      "gpt-4-1106-preview",
                                      "gpt-4-0125-preview",
                                      "gpt-4-turbo-2024-04-09",
                                      "gpt-4o",]

        # assert model_name in self.supported_model_names, f"Model name should be one of {self.supported_model_names}"

        self.model_name = model_name
        self.temperature = temperature
        self.top_p = top_p
        self.max_tokens = max_tokens
        self.default_prompt = "You are a useful assistant who can efficiently complete user-specified tasks or answer user questions well."
        self.default_sleep_time = 2
        self.max_retries = 5

        # self.url="https://reverse.onechat.fun/v1/chat/completions"
        self.url="https://chatapi.onechats.top/v1/chat/completions"

    def set_attr(self,name:str,value)->None:
        if hasattr(self,name):
            setattr(self,name,value)
        else:
            raise AttributeError(f"{name} does not exist in the class")
    
    def get_headers(self)->Dict[str,str]:
        return {
            "Content-Type": "application/json",
            "Authorization":f"Bearer {self.api_key}"
        }
    
    def get_payload(self,prompt:str=None)->Dict:
        if not prompt:
            prompt = self.default_prompt
        return {
            "model": self.model_name,
            "temperature": self.temperature,
            "top_p": self.top_p,
            "max_tokens": self.max_tokens,
            "messages": [
                {
                    "role": "system",
                    "content": [
                        {
                            "type": "text",
                            "text": prompt
                        }
                    ]
                }
            ],
        }

    def chat(self,question:str, image_files:Union[str,list]=None, prompt:str=None, history:dict=None):
        payload=history or self.get_payload(prompt)
        
        payload["messages"].append(
            {
                "role":"user",
                "content":[
                    {
                        "type":"text",
                        "text":question
                    }
                ]
            }
        )

        if image_files:
            # if "gpt-4" not in self.model_name:
            #     raise ValueError("Image input is only supported for GPT-4 models")
            if isinstance(image_files,str):
                image_files = [image_files]
            for image_file in image_files:
                mime_type,_ = guess_type(image_file)
                strImage=self.encode_image(image_file)
                payload["messages"][-1]["content"].append(
                    {
                        "type":"image_url",
                        "image_url":{
                            "url":f"data:{mime_type};base64,{strImage}"
                        }
                    }
                )

        retries = 0
        while retries<self.max_retries:
            response = requests.post(self.url,json=payload,headers=self.get_headers())
            if response.status_code == 200:
                break
            else:
                retries+=1
                time.sleep(self.default_sleep_time)

        if retries==self.max_retries:
            raise Exception("Max retries reached.")
        
        output = self.parse_response(response)
        payload["messages"].append(
            {
                "role":"assistant",
                "content":[
                    {
                        "type":"text",
                        "text":output
                    }
                ]
            }
        )
        history = payload

        return output, history

    def parse_response(self,response):
        return response.json()["choices"][0]["message"]["content"]

        
    def encode_image(self,image_file):
        with open(image_file,"rb") as f:
            return base64.b64encode(f.read()).decode('utf-8')

def gpt4_chatbot(gpt, history, test_data, step_name):
    test_question = test_data[step_name]["question"]
    if test_data[step_name]["image"]:
        test_image_file = os.path.join(image_read_dir, test_data[step_name]["image"])
        output, history = gpt.chat(question=test_question, image_files=test_image_file, history=history)
    else:
        output, history = gpt.chat(question=test_question, history=history)
    return output, history


if __name__ == "__main__":
    
    model_name="gpt-4o"
    cfg=dict(
        model_name=model_name,
        temperature=0,
        top_p=0.1,
        max_tokens=10,
    )
    gpt = GPTS(**cfg)
    
    # Test data preparation
    test_dir = "XXXX.json" ## The task test data file path
    image_read_dir= "test_img" ## The task image read directory
    log_save_dir = "log" ## The log save directory
    
    if not os.path.exists(log_save_dir):
        os.makedirs(log_save_dir)
    with open(test_dir, "r", encoding="utf-8") as f:
        test_data = json.load(f)
    ## log file save
    now = datetime.now(ZoneInfo("Asia/Tokyo"))
    filename = now.strftime("%Y%m%d_%H%M%S") + f"_{model_name}.json"
    path = os.path.join(log_save_dir, filename)

    f = open(path, "w", encoding="utf-8")
    content = f"Start testing... Tested model: {model_name}"
    line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
    f.write(line)
    print(line)
    f.flush()
    
    ## Prepare initial task results
    step_num = 0
    task_score = {
        "perception": 0,
        "decision": 0
    }
    ## Input task description:
    output, history = gpt.chat(test_data["task_description"])
    ## Start the first round of testing:
    output, history = gpt4_chatbot(gpt, history, test_data, "step1")
    mid_decision = test_data["step1"]["answer"][output]
    content = f"step1 Answer: {output}"
    line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
    f.write(line)
    print(line)
    choice_result, choice_decision, choice_score = mid_decision["result"], mid_decision["decision"], mid_decision["score"]
    step_num += 1
    task_score = dict(Counter(task_score) + Counter(choice_score))
    if choice_result:
        content = f"step1 Decision: Go to {choice_result}. {choice_decision}"
    else:
        content = f"step1 Decision: {choice_decision}"
    line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
    f.write(line)
    print(line)
    score_content = f"Current Score: {task_score}"
    line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + score_content + "\n"
    f.write(line)
    f.flush()
    ## Start the testing loop:
    while mid_decision["continue"]:
        mid_step = mid_decision["result"]
        output, history = gpt4_chatbot(gpt, history, test_data, mid_step)
        mid_decision = test_data[mid_step]["answer"][output]
        content = f"{mid_step} Answer: {output}"
        line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
        print(line)
        f.write(line)
        choice_result, choice_decision, choice_score = mid_decision["result"], mid_decision["decision"], mid_decision["score"]
        step_num += 1
        task_score = dict(Counter(task_score) + Counter(choice_score))
        if choice_result:
            content = f"{mid_step} Decision: Go to {choice_result}. {choice_decision}"
        else:
            content = f"{mid_step} Decision: {choice_decision}"
        line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
        print(line)
        f.write(line)
        
        score_content = f"Current Score: {task_score}"
        line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + score_content + "\n"
        f.write(line)
        
        if mid_decision["shown_image"]:
            choice_image = mid_decision["shown_image"]
            content = f"{mid_step} Show Image: {choice_image}"
            line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
            print(line)
            f.write(line)
        f.flush()
    mean_score = {key: task_score[key]/step_num for key in task_score}
    content = f"Step Number: {step_num}. Decision Score: {task_score}. Mean Score: {mean_score}"
    line = datetime.now(ZoneInfo("Asia/Tokyo")).strftime("[%Y:%m:%d:%H:%M:%S]: ") + content + "\n"
    f.write(line)
    ## Test finished. Log saved to log/filename.json
    f.close()
    print(f"Test finished. Log saved to {path}")