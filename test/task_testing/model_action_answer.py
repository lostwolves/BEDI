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
            if "gpt-4" not in self.model_name:
                raise ValueError("Image input is only supported for GPT-4 models")
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

def gpt4_chatbot(gpt, question_dict, save_dir):
    if not isinstance(question_dict,dict):
        print('DataTypeError: Input [path] should be [dict] type !!!')
        return
    
    print('*******************************************************')
    print('Start image question answering !!!')
    query = "You are an agent responsible for generating UAV actions. I will provide you with instructions regarding UAV action decisions. Your task is to convert these instructions into the standard UAV action dictionary format. The standard format is defined as follows: \
    { \
    'action': Action type, one of ['move', 'rotate', 'adjust', 'zoom'], corresponding to UAV movement, UAV rotation, camera orientation adjustment, and camera zoom adjustment, respectively;  \
    'direction': Movement direction, one of ['forward', 'backward', 'left', 'right', 'up', 'down']. This field is only applicable when `action` is 'move'; otherwise, set to 0; \
    'distance': Movement distance in meters. Only applicable when `action` is 'move'; otherwise, set to 0;  \
    'speed': Movement speed in meters per second. Only applicable when `action` is 'move'; otherwise, set to 0;  \
    'duration': Movement duration in seconds. Only applicable when `action` is 'move'; otherwise, set to 0;  \
    'rotate_direction': UAV rotation direction, either 'left' or 'right'. Only applicable when `action` is 'rotate'; otherwise, set to 0;  \
    'adjust_direction': Camera rotation direction, one of ['left', 'right', 'up', 'down']. Only applicable when `action` is 'adjust'; otherwise, set to 0;  \
    'zoom_level': Camera zoom level, one of ['small', 'big', 'keep']. 'small' narrows the field of view and enlarges the target, 'big' widens the field of view and enlarges the target, 'keep' maintains the current view. Only applicable when `action` is 'zoom'; otherwise, set to 0;  \
    } \n \
    Notes: \
    - 1. Each action dictionary must contain only one action. \
    - 2. A single action dictionary must include all eight elements listed above. \
    - 3. If a single action cannot fulfill the required decision, generate multiple action dictionaries. These should be executed sequentially by the UAV to accomplish all necessary operations. \
    - 4. If there is only one action, return the result in dictionary form. If there are multiple actions, place these actions into a list for the UAV to execute sequentially, and return the result in list form. \n \
    Now, I will provide you with a task instruction. Please convert it into an action dictionary in the format described above without any explanation."
    for k, v in tqdm(question_dict.items()):
        mid_dict_name = os.path.join(save_dir, k + "_ans.json")
        if os.path.exists(mid_dict_name):
            continue
        # 读取并解析JSON文件
        chat_ans = {}
        mid_ques = v["instructions"]
        chat_ans["instructions"] = mid_ques
        chat_ans["answer_type"] = v["answer_type"]
        chat_ans["Standard Answer"] = v["action_dict"]
        new_quary = query + mid_ques
        output, history = gpt.chat(new_quary)
        output = output.replace("json", "")
        output = output.replace("```", "")
        output = output.replace("\n", "")
        ## 分析结果格式
        try:
            if v["answer_type"] == "list":
                answer = ast.literal_eval(output)
            elif v["answer_type"] == "dictionary":
                answer = ast.literal_eval(output)
            chat_ans["Generated Answer"] = answer
            with open(mid_dict_name, "w", encoding="utf-8") as fp:
                json.dump(chat_ans, fp, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"Error parsing output for {k}: {e}")
            # answer = output
        
    print('Complete answering all the questions !!!')

if __name__ == "__main__":
    
    # model_name = "gemini-2.5-flash"
    model_name = "claude-3-5-sonnet-latest"
    cfg=dict(
        model_name=model_name,
        # model_name="gpt-4o",
        temperature=0,
        top_p=0.9,
        max_tokens=1000,
    )
    gpt = GPTS(**cfg)
    
    # Dir preparation
    input_file = "action_instructions.json"   # Input Task JSON file path
    output_dir = "ques_action" # Output directory path
    answer_save_dir = os.path.join(output_dir, model_name)
    if not os.path.exists(answer_save_dir):
        os.makedirs(answer_save_dir)

    # Read JSON file
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)
    gpt4_chatbot(gpt, data, answer_save_dir)
