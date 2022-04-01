from bert_ner.processor import NerProcessor

import argparse
import csv
import json
import logging
import os
import random
import sys

import numpy as np
import torch
import torch.nn.functional as F
from transformers import (AdamW, BertConfig, BertForTokenClassification, BertTokenizer, get_linear_schedule_with_warmup)
from torch import nn
from torch.utils.data import (DataLoader, RandomSampler, SequentialSampler, TensorDataset)
from tqdm import tqdm, trange

from seqeval.metrics import classification_report
from bert_ner.model import BertForNer
from typing import Tuple, List
from bert_ner.utils import auto_create, is_english

import os


logging.basicConfig(format = '%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S',
                    level = logging.INFO)
logger = logging.getLogger(__name__)

def build_dataset(args, processor, tokenizer, dataset_type: str="train"):
    if dataset_type == 'train':
        examples = processor.get_train_examples(args.data_dir)
    elif dataset_type == 'dev':
        examples = processor.get_dev_examples(args.data_dir)
    else:
        examples = processor.get_test_examples(args.data_dir)
    features = processor.convert_examples_to_features(examples, processor.get_labels(), args.max_seq_length, tokenizer)
    dataset = processor.convert_features_to_dataset(features)
    return dataset

def build_optimizer(args, model):
    param_optimizer = list(model.named_parameters())
    no_decay = ['bias','LayerNorm.weight']
    optimizer_grouped_parameters = [
         {'params': [p for n, p in param_optimizer if not any(nd in n for nd in no_decay)], 'weight_decay': args.weight_decay},
         {'params': [p for n, p in param_optimizer if any(nd in n for nd in no_decay)], 'weight_decay': 0.0}
         ]
    return AdamW(optimizer_grouped_parameters, lr=args.learning_rate, eps=args.adam_epsilon)

def build_scheduler(args, optimizer, train_set_size):
    num_train_optimization_steps = int(train_set_size/ args.batch_size) * args.epochs
    warmup_steps = int(args.warmup_proportion * num_train_optimization_steps) 
    scheduler = get_linear_schedule_with_warmup(optimizer, num_warmup_steps=warmup_steps, num_training_steps=num_train_optimization_steps)
    return scheduler

def evaluate(args, model, processor, tokenizer, evaluate_dataset:str='dev', epoch:int=None):
    dataset = auto_create("{}_{}".format(evaluate_dataset, args.language), lambda:build_dataset(args, processors, tokenizer, evaluate_dataset),True, path=args.cache_dir)
    # Run prediction for full data
    eval_sampler = SequentialSampler(dataset)
    eval_dataloader = DataLoader(dataset, sampler=eval_sampler, batch_size=args.batch_size)
    model.eval()
    y_true = []
    y_pred = []
    label_to_idx = {label: i for i, label in enumerate(processor.get_labels())}
    label_map = {i: label for i, label in enumerate(processor.get_labels())}
    for batch in tqdm(eval_dataloader):
        if torch.cuda.is_available():
            batch = tuple(t.cuda() for t in batch)
        input_ids, input_mask, segment_ids, label_ids, valid_ids, l_mask = batch

        with torch.no_grad():
            logits = model(input_ids, segment_ids, input_mask, valid_ids=valid_ids)

        logits = torch.argmax(F.log_softmax(logits,dim=2),dim=2)
        logits = logits.detach().cpu().numpy()
        label_ids = label_ids.to('cpu').numpy()
        input_mask = input_mask.to('cpu').numpy()

        for i, label in enumerate(label_ids):
            temp_1 = []
            temp_2 = []
            for j, m in enumerate(label):
                if j == 0:
                    continue
                elif label_ids[i][j] == label_to_idx['[SEP]']:
                    y_true.append(temp_1)
                    y_pred.append(temp_2)
                    break
                else:
                    temp_1.append(label_map[label_ids[i][j]])
                    temp_2.append(label_map[logits[i][j]])

    report = classification_report(y_true, y_pred, digits=4)
    output_eval_file = os.path.join(args.output_dir, "eval_results.txt")
    with open(output_eval_file, "a") as writer:
        writer.write("epoch {}\n".format(epoch))
        writer.write(report)

