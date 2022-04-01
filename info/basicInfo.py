from info.utils import str_is_number,char_is_number
from info.utils import str_is_english
from info.utils import str_is_chinese
from info.utils import str_is_number
from info.utils import str_without_alphabet
from info.utils import replaceMutiSpaceToOneSpace
from info.utils import deleteAllSpace
from info.utils import get_last_index
from info.utils import char_is_alphabet
from info.utils import char_is_chinese
from info.utils import char_is_number
from info.utils import reviseSymbolPair
from info.utils import revisePrefixAndSuffix
from info.utils import get_all_major_list
from info.utils import get_all_title_list
from info.utils import get_all_title_list_with_priorty
from info.utils import get_all_post_list
from info.utils import delete_str_end_alphabet
from info.utils import delete_str_begin_alphabet
from info.utils import delete_str_begin_chinese
from info.utils import delete_str_end_chinese
from info.utils import check_str_prefix_with_list
from info.utils import reviseCNBracketsToEN
from info.utils import replace_str_with_list
from info.utils import get_all_country_map
from info.utils import get_delete_native_place_list
from info.utils import get_native_place_list
from info.utils import get_native_place_introducation_str
from info.utils import split_org_to_cn_and_en
from info.utils import delete_str_begin_end_parentheses
from cocoNLP.extractor import extractor


