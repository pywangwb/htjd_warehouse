# -*- coding: UTF-8 -*-
# !usr/bin/python
from multiprocessing import Pool
import requests
from lxml import etree
import re
import pymysql
import time
import datetime
from selenium import webdriver
import logging
import sys
import io
import urllib
from requests import exceptions
from http import cookiejar
import warnings
warnings.filterwarnings('ignore')

class Logs():
    def __init__(self):
        self.logger = logging.getLogger()
        formater = logging.Formatter('%(asctime)s,%(levelname)-12s:%(message)s')
        crawl_time = int(time.time())
        timeArray1 = time.localtime(crawl_time)
        otherStyleTime1 = time.strftime("%Y%m%d%H%M%S", timeArray1)
        names = '%s.log' % (otherStyleTime1)
        file_handler = logging.FileHandler('/home/logs/%s' % (names))
        # file_handler = logging.FileHandler(names)
        file_handler.setFormatter(formater)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formater
        self.logger.addHandler(file_handler)
        self.logger.addHandler(console_handler)
        self.logger.setLevel(logging.DEBUG)

    def log(self):
        return self.logger

class CRAW(object):

    def __init__(self):
        self.host = '127.0.0.1'
        self.password = '123456'
        self.user = 'root'
        self.db = 'pingguserver'
        self.port = 3306
        self.charset = 'utf8'

        self.logger = Logs().log()

        self.href_daughter = set()
        self.href_s = set()
        self.src_s = set()
        self.us = ''
        self.video_links=set()

        self.conn = pymysql.Connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    db=self.db,
                                    port=self.port,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()

        self.headers={
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36',
            'Connection': 'close',
            }
        self.serial_num = ''
        self.lists = []
        self.n = 0
        self.error = "该网站目前无法扫描"
        self.call_back = ""
        self.flag = ""
        self.audio=set()

    def interior(self, in_sets, url):
        h_set = set()
        h_filter = set()
        for i in in_sets:
            try:
                s_u = i.split('/')[2]
                if s_u not in h_set:
                    h_set.add(s_u)
                    h_filter.add(i)
            except:
                pass
        try:
            return h_filter
        except:
            pass

    def external(self, out_sets, url):
        o_set = set()
        o_filter = set()
        for i in out_sets:
            s_u = list(filter(None,i.split('/')))[0]
            if s_u not in o_set:
                o_set.add(s_u)
                o_filter.add(urllib.parse.urljoin(url , i))
        try:
            return o_filter
        except:
            pass

    def data_p(self, url_lis, types, url_f="",audio=2):
        if url_f == "":
            url_f = self.call_back
        else:
            pass
        while url_lis != set():
            href_once = url_lis.pop()
            if "javascript" not in href_once:
                if 'blob' in href_once :
                    audio = 1
                    href_once=href_once.split('blob:')[1]

                elif "youku" in href_once or href_once.endswith('.swf') or href_once.endswith('.mp4') :
                    audio=1

                elif self.call_back in href_once:
                    audio=3
                else:
                    audio=2

                href_once_l = [types, 1, href_once, self.serial_num, types, url_f,audio]

                self.lists.append(href_once_l)
                self.n += 1
                if self.n >= 5 or url_lis == set():
                    self.storage_manys()
                    self.n = 0

    def second_href(self, url):
        for i in self.href_daughter:
            try:
                try:
                    try:
                        requests.packages.urllib3.disable_warnings()
                        staus_c = requests.get(url=i, headers=self.headers, verify=False, timeout=5)
                    except exceptions.Timeout:
                        continue
                    if staus_c.status_code == 200:
                        try:
                            time.sleep(0.5)
                            cookie = staus_c.cookies
                            requests.packages.urllib3.disable_warnings()
                            res = requests.get(url=i, cookies=cookie, headers=self.headers, verify=False,
                                               timeout=5).text
                            ele = etree.HTML(res)
                            href = ele.xpath("//@href")

                            values = ele.xpath("//option/@value")
                            src = ele.xpath("//@src")

                        except exceptions.Timeout:
                            continue

                        href_set = set()
                        second_rule = set()
                        # print("跟新",href)
                        for j in href:
                            #
                            if "javascript" not in j:
                                if 'http' in j:
                                    s_u = j.split('/', 4)[2]
                                    if s_u not in second_rule:
                                        second_rule.add(s_u)
                                        href_set.add(j)
                                elif '/' in j and len(j) > 1 and 'http' not in j:
                                    s_u=list(filter(None,j.split('/')))[0]
                                    if s_u not in second_rule:
                                        second_rule.add(s_u)
                                        href_set.add(urllib.parse.urljoin(url,j))
                                        # if j[0] != '/' and j[0] != ".":
                                        #     href_set.add(url + '/' + j)
                                        # elif j[0] != '/' and j[0] == ".":
                                        #     href_set.add(url + '/' + j[0:-1])
                                        # else:
                                        #     href_set.add(url + j)
                        for k in values:
                            if 'http' in k:
                                href_set.add(k)

                        self.data_p(url_lis=href_set, types="href", url_f=i)

                        src_set_rule = set()
                        src_set = set()
                        for j in src:
                            if "javascript" not in j:
                                if 'http' in j:
                                    s_u = j.split('/', 3)[2]
                                    if s_u not in src_set_rule:
                                        src_set_rule.add(s_u)
                                        src_set.add(j)
                                if '/' in j and len(j) > 0 and 'http' not in j:
                                    s_u = list(filter(None,j.split('/')))[0]
                                    if s_u not in src_set_rule:
                                        src_set_rule.add(s_u)
                                        src_set.add(urllib.parse.urljoin(url,j))
                                        # if j[0] != '/' and j[0] != ".":
                                        #     src_set.add(url + '/' + j)
                                        # elif j[0] != '/' and j[0] == ".":
                                        #     src_set.add(url + '/' + j[0:-1])
                                        # else:
                                        #     src_set.add(url + j)
                        self.data_p(url_lis=src_set, types="src", url_f=i)
                    else:
                        continue
                except:
                    pass
            except:
                continue

    def href(self, url, ele):
        href_in = set()
        href_out = set()
        hrefs = ele.xpath("//@href")
        values = ele.xpath("//option/@value")
        for j in values:
            if 'http' in j:
                href_in.add(j)
        for i in hrefs:

            if self.us in i and '-' + self.us not in i and 'javascript' not in hrefs:
                if 'http' not in i:
                    new_url=urllib.parse.urljoin(url, i)
                    self.href_daughter.add(new_url)
                    # if i[0].isalpha() and i[1].isalpha():
                    #     self.href_daughter.add(url + "/" + i)
                    # elif not i[0].isalpha() and i[1].isalpha():
                    #     self.href_daughter.add(url + "/" + i[1:])
                    # elif not i[1].isalpha() and not i[0].isalpha():
                    #     u = url + "/" + i[2:]
                    #     self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)

            if i.endswith('.html') or i.endswith('.htm') or i.endswith('.shtml') or i.endswith(
                    '.php') or i.endswith('.net') or i.endswith('.com') or i.endswith('.cn'):
                if 'http' not in i:
                    new_url=urllib.parse.urljoin(url,i)
                    self.href_daughter.add(new_url)
                    # if i[0] != "." and i[1].isalpha():
                    #     self.href_daughter.add(url + i)
                    # else:
                    #     u = url + i[1:]
                    #     self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)
            if 'http' in i:
                href_in.add(i)
            if 'http' not in i and '/' in i and len(i) > 1:
                # new_url=urllib.parse.urljoin
                # print(i)
                # href_out.add(urllib.parse.urljoin())
                if i[0] != "." and i[0] == "/":
                    href_out.add(i)
                elif i[0] != "." and i[0] != "/":
                    href_out.add("/" + i)
                elif i[0] == "." and i[1] != "/":
                    href_out.add("/" + i[1:-1])

        ints = self.interior(href_in, url)
        outs = self.external(href_out, url)
        href_datas = ints | outs
        return href_datas

    def src(self, url, ele):
        src_list = set()
        src = ele.xpath("//@src")
        for i in src:
            if 'http' not in i and len(i) > 1 and i.split('.')[-1]!="js" and 'javascript' not in i:
                src_list.add(urllib.parse.urljoin(url,i))
                # if i[0] != ".":
                #     src_list.add(url + i)
                # elif i[0] != "/" and i[0] != ".":
                #     src_list.add(url + "/" + "i")
                # else:
                #     src_list.add(url + i[1:-1])
            elif 'http' in i:
                src_list.add(i)


        return src_list

    def respectively(self):
        for i in self.lists:
            try:
                # warnings.filterwarnings(action='ignore', category=Warning, module='gensim')
                sql = "insert into assess_links_info (icp,index_sign,link,serial_id,source,level_page,application_type_id) values('%s','%s','%s','%s','%s','%s','%s')" % (
                    i[0], i[1], i[2], i[3], i[4], i[5],i[6])
                self.cursor.execute(sql)
                self.conn.commit()
            except :
                pass

    def storage_manys(self):
        try:
            sql = "insert into assess_links_info (icp,index_sign,link,serial_id,source,level_page,application_type_id) values(%s,%s,%s,%s,%s,%s,%s)"
            self.cursor.executemany(sql, self.lists)
            self.conn.commit()
        except :
            self.respectively()
        self.lists.clear()

    def s_code(self,url):
        try:
            self.headers["Host"]="www.baidu.com"
            requests.adapters.DEFAULT_RETRIES = 5
            requests_session = requests.Session()
            requests_session.cookies = cookiejar.LWPCookieJar('cookiejar')
            cookies = requests_session.get(url=url, headers=self.headers).cookies
            requests.packages.urllib3.disable_warnings()
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            res = requests.get(url=url, headers=self.headers, cookies=cookies, verify=False)

            return res
        except Exception as e:
            error_datas = ''.join(str(e))

            res = self.web_cook(url=url, error_datas=error_datas)
            return res

    def web_cook(self,url,error_datas):
        try:
            # strs = "".join(str(e))
            rule = re.compile(r"host='(.*?)',")
            data = rule.findall(error_datas)
            if data:
                self.headers['Host'] = data[0]

            requests.adapters.DEFAULT_RETRIES = 5
            requests_session = requests.Session()
            requests_session.cookies = cookiejar.LWPCookieJar('cookiejar')
            cookies = requests_session.get(url=url, headers=self.headers).cookies
            requests.packages.urllib3.disable_warnings()
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

            res = requests.get(url=url, headers=self.headers, cookies=cookies, verify=False)
            return res
        except:
            pass

    def result(self, urll):
        s_u = urll.split('-', 1)
        flag = s_u[0]
        self.flag = flag
        url = (str(str(s_u[1]).replace("\r", ""))).replace(" ", "")
        self.call_back = url
        now_time = int(time.time())
        timeArray = time.localtime(now_time)
        otherStyleTime = time.strftime("%Y%m%d%H%M%S", timeArray)
        time_now = datetime.datetime.now().strftime('%H%M%S%f')
        serial_num = str(otherStyleTime + time_now)
        self.serial_num = serial_num

        self.conn.begin()
        sql = "SELECT id FROM assess_website where site_address='%s' " % (url)
        self.cursor.execute(sql)
        addr = self.cursor.fetchall()
        self.conn.commit()

        crawl_time = int(time.time())
        timeArray1 = time.localtime(crawl_time)
        otherStyleTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)

        if addr:
            w_id = addr[0][0]
            sql = "update assess_website set scan_time='%s' where id ='%s'" % (otherStyleTime1, w_id)
            self.cursor.execute(sql)
            self.conn.commit()

        elif not addr:
            self.conn.begin()
            sql = "insert into assess_website (scan_time,site_address) values('%s','%s')" % (otherStyleTime1, url)
            self.cursor.execute(sql)
            self.conn.commit()
        else:
            pass

        self.cursor.execute("SELECT id FROM assess_website where site_address='%s'" % (url))
        v = self.cursor.fetchall()
        self.conn.commit()
        self.conn.begin()

        sql = "insert into assess_logs (scan_start_time,serial_id,status,status_info,website_id) values('%s','%s','%s','%s','%s')" % (
            otherStyleTime1, self.serial_num, 'is scanning', 'begin analyzed', v[0][0])
        self.cursor.execute(sql)
        self.conn.commit()

        try:
            try:
                options = webdriver.ChromeOptions()
                prefs = {
                    'profile.default_content_settings': {
                        'profile.default_content_setting_values': {
                            # 'images': 2,
                            # 'javascript': 2,
                            # "User-Agent": ua,
                        }}}
                options.add_experimental_option("prefs", prefs)
                options.add_argument('blink-settings=imagesEnabled=false')
                options.add_argument('--headless')
                options.add_argument('--disable-gpu')

                # driver = webdriver.Chrome(options=options, executable_path=r'./verisons_file/chromedriver%s.exe' % (i))
                driver = webdriver.Chrome(options=options)
                driver.maximize_window()
                driver.get(url)
                res_text = driver.page_source
                driver.quit()
                # return source
                # requests.adapters.DEFAULT_RETRIES = 5
                # requests_session = requests.Session()
                # requests_session.cookies = cookiejar.LWPCookieJar('cookiejar')
                # cookies = requests_session.get(url=url, headers=self.headers).cookies
                #
                # requests.packages.urllib3.disable_warnings()
                # sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
                # res = requests.get(url=url, headers=self.headers, cookies=cookies, verify=False)
                # res_text = res.text
            except Exception as e:
                error_datas=''.join(str(e))
                res = self.web_cook(url=url,error_datas=error_datas)
                res_text=res.text
            ele = etree.HTML(res_text)
            # src = ele.xpath("//@src")
            # href = ele.xpath("//@href")

            # if "header" or "footer" in res_text:
            #     try:
            #         regex=re.compile('.load\(\"(.*?)\"')
            #         links=regex.findall(res.text)
            #         for i in links:
            #             if "http" in i:
            #                 self.href_daughter.add(i)
            #             else:
            #                 self.href_daughter.add(url+"/"+i)
            #     except:
            #         pass

            # if str(200) in str(res) and len(href) > 3:
            if res_text:
                self.main_link(url, ele)

            # elif str(200) in str(res) and len(href) <= 3:
            #     stat, data = self.windows_open(url, src)
            #     if stat == 1:
            #
            #         self.main_link(data, ele,state=1)
            #     else:
            #         if self.t_href(href) != 0:
            #             ind_time = int(time.time())
            #             timeArray5 = time.localtime(ind_time)
            #             otherStyleTime5 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray5)
            #             sql = "update assess_logs set result_index=1,status_info='home page scan completed',scan_end_time='%s' where serial_id = '%s' " % (
            #                 otherStyleTime5, self.serial_num)
            #             self.cursor.execute(sql)
            #             self.conn.commit()
            #
            #             try:
            #                 re_url = 'http://127.0.0.1:38081/links/setIpToIndex?serialId=' + self.serial_num + '&siteAddress=' + self.call_back
            #                 response = requests.get(url=re_url)
            #             except:
            #                 pass
            #         self.error = "该网址连接数过少（少于三）"
            #
            #         crawl_time = int(time.time())
            #         timeArray1 = time.localtime(crawl_time)
            #         otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)
            #         sql = "update assess_logs set result_index=0 ,status_info='%s',status='扫描失败',scan_end_time='%s' where serial_id = '%s' " % (
            #             self.error, otherStyleTime, self.serial_num)
            #         self.cursor.execute(sql)
            #         self.conn.commit()
            #
            # elif len(href)<3:
            #     res=self.s_code(url=url)
            #     res_text=res.text
            #     ele=etree.HTML(res_text)
            #     self.main_link(url, ele)

            else:
                crawl_time = int(time.time())
                timeArray1 = time.localtime(crawl_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)

                sql = "update assess_logs set result_index=0 ,status_info='%s',status='扫描失败',scan_end_time='%s' where serial_id = '%s' " % (
                    self.error, otherStyleTime, self.serial_num)
                self.cursor.execute(sql)
                self.conn.commit()
        except Exception as e:
            print(e)
            s = "".join(str(e))
            if "Invalid URL" in s:
                crawl_time = int(time.time())
                timeArray1 = time.localtime(crawl_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)

                sql = "update assess_logs set result_index=0 ,status_info='%s',status='扫描失败',scan_end_time='%s' where serial_id = '%s' " % (
                    "该域名无效", otherStyleTime, self.serial_num)
                self.cursor.execute(sql)
                self.conn.commit()

            else:
                crawl_time = int(time.time())
                timeArray1 = time.localtime(crawl_time)
                otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)

                sql = "update assess_logs set result_index=0 ,status_info='%s',status='扫描失败',scan_end_time='%s' where serial_id = '%s' " % (
                    self.error, otherStyleTime, self.serial_num)
                self.cursor.execute(sql)
                self.conn.commit()

    def t_href(self, hrefs):
        try:
            href_in = set()
            href_out = set()
            src_list = set()
            for i in hrefs:
                try:
                    ur=i.split("/",10)
                    url=self.call_back+"/"+ur[-1]
                    if url[-1] == '/':
                        u = url.split('/', 10)
                        self.us = u[-2]
                    else:
                        u = url.split('/', 10)
                        self.us = u[-1]
                    requests.packages.urllib3.disable_warnings()
                    res = requests.get(url=url, headers=self.headers, verify=False).content.decode()
                    ele = etree.HTML(res)
                    href = ele.xpath("//@href")
                    src = ele.xpath("//@src")
                    for i in href:
                        if 'http' in i:
                            href_in.add(i)
                        if 'http' not in i and '/' in i and len(i) > 1:

                            if i[0] != "." and i[0] == "/":
                                href_out.add(i)
                            elif i[0] != "." and i[0] != "/":
                                href_out.add("/" + i)
                            elif i[0] == "." and i[1] != "/":
                                href_out.add("/" + i[1:-1])
                    for i in src:
                        if 'http' not in i and '/' in i and len(i) > 1:
                            src_list.add(urllib.parse.urljoin(url,i))
                            # if i[0] != ".":
                            #     src_list.add(url + i)
                            # elif i[0] != "/" and i[0] != ".":
                            #     src_list.add(url + "/" + "i")
                            # else:
                            #     src_list.add(url + i[1:-1])
                        if 'http' in i:
                            src_list.add(i)
                except:
                    pass

            ints = self.interior(href_in, self.call_back)
            outs = self.external(href_out, self.call_back)
            href_lis = ints | outs
            try:
                self.data_p(href_lis, "href")
                self.data_p(src_list, "src")
                return 1
            except:
                return 0
        except:
            return 0

    def main_link(self, urls, ele,state=2):
        try:
            if state != 1:
                if urls[-1] == '/':
                    u = urls.split('/', 10)
                    self.us = u[-2]
                else:
                    u = urls.split('/', 10)
                    self.us = u[-1]

                href_list = self.href(urls, ele)
                src_list = self.src(urls, ele)

            else:
                url=list(urls)
                href_list=set()
                src_list=set()
                if url[-1][-1] == '/':
                    u = url[-1].split('/', 10)
                    self.us = u[-2]
                else:
                    u = url[-1].split('/', 10)
                    self.us = u[-1]

                for i in url:
                    requests.adapters.DEFAULT_RETRIES = 5
                    requests_session = requests.Session()
                    requests_session.cookies = cookiejar.LWPCookieJar('cookiejar')
                    cookies = requests_session.get(url=i, headers=self.headers).cookies

                    requests.packages.urllib3.disable_warnings()
                    res = requests.get(url=i, headers=self.headers, cookies=cookies, verify=False)

                    ele=etree.HTML(res.text)
                    h_list = self.href(i, ele)
                    s_list = self.src(i, ele)

                    href_list=href_list|h_list
                    src_list=src_list|s_list

            if self.flag == 'index':
                try:
                    self.data_p(href_list, "href")
                    self.data_p(src_list, "src")
                    self.second_href(urls)
                    socket_s=self.href_daughter
                    self.data_p(socket_s,"href",audio=0)


                    ind_time = int(time.time())
                    timeArray5 = time.localtime(ind_time)
                    otherStyleTime5 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray5)
                    sql = "update assess_logs set result_index=1,status_info='home page scan completed',scan_end_time='%s' where serial_id = '%s' " % (
                        otherStyleTime5, self.serial_num)
                    self.cursor.execute(sql)
                    self.conn.commit()
                    self.logger.debug("该网址评估完成")

                    try:
                        if "#" in self.call_back:
                            self.call_back=self.call_back.replace("#","@")
                        re_url = 'http://127.0.0.1:38081/links/setIpToIndex?serialId=' + self.serial_num + '&siteAddress=' + self.call_back
                        response = requests.get(url=re_url)
                        self.logger.info("info:首页请求发送成功:%s" % (response.url))
                    except Exception as e:
                        self.logger.error("error:首页请求发送失败,日志为：%s" % (e))
                except Exception as e:
                    sql = "SELECT status_info FROM assess_logs where serial_id='%s' " % (self.serial_num)
                    self.cursor.execute(sql)
                    addr = self.cursor.fetchall()
                    self.conn.commit()
                    self.logger.error("error:入库操作出现异常 %s" % (e))
                    in_time = int(time.time())
                    timeArray6 = time.localtime(in_time)
                    otherStyleTime6 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray6)
                    sql = "update assess_logs set result_index=0,status='scan fail' ,status_info='%s', scan_end_time='%s' where serial_id = '%s' " % (
                        addr[0][0], otherStyleTime6, self.serial_num)
                    self.cursor.execute(sql)
                    self.conn.commit()

        except Exception as e:
            print(e)
            self.logger.error("error:扫描异常，错误信息：,%s" % (e))
            sql = "SELECT status_info FROM assess_logs where serial_id='%s' " % (self.serial_num)
            self.cursor.execute(sql)
            addr = self.cursor.fetchall()
            self.conn.commit()

            crawl_time = int(time.time())
            timeArray1 = time.localtime(crawl_time)
            otherStyleTime1 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)
            if self.flag == 'index':
                sql = "update assess_logs set result_index=0,scan_end_time='%s',status_info='%s' where serial_id = '%s' " % (
                    otherStyleTime1, addr[0][0], self.serial_num)
                self.cursor.execute(sql)
                self.conn.commit()
                print('扫描失败请重新开始')

    def links_test(self, testurl):
        data=set()
        for i in testurl:
            try :
                res = requests.get(url=i, verify=False, headers=self.headers).text
                ele = etree.HTML(res)
                href = ele.xpath("//@href")
                stat = testurl if len(href) > 3 else 0

                if "SSL Error pages" in res:
                    self.error = "该链接需要证书"
                elif stat == 0:
                    self.error = "已被拉入禁爬名单"
                else:
                    data.add(i)

            except Exception as e:
                h = testurl.split(":", 1)[0]
                f = testurl.split(":", 1)[1]
                if h == "http":
                    ur = "https:" + f
                else:
                    ur = "http:" + f
                try:
                    requests.packages.urllib3.disable_warnings()
                    res = requests.get(url=ur, verify=False, timeout=5, headers=self.headers).text

                    if "SSL Error pages" in res:
                        self.error = "该链接需要证书"
                    else:
                        data.add(ur)
                except:
                    pass

        if data!=set():
            return  1,data
        return 0,data

    def links_join(self, data, urls):
        if urls[-1]=='/':
            url=urls[:-1]
        else:
            url=urls
        urla = (data.replace("../", '')).replace("./", '')
        try:
            if "http" in urla:
                return urla
            elif "http" not in urla and len(urla)>3:
                if not urla[0].isalpha() and urla[1].isalpha():
                    return url + '/' + urla[1:]
                elif not urla[0].isalpha() and not urla[1].isalpha():
                    return url + '/' + urla[2:]
                elif urla[0].isalpha():
                    return url + '/' + urla
            return 0
        except:
            pass

    def url_re(self, rule, urls):
        datas=set()
        for i in urls:
            data=self.links_join(data=i, urls=rule)
            if data!=0:
                datas.add(data)
        return datas

    def windows_open(self, url, src):
        url_list=set()
        requests.packages.urllib3.disable_warnings()
        res = requests.get(url=url, verify=False, headers=self.headers).text

        rule_list=['window.open\("(.*?)",','url = (.*?)\"','newdomain="(.*?)";','window.location = "(.*?)";','location.href = "(.*?)";',
                   'window.location="(.*?)"',"window.location = '(.*?)';",'URL=(.*?)"','window.location.href="(.*?)"',
                   "window.location='(.*?)';",'url=(.*?)\"','window.top.location.replace\("(.*?)"\);','top.location.href="(.*?)"',
                   ' action="(.*?)"','window.location.href = "(.*?)"',"window.top.location.href='(.*?)'","window.location.href='(.*?)'",
                   "location.href='(.*?)';",'window.location.href =  "(.*?)"','location.href="(.*)"','<a href="(.*?)">'
                   ]
        for i in rule_list:
            try:
                regex = re.compile(r'%s'%(i))
                __url = regex.findall(res)
                if __url:
                    datas = self.url_re(url, __url)
                    stat, data = self.links_test(testurl=datas)
                    if stat == 1:
                        for i in data:
                            url_list.add(i)
            except:
                pass
        if url_list!=set():
            return 1,url_list
        return 0,url_list

def main(urll):
    CRAW().result(urll)

# if __name__ == '__main__':
#     # main("index-https://www.eco-city.gov.cn/")
#     main("index-https://www.cctv.com/")

if __name__ == '__main__':
    pool = Pool(10)
    for i in range(1, len(sys.argv)):
        pool.apply_async(main, args=(sys.argv[i],))
    pool.close()
    pool.join()