def get_model_with_language(saving_path, language):
    language_saving_path = os.path.join(saving_path, language)
    max_epoch = -1
    for all_dir_name in os.listdir(language_saving_path):
        if os.path.isdir(os.path.join(language_saving_path, all_dir_name)):
            current_saving_epoch = int(all_dir_name.replace("epoch", ""))
            if current_saving_epoch > max_epoch:
                max_epoch = current_saving_epoch
    
    language_saving_path = os.path.join(language_saving_path, "epoch{}".format(max_epoch))
    processors = NerProcessor()
    config = BertConfig.from_pretrained(language_saving_path, num_labels=len(processors.get_labels()))
    tokenizer = BertTokenizer.from_pretrained(language_saving_path, do_lower_case=True)
    model = BertForNer.from_pretrained(language_saving_path, config=config)
    if torch.cuda.is_available():
        model.cuda()
    model.eval()
    return tokenizer, model

def is_subtoken(word):
    if word[:2] == "##":
        return True
    else:
        return False

def predict_with_language(sentence, tokenizer, model) -> Tuple[List, List]:
    def chunks(lst, n:int=500):
        """Yield successive n-sized chunks from lst."""
        for i in range(0, len(lst), n):
            yield lst[i:i + n]

    # TODO: judge too length
    tokenizer_list = tokenizer.tokenize(sentence)

    all_to_pred_list = []
    for current_tokenzier_list in chunks(tokenizer_list, 500):
        tokens = ['[CLS]']
        valid_ids = [1]
        for token in current_tokenzier_list:
            if is_subtoken(token):
                valid_ids.append(0)    
            else:
                valid_ids.append(1)
            tokens.append(token)
        tokens.append('[SEP]')
        valid_ids.append(1)
                
        input_ids = tokenizer.convert_tokens_to_ids(tokens)
        segment_ids = [0] * len(input_ids)
        input_mask = [1] * len(input_ids)

        input_ids_tensor = torch.tensor([input_ids], dtype=torch.long)
        segment_ids_tensor = torch.tensor([segment_ids], dtype=torch.long)
        input_mask_tensor = torch.tensor([input_mask], dtype=torch.long)
        valid_ids_tensor = torch.tensor([valid_ids], dtype=torch.long)

        if torch.cuda.is_available():
            input_ids_tensor = input_ids_tensor.cuda()
            segment_ids_tensor = segment_ids_tensor.cuda()
            input_mask_tensor = input_mask_tensor.cuda()
            valid_ids_tensor = valid_ids_tensor.cuda()

        processors = NerProcessor()
        label_to_idx = {label: i for i, label in enumerate(processors.get_labels())}
        label_map = {i: label for i, label in enumerate(processors.get_labels())}
        
        with torch.no_grad():
            logits = model(input_ids_tensor, segment_ids_tensor, input_mask_tensor, valid_ids=valid_ids_tensor)

        logits_label = torch.argmax(F.softmax(logits,dim=2),dim=2)[0]
        logits_label = logits_label.detach().cpu().numpy()

        logits = []
        pos = 0
        for index,mask in enumerate(valid_ids):
            if index == 0:
                continue
            if mask == 1:
                logits.append(logits_label[index-pos])
            else:
                pos += 1
        logits.pop()
        pred_list = [label_map[pred_idx][2:] for pred_idx in logits]
        all_to_pred_list.extend(pred_list)
    
    return tokenizer_list, all_to_pred_list

# 之前曾学长版本有点小问题
# def detokenizer(tokens):
#     restored_text = []
#     for i in range(len(tokens)):
#         if not is_subtoken(tokens[i]) and (i+1)<len(tokens) and is_subtoken(tokens[i+1]):
#             restored_text.append(tokens[i] + tokens[i+1][2:])
#             if (i+2)<len(tokens) and is_subtoken(tokens[i+2]):
#                 restored_text[-1] = restored_text[-1] + tokens[i+2][2:]
#         elif not is_subtoken(tokens[i]):
#             restored_text.append(tokens[i])
#     return restored_text

