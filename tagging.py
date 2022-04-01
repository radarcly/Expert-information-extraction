# 读取数据
# -*- coding: utf-8 -*-
import json
import re

import xlrd
import xlwt
import nltk

# 判断一个字符串是否是int
def str_is_number(s):
    try:
        int(s)
        return True
    except ValueError:
        pass

# 获得所有专家
def readData():
    xlsx = xlrd.open_workbook('dataset/TC1/TC1数据集.xls')
    sheet = xlsx.sheets()[0]
    # 获得行数列数 行数为2001 列数为9
    rows = sheet.nrows
    cols = sheet.ncols
    key_list = []
    # 获得key_list id 名字 所在机构 简介
    for i in range(cols):
        key_list.append(sheet.cell(0, i).value)
    # 获得experts
    experts = []
    for i in range(1, rows):
        expert = {}
        introduction = ""
        # 获得专家 id 名字 所在机构信息
        for j in range(0, 3):
            # 比如id默认是float格式需要转为int
            if type(sheet.cell(i, j).value) == float:
                expert[key_list[j]] = str(int(sheet.cell(i, j).value))
            # 排除机构名为null的情况
            elif str(sheet.cell(i, j).value) == "null":
                expert[key_list[j]] = ""
            else:
                expert[key_list[j]] = str(sheet.cell(i, j).value)

        # 专家的简介信息需要合并第四列到第九列
        for j in range(3, cols):
            if type(sheet.cell(i, j).value) == float:
                introduction += str(int(sheet.cell(i, j).value))
            else:
                introduction += str(sheet.cell(i, j).value)
        # 用正则表达式删除html标签，之后删掉&nbsp,换行符和制表符
        expert[key_list[3]] = re.sub('<[^<]+?>', '', introduction).replace("&nbsp;", '').replace('\n', '').replace('\t','').strip()

        experts.append(expert)
    return experts

def getTableInfo(workbook,str,experts):
    # 读取work的信息
    work_sheet = workbook.sheets()[0]
    # works为一个map key是id,value是一个列表
    rows = work_sheet.nrows
    cols = work_sheet.ncols
    key_list = []
    for i in range(0,cols - 1):
        key_list.append(work_sheet.cell(0, i).value)
    for i in range(1, rows):
        if str_is_number(work_sheet.cell(i, 0).value) and work_sheet.cell(i, 0).value in experts.keys() :
            work = {}
            # 遍历每一列
            for j in range(1,cols-1):
                if work_sheet.cell(i,j).value != "unknown":
                    work[key_list[j]] = work_sheet.cell(i,j).value
            if str not in experts[work_sheet.cell(i, 0).value].keys():
                experts[work_sheet.cell(i, 0).value][str] = [work]
            else:
                experts[work_sheet.cell(i, 0).value][str].append(work)
    return experts

# 获得已标注专家信息
def get_marked_experts():
    basic_workbook = xlrd.open_workbook('data/basic.xls')
    work_workbook = xlrd.open_workbook("data/work.xls")
    credit_workbook = xlrd.open_workbook("data/credit.xls")
    education_workbook = xlrd.open_workbook("data/education.xls")

    # 读取basic的信息
    basic_sheet = basic_workbook.sheets()[0]
    # 专家为一个map key是id,value是一个列表，包含一堆信息
    experts = {}
    rows = basic_sheet.nrows
    cols = basic_sheet.ncols
    basic_key_list = []
    for i in range(0, cols):
        basic_key_list.append(basic_sheet.cell(0, i).value)

    for i in range(1, rows):
        expert = {}
        # 如果id是正常的数字的话
        if str_is_number(basic_sheet.cell(i, 0).value):
            # 遍历每一列
            for j in range(1,cols):
                # float转int
                if type(basic_sheet.cell(i, j).value) == float:
                    expert[basic_key_list[j]] = str(int(basic_sheet.cell(i, j).value))
                # 无视unknown
                elif str(basic_sheet.cell(i, j).value) == "unknown":
                    expert[basic_key_list[j]] = ""
                else:
                    expert[basic_key_list[j]] = str(basic_sheet.cell(i, j).value)
                experts[str(int(basic_sheet.cell(i,0).value))] = expert


    experts = getTableInfo(work_workbook,"work",experts)
    experts = getTableInfo(credit_workbook,"credit",experts)
    experts = getTableInfo(education_workbook,"education",experts)
    return experts

# 判断一个字符是不是英文字符
def is_alphabet(uchar):
    """判断一个unicode是否是英文字母"""
    if (u'\u0041' <= uchar <= u'\u005a') or (u'\u0061' <= uchar <= u'\u007a'):
        return True
    else:
        return False

# 判断一个字符是不是汉字
def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if  u'\u4e00' <= uchar <= u'\u9fa5':
        return True
    else:
        return False

#判断一个字符串是不是英文字符串，如果一个字符串英文字符长度是中文字符长度5倍就认为他是英文字符串
def is_English_String(str):
    e_num = 0
    c_num =0
    for ch in str:
        if is_alphabet(ch):
            e_num += 1
        elif is_chinese(ch):
            c_num += 1
    if e_num > 5*c_num:
        return True
    else:
        return False

