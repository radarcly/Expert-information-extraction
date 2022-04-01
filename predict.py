import re
import time
from info.utils import reviseIntroducation,introducation_is_english_or_chinese
from info.utils import readInputDataByXlrd,readInputDataByOpenpyxl
from run_ner import predict
import argparse
import os
import json
from tqdm import tqdm

os.environ["CUDA_VISIBLE_DEVICES"] = "1"

def get_experts_with_language(experts):
    cn_experts,en_experts={},{}
    for key,value in tqdm(experts.items()):
        language,introducation = introducation_is_english_or_chinese(value["简介"])
        if language == "chinese":
            cn_experts[key] = introducation
        elif language == "english":
            en_experts[key] = introducation
    return cn_experts,en_experts

def save_predict_result(cn_results,en_results):
    save_cn_filename = "predict_result/predict_result_cn.json"
    save_en_filename = "predict_result/predict_result_en.json"

    with open(save_cn_filename, "w", encoding='utf-8') as f:
        f.write(json.dumps(cn_results ,ensure_ascii=False,indent=2))

    with open(save_en_filename, "w", encoding='utf-8') as f:
        f.write(json.dumps(en_results ,ensure_ascii=False,indent=2))

parser = argparse.ArgumentParser()

parser.add_argument("--filename",
                    default="data/data.xlsx",
                    type=str)
args = parser.parse_args()


# 读取所有专家信息
experts = readInputDataByXlrd(args.filename)

# 将专家分为中文介绍和英文介绍
cn_experts,en_experts = get_experts_with_language(experts)

# 获取模型预测结果
cn_results,en_results = predict(cn_experts,en_experts)

# 存储模型预测结果
save_predict_result(cn_results,en_results)




