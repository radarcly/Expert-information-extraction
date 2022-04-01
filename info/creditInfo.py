from info.utils import str_is_number
from info.utils import str_is_english
from info.utils import str_is_chinese
from info.utils import replaceMutiSpaceToOneSpace
from info.utils import deleteAllSpace
from info.utils import checkTime
from info.utils import reviseSymbolPair
from info.utils import reviseEnglishItem
from info.utils import revisePrefixAndSuffix
from info.utils import revise_credit_with_year
from info.utils import check_len_more_than_threshold
from info.utils import delete_wrong_result_with_list
from info.utils import delete_wrong_result_with_suffix_list
from info.utils import delete_year_credit
from info.utils import get_all_touxian_list
from info.utils import get_all_rongyu_list
from info.utils import get_credit_level_list
from info.utils import get_credit_grade_list
from info.utils import get_school_list
from info.utils import get_credit_org_list
from info.utils import get_credit_place_list
from info.utils import get_credit_place_map
from info.utils import get_all_country_map
from info.utils import get_credit_category_map
from info.utils import get_all_cn_province_map
from info.utils import get_all_cn_city_map
from info.utils import delete_str_begin_end_parentheses

class CreditInfo:
    def __init__(self):
        self.credit = ""
        self.year = ""
        self.level = ""
        self.org = ""
        self.place = ""
        self.category = ""
        self.endyear = ""
        self.grade = ""
        self.reason= ""
        self.content = ""
        self.type = ""     
        self.creditIndex = 0
        self.yearIndex = 0
        self.lastTagIndex = 0 
        

    def revise(self): 
        self.reviseCredit()
        self.reviseYear()
        self.reviseLevel()
        self.reviseOrg()
        self.revisePlace()
        self.reviseGrade()

    # 设置当前record最后出现的结束lastTagIndex，同时针对多值，如果是tag为year或者credit对应设置yearIndex或者creditIndex
    def setIndex(self,tag,value):
        self.lastTagIndex = value
        if tag == "year":
            self.yearIndex = value
        elif tag == "credit":
            self.creditIndex = value

    # 打印所有属性与属性值
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
    
    # 打印所有属性与属性值
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())
        
    def reviseCredit(self):
        # 英文删除去掉stopword只有单字词的荣誉名称
        if str_is_english(self.credit):
            self.credit = reviseEnglishItem(self.credit)


        self.credit = reviseSymbolPair(self.credit)
        self.credit = revisePrefixAndSuffix(self.credit,["年度","年获","年","度","获得","获"],["由"])
        self.credit,self.year = revise_credit_with_year(self.credit,self.year)
        self.credit = delete_str_begin_end_parentheses(self.credit)

        gradeList = get_credit_grade_list()
        shengMap = get_all_cn_province_map()        
        shiMap =  get_all_cn_city_map()
        guoList = get_all_country_map().keys()    
        touxianList = get_all_touxian_list()
        rongyuList = get_all_rongyu_list()
        levelList = get_credit_level_list()        
        categoryMap = get_credit_category_map()
        orgList = get_credit_org_list()
        
        place_list = get_credit_place_list()  
        place_map = get_credit_place_map()
        school_list = get_school_list()        
        # Todo
        # 1.被书名号包围得荣誉奖项删除
        # 2.博士后结尾但不含优秀删除
        # 3.部结尾但不含优秀删除
        # 4.诸如第一届，第6届删除
        # 5.开头第一个英语单词是of删除
        # 6.荣誉奖项等于人名删除
        # 7.修正以区结尾
        delete_list =  ["获校",
                        "秘书长","共产党员","委员会",                   
                        "医学","光学","哲学","科学","经济学","药理学","社会科学","化学","力学","物理学",
                        "国家","国际",
                        "The","荣誉","专家","二层次","计划","工程","学会","人员","大赛","学院","层次","大学生","荣誉","教学","荣誉称号","老师",
                        "奖共","教育部","优秀","人才","成果","教师","导师","学者","科技","班主任","个人","科学家","主席","基金","副会长","工作者","先进",
                        "研究","军队","年度","教授","青年","上海交大","技术","奖励","第二届","人选","院长","高校","成员",
                        "学年","工业","毕业生","科研","大奖","新世纪","副理事长","指导教师","分会","理事","常务理事",
                        "二级","三级","一级","高级","顶级","超级",
                        "进步","中华","大学","论文","委员","项目",
                        "科技部",
                        "（优秀）","(完成人)","(排名2)","（学科）学科","30位30",
                        "华东地区","上海地区","苏州工业园区",
                        "胰腺癌的生物","复星医药","生物医学仪器","海上来油平台","联轴器","浙江省化学","全国高等","带头人"
                        ]


        # 删除以地名为后缀的荣誉名
        self.credit = delete_wrong_result_with_suffix_list(self.credit,place_list)    
        
        # 删除以校名为后缀的荣誉名
        self.credit = delete_wrong_result_with_suffix_list(self.credit,school_list)  

        # 删除荣誉奖励等于年份的荣誉 1900-2050
        self.credit = delete_year_credit(self.credit)      


        # 删除以特定词为后缀的荣誉名
        self.credit = delete_wrong_result_with_suffix_list(self.credit,["市","国","省","分校","公司","所","院","系","局","县","镇","村"])
        # 局包括海洋局，卫生局，知识产权局，科技局，地震局，体育局，财政局，药监局等
        # 系包括了教育系，中文系等
        # 院包括了科学院，工程院，医学院，国务院等
        # 所包括了研究所，计算所，药物所，事务所等
        # 国包括了我国,全国,外国,回国,联合国,申银万国,世界强国等 国家在前面已被删除
        # 省包括了获省,年省,获部省,部省,全省,日本文部省等  省份在前面已被删除
        # 市包括了获市,城市,可变城市等 市在前面已被删除
        # 县,镇,村直接删除,
        #
        # 存在高等学校奖，校不能删，只能删一个分校
        # 大学

        # 删除只有等第的奖项名
        self.credit = delete_wrong_result_with_list(self.credit,gradeList)  
        
        # 删除只有级别的奖项名
        self.credit = delete_wrong_result_with_list(self.credit,levelList)  

        # 删除不合法的荣誉名
        self.credit = delete_wrong_result_with_list(self.credit,delete_list)
        
        # 补充荣誉等第
        for grade in gradeList:
            if grade in self.credit.lower():
                self.grade = grade
                break

        # 如果包含国家名就补充级别国家级，并且设置颁奖地点
        for guo in guoList:
            if guo in self.credit:
                self.level = "国家级"
                self.place = guo
                break

        # 如果包含省份名就补充级别省级，并且设置颁奖地点
        for key,value in shengMap.items():
            # 如果荣誉名称包含省级的全程或者简称
            if key in self.credit or value in self.credit:
                self.level = "省级"
                self.place = place_map[key]
                break
          
        # 如果包含市名就补充级别市级，并且设置颁奖地点      
        for key,value in shiMap.items():
            # 如果荣誉名称包含市级的全程或者简称
            if key in self.credit or value in self.credit:
                self.level = "市级"
                self.place = place_map[key]
                break
      
        # 如果包含学校名就补充级别校级，并且设置颁奖组织      
        for school in school_list:
            if school in self.credit:
                self.level = "校级"
                self.org = school
                break
        
        # 如果包含组织名就设置颁奖组织
        for org in orgList:
            if org in self.credit:
                self.org = org
                break
        
        # 如果包含荣誉字典就设置获奖类型荣誉
        for rongyu in rongyuList:
            if rongyu in self.credit:
                self.type = "荣誉"
                break
        
        # 如果包含头衔字典就设置获奖类型头衔
        for touxian in touxianList:
            if touxian in self.credit:
                self.type = "头衔"
                break

        # 补充获奖种类
        for key,value in categoryMap.items():
            if key in self.credit.lower():
                self.category = value
                break
        
        # 解决同一奖项名称不同（如国家科技进步奖、国家科技进步、项国家科技进步、中国国家科技进步等）
        if "国家科技进步" in self.credit:
            self.credit = "国家科技进步奖"
            self.level = "国家级"
        elif self.credit in ["151","151 人才工程","151人才"]:
            self.credit = "151人才工程"

        # 获奖名称长度应大于3
        self.credit = check_len_more_than_threshold(self.credit,3)


    def reviseYear(self):
        year_list = self.year.split(";") 
        self.year = ""  
        year_set = set()
        for year in year_list:
            year = year[0:4]
            if str_is_number(year) and int(year) > 1800 and int(year) < 2022:
                year_set.add(year + "年")  
        self.year = ";".join(year for year in year_set)

    def reviseLevel(self):
        map = {"家":"国家级","家级":"国家级","国家":"国家级","部":"部级","省":"省级","市":"市级","校":"校级","院":"院级"}
        levelList = get_credit_level_list()     
        if self.level in map.keys():
            self.level = map[self.level]
        if self.level not in levelList:
            self.level = ""
        # key为简称 value为全称 根据place调节二不正确的level
        shengMap = get_all_cn_province_map()
        shiMap = get_all_cn_city_map()
        if self.place in shengMap.values():
            self.level = "省级"
        if self.place in shiMap.values():
            self.level = "市级"

    def reviseOrg(self):
        # 加入所有省份全称
        transfer_list = get_credit_place_list()  
        transfer_map = get_credit_place_map()    

        delete_list = ["委员会","总公司","集团公司","研究所","出版社","最大制药公司"]
        # 因为只保留长度大于2的组织所以下面这些不需要再delete_dict中了
        # "国家","全国","工程","公路","管理","学院","大学","学会","协会","海事","技术","科技","公司","医院"
        
        self.org = reviseSymbolPair(self.org)
        self.org = revisePrefixAndSuffix(self.org)
        self.org = delete_str_begin_end_parentheses(self.org)
        
        # 在转移字典中则转移到place字段
        for place in transfer_list:
            if place == self.org:
                self.org = ""
                self.place = transfer_map[place]
                break
        
        # 中科院和中国科学院统一
        if self.org == "中科院":
            self.org = "中国科学院"

        # 在删除字典中则删除
        self.org = delete_wrong_result_with_list(self.org,delete_list)

        # 保留长度大于3的组织
        self.org = check_len_more_than_threshold(self.org,3)
        
    def revisePlace(self):
        # 得到所有可能授予地列表
        place_list = get_credit_place_list()      
        # 得到所有可能授予地字典
        place_map = get_credit_place_map()
        delete_list = ["国际","中共","国家","我国","全国","全国高校","中华"]
        transfer_list = ["国家海洋局","国家科技部","国家中医药管理局","国家教育部","国家自然科学基金","华中科技大学","上海交通大学","中共","教育部"
                               "中共中央组织部","中海","中航","中科","中科院","中欧国际工商学院","中央","中央研究院"]
        # retain_two_org_list = ["中国科学院","中国化学会","英国皇家学会","英国皇家","中国工程院","中国科协","中国船舶工业集团公司","中国教育部",
        #                        "中国计算机学会","中国农业科学院","中国人民大学","中国抗癌协会","中国物理学会","中国农科院","中国法学会",]

        # 第一种情况place不完全等于place_list中内容，说明还携带单位，此时移动到org，place设置为place_map中指定key的value值
        for place in place_list:
            # 如果place被self.place包含，且不等，那么就让self.org = self.place,self.place = place_map[place]
            # 一定要break
            if place in self.place and place != self.place:
                self.org = self.place
                self.place = place_map[place]
                break
            # 如果place被self.place包含，且相等，也要break
            elif place in self.place:
                self.place = place_map[place]
                break
        
        # 第二种情况place在转移字典中，则移至org中
        for place in transfer_list:
            if place == self.place:
                self.org = self.place
                self.place = ""
        
        self.place = delete_wrong_result_with_list(self.place,delete_list)
        # 长度小于2删除
        self.place = check_len_more_than_threshold(self.place,2)

    def reviseGrade(self):
        self.grade = reviseSymbolPair(self.grade)
        grade_list = get_credit_grade_list()
        # 由于的严格的符规性检查，deleteList实际没用
        # deleteList = ["#NAME?","荣誉称号","等奖","荣誉","省部级","排名","优异","支持","指导","至尊","中级","最高级别","引奖","特级","厅级","一金"
        #               "省级奖","市级奖","三篇之一","三？等奖"]
        # 先删除中文中所有空格
        if str_is_chinese(self.grade):
            self.grade = deleteAllSpace(self.grade)
            # 再将1,2,3转变为一,二,三
            self.grade = self.grade.replace("1","一")
            self.grade = self.grade.replace("壹","一")
            self.grade = self.grade.replace("2","二")
            self.grade = self.grade.replace("贰","二")            
            self.grade = self.grade.replace("3","三")
            self.grade = self.grade.replace("叁","三")          
            self.grade = self.grade.replace("4","四")
            self.grade = self.grade.replace("肆","四")
            self.grade = self.grade.replace("獎","奖")           
            # 再将一等，二等，三等修改为一等奖，二等奖，三等奖
            if self.grade in ["一等","二等","三等","四等"]:
                self.grade = self.grade + "奖"
            # 最后做严格的符规性检查
            if self.grade.lower() not in grade_list:
                self.grade = ""
           