def addtags(tags,g_tags,index1,index2,str,value):
    #将value中的空格也删掉，防止奖项英文单词含空格 匹配不到
    value = "".join(value.split())
    if str.find(value) > -1 and len(value) > 0:
        # 获得开始位置
        begin = str.find(value)
        # 获得结束位置
        end = begin + len(value) - 1
        # 先确保每个标记都是O,否则查找下一个位置
        flag = True
        for i in range(begin, end):
            if tags[i] != "O":
                flag = False
                break
        # 在有标记的情况下查找下一个位置
        if not flag:
            if str.find(value,end) > -1:
                # print(value,end)
                begin = str.find(value,end)
                end = begin + len(value) - 1
                flag = True
                for i in range(begin, end):
                    if tags[i] != "O":
                        flag = False
                        break

        # 在每个标记都为o的情况下
        if (flag):
            if end - begin == 0:
                tags[begin] = g_tags[index1][index2][0]
            elif end - begin == 1:
                tags[begin] = g_tags[index1][index2][0]
                tags[end] = g_tags[index1][index2][2]
            else:
                tags[begin] = g_tags[index1][index2][0]
                tags[end] = g_tags[index1][index2][2]
                for i in range(begin + 1, end):
                    tags[i] = g_tags[index1][index2][1]
    return tags

def addentags(tags,g_tags,index1,index2,str,value):
    if str.find(value) > -1:
        arr1 = str.split(" ")
        arr2 = value.split(" ")
        begin = end = 0
        for i in range(len(arr1)):
            if arr1[i] == arr2[0]:
                begin = i
                end = begin + len(arr2) - 1
        # 先确保每个标记都是O
        flag = True
        if(end >= len(tags)):
            flag = False
        else:
            for i in range(begin, end):
                if tags[i] != "O":
                    flag = False
        # 在每个标记都为o的情况下
        if (flag):
            if end - begin == 0:
                tags[begin] = g_tags[index1][index2][0]
            elif end - begin == 1:
                tags[begin] = g_tags[index1][index2][0]
                tags[end] = g_tags[index1][index2][2]
            else:
                tags[begin] = g_tags[index1][index2][0]
                tags[end] = g_tags[index1][index2][2]
                for i in range(begin + 1, end):
                    tags[i] = g_tags[index1][index2][1]
    return tags

