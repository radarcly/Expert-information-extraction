#废弃的方法
#  def revisePost(self):
#         post_list = self.post.split(";") 
#         self.post = ""  
#         post_set = set()
#         # 需要补充部门信息
#         post_dict_with_depart = ["学院院长","副院长","院长",
#                                  "副主任","系主任","副系主任","科主任","主任",
#                                  "教研室主任",
#                                  "负责人",
#                                  "课题组长","组长",
#                                  "院长助理",
#                                  "副处长","处长"                         
#                                 ]
#         # 不属于职务需要删除
#         delete_dict = ["博士后","博士生","硕士生","本科生","访问学者","博士","硕士"
#                         "法学博士后","上海","上海市","行政","科研","内科","技术","管理","学院","研发","长聘","编辑","材料","大学","实验"
#                         "骨科","软件工程","急诊科","外科","委员会","中国","浙江省","长陆","中药","执行","主诊","成员","创新","大师","该所","国际",
#                         "化学家","教授","火箭","结构","金融","科室","斯特林","团队","问题","协会","学会","学科","研究室","遗传","应用","中科院",
#                         "肿瘤科","重点","战略","肿瘤科","口腔科","中心","现场","全国","天文","天文台","体育部","睡眠",
#                         "长江学者","院士","江青年学者","上海市曙光学者"                    
#                       ]
#         # 需要补充组织信息
#         post_dict_with_org =  ["专任教师","教师",
#                                "副校长","校长",
#                                "党委书记","党委副书记"                                  
#                               ]
#         # 如果有部门优先补充部门，没有部门就补充组织
#         post_dict_with_depart_and_org = ["副所长","所长",                                         
#                                          "总经理","副总经理","经理",
#                                          "技术总监",     
#                                          "副总裁","总裁",
#                                          "首席科学家"
#                                         ]
#         # 不需要补充任何信息
#         post_dict_without_add = ["博士生导师","硕士生导师","研究生导师","导师","博导","硕导",
#                                  "副主席","主席",
#                                  "秘书长",
#                                  "委员",
#                                  "辅导员"         
#                                 ]
#         for post in post_list:            
#             post = reviseSymbolPair(post)
#             post = revisePrefixAndSuffix(post)
#             if post not in delete_dict and len(post) > 1:
#                 post_set.add(post) 
#         self.post = ";".join(post for post in post_set)

    # def reviseFax(self):
    #     fax_list = self.fax.split(";") 
    #     self.fax = ""  
    #     fax_set = set()        
    #     for fax in fax_list:
    #         str_fax = ""
    #         # 先删除所有英文字母和汉字
    #         for char in fax:
    #             if not char_is_alphabet(char) and not char_is_chinese(char):
    #                 str_fax += char          
    #         # 如果长度大于等于8那么是传真
    #         if len(str_fax) >= 8:
    #             fax_set.add(str_fax)            
    #     self.fax = ";".join(fax for fax in fax_set)








# def strangeSymbolReplace(s):
#     # 用英语字母替代德语
#     s = s.replace("ö","o").replace("ü","u").replace("Ö","o").replace("ï","i").replace("ä","a").replace("Å","a").replace("ó","o")
#     # 去掉韩语和日语 \uAC00-\uD7A3为匹配韩文的，其余为日文
#     s = re.sub(r'[\u3040-\u309F\u30A0-\u30FF\uAC00-\uD7A3]', '', s) 
#     # 用英语字母替代法语
#     s = replaceFrenchLetterWithEnglishLetter(s)
#     return s

# def delete_UNK(intro_list):
#     for intro in intro_list:
#         intro = intro.replace("[UNK]","")

# def delete_UNK_And_Symbol(str):
#     str = str.strip()
#     str = str.replace("[UNK]","")
#     return str


# def charTokenizerToBertTokenizer(intro_list,tag_list):
#     index = 0
#     tags = []    
#     for intro in intro_list:
#         tags.append(tag_list[index])
#         index += len(intro) 
#     return tags


# def replaceFrenchLetterWithEnglishLetter(s):
#     s = s.replace('é', 'e')
#     s = s.replace('à', 'a')
#     s = s.replace('è', 'e')
#     s = s.replace('ù', 'u')
#     s = s.replace('â', 's')
#     s = s.replace('ê', 'e')
#     s = s.replace('î', 'i')
#     s = s.replace('ô', 'o')
#     s = s.replace('û', 'u')
#     s = s.replace('ç', 'c')
#     return s

# def initTags(tokens,origin_tags):
#     tags = []
#     for i in range(len(tokens)):
#         for j in range(len(tokens[i])):
#             tags.append(origin_tags[i])
#     return tags

# # 将第一个列表中出现的[UNK] 替换为第二个字符串中得指定值,如果多个UNK连续出现
# def replaceUNK(intro_list,intro_str):
    # str_index = 0
    # list_index = 0
    # # 循环遍历列表中的所有值
    # while list_index < len(intro_list):
    #     current_token = intro_list[list_index] 
    #     # 如果当前token不是unk，那么就将str_index往前移，同时ist_index移到下一个
    #     if current_token != "[UNK]":
    #         str_index += len(current_token)            
    #         list_index += 1
    #     else:
    #         print(intro_list[list_index-1])
    #         # print(intro_list[list_index+1])
    #         print(intro_str[str_index:str_index+10])
           
    #         intro_list[list_index] = intro_str[str_index:str_index+1]
    #         str_index += 1
    #         list_index += 1
    # return intro_list,intro_str








# def mergeENAdjacentTag(introducation,tags,distance):
#     lastIndex = 0
#     lastTag = tags[0]
#     for i in range(len(tags)):
#         if tags[i] != "" and tags[i] == lastTag and i - lastIndex <= distance and i - lastIndex > 1:
#             for j in range(lastIndex+1,i):
#                 # 是中文或者英文字符才合并
#                 if char_is_chinese(introducation[j]) or char_is_alphabet(introducation[j]) or char_is_space(introducation[j]):
#                     # print("相邻合并",j)
#                     tags[j] = lastTag                  
#             lastIndex = i
#             lastTag = tags[i]
#         elif tags[i] != "":
#             lastIndex = i
#             lastTag = tags[i]
#     return tags
