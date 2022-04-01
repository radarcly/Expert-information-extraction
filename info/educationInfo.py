from info.utils import str_is_number
from info.utils import checkTime
from info.utils import str_is_english
from info.utils import str_is_chinese
from info.utils import char_is_chinese
from info.utils import char_is_alphabet
from info.utils import reviseSymbolPair
from info.utils import get_last_index
from info.utils import str_without_alphabet
from info.utils import split_org_to_cn_and_en
from info.utils import delete_str_begin_number_and_symbol
from info.utils import delete_str_begin_end_parentheses
from info.utils import delete_str_begin_chinese
from info.utils import delete_str_end_chinese
class EducationInfo:
    def __init__(self):
        self.org = ""
        self.startyear = ""
        self.endyear = ""
        self.department = ""
        self.major = ""
        self.education = ""
        self.degree = ""      
        self.orgIndex = 0
        self.degreeIndex = 0 
        self.endyearIndex = 0  
        self.lastTagIndex = 0    
        self.cn_org = ""
        self.en_org = ""
         

    def revise(self): 
        self.reviseOrg()
        self.reviseStartYear()
        self.reviseEndYear()
        self.reviseDepartment()
        self.reviseMajor()
        self.reviseDegree()
        self.reviseEducation()

     # 打印所有属性与属性值
   
    def setIndex(self,tag,value):
        self.lastTagIndex = value
        if tag == "org":
            self.orgIndex = value
        elif tag == "degree":
            self.degreeIndex = value
        elif tag ==  "endyear":
            self.endyearIndex = value
    
    # 打印所有属性与属性值
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
    
    # 打印所有属性与属性值
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())

    def reviseOrg(self):
        self.org = reviseSymbolPair(self.org)
        # 不含字母则删除所有空格
        if str_without_alphabet(self.org):
            self.org = "".join(self.org.split())
        
                
        # 删除被包裹着的括号
        self.org = delete_str_begin_end_parentheses(self.org) 

        delete_prefix_dict = ["年获",",","-","及","与",".","&","'",",","/","获","，","an","and","edu",":","：","于","和","年","赴","现","原"]
        delete_suffix_dict = ["和",",","-","与","及",";"]
        delete_dict = ["University","China","Department","of","Michigan","Columbia","California","in","math","USA","Florida","B.","B. Sc.","Bachlor",
                       "学院","大学","安徽","安徽省","巴黎","办学","北京","上海","日本","合肥"]
        degree_dict = ["博士","硕士","学士","Bachelor"]
        education_dict = ["本科","大专","专科","中专","本科生","研究生","高中"]
        
        # 将学位和学历加入删除前缀字典，可能是上一条学历/学位
        delete_prefix_dict.extend(degree_dict)
        delete_prefix_dict.extend(education_dict)

        transfer_major_dict = ["Economics","Electrical Engineering","Mechanical","Technology","Electrical","Engineering","Mathematics"]
        
        # 解决ner组织错误
        if self.org.endswith(" 科"):
            self.org = self.org[:-2]
        
        # 解决识别出教授，中文分词导致
        if "教授" in self.org:
            self.org = ""
        
        # 删除指定前缀
        for prefix in delete_prefix_dict:
            if self.org.startswith(prefix):
                self.org = self.org[len(prefix):]
                break
        
        # 删除指定后缀
        for suffix in delete_suffix_dict:
            if self.org.endswith(suffix):
                self.org = self.org[:-len(suffix)]
                break

        # 删除不合法输出
        for delete in delete_dict:
            if self.org.startswith(delete):
                self.org = ""
                break
        
        # 删除仅包含major
        for major in transfer_major_dict:
            if self.org == major:
                self.major = major
                self.org = ""
                break
        
        # 末尾学位转移
        for degree in degree_dict:
            if self.org.endswith(degree):
                self.degree = degree
                self.org = self.org[:-len(degree)]
                break
        
        # 末尾学历转移
        for education in education_dict:
            if self.org.endswith(education):
                self.education = education
                self.org = self.org[:-len(education)]
                break

        # 删除开头所有非英文字母和汉字
        self.org = delete_str_begin_number_and_symbol(self.org)

        # 拆分学校和院系
        index = get_last_index(self.org,["分校","大学","公司","医院","大學","研究院","科学院","中科院","海洋局"])
        if index != -1 and index < len(self.org) and char_is_chinese(self.org[index]):
            self.department = self.org[index:]
            self.org = self.org[:index]

        # 处理完的教育经历组织如果仍包含博士 硕士 学士 本科则大概率把两条预测成一条放进org中则直接删除 
        delect_include_dict = ["博士","硕士","学士","本科"]
        for delect_include_str in delect_include_dict:
            if delect_include_str in self.org:
                self.org = ""

        self.cn_org,self.en_org = split_org_to_cn_and_en(self.org)

        # 将中科院统一为中国科学院
        if self.cn_org == "中科院":
            self.cn_org = "中国科学院"
        elif len(self.cn_org) < 3:
            self.cn_org = ""
        
        # 将英文机构前的中文删掉
        self.en_org =  delete_str_begin_chinese(self.en_org)
        self.en_org =  delete_str_end_chinese(self.en_org)      

    def reviseStartYear(self):
        if len(self.startyear) < 4:
            self.startyear = ""
        elif str_is_number(self.startyear[0:4]):
            year = self.startyear[0:4]
            if  2018 > int(year) > 1800:
                 self.startyear = year + "年"
            else:
                self.startyear = ""
        else:
            self.startyear = ""

    def reviseEndYear(self):
        if len(self.endyear) < 4:
            self.endyear = ""
        elif str_is_number(self.endyear[0:4]):
            year = self.endyear[0:4]
            if  2021 > int(year) > 1800:
                self.endyear = year + "年"
            else:
                self.endyear = ""
        else:
            self.endyear = ""
        # 最后一个参数为interval参数表明结束年份至少比开始年份大于等于1
        self.endyear = checkTime(self.startyear,self.endyear,1)
        
    def reviseDepartment(self):
        self.department = reviseSymbolPair(self.department)
        delete_prefix_dict = ["大学","和","及","与",",","、",". ",".","18","11","77","81","and","of","& "]
        delete_suffix_dict = ["和","及","与","大学","大学本科","of","获","专业学习","，","，工学"]
        delete_dict = ["学院","大学","二系","大学院","大学本科","北京航空航天","八系","北京","本部","本科","部本","毕业","School of",
                       "附属中学","7年制","基地","学院","S.","School o","前身","MS","附属医学院","联合","联合培养","前身","前身之一"
                       "专业","师范","师资","本硕连","办公室","学习","比较"]      

        for prefix in delete_prefix_dict:
            if self.department.startswith(prefix):
                self.department = self.department[len(prefix):]
                break
        
        for suffix in delete_suffix_dict:
            if self.department.endswith(suffix):
                self.department = self.department[:-len(suffix)]
                break
        
        # 删除包括的括号
        self.department = delete_str_begin_end_parentheses(self.department) 

        if self.department in delete_dict:
            self.department = "" 

        if len(self.department) == 1:
            self.department = ""
        
        # 院系通常应该以院/系结尾，如果以专业二字结尾那么移动到major中
        if self.department.endswith("专业"):
            self.major = self.department
            self.department = ""

    
    def reviseMajor(self):
        self.major = reviseSymbolPair(self.major)
        delete_prefix_dict = ["获","和","及","与","）",",","、","/",".S."]
        delete_suffix_dict = ["和","及","与"]
        degree_dict = ["博士","硕士","学士"]
        education_dict = ["本科","大专","专科","中专"]
        delete_dict = ["专业","4.0","in","major","巴基斯坦",]
        
        for prefix in delete_prefix_dict:
            if self.major.startswith(prefix):
                self.major = self.major[1:]
                break
        
        for suffix in delete_suffix_dict:
            if self.major.endswith(suffix):
                self.major = self.major[:-1]
                break

         # 删除包括的括号
        self.major = delete_str_begin_end_parentheses(self.major) 

        for degree in degree_dict:
            if degree in self.major:
                self.degree = degree
                self.major = self.major.replace(degree,"")
                break

        for education in education_dict:
            if education in self.major:
                self.education = education
                self.major = self.major.replace(education,"")
                break

        if self.major in delete_dict:
            self.major = ""

        if len(self.major) == 1:
            self.major = ""
    
    def reviseDegree(self):
        degree_list = self.degree.split(";")
        degree_set = set()
        for degree in degree_list:
            if not str_is_english(degree):
                if degree[0:2] in ["学士","硕士","博士"]:
                    degree_set.add(self.degree[0:2])
        self.degree =  ";".join(degree for degree in degree_set)
    
    def reviseEducation(self):
        education_list = self.education.split(";") 
        education_set = set()
        for education in education_list:     
            if education == "研究" or education == "究生":    #                   
                education_set.add("研究生")
            if education == "本科毕业":
                education_set.add("本科")
            if education in ["本科生","本科","研究生","专科","中专","大专"]:
                education_set.add(education)            
        self.education = ";".join(education for education in education_set)

    # def reviseOrgAndDepartAndTitle(self):  
    #     org = self.org
    #     org = org.strip()
    #     if len(org) > 0:
    #         if "中国科学院" in org and org[-5:] !="中国科学院" and self.depart == "":
    #             org = "中国科学院"
    #             self.depart = org[ org.find("中国科学院") + 5 : -1]
    #         else:
    #             index = get_last_index(org,["分校","大学","公司","医院","大學","研究院"])
    #             if index != -1 and index < len(org) and self.depart == "" and org[index]!="(":
    #                 self.department = org[index:]
    #                 org = org[:index]            
    #     self.org = org