def getDataset(experts,marked_experts,g_tags):
    train = open('train_cn.txt', 'w', encoding='utf-8')
    train_en = open('train_en.txt', 'w', encoding='utf-8')
    test = open('test.json', 'a', encoding='utf-8')
    num_set = 0
    for expert in experts:
        # 如果id能够在已标记专家中找到，并且介绍是中文字符串
        # ids = ["68576", "111921", "111926", "97005", "28473"]
        # ids = ["28473"]
        if expert['id'] in marked_experts.keys() and not is_English_String(expert['简历']) :
            str = "".join(expert['简历'].split())
            # print(str)
            # print(marked_experts['28473'])
            tags = []
            s = set()
            for i in range(len(str)):
                tags.append("O")


            # 对于标记的每个key
            for key,value in marked_experts[expert['id']].items():

                if key == "work":
                    for element in value:
                        if "startYear" in element.keys():
                            tags = addtags(tags, g_tags, "work", "year", str, element['startYear'])
                        if "corganization" in element.keys():
                            tags = addtags(tags, g_tags, "work", "org",  str, element["corganization"])
                elif key == "credit":
                    for element in value:
                        if "credit" in element.keys():
                            tags = addtags(tags, g_tags, "credit", "name",  str, element["credit"])
                        if "year" in element.keys():
                            tags = addtags(tags, g_tags, "credit",  "year", str, element["year"])
                elif key == "education":
                    for element in value:
                        if "cschool" in element.keys():
                            tags = addtags(tags,g_tags, "edu","org",str,element["cschool"])
                        if "department" in element.keys():
                            tags = addtags(tags, g_tags, "edu", "depart", str, element["department"])
                        if "major" in element.keys():
                            tags = addtags(tags, g_tags, "edu", "major", str, element["major"])
                        if "degree" in element.keys():
                            tags = addtags(tags, g_tags, "edu", "degree", str, element["degree"])
                        if "year" in element.keys():
                            tags = addtags(tags, g_tags, "edu", "year",  str, element["endYear"])
                elif key in ['year','month','day','nationality']:
                    tags = addtags(tags, g_tags, "basic", key, str, value)
                elif key in ['post',"subject","interest"]:
                    if value.find(";")  > - 1:
                        arr = value.split(";")
                        for a in arr:
                            tags = addtags(tags, g_tags, "basic", key, str, a)
                    elif value.find("；") > -1:
                        arr = value.split("；")
                        for a in arr:
                            tags = addtags(tags, g_tags, "basic", key, str, a)
                    else:
                        tags = addtags(tags, g_tags, "basic", key, str, value)

            for i in range(len(tags)):
                # print(str[i] + " " + tags[i])
            # print(marked_experts[expert['id']])
            # print(expert)
                train.write(str[i] + "\t" + tags[i] +"\n")
            num_set += 1
            train.write("\n")
        # print(num_set)

        elif expert['id'] in marked_experts.keys() and is_English_String(expert['简历']) and is_English_String(expert['名字']):
            nltk.download('punkt')
            print(nltk.sent_tokenize(expert['简历']))
        #      str = expert['简历']
        #      # print(str.split())
        #      length = len(str.split(" "))
        #      print(length)
        #      tags = []
        #      for i in range(length):
        #          tags.append("O")
        #      for key, value in marked_experts[expert['id']].items():
        #          if key == "work":
        #              for element in value:
        #                 if "startYear" in element.keys():
        #                     tags = addentags(tags, g_tags, "work", "year", str, element['startYear'])
        #                 if "eorganization" in element.keys():
        #                     tags = addentags(tags, g_tags, "work", "org", str, element["eorganization"])
        #          elif key == "credit":
        #              for element in value:
        #                  if "credit" in element.keys():
        #                      tags = addentags(tags, g_tags, "credit", "name", str, element["credit"])
        #                  if "year" in element.keys():
        #                      tags = addentags(tags, g_tags, "credit", "year", str, element["year"])
        #          elif key == "education":
        #              for element in value:
        #                  if "cschool" in element.keys():
        #                      tags = addentags(tags, g_tags, "edu", "org", str, element["cschool"])
        #                  if "department" in element.keys():
        #                      tags = addentags(tags, g_tags, "edu", "depart", str, element["department"])
        #                  if "major" in element.keys():
        #                      tags = addentags(tags, g_tags, "edu", "major", str, element["major"])
        #                  if "degree" in element.keys():
        #                      tags = addentags(tags, g_tags, "edu", "degree", str, element["degree"])
        #                  if "year" in element.keys():
        #                      tags = addentags(tags, g_tags, "edu", "year", str, element["endYear"])
        #          elif key in ['year', 'month', 'day', 'nationality', 'interest']:
        #              tags = addentags(tags, g_tags, "basic", key, str, value)
        #          elif key in ['post', "subject"]:
        #              if value.find(";") > - 1:
        #                 arr = value.split(";")
        #                 for a in arr:
        #                     tags = addentags(tags, g_tags, "basic", key, str, a)
        #              else:
        #                 tags = addentags(tags, g_tags, "basic", key, str, value)
        #      arr = str.split()
        #      # print(len(tags))
        #      # print(len(arr))
        #      for i in range(len(arr)):
        #          if arr[-1]
        #          print(arr[i] + " " + tags[i])
        #          train_en.write(arr[i] + "\t" + tags[i] +"\n")
        #      train_en.write("\n")
    # print(num)




tags = {}
tags['basic'] = {}
tags['basic']['org'] = ["B-ORG","I-ORG","E-ORG"]
tags['basic']['nationality'] = ["B-NATION","I-NATION","E-NATION"]
tags['basic']['interest'] = ["B-INTEREST","I-INTEREST","E-INTEREST"]
tags['basic']['post'] = ["B-POST","I-POST","E-POST"]
tags['basic']['subject'] = ["B-SUBJECT","I-SUBJECT","E-SUBJECT"]
tags['basic']['year'] = ["B-YEAR","I-YEAR","E-YEAR"]
tags['basic']['month'] = ["B-MONTH","I-MONTH","E-MONTH"]
tags['basic']['day'] = ["B-DAY","I-DAY","E-DAY"]
tags['work'] = {}
tags['work']['year'] = ["B-WORK-YEAR","I-WORK-YEAR","E-WORK-YEAR"]
tags['work']['org'] = ["B-WORK-ORG","I-WORK-ORG","E-WORK-ORG"]
tags['edu'] = {}
tags['edu']['org'] = ["B-EDU-ORG","I-EDU-ORG","E-EDU-ORG"]
tags['edu']['depart'] = ["B-EDU-DEPART","I-EDU-DEPART","E-EDU-DEPART"]
tags['edu']['major'] = ["B-EDU-MAJOR","I-EDU-MAJOR","E-EDU-MAJOR"]
tags['edu']['degree'] = ["B-EDU-DEGREE","I-EDU-DEGREE","E-EDU-DEGREE"]
tags['edu']['year'] = ["B-EDU-YEAR","I-EDU-YEAR","E-EDU-YEAR"]
tags['credit'] = {}
tags['credit']['name'] = ["B-CRE-NAME","I-CRE-NAME","E-CRE-NAME"]
tags['credit']['year'] = ["B-CRE-YEAR","I-CRE-YEAR","E-CRE-YEAR"]
tags['credit']['class'] = ["B-CRE-CLA","I-CRE-CLA","E-CRE-CLA"]
#
#
# list = []
# for key,value in tags.items():
#     for kk,vv in value.items():
#         for l in vv:
#             list.append(l)
# print(list)


experts = readData()
marked_experts = get_marked_experts()

getDataset(experts,marked_experts,tags)
