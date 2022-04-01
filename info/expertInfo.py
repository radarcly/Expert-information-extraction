from info.basicInfo import BasicInfo
from info.creditInfo import CreditInfo
from info.educationInfo import EducationInfo
from info.workInfo import WorkInfo
from info.utils import get_element
from info.utils import checkFullStopInTokens
from info.utils import str_is_number
class ExpertInfo:
    def __init__(self,key,langauge,origin_introducation,introducation,cnTheSameRecordDistance):     
        self.workInfos = []
        self.educationInfos = []
        self.creditInfos = []
        self.basicInfo = BasicInfo()
        
        
        self.credit_cols =  ['credit', 'year', 'level', 'org', 'place', 'category', 'endYear', 'grade', 'reason', 'content']
        self.basic_cols = ['name', 'org', 'year', 'month', 'day', 'nationality', 'interest', 'major', 'title', 'post',
                'depart', 'sex', 'nation', 'nativePlace', 'address', 'code', 'phone', 'telephone', 'fax', 'mail','website']
        self.work_cols =  ['org', 'title', 'post', 'startTime', 'endTime',
                  'technology', 'content','depart']
        self.education_cols = ['org', 'startYear', 'endYear', 'department', 'major', 'education', 'degree']
        self.langauge = langauge
        self.origin_introducation = origin_introducation
        self.introducation = introducation
        self.cnTheSameRecordDistance = cnTheSameRecordDistance
        self.key = key
        self.number = 0

    # 打印所有属性与属性值
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
    
    # 打印所有属性与属性值
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())

    # 解码算法    
    def decoder(self,tokens,tags):
        
        self.decoderBasic(tokens,tags)
        
        self.decoderCredit(tokens,tags)
        
        self.decoderWork(tokens,tags)
        
        self.decoderEducation(tokens,tags)

        # 处理教育经历多值，主要指的是毕业年份和学位的多值
        self.reviseEduMutipleValue()

        # 将教育经历里学位预测为博士后的更改至工作经历中
        self.reviseEduToWork()

        # 处理获奖经历多值，主要指的是获奖年份多值和所获奖项多值
        self.reviseCreMutipleValue()


        # self.revise()                

    # 修正算法
    def revise(self,expert):        
        self.basicInfo.revise(expert,self.introducation)

        workInfos = []
        creditInfos = []
        educationInfos = []
        education_endyear_list = []
        education_degree_list = []

        for workInfo in self.workInfos:            
            # 对每个经历做revise
            workInfo.revise()     
            # 如果revise后组织名大于1 符合保存
            if len(workInfo.cn_org) > 2 or len(workInfo.en_org) > 2:
                workInfos.append(workInfo)        
        self.workInfos = workInfos

        for creditInfo in self.creditInfos:            
            # 对每个经历做revise
            creditInfo.revise()     
            # 如果revise后荣誉名大于1 符合保存
            if len(creditInfo.credit) > 1:
                creditInfos.append(creditInfo)        
        self.creditInfos = creditInfos     

        for educationInfo in self.educationInfos:            
            # 对每个经历做revise
            educationInfo.revise()     
            # 如果revise后组织名大于1 并且结束时间没有出现过符合保存            
            if (len(educationInfo.cn_org) > 1 or len(educationInfo.en_org) > 2) and educationInfo.endyear not in education_endyear_list:
                educationInfos.append(educationInfo) 
                if educationInfo.endyear != "":
                    education_endyear_list.append(educationInfo.endyear)
        self.educationInfos = educationInfos     

               
        # # 民族招回率检查
        # if "汉族" in self.introducation and self.basicInfo.nation == "":
        #     print(self.basicInfo.id,self.introducation)

        # 国籍召回率检查
        # if "国籍" in self.introducation and self.basicInfo.nationality == "":
        #     print(self.basicInfo.id,self.introducation)

        # 籍贯召回率检查
        # if "籍贯" in self.introducation and self.basicInfo.nativePlace == "":
        #     print(self.basicInfo.id,self.introducation)  

        # 研究方向召回率检查
        # if self.basicInfo.interest == "":
        #     if "研究方向" in self.introducation or "研究领域" in self.introducation:
        #         print(self.basicInfo.id,self.introducation)
            
        # 学科领域召回率检查
        # if self.basicInfo.major == "":
        #     if "学科" in self.introducation or "专业" in self.introducation:
        #         print(self.basicInfo.id,self.introducation)

        # # 邮箱召回率检查
        # if self.basicInfo.mail == "":
        #     if "mail" in self.introducation:
        #         print(self.basicInfo.id,self.introducation)

        # 地址召回率检查
        # if self.basicInfo.address == "":
        #     if "地址" in self.introducation:
        #         print(self.basicInfo.id,self.introducation)
       
    # 基本信息解码
    def decoderBasic(self,tokens,tags):        
        expert = {}
        # 设置好id 和简介
        expert["ID"] = self.key
        expert["INTRODUCTION"] = self.origin_introducation
        # 每个值默认为空字符串
        for basic_col in self.basic_cols:
            expert[basic_col.upper()] = ""
        i = 0 
        # 第一遍循环解析basic 信息
        while i < len(tokens):
            if tags[i] in expert.keys():
                element,tag,i = get_element(tokens, tags, i, tags[i])
                expert[tag] = element if expert[tag] == "" else expert[tag] + ";" + element
            else:
                i = i + 1      
        # 填写basic信息，将字典类型的expert数据存入basicInfo对象中
        self.basicInfo.decoder(expert)

        # if "国籍" in self.introducation and self.basicInfo.nationality == "":
        #     print(self.basicInfo.id,self.introducation)

    # 荣誉信息解码
    def decoderCredit(self,tokens,tags):
        self.credit_cols = self.cols_upper_with_prefix(self.credit_cols,"CRE-")
        i = 0
        # print(self.credit_cols)
        while i < len(tokens):
            if tags[i] in self.credit_cols:
                begin_index = i
                element,tag,i = get_element(tokens, tags, i, tags[i])
                # 第一种情况当前还没有荣誉经历,那么直接new一个并添加相关信息就好
                if len(self.creditInfos) == 0:
                    creditInfo = CreditInfo()        
                    setattr(creditInfo,tag[4:].lower(),element)
                    # 设置yearIndex,creditIndex和lastTagIndex                                        
                    creditInfo.setIndex(tag[4:].lower(),i)                                      
                    self.creditInfos.append(creditInfo)
                # 第二种情况,介绍为中文，并且当前起始标签相比上一个结束标签距离超过15
                elif self.langauge == "chinese" and begin_index - self.creditInfos[-1].lastTagIndex > self.cnTheSameRecordDistance:
                    creditInfo = CreditInfo()        
                    setattr(creditInfo,tag[4:].lower(),element)
                    # 设置yearIndex,creditIndex和lastTagIndex                                             
                    creditInfo.setIndex(tag[4:].lower(),i)                                      
                    self.creditInfos.append(creditInfo)
                # 第三种情况当前有荣誉经历,且指定值为空，那么直接设置值就好
                elif getattr(self.creditInfos[-1],tag[4:].lower()) == "":
                    setattr(self.creditInfos[-1],tag[4:].lower(),element)
                    # 设置yearIndex,creditIndex和lastTagIndex          
                    self.creditInfos[-1].setIndex(tag[4:].lower(),i)  
                # 第四种情况当前有荣誉经历，且指定值不为空，就要区分这个是当前条目还是下一条
                # 默认遇到非获奖时间以及所获奖项的情况下都是下一条           
                elif tag[4:].lower() not in ["year","credit"]:
                    creditInfo = CreditInfo()        
                    setattr(creditInfo,tag[4:].lower(),element)
                    creditInfo.setIndex(tag[4:].lower(),i)                 
                    self.creditInfos.append(creditInfo)    
                    self.creditInfos[-1].setIndex(tag[4:].lower(),i)  
                # 年份多值 要求年份之间没有句号 且距离小于3 且荣誉没有多值
                # todo 暂时不考虑年份和荣誉同时多值
                elif tag[4:].lower() == "year" and begin_index - self.creditInfos[-1].yearIndex <= 3 and ";" not in self.creditInfos[-1].credit and not checkFullStopInTokens(tokens,self.creditInfos[-1].yearIndex,begin_index):
                    setattr(self.creditInfos[-1],"year",self.creditInfos[-1].year+";"+element) 
                    creditInfo.setIndex(tag[4:].lower(),i)  
                # 荣誉多值 如果上一个荣誉index的末尾和当前荣誉的起始点距离小于等于3就认为是荣誉多值 且年份没有多值
                elif tag[4:].lower() == "credit" and begin_index - self.creditInfos[-1].creditIndex <= 3 and ";" not in self.creditInfos[-1].year and not checkFullStopInTokens(tokens,self.creditInfos[-1].yearIndex,begin_index):
                    setattr(self.creditInfos[-1],"credit",self.creditInfos[-1].credit+";"+element)                    
                    creditInfo.setIndex(tag[4:].lower(),i)      
                # 其他情况,新加入一条获奖信息                    
                else:
                    creditInfo = CreditInfo()        
                    setattr(creditInfo,tag[4:].lower(),element) 
                    creditInfo.setIndex(tag[4:].lower(),i)         
                    self.creditInfos.append(creditInfo)
            else:
                i = i + 1       
        # for creditInfo in self.creditInfos:
        #     print(creditInfo)

    # 工作经历解码
    def decoderWork(self,tokens,tags):
        self.work_cols = self.cols_upper_with_prefix(self.work_cols,"WORK-")
        i = 0
        while i < len(tokens):
            if tags[i] in self.work_cols:
                begin_index = i
                element,tag,i = get_element(tokens, tags, i, tags[i])
                # 第一种情况当前还没有工作经历,那么直接new一个并添加相关信息就好
                if len(self.workInfos) == 0:
                    workInfo = WorkInfo()        
                    setattr(workInfo,tag[5:].lower(),element)
                    # 设置index                                      
                    workInfo.setIndex(tag[5:].lower(),i)                                      
                    self.workInfos.append(workInfo)
                # 第二种情况，当介绍为中文，并且当前起始标签相比上一个结束标签距离超过15
                elif self.langauge == "chinese" and begin_index - self.workInfos[-1].lastTagIndex > self.cnTheSameRecordDistance:
                    workInfo = WorkInfo()        
                    setattr(workInfo,tag[5:].lower(),element)
                    # 设置index                                      
                    workInfo.setIndex(tag[5:].lower(),i)                                      
                    self.workInfos.append(workInfo)
                # 第三种情况当前有工作经历,且指定值为空，那么直接设置值就好
                elif getattr(self.workInfos[-1],tag[5:].lower()) == "":
                    setattr(self.workInfos[-1],tag[5:].lower(),element)
                    # 设置index为                                         
                    self.workInfos[-1].setIndex(tag[5:].lower(),i)  
                # 第四种情况当前有工作经历，且指定值不为空，就要区分这个是当前条目还是下一条
                # 默认遇到非部门，职务的情况下都是下一条           
                elif tag[5:].lower() != "depart" and tag[5:].lower() != "post":
                    workInfo = WorkInfo()        
                    setattr(workInfo,tag[5:].lower(),element) 
                    # 设置index  
                    workInfo.setIndex(tag[5:].lower(),i)         
                    self.workInfos.append(workInfo)
                # 最后如果是部门，职务，那么就要判断是当前条的部门，职务，还是下一条的部门职务，
                # 看上一条部门职务标注的更靠近，还是组织注更靠近，如果是部门职务更靠近，就代表还是上一条，如果组织更靠近就是下一条
                # 部门更靠近，那么还是这条，分号分隔
                elif tag[5:].lower() == "depart" and self.workInfos[-1].departIndex > self.workInfos[-1].orgIndex:
                    setattr(self.workInfos[-1],"depart",self.workInfos[-1].depart+";"+element) 
                    workInfo.setIndex(tag[5:].lower(),i)     
                # 职务更靠近，那么还是这条，分号分隔
                elif tag[5:].lower() == "post" and self.workInfos[-1].postIndex > self.workInfos[-1].orgIndex:
                    setattr(self.workInfos[-1],"post",self.workInfos[-1].post+";"+element) 
                    workInfo.setIndex(tag[5:].lower(),i)     
                else: 
                    workInfo = WorkInfo()        
                    setattr(workInfo,tag[5:].lower(),element) 
                    workInfo.setIndex(tag[5:].lower(),i)         
                    self.workInfos.append(workInfo)
            else:
                i = i + 1       
        # for workInfo in self.workInfos:
        #     print(workInfo)
        
    # 教育经历解码
    def decoderEducation(self,tokens,tags):
        self.education_cols = self.cols_upper_with_prefix(self.education_cols,"EDU-")
        i = 0
        while i < len(tokens):
            if tags[i] in self.education_cols:
                begin_index = i
                element,tag,i = get_element(tokens, tags, i, tags[i])
                # 第一种情况当前还没有教育经历,那么直接new一个并添加相关信息就好
                if len(self.educationInfos) == 0:
                    educationInfo = EducationInfo()        
                    setattr(educationInfo,tag[4:].lower(),element)
                    # 设置index为了第四种情况                                         
                    educationInfo.setIndex(tag[4:].lower(),i)                                      
                    self.educationInfos.append(educationInfo)
                # 第二种情况，当介绍为中文，并且当前起始标签相比上一个结束标签距离超过15
                elif self.langauge == "chinese" and begin_index - self.educationInfos[-1].lastTagIndex > self.cnTheSameRecordDistance:
                    educationInfo = EducationInfo()        
                    setattr(educationInfo,tag[4:].lower(),element)
                    # 设置index为了第四种情况                                         
                    educationInfo.setIndex(tag[4:].lower(),i)                                      
                    self.educationInfos.append(educationInfo)
                # 第三种情况当前有教育经历,且指定值为空，
                elif getattr(self.educationInfos[-1],tag[4:].lower()) == "":                    
                    setattr(self.educationInfos[-1],tag[4:].lower(),element)
                    # 设置index                                      
                    self.educationInfos[-1].setIndex(tag[4:].lower(),i)  
                # 第四种情况当前有教育经历，且指定值不为空，就要区分这个是当前条目还是下一条
                # 默认遇到非学位和毕业年份的情况下都是下一条           
                elif tag[4:].lower() not in ["endyear","degree"]:
                    educationInfo = EducationInfo()        
                    setattr(educationInfo,tag[4:].lower(),element) 
                    # 设置index    
                    educationInfo.setIndex(tag[4:].lower(),i)         
                    self.educationInfos.append(educationInfo)
                # 最后如果是学位和毕业年份，那么就要判断是当前条的学历，还是下一条的学历，
                # 毕业年份多值的情况
                elif tag[4:].lower() == "endyear" and begin_index - self.educationInfos[-1].endyearIndex <= 3:
                    setattr(self.educationInfos[-1],"endyear",self.educationInfos[-1].endyear+";"+element) 
                    educationInfo.setIndex(tag[4:].lower(),i)    
                # 学位多值
                elif tag[4:].lower() == "degree" and begin_index - self.educationInfos[-1].degreeIndex <= 3:
                    setattr(self.educationInfos[-1],"degree",self.educationInfos[-1].degree+";"+element) 
                    educationInfo.setIndex(tag[4:].lower(),i)    
                else: 
                    #下一条
                    educationInfo = EducationInfo()        
                    setattr(educationInfo,tag[4:].lower(),element) 
                    # 设置index况    
                    educationInfo.setIndex(tag[4:].lower(),i)         
                    self.educationInfos.append(educationInfo)
            else:
                i = i + 1       
        # for educationInfo in self.educationInfos:
        #     print(educationInfo)

    # 调整教育经历多值，主要指学位多值和毕业年份多值
    def reviseEduMutipleValue(self):
        new_educationInfos = []
        for educationInfo in self.educationInfos:
            # educationInfo = educationInfos[i]
            # 第一种情况只有学位多值
            if ";" in educationInfo.degree and ";" not in educationInfo.endyear:            
                degree_list = educationInfo.degree.split(";")
                # 先设置当前学位为第一个分号前信息
                educationInfo.degree = degree_list[0]
                degree_list = degree_list[1:]
                # 对于除开第一个学位其他所有学位信息
                for degree in degree_list:
                    new_educationInfo = EducationInfo()        
                    setattr(new_educationInfo,"degree",degree)
                    setattr(new_educationInfo,"org",educationInfo.org)
                    new_educationInfos.append(new_educationInfo)
            elif ";" in educationInfo.degree and ";" in educationInfo.endyear:
                degree_list = educationInfo.degree.split(";")
                endyear_list = educationInfo.endyear.split(";")
                # 先设置当前学位为第一个分号前信息
                educationInfo.degree = degree_list[0]
                educationInfo.endyear = endyear_list[0]
                # 对于除开第一个学位其他所有学位信息
                degree_list = degree_list[1:]
                endyear_list = endyear_list[1:]
                for i in range(len(degree_list)):
                    new_educationInfo = EducationInfo()     
                    setattr(new_educationInfo,"degree",degree_list[i])
                    if i < len(endyear_list):   
                        setattr(new_educationInfo,"endyear", endyear_list[i])
                    setattr(new_educationInfo,"org",educationInfo.org)
                    new_educationInfos.append(new_educationInfo)
        self.educationInfos.extend(new_educationInfos)       
    

        # 调整教育经历多值，主要指学位多值和毕业年份多值
    
    # 调整获奖经历多值
    def reviseCreMutipleValue(self):
        # print("正在调整获奖经历多值")
        new_creditInfos = []
        for creditInfo in self.creditInfos:
            # print(creditInfo)
            # 奖项多值
            if ";" in creditInfo.credit:            
                credit_list = creditInfo.credit .split(";")
                # 先设置当前奖项为第一个分号前信息
                creditInfo.credit = credit_list[0]
                credit_list = credit_list[1:]
                # 对于除开第一个奖项其他所有奖项信息
                for credit in credit_list:
                    new_creditInfo = CreditInfo()        
                    setattr(new_creditInfo,"credit",credit)
                    setattr(new_creditInfo,"year",creditInfo.year)
                    # setattr(new_creditInfo,"place",creditInfo.place)
                    new_creditInfos.append(new_creditInfo)
            # 年份多值
            elif ";" in creditInfo.year:
                # print("here",creditInfo.year)
                year_list = creditInfo.year.split(";")
                # print(year_list)
                # 先设置当前年份为第一个分号前信息
                creditInfo.year = year_list[0]
                # 对于除开第一个年份其他所有年份位信息
                year_list = year_list[1:]
                for year in year_list:
                    year = year[0:4]
                    if str_is_number(year) and int(year) > 1800 and int(year) < 2022:
                        new_creditInfo = CreditInfo()        
                        setattr(new_creditInfo,"credit",creditInfo.credit)
                        setattr(new_creditInfo,"year",year)
                        new_creditInfos.append(new_creditInfo)           
        self.creditInfos.extend(new_creditInfos)       

    # 调整教育,将学位为博士后的移至工作经历
    def reviseEduToWork(self):
        for educationInfo in self.educationInfos:
            if educationInfo.degree == "博士后":                
                workInfo = WorkInfo()     
                setattr(workInfo,"org",educationInfo.org)
                setattr(workInfo,"post",educationInfo.degree)
                # 在工作经历中加入这条工作
                self.workInfos.append(workInfo)
                # 同时设置此条信息的组织为空，这样在revise的时候会自动将这条记录删除
                educationInfo.org = ""

    def cols_upper_with_prefix(self,cols,prefix):
        for i in range(len(cols)):
            cols[i] = prefix + cols[i].upper()
        return cols