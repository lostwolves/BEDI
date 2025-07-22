import re
import json
import numpy as np
import ast
from PIL import Image, ImageDraw
import os

CACHE_DIR = "cache/modified_images"

def extract_json(text:str):
    # print(text)

    json_data=None
    if "json" in text:
        json_data=re.compile(r"```json\n(.*?)\n```", re.DOTALL).findall(text)
        json_data=json_data[0]
    elif "{" in text:
        json_data=re.search(r'\{.*\}', text, re.DOTALL)
        json_data=json_data.group(0)
    else:
        json_data=text

    if json_data:
        try:
            json_data=json.loads(json_data)
            return json_data
        except json.JSONDecodeError:
            json_data=ast.literal_eval(json_data)
            return json_data
        except:
            raise ValueError("Failed to extract json data from text")
    else:
        raise ValueError("Failed to extract json data from text")

def draw_box(image:str,
             height:int=80,
             width:int=80):
    

    os.makedirs(CACHE_DIR, exist_ok=True)

    src_image=Image.open(image)
    w,h=src_image.size

    draw = ImageDraw.Draw(src_image)

    box = [(w-width)//2, (h-height)//2, (w+width)//2, (h+height)//2]
    draw.rectangle(box, outline="red", width=5)

    basename = os.path.basename(image)
    modified_image = os.path.join(CACHE_DIR, basename.split(".")[0] + "_modified." + basename.split(".")[1])
    src_image.save(modified_image)
    return modified_image