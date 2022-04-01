from bert_ner.example import InputExample, InputFeatures

import os
import re
import torch
from torch.utils.data import TensorDataset

def readfile(filename, is_chinese:bool=True):
    '''
    read file
    '''
    with open(filename, 'r', encoding="utf8") as file:
        lines = list(file.readlines())
    
    data = []
    if is_chinese:
        sentence = []
        labels = []
        index = 0
        while index < len(lines):
            line = lines[index].strip()
            if len(line) == 0:
                if len(sentence) > 0:
                    data.append((sentence,labels))
                    sentence = []
                    labels = []
                index += 1
                continue
        
            splits = line.split('\t')
            if splits[0].isdigit():
                label = splits[1] 
                digit_merge = []
                while lines[index].strip().split('\t')[0].isdigit():
                    digit_merge.append(lines[index].strip().split('\t')[0])
                    index += 1
                token = "".join(digit_merge)
            elif splits[0].encode().isalpha():
                label = splits[1] 
                alpha_merge = []
                while lines[index].strip().split('\t')[0].encode().isalpha():
                    alpha_merge.append(lines[index].strip().split('\t')[0])
                    index += 1
                token = "".join(alpha_merge)
            else:
                token = splits[0]
                label = splits[1]
                index += 1
            sentence.append(token)
            labels.append(label)

        if len(sentence) > 0:
            data.append((sentence,labels))
    else:
        sentence = []
        labels = []
        for line in lines:
            if len(line)==0:
                if len(sentence) > 0:
                    data.append((sentence,label))
                    sentence = []
                    label = []
                continue
            splits = line.split(' ')
            sentence.append(splits[0])
            label.append(splits[1])

        if len(sentence) >0:
            data.append((sentence,label))
    return data

