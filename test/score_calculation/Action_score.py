import json
import os
from typing import Any, Dict, List, Union
from pprint import pprint

from tqdm import tqdm

Action = Dict[str, Any]
ActionLike = Union[Action, List[Action]]

def _to_list(x: ActionLike) -> List[Action]:
    """Convert a single action or a list of actions into a list."""
    return [x] if isinstance(x, dict) else list(x)

def indicator_equal(a: Any, b: Any) -> int:
    """Indicator function P(·): return 1 if values are exactly equal, else 0."""
    return 1 if a == b else 0

def filter_non_zero(d):
    return {k: v for k, v in d.items() if v != 0}

def filter_numeric_values(d):
    return {k: v for k, v in d.items() if isinstance(v, (int, float, complex)) and not isinstance(v, bool)}

def dict_score(D_ans: Action, D_prd: Action) -> Dict[str, Any]:
    """
    Compute the Score_{Str-Acc} for a single action dictionary pair.

    Returns:
        dict containing score, jaccard, value_match_avg, and per-key details.
    """
    K_ans = set(D_ans.keys())
    K_prd = set(D_prd.keys())

    # Jaccard similarity = |intersection| / |union|
    inter = K_ans & K_prd
    union = K_ans | K_prd
    jaccard = (len(inter) / len(union)) if union else 1.0  # defined as 1 if both empty

    # p = number of keys in the ground truth dictionary
    p = len(K_ans) if K_ans else 1  # avoid division by zero
    per_key = {}
    match_sum = 0
    for k in K_ans:
        v_ans = D_ans[k]
        v_prd_prime = D_prd.get(k, None)  # if missing, assign None
        m = indicator_equal(v_ans, v_prd_prime)
        per_key[k] = {"v_ans": v_ans, "v_prd_prime": v_prd_prime, "P_equal": m}
        match_sum += m

    value_match_avg = match_sum / p
    score = jaccard * value_match_avg

    return score

def str_acc_single(D_ans: Action, D_prd: Action) -> Dict[str, Any]:
    # structure_score = dict_score(D_ans, D_prd)
    try:
        structure_score = dict_score(D_ans, D_prd)
    except:
        structure_score = 0
    
    value_D_ans = filter_non_zero(D_ans)
    num_D_ans = filter_numeric_values(value_D_ans)
    value_D_prd = filter_non_zero(D_prd)
    num_D_prd = filter_numeric_values(value_D_prd)
    value_score = dict_score(value_D_ans, value_D_prd)
    if not num_D_ans:
        num_score = 1
    else:
        num_score = dict_score(num_D_ans, num_D_prd)

    return {
        "Structure_score": structure_score,
        "value_score": value_score,
        "num_score": num_score,
        "Action_score": value_score * num_score
    }

def str_acc_dict(D_ans: ActionLike, D_prd: ActionLike) -> Dict[str, Any]:
    """
    Evaluate structural accuracy for either a single action or a list of actions.

    - If both are dicts: compute single action result.
    - If both are lists: align actions sequentially up to min(len(ans), len(prd)),
      compute scores for each pair, and average.
    - If ground truth has extra unmatched actions, they are assigned score=0
      (strict penalty for missing predictions).
    """
    ans_list = _to_list(D_ans)
    prd_list = _to_list(D_prd)

    n_ans = len(ans_list)
    n_prd = len(prd_list)
    min_len = min(n_ans, n_prd)

    total_structure = 0.0
    total_action = 0.0

    for i in range(min_len):
        res = str_acc_single(ans_list[i], prd_list[i])
        total_structure += res["Structure_score"]
        total_action += res["Action_score"]

    overall_structure = total_structure / n_ans if n_ans else 1.0
    overall_action = total_action / n_ans if n_ans else 1.0

    return {
        "structure_score": overall_structure,
        "action_score": overall_action,
        "counts": {"n_ans": n_ans, "n_prd": n_prd, "paired": min_len}
    }

def str_acc_sequence(L_ans: ActionLike, L_prd: ActionLike) -> Dict[str, Any]:
    """
    Sequence-level structural accuracy with penalty factor t/s:
        Score' = (t/s) * (1/t) * Σ Score_{Str-Acc}(D_ans,i, D_prd,i)

    - If both are empty: return 1.0.
    - If one is empty: return 0.0.
    - Align first t = min(m, n) pairs.
    - Apply penalty factor t/s, where s = max(m, n).
    """
    ans_list, prd_list = _to_list(L_ans), _to_list(L_prd)
    m, n = len(ans_list), len(prd_list)

    if m == 0 and n == 0:
        return {"structure_score": 1.0, "paired": 0, "penalty": 1.0, "per_action": []}
    if m == 0 or n == 0:
        return {"structure_score": 0.0, "paired": 0, "penalty": 0.0, "per_action": []}

    # t = min(m,n), s = max(m,n)
    t, s = min(m, n), max(m, n)
    A = ans_list[:t]  # ground truth truncated to first t
    P = prd_list[:t]  # prediction truncated to first t

    
    total_structure = 0.0
    total_action = 0.0

    for i in range(t):
        try:
            res = str_acc_single(A[i], P[i])
            total_structure += res["Structure_score"]
            total_action += res["Action_score"]
        except:
            total_structure += 0
            total_action += 0

    mean_pair_score_structure = total_structure / t
    mean_pair_score_action = total_action / t
    penalty = t / s
    overall_prime_structure = penalty * mean_pair_score_structure
    overall_prime_action = penalty * mean_pair_score_action

    return {
        "structure_score": overall_prime_structure,
        "action_score": overall_prime_action,
        "paired": t,
        "penalty": penalty,      # = t/s
        "counts": {"m_ans": m, "n_prd": n},
    }

if __name__ == "__main__":
    
    read_dir = "/opt/action_answer_gpt4o" # Dir for saving action capability test results
    save_path = "/opt/action_score.json" # Output path for accuracy statistics
    
    results = {}
    sum_num = 0
    sum_score_structure = 0.0
    sum_score_action = 0.0
    for root, _, files in tqdm(os.walk(read_dir)):
        for file in files:
            if file.endswith(".json"):
                file_path = os.path.join(root, file)
                # print(f"Processing file: {file_path}")
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if data["Generated Answer"] == None:
                    sample_score_structure = 0.0
                    sample_score_action = 0.0
                elif data["answer_type"] == "list":
                    score_dict = str_acc_sequence(data["Standard Answer"], data["Generated Answer"])
                elif data["answer_type"] == "dictionary":
                    score_dict = str_acc_dict(data["Standard Answer"], data["Generated Answer"])
                sample_score_structure = score_dict["structure_score"]
                sample_score_action = score_dict["action_score"]
                sum_num += 1
                sum_score_structure += sample_score_structure
                sum_score_action += sample_score_action
    results["sum_num"] = sum_num
    results["structure_score_sum"] = sum_score_structure
    results["structure_score_mean"] = sum_score_structure / sum_num
    results["action_score_sum"] = sum_score_action
    results["action_score_mean"] = sum_score_action / sum_num
    with open(save_path, "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=4)
    print(results)