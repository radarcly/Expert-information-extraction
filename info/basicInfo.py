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

    # ??????????????????????????????
    def gatherAttrs(self):
        return ",".join("{}={}"
                        .format(k, getattr(self, k))
                        for k in self.__dict__.keys())
    
    # ??????????????????????????????
    def __str__(self):
        return "[{}:{}]".format(self.__class__.__name__, self.gatherAttrs())
    
    # ?????????????????????
    def keys(self):
        return ('id', 'name','org','year','month','day','nationality','interest','major','title','post',
                'depart','sex','nation','nativePlace','address','code','phone','telephone','fax','mail','website','introduction' )

    # ?????????????????????
    def __getitem__(self, item):
        return getattr(self, item)

    def revise(self,expert,introducation):
        self.reviseName(expert['??????'])        
        self.reviseOrg(expert['??????'])
        self.reviseDepart()
        # ?????????????????????revise
        self.reviseTitleAndPost()
        # ?????????????????????????????????revise
        self.reviseMajorAndInterest()  
       
        self.reviseBirthYear()
        self.reviseBirthMonth()
        self.reviseBirthDay()
        self.reviseNation()
        self.reviseSex()
        self.reviseWebsite()
        self.reviseIntroduction()
        # ????????????
        self.reviseNativePlace()
        # ??????????????????????????????????????????
        self.addNativePlace(introducation)

        # ????????????
        self.reviseMail()
        # ??????????????????????????????????????????????????????
        self.addMail(introducation)
        
        # ????????????
        self.reviseNationality()
        # ??????????????????????????????????????????
        self.addNationality(introducation)
        
        self.reviseCode()     
        self.revisePhoneAndFax()
        self.reviseAddress()
      
    def reviseName(self,name):
        # name_list = self.name.split(";") 
        # ?????????????????????????????????????????????????????????????????????
        # name = name_list[0] if name_list[0] != "" else name  
        # name = reviseSymbolPair(name)
        name = name  
        if name != "" and str_is_english(name):
            self.ename = name 
        else:            
            self.cname = "".join(name.split())  

    def reviseOrg(self,dataset_org):
        # delete_dict = ["??????","??????","??????","??????"]
        include_delete_dict = ["???","??????","??????","??????"]
        include_transfer_dict = ["?????????","?????????","??????","??????"]
        org_list = self.org.split(";") 
        # ???????????????,??????????????????????????????,????????????????????? ????????????????????????
        # if len(org_list[0]) < 3 or (not char_is_chinese(org_list[0][0])) or "???" in self.org:
        #     org_list = [org]     
        cn_org_set = set()
        en_org_set = set()
        for org in org_list:
            org = reviseSymbolPair(org)  
            org = revisePrefixAndSuffix(org,[],[" ???"])            
            # ?????????????????????????????????
            if str_without_alphabet(org):
                org = deleteAllSpace(org)

            # ????????????????????????????????????title???
            if org[-2:] == "??????":
                org = org[:-2]
                self.title += ";??????"

            for include_transfer in include_transfer_dict:
                if include_transfer in org:
                    org = org.replace(include_transfer,"")
                    self.post += ";" + org
            

            # ?????????????????????
            for include_delete in include_delete_dict:
                if include_delete in org:
                    org = ""        

            # ?????????????????????
            org = delete_str_begin_end_parentheses(org)
            # ????????????????????????
            cn_org,en_org = split_org_to_cn_and_en(org)

            # ?????????????????????
            index = get_last_index(cn_org,["??????","??????","??????","??????","??????","?????????","?????????","?????????","?????????","?????????","????????????","?????????"])
            if index != -1 and index < len(cn_org) and char_is_chinese(cn_org[index]):
                self.depart += ";" + cn_org[index:]
                cn_org = cn_org[:index]

            en_org_set.add(en_org)

            # ??????????????????????????????2
            if len(cn_org) > 2:
                cn_org_set.add(cn_org)

        if len(en_org_set) == 0 and len(cn_org_set) == 0 :
            if str_is_chinese(dataset_org):
                cn_org_set.add(dataset_org)
            else:
                en_org_set.add(dataset_org)

        # ????????????????????????
        cn_org_set.discard("")
        en_org_set.discard("")
        self.eorganization = ";".join(org for org in en_org_set)       
        self.corganization = ";".join(org for org in cn_org_set)
   
    def reviseDepart(self):
        depart_list =  self.depart.split(";") 
        self.depart = ""  
        depart_set = set()
        for depart in depart_list:  
            delete_dict = ["??????","??????","??????","??????","??????","?????????","??????","???","Professor","?????????","?????????"]

            transfer_org_dict = []
            transfer_post_dict = ["??????","??????"]
            post_dict = ["??????","???????????????","??????","???????????????"]


            depart = reviseSymbolPair(depart)
            depart = revisePrefixAndSuffix(depart)

            # ??????????????????????????????????????? ????????????????????? ???????????????(???????????????????????????)
            if depart.endswith("??????") or depart.endswith("??????"):
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
        # ????????????????????????4?????????
        if len(self.year) > 4:
            self.year = self.year[0:4]
        # ????????????????????????4?????????
        elif len(self.year) < 4:
            self.year = ""
        # ?????????????????????????????????????????????????????????
        if not str_is_number(self.year):
            self.year = ""
        # ???????????????????????????????????????????????????1800-2010??????
        if self.year != "":
            if int(self.year) < 1800 or int(self.year) > 2010:
                self.year = ""

    def reviseBirthMonth(self):
        # ?????????????????????
        if self.month.find(";") != -1:
            self.month = self.month[0: self.month.find(";")]
        # ?????????????????????????????????????????????
        cnMonthtransfer = {"???":"1","???":"2","???":"3","???":"4","???":"5","???":"6",
                           "???":"7","???":"8","???":"9","???":"10","??????":"11","??????":"12"}
        if self.month in cnMonthtransfer.keys():
            self.month = cnMonthtransfer[self.month]
    
        # ???????????????????????????????????????????????????????????????????????????????????????????????????2~?????????????????????
        result = ""
        for letter in self.month:
            if char_is_number(letter):
                result += letter
        self.month = result
    
        # ???????????????0????????? ?????????01-09??????1-9
        if self.month.startswith("0"):
            self.month = self.month[1:]
       
    def reviseBirthDay(self):
        # ?????????????????????
        if self.day.find(";") != -1:
            self.day = self.day[0: self.day.find(";")]
      
        # ???????????????0????????? ?????????01-09??????1-9
        if self.day.startswith("0"):
            self.day = self.day[1:]
        
        # ????????????????????????????????????????????????????????????????????????????????? ??????????????? ????????? ??????????????????????????????
        for letter in self.day:
            if not char_is_number(letter):
                self.day = ""
  
    # ????????????
    def reviseNation(self):
        if len(self.nation) > 0:
            # ?????????????????????
            nation = self.nation.split(";")[0]
            # ???????????? 
            nation = "".join(nation.split())
            self.nation = ""
            # ?????????????????????????????????
            if nation.startswith("???"):
                nation = nation[1:]
            # ???????????????????????????
            if len(nation) == 1 and nation != "???":
                nation = ""
            elif nation in ["???","?????????","???????????????","????????????"]:
                nation = "??????"
            if len(nation) > 1:
                self.nation = nation
    
    # ????????????
    def reviseSex(self):
        # ?????????????????????
        if self.sex.find(";") != -1:
            self.sex = self.sex[0:self.sex.find(";")]
        # ?????????????????????
        if self.sex.strip() not in ["???","???","male","female"]:
            self.sex  = "" 

    # ??????????????????
    def reviseWebsite(self):
        website_list = self.website.split(";")
        self.website = ""
        website_set = set()
        for website in website_list:
            index_http = website.find("http")
            # ????????????http ??????http??????????????????
            if index_http != -1:
                website = website[index_http:]
            # ????????????????????? ??????http
            elif website.startswith(":") or website.startswith("???"):
                website = "https" + website
            # ??????????????????????????????http
            elif website.startswith("/"):
                website = "https:" + website            
            # ???????????????????????????????????????????????????????????????
            elif website.startswith(".com") or website.startswith(".edu") or website.startswith(".net") or website.startswith(".ca"):
                website = ""     
            # ????????????????????????www
            elif website.startswith("."):
                website = "www" + website   
            elif website.startswith("???"):
                website = website[1:]
            # ???????????????????????????
            if website.endswith("."):
                website = ""
            # ??????????????????????????????12 ?????????????????? ???????????????????????????
            if len(website) >= 12  and website.count(".") >= 2 and website.find("@") == -1:
                website_set.add(website)
        self.website = ";".join(website for website in website_set)

    # ??????????????????
    def reviseIntroduction(self):
        endIndex = self.introduction.rfind('<')
        if endIndex != -1:
            self.introduction = self.introduction[0:endIndex-1]

   
    # ????????????
    def reviseNativePlace(self):
        # ??????????????????????????????????????? ????????????????????????
        delete_list = get_delete_native_place_list()
        # ????????????????????????????????????
        all_country_list = get_all_country_map().keys()     
        if len(self.nativePlace) > 0: 
            # ?????????????????????
            nativePlace = self.nativePlace.split(";")[0] 
            # ????????????
            nativePlace = deleteAllSpace(nativePlace)
            nativePlace = reviseSymbolPair(nativePlace)
            self.nativePlace = ""
            if str_is_english(nativePlace):
                nativePlace = ""
            else:
                # ????????????
                nativePlace = " ".join(nativePlace.split())
                # ??????????????????"???"??????"???"??? ??? ??????????????? ?????????
                if nativePlace[-1] == "???":
                    nativePlace = nativePlace[0:-1]
                if nativePlace[-1] == "???":
                    nativePlace = nativePlace[0:-1]
            # ??????????????????????????????????????? ??????????????????????????????????????????????????????
            if nativePlace == "??????":
                nativePlace = ""
            elif nativePlace.startswith("??????"):
                nativePlace = nativePlace[2:]
            # ????????????????????????????????? ???????????????
            else:
                for country_name in all_country_list:
                    if nativePlace.startswith(country_name):
                        nativePlace = ""
            # ??????????????????1 ?????????????????????????????????
            if len(nativePlace) > 1 and nativePlace not in delete_list :         
                self.nativePlace = nativePlace         
    
    # ??????????????????????????????????????????
    def addNativePlace(self,introducation):
        nativePlace_list = get_native_place_list()
        # ????????????????????????????????????????????????
        if self.nativePlace == "" and introducation.find("??????") != -1:
            index = introducation.find("??????") + 2
            # ????????????????????????????????????
            introducation = get_native_place_introducation_str(introducation,index)
            # ??????nativePlace????????????????????????????????????????????? ?????? break
            for nativePlace in nativePlace_list:
                if introducation.startswith(nativePlace):
                    self.nativePlace = nativePlace
                    break

    # ????????????
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

    # ??????????????????????????????????????? ????????????mail????????????
    def addMail(self,introducation):
        ex = extractor()
        if self.mail == "" and "mail" in introducation:
            index = introducation.find("mail")
            if index + 4 < len(introducation):
                introducation = introducation[index + 4:]
                while introducation !="" and introducation[0] in [":","???"]:
                    introducation = introducation[1:]
                mails = ex.extract_email(introducation)
                self.mail = ";".join(mails)
        
        if self.mail == "" and "??????" in introducation:
            index = introducation.find("??????")
            if index + 2 < len(introducation):
                introducation = introducation[index + 2:]
                while introducation !="" and introducation[0] in [":","???"]:
                    introducation = introducation[1:]
                mails = ex.extract_email(introducation)
                self.mail = ";".join(mails)

    # ????????????/?????????
    def reviseNationality(self):
        transfer_nationality_map = {}
        transfer_nationality_map["????????????"] = "??????"
        transfer_nationality_map["????????????"] = "??????"
        transfer_nationality_map["??????)?????????"] = "??????"
        transfer_nationality_map["????????????"] = "??????;??????"
        transfer_nationality_map["????????????"] = "??????;??????"
        transfer_nationality_map["???????????????"] = "??????;?????????"
        transfer_nationality_map["??????"] = "??????;??????" 
        transfer_nationality_map["????????????"] = "?????????" 
        transfer_nationality_map["????????????"] = ""
        transfer_nationality_map["??????"] = ""
        transfer_nationality_map["??????"] = ""
        
        
        # ??????????????????????????????key???????????????value????????????
        nationality_map = get_all_country_map()
        if "?????????????????????" in self.nationality:
            self.nationality = "??????"
        # ????????????????????? ????????????????????????????????????????????????
        self.nationality = self.nationality.replace("???",";")
        self.nationality = self.nationality.replace(" ",";")
        nationality_list = self.nationality.split(";") 
        nationality_set = set()

        for nationality in nationality_list:
            nationality = nationality.strip()
            # ??????????????????????????????????????????????????????????????????????????????
            if nationality.endswith("??????"):
                nationality = nationality[:-2]
            elif nationality.endswith("???"):
                nationality = nationality[:-1]

            # ????????????????????? ??? ??? ???????????????????????? ????????? ???????????? ?????? e.g "?????????????????????"
            # ??????if else ????????????if ?????? e.g. ???????????????????????????????????????????????????
            if "???" in nationality:
                nationality = nationality[nationality.find("???")+1:]
            if "???" in nationality:
                # ????????? ??? ??????????????????????????????????????? ?????? e.g ??????
                if nationality[-1] != "???":
                    nationality = nationality[nationality.find("???")+1:]
                else:
                    nationality = ""

            # ????????????????????? ?????????????????????
            if nationality == "??????":
                nationality = "??????"   
            # ????????????????????????????????????????????????????????? e.g ????????????
            elif nationality.endswith("??????"):
                nationality = nationality[:-2]     
            # ?????????????????????????????????????????????????????? e.g ?????????
            elif nationality.endswith("???"):
                nationality = nationality[:-1]
            # ????????????????????????????????????????????????????????? ???nationality?????? ?????????nationality_set?????????e.g ????????????
            elif "???" in nationality:
                ll = nationality.split("???")
                nationality = ""
                for e in ll:
                    if e == "???":
                        nationality_set.add("??????") 
                    else:
                        nationality_set.add(e) 

            
            # ??????????????????????????????????????????????????????????????????????????????????????????????????????            
            if "??????" in nationality:
                nationality = "??????"
            # ??????????????? ??????nationality_map???????????????
            elif nationality in nationality_map.values():
                nationality = [k for k,v in nationality_map.items() if v == nationality]
            elif nationality in transfer_nationality_map.keys():
                nationality = transfer_nationality_map[nationality]
    
            if len(nationality) > 1:
                nationality_set.add(nationality) 
        self.nationality = ";".join(nationality for nationality in nationality_set)

    # ???????????????????????????????????????
    def addNationality(self,introducation):
        nationality_map = {}
        nationality_map["????????????"] = "??????"
        nationality_map["????????????"] = "??????"
        nationality_map["????????????"] = "??????"
        nationality_map["????????????"] = "??????"
        nationality_map["????????????"] = "??????"
        nationality_map["?????????"] = "??????"
        nationality_map["?????????"] = "??????"
        nationality_map["?????????"] = "??????"
        nationality_map["?????????"] = "??????"
        nationality_map["?????????"] = "??????"
        nationality_map["?????? ??????"] = "??????"
        nationality_map[" ???????????????"] = "??????"
        if self.nationality == "":
            for key,value in nationality_map.items():
                if key in introducation:
                    self.nationality = value
                    break

    # ???????????????????????????????????????
    def reviseMajorAndInterest(self):
        interest_list = self.interest.split(";") 
        major_list = self.major.split(";")
        interest_set = set()
        major_set = set()
        all_major_list = get_all_major_list()
        for interest in interest_list:
            interest = revisePrefixAndSuffix(interest,["Research Interests)","Interests)","????????????","?????????","??????","??????","??????","??????"],["???"])

            # ??????interst??????????????????????????????????????????????????????
            if interest in all_major_list:
                major_set.add(interest)
            elif len(interest) >  2:
                interest_set.add(interest) 

        for major in major_list:
            # ??????????????????????????????           
            major = revisePrefixAndSuffix(major,[],["???"])
            if str_is_chinese(major) and len(major) > 6:
               interest_set.add(major)
            elif str_is_chinese(major):
                if major in all_major_list:
                    major_set.add(major)
            else:
                major_set.add(major)          

        self.interest = ";".join(interest for interest in interest_set)
        self.major =  ";".join(major for major in major_set)
    
    # ???????????????????????????
    def reviseTitleAndPost(self):
        # title post????????????
        all_title_list = get_all_title_list()
        all_title_list_with_priorty = get_all_title_list_with_priorty()
        all_post_list = get_all_post_list()
        # ??????title??????????????????????????????????????????delete_dict 
        # title_delete_dict = ["????????????","??????","????????????","??????","??????","??????","????????????","?????????"]
        post_delete_dict = ["?????????","?????????","?????????","?????????","????????????","??????","??????",
                            "???????????????","??????","?????????","??????","??????","??????","??????","??????","??????","??????","??????","??????","??????","??????","??????",
                            "??????","????????????","?????????","??????","?????????","??????","?????????","??????","??????","??????","??????","??????","??????","??????","??????","??????",
                            "?????????","??????","??????","??????","??????","??????","?????????","??????","??????","??????","??????","??????","?????????","??????","??????","?????????",
                            "?????????","??????","??????","?????????","?????????","??????","??????","??????","??????","?????????","?????????","??????",
                            "????????????","??????","???????????????","?????????????????????","???????????????","??????","??????","??????","?????????","?????????","????????????","??????",
                            "??????","??????","??????","??????","??????","??????","?????????"                
                           ]
        title_split_dict = [",","???","/","???","???","???","???"]
        #????????????????????????????????????,???,??? ??????post???split_dict??????
        post_split_dict = [",","???","/","???"]
        # ?????????????????????
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
        # ???????????????title
        for title in title_list:
            flag = False
            title = reviseSymbolPair(title)
            title = revisePrefixAndSuffix(title)
            # ??????????????????????????????
            if str_without_alphabet(title):
                title = deleteAllSpace(title)
            for title_regular in all_title_list:
                if title.find(title_regular) != -1:
                    title_set.add(title_regular)
                    flag = True
                    break
            # ????????????????????????????????????????????????????????????????????????
            if flag == False:
                # ????????????????????????
                title = delete_str_begin_end_parentheses(title)
                if len(title) > 0 and title[0] == "???" and title[-1]=="???":
                    title = ""
                if title not in post_delete_dict and len(title) > 1:
                    post_set.add(title)

        # ???????????????post
        for post in post_list: 
            flag = False           
            post = reviseSymbolPair(post)
            post = revisePrefixAndSuffix(post)
            # ??????????????????????????????
            if str_without_alphabet(post):
                post = deleteAllSpace(post)
            for title_regular in all_title_list:
                if post.find(title_regular) != -1:
                    title_set.add(title_regular)
                    flag = True
                    break
            # ????????????????????????????????????????????????????????????????????????
            if flag == False:
                # ????????????????????????
                post = delete_str_begin_end_parentheses(post)
                # ?????????????????????????????????
                if len(post) > 0 and post[0] == "???" and post[-1]=="???":
                    post = ""
                if post not in post_delete_dict and len(post) > 1:
                    post_set.add(post)

        # ??????title_set????????????title?????? all_title_list_with_priority????????????
        for title_sequence in all_title_list_with_priorty:
            for i in range(len(title_sequence)):
                # ????????????????????????????????????????????????
                if title_sequence[i] in title_set:
                    # ??????????????????remove??????????????????????????? discard??????
                    for j in range(i + 1,len(title_sequence)):
                        title_set.discard(title_sequence[j])
                    break
            
        self.title = ";".join(title for title in title_set)
        self.post = ";".join(post for post in post_set)

    # ????????????????????????????????????
    def revisePhoneAndFax(self):
        self.phone = replace_str_with_list(self.phone,[",","???","???","/","???","???","???","&"],";")
        self.fax = replace_str_with_list(self.fax,[",","???","???","/","???","???","???","&"],";")      
        
        phone_list = self.phone.split(";") 
        fax_list = self.fax.split(";")
        
        phone_set = set()
        telephone_set = set()
        fax_set = set()
        
        for phone in phone_list:
            phone = reviseSymbolPair(phone)
            phone = phone.strip("-")
            phone = phone.replace("+","")
            phone = phone.replace("???","")
            phone = delete_str_end_alphabet(phone)
            phone = delete_str_begin_alphabet(phone)
            phone = delete_str_begin_chinese(phone)
            phone = delete_str_end_chinese(phone)
            phone = phone.strip()
            phone = reviseCNBracketsToEN(phone)

            # ?????????????????????????????????????????????11???????????????13 14 15 17 18 19????????????????????????????????????????????? 
            if len(phone) == 11 and str_is_number(phone) and check_str_prefix_with_list(phone,check_list=["13","14","15","17","18","19"]):
                telephone_set.add(phone)
            # elif phone.startswith("021"):
            #     phone_set.add(phone)
            # ????????????????????????8?????????????????????
            elif len(phone) >= 8 :
                phone_set.add(phone)       
        
        for fax in fax_list:
            fax = reviseSymbolPair(fax)
            fax = fax.strip("-")
            fax = fax.replace("+","")
            fax = fax.replace("???","")
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

    # ??????????????????
    def reviseCode(self):
        if len(self.code) > 0: 
            code = self.code.split(";")[0]
            # ??????????????????
            code = delete_str_end_alphabet(code)
            # ????????????????????????6 ?????????????????????????????????
            if len(code) != 6 :
                code = "" 
            # ????????????6????????????????????????????????????
            if (not str_is_number(code)) or (code in ["013396","023506","992548","993122"]):
                code = ""
            self.code = code 

    # ????????????
    def reviseAddress(self):
        address_list =  self.address.split(";") 
        self.address = ""  
        address_set = set()
        for address in address_list:
            # ????????????
            address = deleteAllSpace(address)
            addresss = revisePrefixAndSuffix(address)
            address = reviseSymbolPair(address)        
            # #??????????????????
            if address.startswith("#"):
                address = ""
            #  ????????????????????????
            if len(address) > 0 and char_is_number(address[0]):
                address = ""
            #  ??????????????????????????????
            if len(address) > 0 and address[0] in ["???"]:
                address = ""
            if len(address) > 5:
                address_set.add(address)
        self.address = ";".join(address for address in address_set)

    # ???????????????????????????????????????
    def getBirthDate(self):
        if self.year != "" and self.month != "" and self.day != "":
            return self.year + "???" + self.month + "???" + self.day + "???"
        elif self.year != "" and self.month != "":
            return self.year + "???" + self.month + "???"
        elif self.year != "":
            return self.year + "???"
        else:
            return ""

   

