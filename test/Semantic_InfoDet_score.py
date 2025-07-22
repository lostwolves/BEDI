import json
import os
import pathlib
import numpy as np
import re

from tqdm import tqdm

def extract_numbers(text):
    numbers = re.findall(r'\d+', text)
    return [int(num) for num in numbers]

def compare_lists_score(list1, list2):
    set1 = set(list1)
    set2 = set(list2)
    
    intersection = set1.intersection(set2) 
    union = set1.union(set2)
    
    return len(intersection)/len(union)


def score_clock(read_name, save_name, ques_type = "Semantic_InfoDet"):
    
    with open(read_name, 'r', encoding='utf-8') as file:
        ques_list = json.load(file)[ques_type]
    ans_dict = {}
    score_sum = 0
    question_sum = 0
    for que_id, chat_answer in ques_list.items():
        Standard_clock = extract_numbers(chat_answer["Standard Answer"])
        Generated_clock = extract_numbers(chat_answer["Generated Answer"])
        output = compare_lists_score(Standard_clock, Generated_clock)
        
        score_sum += float(output)
        question_sum += 1
        
        ans_dict[que_id] = float(output)
    ans_dict["Score_sum"] = score_sum
    ans_dict["Question_number"] = question_sum
    with open(save_name, "w", encoding="utf-8") as fp:
        json.dump(ans_dict, fp, indent=4, ensure_ascii=False)
    
    return score_sum, question_sum


if __name__ == "__main__":
    
    ## Get path dict
    test_ques_type = "Semantic_InfoDet"
    json_read_dir = "test model answer json dir"
    txt_score_save_dir = os.path.join(json_read_dir, test_ques_type)
    if not os.path.exists(txt_score_save_dir):
        os.makedirs(txt_score_save_dir)
    sum_json = os.path.join(txt_score_save_dir, "score_sum.json")
    json_list = list(pathlib.Path(json_read_dir).glob('*.json'))
    ## Start
    final_dict={}
    final_score = 0
    final_num = 0
    for json_name in tqdm(json_list):
        json_name = str(json_name)
        image_id = json_name.split('/')[-1]
        save_name = os.path.join(txt_score_save_dir, image_id.replace(".json", f"_{test_ques_type}.json"))
        if os.path.exists(save_name):
            with open(save_name, 'r', encoding='utf-8') as file:
                score_dict = json.load(file)
            final_score += score_dict["Score_sum"]
            final_num += score_dict["Question_number"]
            continue
        else:
            mid_score, mid_num = score_clock(json_name, save_name, ques_type = test_ques_type)
            final_score += mid_score
            final_num += mid_num
    final_dict["Score sum"] = final_score
    final_dict["Question number"] = final_num
    final_dict["Average score"] = final_score/final_num
    with open(sum_json, "w", encoding="utf-8") as fp:
        json.dump(final_dict, fp, indent=4, ensure_ascii=False)
    print("Complete the score evaluating of all images !!!")