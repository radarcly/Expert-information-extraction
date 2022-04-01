from info.utils import reviseTime
from info.utils import checkTime
from info.utils import reviseSymbolPair
from info.utils import get_last_index
from info.utils import str_is_chinese
from info.utils import char_is_chinese
from info.utils import str_without_alphabet
from info.utils import revisePrefixAndSuffix
from info.utils import split_org_to_cn_and_en
from info.utils import delete_str_begin_number_and_symbol
from info.utils import delete_str_begin_end_parentheses
from info.utils import delete_str_begin_chinese
from info.utils import delete_str_end_chinese
from info.utils import delete_str_end_number_and_symbol
class WorkInfo:
    def __init__(self):     
        self.org = ""
        self.title = ""
        self.post = ""
        self.starttime = ""
        self.endtime = ""
        self.depart = ""
        self.technology = ""      
        self.content = ""
        self.cn_org = ""
        self.en_org = ""  
        self.orgIndex = 0
        self.departIndex = 0
        self.postIndex = 0
        self.lastTagIndex = 0    

    def revise(self): 
        self.reviseOrg()
        self.reviseOrgAndDepartAndTitle()     
        self.reviseTitle()
        self.revisePost()
        self.reviseStartTime()
        self.reviseEndTime()
        self.reviseDepart()
        self.reviseTechnology()
        self.reviseContent()   
     
    
    def setIndex(self,tag,value):
        self.lastTagIndex = value
        if tag == "org":
            self.orgIndex = value
        elif tag == "depart":
            self.departIndex = value
        elif tag == "post":
            self.postIndex = value


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
        if self.org.endswith(" 科"):
            self.org = self.org[:-2]
    
    def reviseTitle(self):
        # 修正title
        title_dict = ["教授级高级工程师","教授级高工","研究员级高级工程师","教授特许工程师"
                      "二级教授","副教授","特聘教授","特任教授","首席教授",
                      "终身正教授","终身教授","客座教授","助理教授","名誉教授","兼职教授","讲座教授","讲习教授","教授",
                      "青年副研究员","副研究员","助理研究员","高级研究员","首席研究员","特聘研究员","实习研究员","青年研究员","特别研究员","资深研究员","研究员",
                      "副主任医师","主任医师","主治医师","主管医师","住院医师","医师",
                      "副主任法医师","主任法医师","法医师",
                      "副主任中医师","主任中医师","中医师",
                      "副主任护师","主任护师","护师",
                      "副主任药师","主任药师","药师",
                      "正高级工程师","高级工程师","中级工程师","副总工程师","总工程师","首席工程师","工程师",
                      "高级技师","副主任技师","主任技师","技师",
                      "正高级会计师","高级会计师","助理会计师","会计师","会计员"
                      "正高级实验师","高级实验师","助理实验师","实验师","实验员",                
                      "高级讲师","助理讲师","讲师",
                      "高级教师","一级教师","二级教师","三级教师","教师","教员",
                      "经济师",
                      "国家二级心理咨询师","心理咨询师",
                      "二级鉴定官"
                      ]
        # delete_dict = ["工作人员","中化","访问学者","助教","硕导","老师","雅思老师","辅导员"]
        split_dict = ["，","/","和","、"]
        for element in split_dict:
            self.title = self.title.replace(element,";")
        title_list =  self.title.split(";") 
        self.title = ""  
        title_set = set()
        for title in title_list:
            title = title.strip()
            # 删除中文职称中的空格
            if str_is_chinese(title):
                title.replace(" ","")
            for title_regular in title_dict:
                if title.find(title_regular) != -1:
                    title_set.add(title_regular)
                    break
        self.title = ";".join(title for title in title_set)
    
    def revisePost(self):
        delete_dict = ["访问","支教","筹备","德语","处理","创始","创新","德语","低功耗射频发射机研发设计","妇科","附属","高等","曙光学者","核心",
                       "参访","参赞","产品","办公室","北京","病区","初级","大肠","大学生","注册","实验室","计算机科学","钱德拉","人员","家禽",
                       "港湾","百人","百人计划"
                       "14任校长","45纳米工艺","5年资讯科科长","91年级班主任","Graduate School","in","of","post","Vice","Post","In"]  
        
        post_list = self.post.split(";") 
        self.post = ""  
        post_set = set()
        for post in post_list:
            # 先去掉两边空白
            post = post.strip()
            # 再对齐symbol
            post = reviseSymbolPair(post)
            # 再去掉乱七八糟的前缀和后转
            post = revisePrefixAndSuffix(post,["做","作","部","处","室","问","组"]) 
            # 再删去包裹着的括号
            post = delete_str_begin_end_parentheses(post)
            # 删去末尾数字和符号
            post = delete_str_end_number_and_symbol(post)
            if str_is_chinese(post):
                post = "".join(post.split())
            if len(post) > 1 and post not in delete_dict:
                post_set.add(post) 
        self.post = ";".join(post for post in post_set)
        
    def reviseStartTime(self):
        self.starttime =reviseTime(self.starttime)
        pass
    
    def reviseEndTime(self):
        self.endtime = reviseTime(self.endtime)
        self.endtime = checkTime(self.starttime,self.endtime)
        pass

    def reviseDepart(self):
        depart_list = self.depart.split(";") 
        self.depart = ""  
        depart_set = set()
        for depart in depart_list:
            # 先去掉两边空白
            depart = depart.strip()
            # 再对齐symbol
            depart = reviseSymbolPair(depart)
            # 再去掉乱七八糟的前缀和后转
            depart = revisePrefixAndSuffix(depart)
            if len(depart) > 2:
                depart_set.add(depart) 
        self.depart = ";".join(depart for depart in depart_set)

    def reviseTechnology(self):
        # 先去掉两边空白
        self.technology = self.technology.strip()
        # 再对齐symbol
        self.technology = reviseSymbolPair(self.technology)
        # 再去掉乱七八糟的前缀和后转
        self.technology = revisePrefixAndSuffix(self.technology)
        if len(self.technology) < 3:
            self.technology = ""
       

    def reviseContent(self):
        # 先去掉两边空白
        self.content = self.content.strip()
        # 再对齐symbol
        self.content = reviseSymbolPair(self.content)
        # 再去掉乱七八糟的前缀和后转
        self.content = revisePrefixAndSuffix(self.content)
        if len(self.content) < 5:
            self.content = ""


    def reviseOrgAndDepartAndTitle(self):  
        org = self.org        
        org = org.strip()
        org = reviseSymbolPair(org)
        org = revisePrefixAndSuffix(org)
        # 不含字母则删除所有空格
        if str_without_alphabet(org):
            self.org = "".join(org.split())
        if len(org) > 0:
            # 处理分词错误造成大学教授
            if org[-2:] == "教授":
                org = org[:-2]
                self.title = "教授"         
            else:
                index = get_last_index(org,["分校","大学","公司","医院","大學","研究院","科学院","中科院","海洋局"])
                if index != -1 and index < len(org) and char_is_chinese(org[index]):
                    self.depart = org[index:]
                    org = org[:index]                      
        
        # 针对id 8526332800 Research Associate被预测包含在depart里面
        if "Research Associate" in self.depart:
            self.depart.replace("Research Associate","")
            self.title = "Research Associate" 
       
        delete_dict = ["University","China","Department","of","Michigan","Columbia","California","in","math","USA","Florida","B.","B. Sc.","Bachlor"
                       "学院","大学","安徽","安徽省","巴黎","办学","北京","上海","日本","合肥"]
        
        # 删除不合法输出
        for delete in delete_dict:
            if org.startswith(delete):
                org = ""
                break

        self.cn_org,self.en_org = split_org_to_cn_and_en(self.org)

        # 将中科院统一为中国科学院
        if self.cn_org == "中科院":
            self.cn_org = "中国科学院"
        elif len(self.cn_org) < 2:
            self.cn_org = ""
        
        # 将英文机构前的中文删掉
        self.en_org =  delete_str_begin_chinese(self.en_org)
        self.en_org =  delete_str_end_chinese(self.en_org)    