class DataProcessor(object):
    def __init__(self):
        pass

    """Base class for data converters for sequence classification data sets."""
    def get_train_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the train set."""
        raise NotImplementedError()

    def get_dev_examples(self, data_dir):
        """Gets a collection of `InputExample`s for the dev set."""
        raise NotImplementedError()

    def get_labels(self):
        """Gets the list of labels for this data set."""
        raise NotImplementedError()

    @classmethod
    def _read_tsv(cls, input_file, quotechar=None):
        """Reads a tab separated value file."""
        return readfile(input_file)


class NerProcessor(DataProcessor):
    def __init__(self, bioe: bool = True):
        super().__init__()
        self.bioe = bioe

    def get_train_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "train.txt")), "train")

    def get_dev_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "dev.txt")), "dev")

    def get_test_examples(self, data_dir):
        """See base class."""
        return self._create_examples(
            self._read_tsv(os.path.join(data_dir, "test.txt")), "test")

    def get_labels(self):
        if self.bioe:
            # return ['X', 'O', '[CLS]', '[SEP]','B-NAME', 'I-NAME', 'E-NAME', 'B-ORG', 'I-ORG', 'E-ORG', 'B-YEAR', 'I-YEAR', 'E-YEAR', 'B-MONTH', 'I-MONTH', 'E-MONTH', 'B-DAY', 'I-DAY', 'E-DAY', 'B-NATIONALITY', 'I-NATIONALITY', 'E-NATIONALITY', 'B-INTEREST', 'I-INTEREST', 'E-INTEREST', 'B-MAJOR', 'I-MAJOR', 'E-MAJOR', 'B-TITLE', 'I-TITLE', 'E-TITLE', 'B-POST', 'I-POST', 'E-POST', 'B-DEPART', 'I-DEPART', 'E-DEPART', 'B-SEX', 'I-SEX', 'E-SEX', 'B-NATION', 'I-NATION', 'E-NATION', 'B-NATIVEPLACE', 'I-NATIVEPLACE', 'E-NATIVEPLACE', 'B-ADDRESS', 'I-ADDRESS', 'E-ADDRESS', 'B-CODE', 'I-CODE', 'E-CODE', 'B-PHONE', 'I-PHONE', 'E-PHONE', 'B-TELEPHONE', 'I-TELEPHONE', 'E-TELEPHONE', 'B-FAX', 'I-FAX', 'E-FAX', 'B-MAIL', 'I-MAIL', 'E-MAIL', 'B-WEBSITE', 'I-WEBSITE', 'E-WEBSITE', 'B-WORK-ORG', 'I-WORK-ORG', 'E-WORK-ORG', 'B-WORK-TITLE', 'I-WORK-TITLE', 'E-WORK-TITLE', 'B-WORK-POST', 'I-WORK-POST', 'E-WORK-POST', 'B-WORK-STARTYEAR', 'I-WORK-STARTYEAR', 'E-WORK-STARTYEAR', 'B-WORK-ENDYEAR', 'I-WORK-ENDYEAR', 'E-WORK-ENDYEAR', 'B-WORK-STARTMONTH', 'I-WORK-STARTMONTH', 'E-WORK-STARTMONTH', 'B-WORK-ENDMONTH', 'I-WORK-ENDMONTH', 'E-WORK-ENDMONTH', 'B-WORK-STARTDAY', 'I-WORK-STARTDAY', 'E-WORK-STARTDAY', 'B-WORK-ENDDAY', 'I-WORK-ENDDAY', 'E-WORK-ENDDAY', 'B-WORK-TECHNOLOGY', 'I-WORK-TECHNOLOGY', 'E-WORK-TECHNOLOGY', 'B-WORK-CONTENT', 'I-WORK-CONTENT', 'E-WORK-CONTENT', 'B-CRE-CREDIT', 'I-CRE-CREDIT', 'E-CRE-CREDIT', 'B-CRE-YEAR', 'I-CRE-YEAR', 'E-CRE-YEAR', 'B-CRE-LEVEL', 'I-CRE-LEVEL', 'E-CRE-LEVEL', 'B-CRE-ORG', 'I-CRE-ORG', 'E-CRE-ORG', 'B-CRE-PLACE', 'I-CRE-PLACE', 'E-CRE-PLACE', 'B-CRE-CATEGORY', 'I-CRE-CATEGORY', 'E-CRE-CATEGORY', 'B-CRE-ENDYEAR', 'I-CRE-ENDYEAR', 'E-CRE-ENDYEAR', 'B-CRE-GRADE', 'I-CRE-GRADE', 'E-CRE-GRADE', 'B-CRE-REASON', 'I-CRE-REASON', 'E-CRE-REASON', 'B-CRE-CONTENT', 'I-CRE-CONTENT', 'E-CRE-CONTENT', 'B-EDU-ORG', 'I-EDU-ORG', 'E-EDU-ORG', 'B-EDU-STARTYEAR', 'I-EDU-STARTYEAR', 'E-EDU-STARTYEAR', 'B-EDU-ENDYEAR', 'I-EDU-ENDYEAR', 'E-EDU-ENDYEAR', 'B-EDU-DEPARTMENT', 'I-EDU-DEPARTMENT', 'E-EDU-DEPARTMENT', 'B-EDU-MAJOR', 'I-EDU-MAJOR', 'E-EDU-MAJOR', 'B-EDU-EDUCATION', 'I-EDU-EDUCATION', 'E-EDU-EDUCATION', 'B-EDU-DEGREE', 'I-EDU-DEGREE', 'E-EDU-DEGREE']
            return ['X', 'O', '[CLS]', '[SEP]','B-NAME', 'I-NAME', 'E-NAME', 'B-ORG', 'I-ORG', 'E-ORG', 'B-YEAR', 'I-YEAR', 'E-YEAR', 'B-MONTH', 'I-MONTH', 'E-MONTH', 'B-DAY', 'I-DAY', 'E-DAY', 'B-NATIONALITY', 'I-NATIONALITY', 'E-NATIONALITY', 'B-INTEREST', 'I-INTEREST', 'E-INTEREST', 'B-MAJOR', 'I-MAJOR', 'E-MAJOR', 'B-TITLE', 'I-TITLE', 'E-TITLE', 'B-POST', 'I-POST', 'E-POST', 'B-DEPART', 'I-DEPART', 'E-DEPART', 'B-SEX', 'I-SEX', 'E-SEX', 'B-NATION', 'I-NATION', 'E-NATION', 'B-NATIVEPLACE', 'I-NATIVEPLACE', 'E-NATIVEPLACE', 'B-ADDRESS', 'I-ADDRESS', 'E-ADDRESS', 'B-CODE', 'I-CODE', 'E-CODE', 'B-PHONE', 'I-PHONE', 'E-PHONE', 'B-TELEPHONE', 'I-TELEPHONE', 'E-TELEPHONE', 'B-FAX', 'I-FAX', 'E-FAX', 'B-MAIL', 'I-MAIL', 'E-MAIL', 'B-WEBSITE', 'I-WEBSITE', 'E-WEBSITE', 'B-WORK-ORG', 'I-WORK-ORG', 'E-WORK-ORG', 'B-WORK-TITLE', 'I-WORK-TITLE', 'E-WORK-TITLE', 'B-WORK-POST', 'I-WORK-POST', 'E-WORK-POST', 'B-WORK-STARTTIME', 'I-WORK-STARTTIME', 'E-WORK-STARTTIME', 'B-WORK-ENDTIME', 'I-WORK-ENDTIME', 'E-WORK-ENDTIME', 'B-WORK-TECHNOLOGY', 'I-WORK-TECHNOLOGY', 'E-WORK-TECHNOLOGY', 'B-WORK-CONTENT', 'I-WORK-CONTENT', 'E-WORK-CONTENT', 'B-WORK-DEPART', 'I-WORK-DEPART', 'E-WORK-DEPART', 'B-CRE-CREDIT', 'I-CRE-CREDIT', 'E-CRE-CREDIT', 'B-CRE-YEAR', 'I-CRE-YEAR', 'E-CRE-YEAR', 'B-CRE-LEVEL', 'I-CRE-LEVEL', 'E-CRE-LEVEL', 'B-CRE-ORG', 'I-CRE-ORG', 'E-CRE-ORG', 'B-CRE-PLACE', 'I-CRE-PLACE', 'E-CRE-PLACE', 'B-CRE-CATEGORY', 'I-CRE-CATEGORY', 'E-CRE-CATEGORY', 'B-CRE-ENDYEAR', 'I-CRE-ENDYEAR', 'E-CRE-ENDYEAR', 'B-CRE-GRADE', 'I-CRE-GRADE', 'E-CRE-GRADE', 'B-CRE-REASON', 'I-CRE-REASON', 'E-CRE-REASON', 'B-CRE-CONTENT', 'I-CRE-CONTENT', 'E-CRE-CONTENT', 'B-CRE-TYPE', 'I-CRE-TYPE', 'E-CRE-TYPE', 'B-EDU-ORG', 'I-EDU-ORG', 'E-EDU-ORG', 'B-EDU-STARTYEAR', 'I-EDU-STARTYEAR', 'E-EDU-STARTYEAR', 'B-EDU-ENDYEAR', 'I-EDU-ENDYEAR', 'E-EDU-ENDYEAR', 'B-EDU-DEPARTMENT', 'I-EDU-DEPARTMENT', 'E-EDU-DEPARTMENT', 'B-EDU-MAJOR', 'I-EDU-MAJOR', 'E-EDU-MAJOR', 'B-EDU-EDUCATION', 'I-EDU-EDUCATION', 'E-EDU-EDUCATION', 'B-EDU-DEGREE', 'I-EDU-DEGREE', 'E-EDU-DEGREE']
            # return [
            #     'B-ORG', 'I-ORG', 'E-ORG', 
            #     'B-NATION', 'I-NATION', 'E-NATION', 
            #     'B-INTEREST', 'I-INTEREST', 'E-INTEREST', 
            #     'B-TITLE', 'I-TITLE', 'E-TITLE', 
            #     'B-POST', 'I-POST', 'E-POST', 
            #     'B-SUBJECT', 'I-SUBJECT', 'E-SUBJECT', 
            #     'B-YEAR', 'I-YEAR', 'E-YEAR', 
            #     'B-MONTH', 'I-MONTH', 'E-MONTH', 
            #     'B-DAY', 'I-DAY', 'E-DAY', 
            #     'B-WORK-EYEAR', 'I-WORK-EYEAR', 'E-WORK-EYEAR', 
            #     'B-WORK-SYEAR', 'I-WORK-SYEAR', 'E-WORK-SYEAR', 
            #     'B-WORK-ORG', 'I-WORK-ORG', 'E-WORK-ORG', 
            #     'B-WORK-TITLE', 'I-WORK-TITLE', 'E-WORK-TITLE', 
            #     'B-WORK-POST', 'I-WORK-POST', 'E-WORK-POST', 
            #     'B-EDU-ORG', 'I-EDU-ORG', 'E-EDU-ORG', 
            #     'B-EDU-DEPART', 'I-EDU-DEPART', 'E-EDU-DEPART', 
            #     'B-EDU-MAJOR', 'I-EDU-MAJOR', 'E-EDU-MAJOR', 
            #     'B-EDU-DEGREE', 'I-EDU-DEGREE', 'E-EDU-DEGREE', 
            #     'B-EDU-YEAR', 'I-EDU-YEAR', 'E-EDU-YEAR', 
            #     'B-CRE-NAME', 'I-CRE-NAME', 'E-CRE-NAME', 
            #     'B-CRE-YEAR', 'I-CRE-YEAR', 'E-CRE-YEAR']
        else:
            return ['X', 'O', '[CLS]', '[SEP]',
            'I-ORG','I-NATION','I-INTEREST','I-TITLE',
            'I-POST','I-SUBJECT','I-YEAR', 'I-MONTH','I-DAY',
            'I-WORK-EYEAR', 'I-WORK-SYEAR', 'I-WORK-ORG', 'I-WORK-TITLE', 'I-WORK-POST',
            'I-EDU-ORG', 'I-EDU-DEPART', 'I-EDU-DEGREE', 'I-EDU-YEAR',
            'I-CRE-NAME', 'I-CRE-YEAR']

    def _create_examples(self, lines, set_type):
        examples = []
        for i,(sentence,read_label) in enumerate(lines):
            guid = "%s-%s" % (set_type, i)
            text_a = sentence
            text_b = None
            if self.bioe:
                label = read_label
            else:
                label = []
                for each_label in read_label:
                    if each_label.startswith("B-") or each_label.startswith("E-"):
                        label.append("I-{}".format(each_label[2:]))
                    else:
                        label.append(each_label)

            examples.append(InputExample(guid=guid,text_a=text_a,text_b=text_b,label=label))
        return examples

    @classmethod
    def convert_examples_to_features(cls, examples, label_list, max_seq_length, tokenizer):
        """Loads a data file into a list of `InputBatch`s."""
        label_map = {label : i for i, label in enumerate(label_list)}
        add_label = 'X'

        features = []
        for (_, example) in enumerate(examples):
            textlist = example.text_a
            tokens = ['[CLS]']
            valid_ids = [1]
            label_ids = [label_map['[CLS]']]
            for i, word in enumerate(textlist):
                sub_words = tokenizer.tokenize(word)
                if not sub_words:
                    sub_words = ['[UNK]']
                tokens.extend(sub_words)
                for j in range(len(sub_words)):
                    if j == 0:
                        valid_ids.append(1)
                        label_ids.append(label_map[example.label[i]])
                    else:
                        valid_ids.append(0)
        
            if len(tokens) >= max_seq_length - 1:
                tokens = tokens[0:(max_seq_length - 2)]
                label_ids = label_ids[0:(max_seq_length - 2)]
                valid_ids = valid_ids[0:(max_seq_length - 2)]
            tokens.append('[SEP]')
            valid_ids.append(1)
            label_ids.append(label_map['[SEP]'])
            label_mask = [1] * len(label_ids)
            
            input_ids = tokenizer.convert_tokens_to_ids(tokens)
            segment_ids = [0] * len(input_ids)
            input_mask = [1] * len(input_ids)

            if len(input_ids) < max_seq_length:
                diff = max_seq_length - len(input_ids)
                input_ids.extend([tokenizer.pad_token_id] * diff)
                segment_ids.extend([0] * diff)
                input_mask.extend([0] * diff)
                valid_ids.extend([0] * diff)
            if len(label_ids) < max_seq_length:
                diff = max_seq_length - len(label_ids)
                label_ids.extend([label_map[add_label]] * diff)
                label_mask.extend([0] * diff)
            
            features.append(
                InputFeatures(input_ids=input_ids,
                            input_mask=input_mask,
                            segment_ids=segment_ids,
                            label_id=label_ids,
                            valid_ids=valid_ids,
                            label_mask=label_mask))
        return features

    @classmethod
    def convert_features_to_dataset(cls, features):
        all_input_ids = torch.tensor([f.input_ids for f in features], dtype=torch.long)
        all_input_mask = torch.tensor([f.input_mask for f in features], dtype=torch.long)
        all_segment_ids = torch.tensor([f.segment_ids for f in features], dtype=torch.long)
        all_label_ids = torch.tensor([f.label_id for f in features], dtype=torch.long)
        all_valid_ids = torch.tensor([f.valid_ids for f in features], dtype=torch.long)
        all_label_mask = torch.tensor([f.label_mask for f in features], dtype=torch.long)
        return TensorDataset(all_input_ids, all_input_mask, all_segment_ids, all_label_ids,all_valid_ids, all_label_mask)

    # def get_chinese_word_list(self, sentence):
    #     sentence_list = list(sentence)
    #     index = 0
    #     return_sentence_list = []
    #     while index < len(sentence_list):
    #         if sentence_list[index].isdigit():
    #             digit_merge = []
    #             while sentence_list[index].isdigit():
    #                 digit_merge.append(sentence_list[index])
    #                 index += 1
    #             token = "".join(digit_merge)
    #         elif sentence_list[index].encode().isalpha():
    #             alpha_merge = []
    #             while sentence_list[index].encode().isalpha():
    #                 alpha_merge.append(sentence_list[index])
    #                 index += 1
    #             token = "".join(alpha_merge)
    #         else:
    #             token = sentence_list[index]
    #             index += 1
    #         sentence.append(token)

    #     return return_sentence_list
