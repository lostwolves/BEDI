import json
import os
import pathlib
import numpy as np
import re

from tqdm import tqdm

def clock_distance_score(t1, t2):
    if type(t1)== int and type(t2)== int:
        # Calculate the absolute difference between the two times
        diff = np.abs(t1 - t2)
        # Find the minimum difference on a circular clock (12 hours cycle)
        min_diff = min(diff, 12 - diff)
        # Calculate the score based on the distance, where 1 is the closest (diff=0), 0 is the farthest (diff=6)
        score = 1 - (min_diff / 6)  # Normalize to a score where 6 is the farthest with score 0
    else:
        score = 0
    return score

def extract_time_direction(text):
    match = re.search(r'(\d+)\s*o\'clock', text)
    if match:
        return int(match.group(1))
    else:
        return None

def score_clock(read_name, save_name, ques_type = "Spatial_PosRelDis"):
    
    with open(read_name, 'r', encoding='utf-8') as file:
        ques_list = json.load(file)[ques_type]
    ans_dict = {}
    score_sum = 0
    question_sum = 0
    for que_id, chat_answer in ques_list.items():
        Standard_clock = extract_time_direction(chat_answer["Standard Answer"])
        Generated_clock = extract_time_direction(chat_answer["Generated Answer"])
        output = clock_distance_score(Standard_clock, Generated_clock)
        
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
    test_ques_type = "Spatial_PosRelDis"
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