def detokenizer(tokens):
    restored_text = []
    for i in range(len(tokens)):
        if not is_subtoken(tokens[i]):
            restored_text.append(tokens[i])
            j = 1
            while (i+j) < len(tokens) and is_subtoken(tokens[i+j]):
                restored_text[-1] = restored_text[-1] + tokens[i+j][2:]
                j += 1
    return restored_text


# def predict(sentence_list: List[str], saving_path: str = "bert_ner/save_models/") -> List[Tuple[List, List]]:
#     english_tokenizer, english_model = get_model_with_language(saving_path, "english")
#     chinese_tokenizer, chinese_model = get_model_with_language(saving_path, "chinese")

#     results = []
#     for sentence in tqdm(sentence_list):
#         if is_english(sentence):
#             print("")
#             input_list, output_list = predict_with_language(sentence, english_tokenizer, english_model)
#             input_list = detokenizer(input_list)
#             assert(len(input_list) == len(output_list))
#             results.append((input_list, output_list))
#         else:
#             input_list, output_list = predict_with_language(sentence, chinese_tokenizer, chinese_model)
#             input_list = detokenizer(input_list)
#             assert(len(input_list) == len(output_list))

#             # char_input_list, char_output_list = [], []
#             # for token, label in zip(input_list, output_list):
#             #     if len(token) > 1:
#             #         char_list = list(token)
#             #         for char in char_list:
#             #             char_input_list.append(char)
#             #             char_output_list.append(label)
#             #     else:
#             #         char_input_list.append(token)
#             #         char_output_list.append(label)
#             results.append((input_list, output_list))
#     return results

def predict(cn_sentence_list,en_sentence_list, saving_path: str = "bert_ner/save_models/"):
    english_tokenizer, english_model = get_model_with_language(saving_path, "english")
    chinese_tokenizer, chinese_model = get_model_with_language(saving_path, "chinese")

    cn_results = {}
    en_results = {}
    for id,sentence in tqdm(cn_sentence_list.items()):      
        input_list, output_list = predict_with_language(sentence, chinese_tokenizer, chinese_model)
        input_list = detokenizer(input_list)
        assert(len(input_list) == len(output_list))
        cn_results[id] = (input_list, output_list)
        
    for id,sentence in tqdm(en_sentence_list.items()):
        input_list, output_list = predict_with_language(sentence, english_tokenizer, english_model)
        input_list = detokenizer(input_list)
        assert(len(input_list) == len(output_list))
        en_results[id] = (input_list, output_list)    
    return cn_results,en_results



