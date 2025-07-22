from openai import OpenAI
import os
import base64
from mimetypes import guess_type
import json


def encode_image(image_file:str):
    with open(image_file,"rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")
    
class QwenVL:
    def __init__(self, 
                 base_url:str="https://dashscope.aliyuncs.com/compatible-mode/v1",
                 api_key:str=None,
                 model_name:str="qwen-vl-max",
                 max_tokens:int=300
    ):
        api_key = api_key or os.environ.get("DASHSCOPE_API_KEY",None)
        if not api_key:
            raise Exception("Please provide DASHSCOPE_API_KEY.")
        self.client=OpenAI(
            api_key=api_key,
            base_url=base_url
        )
        self.model_name=model_name
        self.max_tokens=max_tokens

    def __call__(self, question:str, image_file:str=None):
        messages=[
            {
                "role":"user",
                "content":[
                    {
                        "type":"text",
                        "text":question
                    }
                ]
            }
        ]
        if image_file:
            mime_type,_ = guess_type(image_file)
            strImage=encode_image(image_file)
            messages[-1]["content"].append(
                {
                    "type":"image_url",
                    "image_url":{
                        "url":f"data:{mime_type};base64,{strImage}"
                    }
                }
            )
        completion=self.client.chat.completions.create(
            model=self.model_name,
            messages=messages,
            max_tokens=self.max_tokens,
            stream=False
        )

        response=json.loads(completion.model_dump_json())
        output=response["choices"][0]["message"]["content"]

        return output
    
if __name__=="__main__":
    cfg=dict(
        model_name="qwen-vl-max",
        max_tokens=3,
    )
    bot=QwenVLMax()
    question="1+1=?"
    response=bot(question,image_file=r"test.png")
    print(response)

    