import re
class BasicInfo:
    def __init__(self,id,name,org,year,month,day,nationality,interest,major,title,post,
                 depart,sex,nation,nativePlace,address,code,phone,telephone,fax,mail,website
                ):
        self.id = id
        self.name = name
        self.org = org
        self.year = year
        self.month = month
        self.day = day
        self.nationality =nationality
        self.interest = interest
        self.major = major
        self.title = title
        self.post = post
        self.depart = depart
        self.sex = sex
        self.nation = nation 
        self.nativePlace = nativePlace
        self.address = address
        self.code = code
        self.phone = phone
        self.telephone = telephone
        self.fax = fax 
        self.mail = mail
        self.website = website
        self.cname = ""
        self.ename = ""
        self.corganization = ""
        self.eorganization = ""
    
    def __init__(self):
        self.id = ""
        self.name = ""
        self.org = ""
        self.year = ""
        self.month = "" 
        self.day = ""
        self.nationality = ""
        self.interest = ""
        self.major = ""
        self.title = ""
        self.post = ""
        self.depart = ""
        self.sex = ""
        self.nation = ""
        self.nativePlace = ""
        self.address = ""
        self.code = ""
        self.phone = ""
        self.telephone = ""
        self.fax = "" 
        self.mail = ""
        self.website = ""
        self.introduction = ""
        self.cname = ""
        self.ename = ""
        self.corganization = ""
        self.eorganization = ""
    
    def decoder(self,expert):
        self.id = expert["ID"]
        self.name = expert["NAME"]
        self.org = expert["ORG"]
        self.year = expert["YEAR"]
        self.month = expert["MONTH"]
        self.day = expert["DAY"]
        self.nationality = expert["NATIONALITY"]
        self.interest = expert["INTEREST"]
        self.major = expert["MAJOR"]
        self.title = expert["TITLE"]
        self.post = expert["POST"]
        self.depart = expert["DEPART"]
        self.sex = expert["SEX"]
        self.nation = expert["NATION"]
        self.nativePlace = expert["NATIVEPLACE"]
        self.address = expert["ADDRESS"]
        self.code = expert["CODE"]
        self.phone = expert["PHONE"]
        self.telephone = expert["TELEPHONE"]
        self.fax = expert["FAX"]
        self.mail = expert["MAIL"]
        self.website = expert["WEBSITE"]
        self.introduction = expert["INTRODUCTION"]

    # 打印所有属性与属性值
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
    
    # 打印所有属性与属性值
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())
    
    # 对象转字典需要
    def keys(self):
        return ('id', 'name','org','year','month','day','nationality','interest','major','title','post',
                'depart','sex','nation','nativePlace','address','code','phone','telephone','fax','mail','website','introduction' )

    # 对象转字典需要
    def __getitem__(self, item):
        return getattr(self, item)

    def revise(self,expert,introducation):
        self.reviseName(expert['姓名'])        
        self.reviseOrg(expert['机构'])
        self.reviseDepart()
        # 职称和职务一起revise
        self.reviseTitleAndPost()
        # 研究兴趣和学科领域一起revise
        self.reviseMajorAndInterest()  
       
        self.reviseBirthYear()
        self.reviseBirthMonth()
        self.reviseBirthDay()
        self.reviseNation()
        self.reviseSex()
        self.reviseWebsite()
        self.reviseIntroduction()
        # 修正籍贯
        self.reviseNativePlace()
        # 补充一些模型没预测出来的籍贯
        self.addNativePlace(introducation)

        # 修正邮箱
        self.reviseMail()
        # 利用工具补充一些模型没预测出来的邮箱
        self.addMail(introducation)
        
        # 修正国籍
        self.reviseNationality()
        # 补充一些模型没预测出来的国籍
        self.addNationality(introducation)
        
        self.reviseCode()     
        self.revisePhoneAndFax()
        self.reviseAddress()
      
    def reviseName(self,name):
        # name_list = self.name.split(";") 
        # 如果有识别出名字就取识别出的名字，否则取原来的
        # name = name_list[0] if name_list[0] != "" else name  
        # name = reviseSymbolPair(name)
        name = name  
        if name != "" and str_is_english(name):
            self.ename = name 
        else:            
            self.cname = "".join(name.split())  

    def reviseOrg(self,dataset_org):
        # delete_dict = ["学院","浙江","分校","医院"]
        include_delete_dict = ["《","会士","院士","导师"]
        include_transfer_dict = ["副院长","副主任","院长","主任"]
        org_list = self.org.split(";") 
        # 提取有问题,比如提取里面有书名号,提取机构名过短 采用自带的机构名
        # if len(org_list[0]) < 3 or (not char_is_chinese(org_list[0][0])) or "《" in self.org:
        #     org_list = [org]     
        cn_org_set = set()
        en_org_set = set()
        for org in org_list:
            org = reviseSymbolPair(org)  
            org = revisePrefixAndSuffix(org,[],[" 科"])            
            # 不含字母则删除所有空格
            if str_without_alphabet(org):
                org = deleteAllSpace(org)

            # 把分词错误的大学教授移到title中
            if org[-2:] == "教授":
                org = org[:-2]
                self.title += ";教授"

            for include_transfer in include_transfer_dict:
                if include_transfer in org:
                    org = org.replace(include_transfer,"")
                    self.post += ";" + org
            

            # 包含书名号删除
            for include_delete in include_delete_dict:
                if include_delete in org:
                    org = ""        

            # 删掉包括的空格
            org = delete_str_begin_end_parentheses(org)
            # 划分成中文和英文
            cn_org,en_org = split_org_to_cn_and_en(org)

            # 拆分组织和部分
            index = get_last_index(cn_org,["分校","大学","公司","医院","大學","研究院","科学院","中科院","海洋局","研究所","研究中心","植物园"])
            if index != -1 and index < len(cn_org) and char_is_chinese(cn_org[index]):
                self.depart += ";" + cn_org[index:]
                cn_org = cn_org[:index]

            en_org_set.add(en_org)

            # 中文组织长度必须大于2
            if len(cn_org) > 2:
                cn_org_set.add(cn_org)

        if len(en_org_set) == 0 and len(cn_org_set) == 0 :
            if str_is_chinese(dataset_org):
                cn_org_set.add(dataset_org)
            else:
                en_org_set.add(dataset_org)

        # 解决部分添加空白
        cn_org_set.discard("")
        en_org_set.discard("")
        self.eorganization = ";".join(org for org in en_org_set)       
        self.corganization = ";".join(org for org in cn_org_set)
   
    def reviseDepart(self):
        depart_list =  self.depart.split(";") 
        self.depart = ""  
        depart_set = set()
        for depart in depart_list:  
            delete_dict = ["学院","学系","程系","国际","学报","出版社","党委","校","Professor","办公室","系主任"]

            transfer_org_dict = []
            transfer_post_dict = ["主任","院长"]
            post_dict = ["硕导","硕士生导师","博导","博士生导师"]


            depart = reviseSymbolPair(depart)
            depart = revisePrefixAndSuffix(depart)

            # 如果部门以主任或者院长结尾 删除最后两个字 移动到职务(可能是中文分词导致)
            if depart.endswith("主任") or depart.endswith("院长"):
                self.post = self.post + ";" + depart
                depart = depart[:-2]

            for post in post_dict:
                if post in depart:
                    self.post = self.post + ";" + post
                    depart = depart.replace(post,"")

            if len(depart) > 2 and depart not in delete_dict:
                depart_set.add(depart) 
        self.depart = ";".join(depart for depart in depart_set) 

    def reviseBirthYear(self):
        # 出生年份长度大于4取前四
        if len(self.year) > 4:
            self.year = self.year[0:4]
        # 出生年份长度小于4不要了
        elif len(self.year) < 4:
            self.year = ""
        # 检查四位出生年份是否都是数字，是则保留
        if not str_is_number(self.year):
            self.year = ""
        # 出生年份不为空的情况下检查他是否在1800-2010之间
        if self.year != "":
            if int(self.year) < 1800 or int(self.year) > 2010:
                self.year = ""

    def reviseBirthMonth(self):
        # 多值只取第一个
        if self.month.find(";") != -1:
            self.month = self.month[0: self.month.find(";")]
        # 出生月份汉字一到十二转换为数字
        cnMonthtransfer = {"一":"1","二":"2","三":"3","四":"4","五":"5","六":"6",
                           "七":"7","八":"8","九":"9","十":"10","十一":"11","十二":"12"}
        if self.month in cnMonthtransfer.keys():
            self.month = cnMonthtransfer[self.month]
    
        # 检查出生月份每一位，不是数字删掉，之所以只删除非数字位是因为会出现2~这样的预测结果
        result = ""
        for letter in self.month:
            if char_is_number(letter):
                result += letter
        self.month = result
    
        # 删除月份为0的情况 并且将01-09转为1-9
        if self.month.startswith("0"):
            self.month = self.month[1:]
       
    def reviseBirthDay(self):
        # 多值只取第一个
        if self.day.find(";") != -1:
            self.day = self.day[0: self.day.find(";")]
      
        # 删除月份为0的情况 并且将01-09转为1-9
        if self.day.startswith("0"):
            self.day = self.day[1:]
        
        # 检查出生日期每一位是否是数字，有不是数字删掉，防止出现 类似四月初 四月中 四月底这样的预测结果
        for letter in self.day:
            if not char_is_number(letter):
                self.day = ""
  
    # 修正民族
    def reviseNation(self):
        if len(self.nation) > 0:
            # 多值只取第一个
            nation = self.nation.split(";")[0]
            # 去掉空格 
            nation = "".join(nation.split())
            self.nation = ""
            # 如果首字是族，删掉首字
            if nation.startswith("族"):
                nation = nation[1:]
            # 单字如果不是汉删掉
            if len(nation) == 1 and nation != "汉":
                nation = ""
            elif nation in ["汉","汉族人","中国汉族人","中国汉族"]:
                nation = "汉族"
            if len(nation) > 1:
                self.nation = nation
    
    # 修正性别
    def reviseSex(self):
        # 多值只取第一个
        if self.sex.find(";") != -1:
            self.sex = self.sex[0:self.sex.find(";")]
        # 只在给定值有效
        if self.sex.strip() not in ["男","女","male","female"]:
            self.sex  = "" 

    # 修正个人主页
    def reviseWebsite(self):
        website_list = self.website.split(";")
        self.website = ""
        website_set = set()
        for website in website_list:
            index_http = website.find("http")
            # 如果包含http 则将http之前内容删除
            if index_http != -1:
                website = website[index_http:]
            # 如果以冒号开头 加上http
            elif website.startswith(":") or website.startswith("："):
                website = "https" + website
            # 如果以横线开头也加上http
            elif website.startswith("/"):
                website = "https:" + website            
            # 如果以下列开头都代表预测少了东西，直接删掉
            elif website.startswith(".com") or website.startswith(".edu") or website.startswith(".net") or website.startswith(".ca"):
                website = ""     
            # 如果以点开头加上www
            elif website.startswith("."):
                website = "www" + website   
            elif website.startswith("："):
                website = website[1:]
            # 如果以点收尾则清空
            if website.endswith("."):
                website = ""
            # 网页长度至少大于等于12 且包含两个点 且不包含邮箱服啊后
            if len(website) >= 12  and website.count(".") >= 2 and website.find("@") == -1:
                website_set.add(website)
        self.website = ";".join(website for website in website_set)

    # 修正个人介绍
    def reviseIntroduction(self):
        endIndex = self.introduction.rfind('<')
        if endIndex != -1:
            self.introduction = self.introduction[0:endIndex-1]

   
    # 修正籍贯
    def reviseNativePlace(self):
        # 获得所有需要删掉的籍贯预测 （属于国外地点）
        delete_list = get_delete_native_place_list()
        # 获得世界上所有国家的名字
        all_country_list = get_all_country_map().keys()     
        if len(self.nativePlace) > 0: 
            # 多值只取第一个
            nativePlace = self.nativePlace.split(";")[0] 
            # 删掉空白
            nativePlace = deleteAllSpace(nativePlace)
            nativePlace = reviseSymbolPair(nativePlace)
            self.nativePlace = ""
            if str_is_english(nativePlace):
                nativePlace = ""
            else:
                # 去掉空格
                nativePlace = " ".join(nativePlace.split())
                # 去掉最后一个"人"字和"籍"字 如 江苏南京人 上海籍
                if nativePlace[-1] == "人":
                    nativePlace = nativePlace[0:-1]
                if nativePlace[-1] == "籍":
                    nativePlace = nativePlace[0:-1]
            # 如果籍贯等于中国两字则清空 否则如果籍贯以中国开头只取之后字符串
            if nativePlace == "中国":
                nativePlace = ""
            elif nativePlace.startswith("中国"):
                nativePlace = nativePlace[2:]
            # 如果籍贯以外国名字开头 则直接删掉
            else:
                for country_name in all_country_list:
                    if nativePlace.startswith(country_name):
                        nativePlace = ""
            # 保留长度大于1 且不在删除列表中的籍贯
            if len(nativePlace) > 1 and nativePlace not in delete_list :         
                self.nativePlace = nativePlace         
    
    # 补充一些模型没预测出来的籍贯
    def addNativePlace(self,introducation):
        nativePlace_list = get_native_place_list()
        # 如果籍贯为空并且简介中含有籍贯时
        if self.nativePlace == "" and introducation.find("籍贯") != -1:
            index = introducation.find("籍贯") + 2
            # 找到籍贯之后的第一个中文
            introducation = get_native_place_introducation_str(introducation,index)
            # 遍历nativePlace列表看有没有以之开头的，如果有 补充 break
            for nativePlace in nativePlace_list:
                if introducation.startswith(nativePlace):
                    self.nativePlace = nativePlace
                    break

    # 修正邮箱
    def reviseMail(self):        
        mail_list =  self.mail.split(";") 
        mail_set = set()
        for mail in mail_list:
            mail = mail.strip()
            if mail.startswith("-mail"):
                mail = mail[5:]
            pattern = r'^[a-zA-Z0-9_-]+@[a-zA-Z0-9_-]+(\.[a-zA-Z0-9_-]+)+$' 
            if len(mail) > 10 and re.match(pattern,mail) is not None:            
                mail_set.add(mail) 
        self.mail = ";".join(mail for mail in mail_set)

    # 补充一些模型没预测出的国籍 介绍含有mail或者邮箱
    def addMail(self,introducation):
        ex = extractor()
        if self.mail == "" and "mail" in introducation:
            index = introducation.find("mail")
            if index + 4 < len(introducation):
                introducation = introducation[index + 4:]
                while introducation !="" and introducation[0] in [":","："]:
                    introducation = introducation[1:]
                mails = ex.extract_email(introducation)
                self.mail = ";".join(mails)
        
        if self.mail == "" and "邮箱" in introducation:
            index = introducation.find("邮箱")
            if index + 2 < len(introducation):
                introducation = introducation[index + 2:]
                while introducation !="" and introducation[0] in [":","："]:
                    introducation = introducation[1:]
                mails = ex.extract_email(introducation)
                self.mail = ";".join(mails)

    # 修正国籍/所在国
    def reviseNationality(self):
        transfer_nationality_map = {}
        transfer_nationality_map["美国纽约"] = "美国"
        transfer_nationality_map["英国伦敦"] = "英国"
        transfer_nationality_map["瑞典)是瑞典"] = "瑞典"
        transfer_nationality_map["美国瑞士"] = "美国;瑞士"
        transfer_nationality_map["瑞士法国"] = "法国;瑞士"
        transfer_nationality_map["德国奥地利"] = "德国;奥地利"
        transfer_nationality_map["英美"] = "美国;英国" 
        transfer_nationality_map["墨西哥城"] = "墨西哥" 
        transfer_nationality_map["拉丁美洲"] = ""
        transfer_nationality_map["苏烈"] = ""
        transfer_nationality_map["俄国"] = ""
        
        
        # 得到所有国家的字典，key是中文名，value是英文名
        nationality_map = get_all_country_map()
        if "中华人民共和国" in self.nationality:
            self.nationality = "中国"
        # 把和替换成分号 这个会对中华人民共和国造成副作用
        self.nationality = self.nationality.replace("和",";")
        self.nationality = self.nationality.replace(" ",";")
        nationality_list = self.nationality.split(";") 
        nationality_set = set()

        for nationality in nationality_list:
            nationality = nationality.strip()
            # 如果以华人结尾删掉结尾华人，如果以人结尾删掉结尾的人
            if nationality.endswith("华人"):
                nationality = nationality[:-2]
            elif nationality.endswith("人"):
                nationality = nationality[:-1]

            # 如果国籍中出现 的 裔 这两个字取其后面 优先级 的大于裔 因为 e.g "奥地利裔的美国"
            # 不能if else 只能两个if 因为 e.g. 出生于苏格兰的英国裔的美国物理学家
            if "的" in nationality:
                nationality = nationality[nationality.find("的")+1:]
            if "裔" in nationality:
                # 不能以 裔 结尾，如果结尾直接删掉国籍 因为 e.g 美裔
                if nationality[-1] != "裔":
                    nationality = nationality[nationality.find("裔")+1:]
                else:
                    nationality = ""

            # 如果国籍为美籍 则直接变为美国
            if nationality == "美籍":
                nationality = "美国"   
            # 否则如果国籍最后两位为国籍不要最后两位 e.g 美国国籍
            elif nationality.endswith("国籍"):
                nationality = nationality[:-2]     
            # 否则如果国籍最后一位为籍不要最后一位 e.g 美国籍
            elif nationality.endswith("籍"):
                nationality = nationality[:-1]
            # 否则国籍中还是包含籍，则说明此人双国籍 把nationality清空 直接往nationality_set中添加e.g 美籍英国
            elif "籍" in nationality:
                ll = nationality.split("籍")
                nationality = ""
                for e in ll:
                    if e == "美":
                        nationality_set.add("美国") 
                    else:
                        nationality_set.add(e) 

            
            # 不包含台湾，模型预测结果可能有台湾，也可能中国台湾，检测然后直接中国            
            if "台湾" in nationality:
                nationality = "中国"
            # 如果是英文 通过nationality_map转换为中文
            elif nationality in nationality_map.values():
                nationality = [k for k,v in nationality_map.items() if v == nationality]
            elif nationality in transfer_nationality_map.keys():
                nationality = transfer_nationality_map[nationality]
    
            if len(nationality) > 1:
                nationality_set.add(nationality) 
        self.nationality = ";".join(nationality for nationality in nationality_set)

    # 补充一些模型没预测出的国籍
    def addNationality(self,introducation):
        nationality_map = {}
        nationality_map["中国国籍"] = "中国"
        nationality_map["美国国籍"] = "美国"
        nationality_map["英国国籍"] = "英国"
        nationality_map["法国国籍"] = "法国"
        nationality_map["德国国籍"] = "德国"
        nationality_map["中国籍"] = "中国"
        nationality_map["美国籍"] = "美国"
        nationality_map["英国籍"] = "英国"
        nationality_map["法国籍"] = "法国"
        nationality_map["德国籍"] = "德国"
        nationality_map["国籍 中国"] = "中国"
        nationality_map[" 国籍：中国"] = "中国"
        if self.nationality == "":
            for key,value in nationality_map.items():
                if key in introducation:
                    self.nationality = value
                    break

    # 研究兴趣和学科领域一起修正
    def reviseMajorAndInterest(self):
        interest_list = self.interest.split(";") 
        major_list = self.major.split(";")
        interest_set = set()
        major_set = set()
        all_major_list = get_all_major_list()
        for interest in interest_list:
            interest = revisePrefixAndSuffix(interest,["Research Interests)","Interests)","研究方向","研究了","研究","方向","兴趣","以及"],["家"])

            # 如果interst在学科领域列表中，学科领域字典中加入
            if interest in all_major_list:
                major_set.add(interest)
            elif len(interest) >  2:
                interest_set.add(interest) 

        for major in major_list:
            # 后缀删除列表加一个家           
            major = revisePrefixAndSuffix(major,[],["家"])
            if str_is_chinese(major) and len(major) > 6:
               interest_set.add(major)
            elif str_is_chinese(major):
                if major in all_major_list:
                    major_set.add(major)
            else:
                major_set.add(major)          

        self.interest = ";".join(interest for interest in interest_set)
        self.major =  ";".join(major for major in major_set)
    
    # 职称和职务一起修正
    def reviseTitleAndPost(self):
        # title post一起处理
        all_title_list = get_all_title_list()
        all_title_list_with_priorty = get_all_title_list_with_priorty()
        all_post_list = get_all_post_list()
        # 因为title是严格的符规性检查因而不需要delete_dict 
        # title_delete_dict = ["工作人员","中化","访问学者","助教","硕导","老师","雅思老师","辅导员"]
        post_delete_dict = ["博士后","博士生","硕士生","本科生","访问学者","博士","硕士",
                            "法学博士后","上海","上海市","行政","科研","内科","技术","管理","学院","研发","长聘","编辑","材料","大学","实验",
                            "骨科","软件工程","急诊科","外科","委员会","中国","浙江省","长陆","中药","执行","主诊","成员","创新","大师","该所","国际",
                            "化学家","教授","火箭","结构","金融","科室","斯特林","团队","问题","协会","学会","学科","研究室","遗传","应用","中科院",
                            "肿瘤科","重点","战略","肿瘤科","口腔科","中心","现场","全国","天文","天文台","体育部","睡眠",
                            "长江学者","院士","江青年学者","上海市曙光学者","计算机科学","人员","港湾","家禽","钱德拉","巴特利","百人计划","病区",
                            "初级","电信","电子","二级","法学","分析","科技部"                
                           ]
        title_split_dict = [",","，","/","、","和","及","与"]
        #由于一些部门名可能存在和,及,与 因而post的split_dict要少
        post_split_dict = [",","，","/","、"]
        # 第一步替换分号
        for element in title_split_dict:
            self.title = self.title.replace(element,";")
        for element in post_split_dict:
            self.post = self.post.replace(element,";")
        self.title = revisePrefixAndSuffix(self.title,[";"])
        self.post = revisePrefixAndSuffix(self.post,[";"])
        title_list =  self.title.split(";") 
        post_list = self.post.split(";")    
        title_set = set()
        post_set = set()
        # 第二步修正title
        for title in title_list:
            flag = False
            title = reviseSymbolPair(title)
            title = revisePrefixAndSuffix(title)
            # 删除中文职称中的空格
            if str_without_alphabet(title):
                title = deleteAllSpace(title)
            for title_regular in all_title_list:
                if title.find(title_regular) != -1:
                    title_set.add(title_regular)
                    flag = True
                    break
            # 如果没有成功加入到职称中，那么转而投入职务的怀抱
            if flag == False:
                # 删除包裹着的括号
                title = delete_str_begin_end_parentheses(title)
                if len(title) > 0 and title[0] == "《" and title[-1]=="》":
                    title = ""
                if title not in post_delete_dict and len(title) > 1:
                    post_set.add(title)

        # 第三步修正post
        for post in post_list: 
            flag = False           
            post = reviseSymbolPair(post)
            post = revisePrefixAndSuffix(post)
            # 删除中文职称中的空格
            if str_without_alphabet(post):
                post = deleteAllSpace(post)
            for title_regular in all_title_list:
                if post.find(title_regular) != -1:
                    title_set.add(title_regular)
                    flag = True
                    break
            # 如果没有成功加入到职称中，那么转而投入职务的怀抱
            if flag == False:
                # 删除包裹着的括号
                post = delete_str_begin_end_parentheses(post)
                # 如果被书名号包裹就删除
                if len(post) > 0 and post[0] == "《" and post[-1]=="》":
                    post = ""
                if post not in post_delete_dict and len(post) > 1:
                    post_set.add(post)

        # 对于title_set中的所有title利用 all_title_list_with_priority进行修正
        for title_sequence in all_title_list_with_priorty:
            for i in range(len(title_sequence)):
                # 如果找到那么删掉所有低优先级职称
                if title_sequence[i] in title_set:
                    # 在集合操作中remove不存在的元素会报错 discard不会
                    for j in range(i + 1,len(title_sequence)):
                        title_set.discard(title_sequence[j])
                    break
            
        self.title = ";".join(title for title in title_set)
        self.post = ";".join(post for post in post_set)

    # 手机、电话、传真一起修正
    def revisePhoneAndFax(self):
        self.phone = replace_str_with_list(self.phone,[",","，","、","/","或","和","；","&"],";")
        self.fax = replace_str_with_list(self.fax,[",","，","、","/","或","和","；","&"],";")      
        
        phone_list = self.phone.split(";") 
        fax_list = self.fax.split(";")
        
        phone_set = set()
        telephone_set = set()
        fax_set = set()
        
        for phone in phone_list:
            phone = reviseSymbolPair(phone)
            phone = phone.strip("-")
            phone = phone.replace("+","")
            phone = phone.replace("＋","")
            phone = delete_str_end_alphabet(phone)
            phone = delete_str_begin_alphabet(phone)
            phone = delete_str_begin_chinese(phone)
            phone = delete_str_end_chinese(phone)
            phone = phone.strip()
            phone = reviseCNBracketsToEN(phone)

            # 如果字符串全是数字并且长度正好11位，并且以13 14 15 17 18 19开头，那么认为预测的是手机号码 
            if len(phone) == 11 and str_is_number(phone) and check_str_prefix_with_list(phone,check_list=["13","14","15","17","18","19"]):
                telephone_set.add(phone)
            # elif phone.startswith("021"):
            #     phone_set.add(phone)
            # 如果长度大于等于8那么是电话号码
            elif len(phone) >= 8 :
                phone_set.add(phone)       
        
        for fax in fax_list:
            fax = reviseSymbolPair(fax)
            fax = fax.strip("-")
            fax = fax.replace("+","")
            fax = fax.replace("＋","")
            fax = delete_str_end_alphabet(fax)
            fax = delete_str_begin_alphabet(fax)
            fax = delete_str_begin_chinese(fax)
            fax = delete_str_end_chinese(fax)
            fax = fax.strip()
            fax = reviseCNBracketsToEN(fax)

            if len(fax) == 11 and str_is_number(fax) and check_str_prefix_with_list(fax,check_list=["13","14","15","17","18","19"]):
                telephone_set.add(fax)
            # elif fax.startswith("021"):
            #     fax_set.add(fax)
            elif len(fax) >= 8 :
                fax_set.add(fax) 
        
        self.fax = ";".join(fax for fax in fax_set)     
        self.phone = ";".join(phone for phone in phone_set)
        self.telephone = ";".join(telephone for telephone in telephone_set)

    # 修正邮政编码
    def reviseCode(self):
        if len(self.code) > 0: 
            code = self.code.split(";")[0]
            # 删除末尾字母
            code = delete_str_end_alphabet(code)
            # 剩下清空长度不为6 说明预测错了，直接清空
            if len(code) != 6 :
                code = "" 
            # 检查是否6位都为数字，是保留否删除
            if (not str_is_number(code)) or (code in ["013396","023506","992548","993122"]):
                code = ""
            self.code = code 

    # 修正地址
    def reviseAddress(self):
        address_list =  self.address.split(";") 
        self.address = ""  
        address_set = set()
        for address in address_list:
            # 删除空格
            address = deleteAllSpace(address)
            addresss = revisePrefixAndSuffix(address)
            address = reviseSymbolPair(address)        
            # #开头的不要了
            if address.startswith("#"):
                address = ""
            #  数字开头也不要了
            if len(address) > 0 and char_is_number(address[0]):
                address = ""
            #  奇奇怪怪开头也不要了
            if len(address) > 0 and address[0] in ["楼"]:
                address = ""
            if len(address) > 5:
                address_set.add(address)
        self.address = ";".join(address for address in address_set)

    # 合并出生年月日得到出生日期
    def getBirthDate(self):
        if self.year != "" and self.month != "" and self.day != "":
            return self.year + "年" + self.month + "月" + self.day + "日"
        elif self.year != "" and self.month != "":
            return self.year + "年" + self.month + "月"
        elif self.year != "":
            return self.year + "年"
        else:
            return ""

   