def main():
    # os.environ["CUDA_VISIBLE_DEVICES"] = "6"
    parser = argparse.ArgumentParser()
    ## Required parameters
    parser.add_argument("--data_dir",
                        default="bert_ner/dataset",
                        type=str,
                        help="The input data dir. Should contain the .tsv files (or other data files) for the task.")
    parser.add_argument("--output_dir",
                        default="bert_ner/save_models",
                        type=str,
                        help="The output directory where the model predictions and checkpoints will be written.")
    parser.add_argument("--cache_dir",
                        default="bert_ner/cache_path",
                        type=str,
                        help="The output directory where cache path used")

    ## Other parameters
    parser.add_argument("--language",
                        default="chinese",
                        type=str)
    parser.add_argument("--pretrained_path",
                        default="bert_ner/pretrained/",
                        type=str,
                        help="Where do you want to store the pre-trained models downloaded from s3")
    parser.add_argument("--max_seq_length",
                        default=256,
                        type=int,
                        help="The maximum total input sequence length after WordPiece tokenization. \n"
                             "Sequences longer than this will be truncated, and sequences shorter \n"
                             "than this will be padded.")
    parser.add_argument("--mode",
                        default='train',
                        type=str,
                        help="Whether to run training.")
    parser.add_argument("--batch_size",
                        default=16,
                        type=int,
                        help="Total batch size for training.")
    parser.add_argument("--learning_rate",
                        default=1e-5,
                        type=float,
                        help="The initial learning rate for Adam.")
    parser.add_argument("--epochs",
                        default=50,
                        type=float,
                        help="Total number of training epochs to perform.")
    parser.add_argument("--warmup_proportion",
                        default=0.1,
                        type=float,
                        help="Proportion of training to perform linear learning rate warmup for. "
                             "E.g., 0.1 = 10%% of training.")
    parser.add_argument("--weight_decay", default=0.01, type=float,
                        help="Weight deay if we apply some.")
    parser.add_argument("--adam_epsilon", default=1e-8, type=float,
                        help="Epsilon for Adam optimizer.")
    parser.add_argument("--max_grad_norm", default=1.0, type=float,
                        help="Max gradient norm.")
    parser.add_argument('--seed',
                        type=int,
                        default=42,
                        help="random seed for initialization")
    args = parser.parse_args()

    if args.language == "chinese":
        args.chinese = True
        args.data_dir = os.path.join(args.data_dir, "chinese")
        args.output_dir = os.path.join(args.output_dir, "chinese")
        args.pretrained_path = os.path.join(args.pretrained_path, "chinese_wwm_ext_pytorch")
    else:
        args.chinese = False
        args.data_dir = os.path.join(args.data_dir, "english")
        args.output_dir = os.path.join(args.output_dir, "english")
        args.pretrained_path = os.path.join(args.pretrained_path, "bert_base_uncased")


    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)

    processors = NerProcessor()
    config = BertConfig.from_pretrained(args.pretrained_path, num_labels=len(processors.get_labels()))
    tokenizer = BertTokenizer.from_pretrained(args.pretrained_path, do_lower_case=True)
    model = BertForNer.from_pretrained(args.pretrained_path, config=config)
    if torch.cuda.is_available():
        model.cuda()

    assert args.mode in ['train']
    if args.mode == 'train':  
        dataset = auto_create("{}_{}".format("train", args.language), lambda:build_dataset(args, processors, tokenizer, "train"),True, path=args.cache_dir)
        train_sampler = RandomSampler(dataset)
        train_dataloader = DataLoader(dataset, sampler=train_sampler, batch_size=args.batch_size)
        optimizer = build_optimizer(args, model)
        # scheduler = build_scheduler(args, optimizer, len(dataset))

        global_step = 0
        for epoch in trange(int(args.epochs), desc="Epoch"):
            model.train()
            tqdm_description = tqdm(train_dataloader)
            for step, batch in enumerate(tqdm_description):
                model.zero_grad()
                optimizer.zero_grad()

                if torch.cuda.is_available(): 
                    batch = tuple(t.cuda() for t in batch)
                input_ids, input_mask, segment_ids, label_ids, valid_ids,l_mask = batch
                loss = model(input_ids, segment_ids, input_mask, label_ids,valid_ids,l_mask)
                loss = loss.mean() # mean() to average on multi-gpu.

                loss.backward()
                torch.nn.utils.clip_grad_norm_(model.parameters(), args.max_grad_norm)

                optimizer.step()
                # scheduler.step()  # Update learning rate schedule
                global_step += 1

                tqdm_description.set_description("loss: {:.4f}".format(loss.item()))

            evaluate(args, model, processors, tokenizer, evaluate_dataset = 'train', epoch = epoch)

            current_output_dir = os.path.join(args.output_dir, "epoch{}".format(epoch))
            if not os.path.exists(args.output_dir):
                os.makedirs(current_output_dir)
            # Save a trained model and the associated configuration
            model_to_save = model.module if hasattr(model, 'module') else model  # Only save the model it-self
            model_to_save.save_pretrained(current_output_dir)
            tokenizer.save_pretrained(current_output_dir)
            label_map = {i : label for i, label in enumerate(processors.get_labels())}
            model_config = {"bert_model":args.pretrained_path,"do_lower":True,"max_seq_length":args.max_seq_length,"num_labels":len(processors.get_labels()),"label_map":label_map}
            json.dump(model_config,open(os.path.join(current_output_dir,"model_config.json"),"w"))    


if __name__ == "__main__":
    main()
