# -*- coding:UTF-8 -*-
#!usr/bin/python

import requests
from lxml import etree
import re
from multiprocessing import Pool
import json
import sys
import codecs
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())


class Craw_links():

    def __init__(self,index):
        self.headers={
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36",
            # 'accept':"text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,v=b3",
            # 'accept-Encoding': "gzip, deflate",
            # 'accept-Language': "zh-CN,zh;q=0.9",
            # 'connection': "close",
        }
        self.error="该页面无法抓取"
        self.href_daughter=set()
        self.rule=""
        self.res=""
        self.instruct=[0]
        self.sample_data=index
        self.stats=[]
        self.json_str={'status':'','result':''}

    def error_judge(self,res):
        if "SSL Error pages" in res:
            self.error="该链接为私密链接"
            return "y"
        return "n"

    def agreement(self,url):
        h = url.split(":", 1)
        if h[0]=="http:":
            ur = "https:" + h[1]
        else:
            ur="http:" + h[1]
        try:
            res = self.res_test(ur)
            res_stat = 1 if res.status_code==200 else 0

            if res_stat==1:
                self.res=res.text
                ele=etree.HTML(res.text)
                return ele

        except:
            self.stats[0]=-1
            self.error="该域名无效"
            self.stats[0]=-1
            return 0

    def joint_url(self,url_sample,url):
        if url_sample[0][0] != "/":
            cut_out = (url + "/" + url_sample[0])
        else:
            cut_out = (url + url_sample[0])
        res=self.res_test(cut_out)
        state=res.text if res.status_code == 200 else "error"
        if state!="error":
            ele=etree.HTML(state)
            self.res=res.text
            return ele
        elif state=="error":
            ele_stat=self.agreement(cut_out)
            if ele_stat!=0:
                return ele_stat
            else:
                self.stats[0]=-1
                s=self.error_judge(res.text)
                if s=="y":
                    return 0
                else:
                    self.error="该域名无效"

    def replace_url(self,url_sample):
        res=self.res_test(url_sample)
        state=res.text if res.status_code ==200 else "error"
        if state!="error":
            ele=etree.HTML(state)
            self.res=res.text
            return ele
        elif state=="error":
            ele_stat=self.agreement(url_sample)
            if ele_stat!=0:
                return ele_stat
            else:
                self.json_str['status']='-1'
                s=self.error_judge(res.text)
                if s=="y":
                    return 0
                else:
                    self.error="该域名无效"

    def the_climb(self,url,res):
        if res!="error":
            regex1 = re.compile(r'window.open\("(.*?)",')
            __url1 = regex1.findall(res)

            regex2 = re.compile(r'url=(.*?)\"')
            __url2 = regex2.findall(res)

            if __url1:
                ele=self.replace_url(__url1[0])
                return ele
            elif __url2:
                ele=self.joint_url(__url2,url)
                return ele
        elif res=="error":
            return self.agreement(url)

    def res_test(self,url):
        requests.packages.urllib3.disable_warnings()
        cookies=requests.get(url=url, headers=self.headers, verify=False).cookies
        res = requests.get(url=url, headers=self.headers, verify=False,cookies=cookies)
        # res.encoding = 'utf-8'
        return res

    def sound_code(self,url):
        res=self.res_test(url)
        ele=etree.HTML(res.text)
        datas=ele.xpath("//@href")
        href= 1 if len(datas)>3 else 0
        if res.status_code ==200 and href ==1:
            self.res=res.text
            # self.stats[0]=1
            return ele
        else:
            ele=self.the_climb(url,res)
            if ele!=0:
                return ele

    def kernel(self,url):
        ele=self.sound_code(url)
        try:
            href=ele.xpath("//@href")
            return href
        except:
            #未定义
            pass

    def second_url(self,url_list,url):
        for i in url_list:
            if self.rule in i and '-' + self.rule not in i:
                if 'http' not in i and len(i) >5:

                    if i[0].isalpha() and i[1].isalpha() :
                        self.href_daughter.add(url+"/" + i)
                    elif not i[0].isalpha() and i[1].isalpha():
                        self.href_daughter.add(url +"/"+ i[1:])
                    elif  not i[1].isalpha() and not i[0].isalpha():
                        u=url+"/"+i[2:]
                        self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)

            if i.endswith('.html') or i.endswith('.htm') or i.endswith('.shtml') or i.endswith(
                    '.php') or i.endswith('.net') or i.endswith('.com') or i.endswith('.cn'):
                if 'http' not in i:

                    if i[0].isalpha()and i[1].isalpha() :
                        self.href_daughter.add(url + i)
                    else:
                        u=url+i[1:]
                        self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)
        return

    def filtration(self,state,url_list,url):
        url_rule=set()
        url_data=set()

        for i in url_list:
            try:
                if "http" in i :
                    ur_r=i.split("/",5)[2]
                    if ur_r not in url_rule:
                        url_rule.add(ur_r)
                        url_data.add(i)
                elif "http" not in i and "/" in i:
                    ur_r=i.split("/",4)[1]
                    if ur_r not in url_rule:
                        url_rule.add(ur_r)
                        if not i[0].isalpha() and not i[1].isalpha():
                            url_data.add(url+"/"+i[2:])
                        elif not i[0].isalpha() and i[1].isalpha():
                            url_data.add(url + "/" + i[1:])
                        elif i[0].isalpha():
                            url_data.add(url+"/"+i)
            except:
                # print(i)
                pass
        # print("%s链接筛选后得到链接个数是：%s"%(state,len(url_data)))
        return list(url_data)

    def layer_two(self,url):
        url_list=set()
        for i in self.href_daughter:
            try:
                requests.packages.urllib3.disable_warnings()
                cookies=requests.get(url=i,verify=False,headers=self.headers,timeout=5)
                res=requests.get(url=i,verify=False,headers=self.headers,cookies=cookies.cookies,timeout=5)
                # res.encoding = 'utf-8'
                # print(res)
                ele=etree.HTML(res.text)
                href=ele.xpath("//@href")
                for i in href:
                    url_list.add(i)
            except:
                continue
        datas=self.filtration(state="",url_list=url_list,url=url)
        return list(datas)

    def sample(self):
        for i in self.sample_data:
            if i in self.res:
                datas=self.res.split(i,100)
                for j in range(1,len(datas)):
                    if len(datas[j])>50 and len(datas[j+1])>50:
                        data_err='......'+datas[j][-50:]+i+datas[j+1][0:50]+'......'
                        self.json_str['result']=data_err
                        self.json_str['status']=1
                        return data_err
        self.json_str['status']=0
        return 0

    def main(self,urls):
        datas=urls.split("-",3)
        self.instruct[0]=int(datas[0])
        url=datas[1]

        self.rule=url.split("/",10)[-2]
        black_set=set()

        href=self.kernel(url)  #入口

        if self.instruct[0]==1: # 源码
            if self.res!="":
                self.json_str['result'] = self.res
                self.json_str['status'] = '1'
            else:
                self.json_str['result'] = self.res
                self.json_str['status'] = '0'
            # feedback = [self.res.encode(sys.stdout.encoding).decode(sys.stdout.encoding)]

        elif self.instruct[0]==2: # 链接
            self.second_url(href, url)  # 是否二次抓取
            datas = self.layer_two(url) #二层
            #
            data_list = ['doc', 'pdf', 'xls', 'bmp', 'rar', 'exe', 'apk', 'docx', 'ppt', 'pptx', 'xlsx', 'zip']
            for i in href:
                if i.split(".", 10)[-1] not in data_list:
                    black_set.add(i)
            url_data = self.filtration(state="", url_list=black_set, url=url) #一层
            datas_all=[datas,url_data]
            if datas_all!=[]:
                self.json_str['result'] = datas_all
                self.json_str['status'] = '1'

        elif self.instruct[0]==3: #解析
            self.sample()

        else:
            self.json_str['result']='0'
            self.json_str['status']='0'
        datas=json.dumps(self.json_str)
        print(datas)
        sys.exit(datas)

if __name__ == '__main__':



    # index = ["SANGFOR"]
    # url="3-http://www.ahrcu.com"
    # craw_links = Craw_links(index)
    # craw_links.main(url)
    '''
    https://ifcsio.cebbank.com 
    '''
    index=[
        "SANGFOR",
    ]
    for i in range(1,len(sys.argv)):
        craw_links = Craw_links(index)
        craw_links.main(sys.argv[i])
    '''
    pool=Pool(10)
    index=[
        "SANGFOR",
    ]
    for i in range(1,len(sys.argv)):
        craw_links = Craw_links(index)
        # craw_links.main(sys.argv[i])
    pool.apply_async(craw_links.main(sys.argv[i]))
    pool.close()
    pool.join()
    '''
