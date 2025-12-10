import ast
import json
import os
import time
import requests
import base64
import pathlib

from typing import Union, Dict
from mimetypes import guess_type
from tqdm import tqdm

os.environ['OPENAI_API_KEY']="your API key"

class GPTS:
    def __init__(self,
                 api_key:str=None,
                 model_name:str="gpt-4-turbo-preview",
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

        assert model_name in self.supported_model_names, f"Model name should be one of {self.supported_model_names}"

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

def gpt4_chatbot_score(path, save_dir, ques_type = "Spatial_RelDisRelDis"):
    if not isinstance(path,dict):
        print('DataTypeError: Input [path] should be [dict] type !!!')
        return
    
    print('*******************************************************')
    print('Start GPT-based score evaluating !!!')
    score_sum = 0
    question_sum = 0
    score_json_name = os.path.join(save_dir, "score_sum.json")
    for k, v in tqdm(path.items()):
        ## Check whether the file has already been analyzed
        mid_save_dir = os.path.join(save_dir, k + f"_ans_{ques_type}.json")
        if os.path.exists(mid_save_dir):
            with open(mid_save_dir, 'r', encoding='utf-8') as file:
                data = file.read()
                result_dict = ast.literal_eval(data)
            score_sum += result_dict["Score_sum"]
            question_sum += result_dict["Question_number"]
            continue
        ## Build a dictionary to store the score for each file
        mid_answer_list = {}
        mid_que_num = 0
        mid_score_sum = 0
        with open(v[1], 'r', encoding='utf-8') as file:
            ques_list = json.load(file)[ques_type]
        for que_id, chat_answer in ques_list.items():
            Question = chat_answer["Question"]
            Standard_Answer = chat_answer["Standard Answer"]
            Generated_Answer = chat_answer["Generated Answer"]
            TEXT_SCORE = f"""Here are two answers to the same question "{Question}", and the Answers1 is "{Standard_Answer}", the Answers2 is "{Generated_Answer}". Are the objects referred to in Answer 2 and Answer 1 the same? Only answer 'yes' or 'no' without any explanation."""
            output, history = gpt.chat(TEXT_SCORE)
            
            if output in ['yes','Yes','Yes.']:
                output_score = 1
            elif output in ['no','No','No.']:
                output_score = 0
            score_sum += float(output_score)
            question_sum += 1
            
            mid_answer_list[que_id] = float(output_score)
            mid_score_sum += float(output_score)
            mid_que_num += 1
        mid_answer_list["Score_sum"] = mid_score_sum
        mid_answer_list["Question_number"] = mid_que_num
        with open(mid_save_dir, "w", encoding="utf-8") as fp:
            json.dump(mid_answer_list, fp, indent=4, ensure_ascii=False)
    answer_list = {}
    answer_list["Score sum"] = score_sum
    answer_list["Question number"] = question_sum
    answer_list["Average score"] = score_sum/question_sum
    with open(score_json_name, "w", encoding="utf-8") as fp:
        json.dump(answer_list, fp, indent=4, ensure_ascii=False)
    
    print('Complete the score evaluating of all images !!!')

if __name__ == "__main__":
    
    test_ques_type = "Spatial_RelDisRelDis"

    cfg=dict(
        model_name="gpt-4o",
        temperature=0.8,
        top_p=0.9,
        max_tokens=300,
    )
    gpt = GPTS(**cfg)
    ## Get path dict
    pic_read_dir = "task image dir"
    json_read_dir = "test model answer json dir"
    txt_score_save_dir = os.path.join(json_read_dir, test_ques_type)
    if not os.path.exists(txt_score_save_dir):
        os.makedirs(txt_score_save_dir)
    path={}
    uavimage_list = list(pathlib.Path(pic_read_dir).glob('*.jpg'))
    for image_name in uavimage_list:
        image_name = str(image_name)
        image_id = image_name.split('\\')[-1].replace('.jpg', '')
        json_name = os.path.join(json_read_dir, image_id + '_ans.json')
        path[image_id] = [image_name, json_name]
    gpt4_chatbot_score(path, txt_score_save_dir, ques_type = test_ques_type)
