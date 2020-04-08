# -*- coding: UTF-8 -*-
# !usr/bin/python

from multiprocessing import Pool
import requests
from lxml import etree
import re
import pymysql
import time
import datetime
import logging
import sys
import io
from requests import exceptions
from requests_html import HTMLSession
import requests_html

#   D:\宏图佳都\宏图佳都-工作文件
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

# C:\Windows\System32
'''
On branch master
Initial commit
nothing to commit
'''

class CRAW(object):

    def __init__(self):
        # self.host='192.168.0.20'
        # self.password = '123456'

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

        self.conn = pymysql.Connect(host=self.host,
                                    user=self.user,
                                    password=self.password,
                                    db=self.db,
                                    port=self.port,
                                    charset=self.charset)
        self.cursor = self.conn.cursor()
        self.headers = {
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'Connection': 'close'
        }
        self.serial_num = ''
        self.lists = []
        self.n = 0
        self.error = "该网站目前无法扫描"
        self.call_back = ""
        self.flag = ""

    def interior(self, in_sets, url):
        h_set = set()
        h_filter = set()
        for i in in_sets:
            try:
                s_u = i.split('/', 3)[2]
                if s_u not in h_set:
                    h_set.add(s_u)
                    h_filter.add(i)
            except:
                pass
        try:  #
            return h_filter
        except:
            pass

    def external(self, out_sets, url):
        o_set = set()
        o_filter = set()
        for i in out_sets:
            s_u = i.split('/', 2)[1]
            if s_u not in o_set:
                o_set.add(s_u)
                o_filter.add(url + i)
        try:
            return o_filter
        except:
            pass

    def data_p(self, url_lis, types, url_f=""):
        if url_f == "":
            url_f = self.call_back
        else:
            pass
        ##!!
        # print(url_lis)
        while url_lis != set():
            href_once = url_lis.pop()
            self.logger.info("该链接列入存储列表:%s" % (href_once))
            href_once_l = [types, 1, href_once, self.serial_num, types, url_f]

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
                        for j in href:
                            if 'http' in j:
                                s_u = j.split('/', 4)[2]
                                if s_u not in second_rule:
                                    second_rule.add(s_u)
                                    href_set.add(j)
                            if '/' in j and len(j) > 1 and 'http' not in j:
                                s_u = j.split('/', 2)[1]
                                if s_u not in second_rule:
                                    second_rule.add(s_u)
                                    if j[0] != '/' and j[0] != ".":
                                        href_set.add(url + '/' + j)
                                    elif j[0] != '/' and j[0] == ".":
                                        href_set.add(url + '/' + j[0:-1])
                                    else:
                                        href_set.add(url + j)
                        for k in values:
                            if 'http' in k:
                                href_set.add(k)
                        self.data_p(url_lis=href_set, types="href", url_f=i)

                        src_set_rule = set()
                        src_set = set()
                        for j in src:
                            if 'http' in j:
                                s_u = j.split('/', 3)[2]
                                if s_u not in src_set_rule:
                                    src_set_rule.add(s_u)
                                    src_set.add(j)
                            if '/' in j and len(j) > 0 and 'http' not in j:
                                s_u = j.split('/', 2)[1]
                                if s_u not in src_set_rule:
                                    src_set_rule.add(s_u)
                                    if j[0] != '/' and j[0] != ".":
                                        src_set.add(url + '/' + j)
                                    elif j[0] != '/' and j[0] == ".":
                                        src_set.add(url + '/' + j[0:-1])
                                    else:
                                        src_set.add(url + j)
                        self.data_p(url_lis=src_set, types="src", url_f=i)
                    else:
                        continue
                except:
                    pass
            except:
                continue
        return

    def href(self, url, ele):
        href_in = set()
        href_out = set()

        hrefs = ele.xpath("//@href")
        values = ele.xpath("//option/@value")

        for j in values:
            if 'http' in j:
                href_in.add(j)

        for i in hrefs:
            if self.us in i and '-' + self.us not in i:
                if 'http' not in i:
                    if i[0].isalpha() and i[1].isalpha():
                        self.href_daughter.add(url + "/" + i)
                    elif not i[0].isalpha() and i[1].isalpha():
                        self.href_daughter.add(url + "/" + i[1:])
                    elif not i[1].isalpha() and not i[0].isalpha():
                        u = url + "/" + i[2:]
                        self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)

            if i.endswith('.html') or i.endswith('.htm') or i.endswith('.shtml') or i.endswith(
                    '.php') or i.endswith('.net') or i.endswith('.com') or i.endswith('.cn'):
                if 'http' not in i:
                    if i[0] != "." and i[1].isalpha():
                        self.href_daughter.add(url + i)
                    else:
                        u = url + i[1:]
                        self.href_daughter.add(u)
                else:
                    self.href_daughter.add(i)
            if 'http' in i:
                href_in.add(i)
            if 'http' not in i and '/' in i and len(i) > 1:
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
            if 'http' not in i and '/' in i and len(i) > 1:
                if i[0] != ".":
                    src_list.add(url + i)
                elif i[0] != "/" and i[0] != ".":
                    src_list.add(url + "/" + "i")
                else:
                    src_list.add(url + i[1:-1])
            if 'http' in i:
                src_list.add(i)
        return src_list

    def respectively(self):
        for i in self.lists:
            try:
                sql = "insert into assess_links_info (icp,index_sign,link,serial_id,source,level_page) values('%s','%s','%s','%s','%s','%s')" % (
                    i[0], i[1], i[2], i[3], i[4], i[5])
                self.cursor.execute(sql)
                self.conn.commit()
            except Exception as e:
                self.logger.error("error:单条数据入库失败 %s" % (e))
                pass

    def storage_manys(self):
        try:
            sql = "insert into assess_links_info (icp,index_sign,link,serial_id,source,level_page) values(%s,%s,%s,%s,%s,%s)"
            self.cursor.executemany(sql, self.lists)
            self.conn.commit()
        except Exception as e:
            self.logger.error("error:批量数据入库失败%s" % (e))
            self.respectively()
        self.lists.clear()

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
        self.logger.info("info:now time is %s" % (otherStyleTime1))

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
            session = HTMLSession()
            user_agent = requests_html.user_agent()
            headers = {
                'User-Agent': user_agent
            }
            requests.packages.urllib3.disable_warnings()
            r = session.get(url=url, headers=self.headers, verify=False)
            cookies = r.cookies
            sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
            res = session.get(url=url, headers=headers, cookies=cookies, verify=False)
            res_text = res.text
            ele = etree.HTML(res_text)
            src = ele.xpath("//@src")
            href = ele.xpath("//@href")

            if str(200) in str(res) and len(href) > 3:
                self.main_link(url, ele)

            elif str(200) in str(res) and len(href) <= 3:
                # print("该页面可能需要一段时间解析~~~")
                stat, data = self.windows_open(url, src)
                if stat == 1:
                    url = data
                    res = requests.get(url=url, headers=self.headers).text
                    ele = etree.HTML(res)
                    self.main_link(url, ele)
                else:
                    if self.t_href(href) != 0:
                        ind_time = int(time.time())
                        timeArray5 = time.localtime(ind_time)
                        otherStyleTime5 = time.strftime("%Y-%m-%d %H:%M:%S", timeArray5)
                        sql = "update assess_logs set result_index=1,status_info='home page scan completed',scan_end_time='%s' where serial_id = '%s' " % (
                            otherStyleTime5, self.serial_num)
                        self.cursor.execute(sql)
                        self.conn.commit()

                        try:
                            re_url = 'http://127.0.0.1:38081/links/setIpToIndex?serialId=' + self.serial_num + '&siteAddress=' + self.call_back
                            response = requests.get(url=re_url)
                        except:
                            pass
                    self.error = "该网址连接数过少（少于三）"

                    crawl_time = int(time.time())
                    timeArray1 = time.localtime(crawl_time)
                    otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", timeArray1)
                    sql = "update assess_logs set result_index=0 ,status_info='%s',status='扫描失败',scan_end_time='%s' where serial_id = '%s' " % (
                        self.error, otherStyleTime, self.serial_num)
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
        except Exception as e:
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

                    # if i[0] != "/":
                    #     url = self.call_back + "/" + i
                    # else:
                    #     url = self.call_back + i
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
                            if i[0] != ".":
                                src_list.add(url + i)
                            elif i[0] != "/" and i[0] != ".":
                                src_list.add(url + "/" + "i")
                            else:
                                src_list.add(url + i[1:-1])
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

    def main_link(self, url, ele):
        if url[-1] == '/':
            u = url.split('/', 10)
            self.us = u[-2]
        else:
            u = url.split('/', 10)
            self.us = u[-1]
        try:
            href_list = self.href(url, ele)
            src_list = self.src(url, ele)

            if self.flag == 'index':
                try:
                    self.data_p(href_list, "href")
                    self.data_p(src_list, "src")
                    self.second_href(url)
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
                        # print(re_url)
                        response = requests.get(url=re_url)
                        self.logger.info("info:首页请求发送成功:%s" % (response.url))
                    except Exception as e:
                        self.logger.error("error:首页请求发送失败,日志为：%s" % (e))
                except Exception as e:
                    sql = "SELECT status_info FROM assess_logs where serial_id='%s' " % (
                        self.serial_num)
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
        try:
            res = requests.get(url=testurl, verify=False, headers=self.headers).text
            ele = etree.HTML(res)
            href = ele.xpath("//@href")
            stat = testurl if len(href) > 3 else 0
            if "SSL Error pages" in res:
                self.error = "该链接需要证书"
                return 0, 0
            elif stat == 0:
                self.error = "已被拉入禁爬名单"
                return 0, stat
            return 1, testurl
        except:
            h = testurl.split(":", 1)[0]
            f = testurl.split(":", 1)[1]
            if h == "http":
                ur = "https:" + f  # JEGURZF-T4PHQZV-O4JO6Z2-GOKHK4R-MR2VQJV-NJ2NBPY-C3IGAAB
            else:
                ur = "http:" + f
            try:
                requests.packages.urllib3.disable_warnings()
                res = requests.get(url=ur, verify=False, timeout=5, headers=self.headers).text
                if "SSL Error pages" in res:
                    self.error = "该链接需要证书"
                return 1, ur
            except:
                return 0, 0

    def url_re(self, rule, urls):
        if "http" in urls[-1]:
            return urls[-1]
        else:
            return rule + "/" + urls[-1]

    def windows_open(self, url, src):
        requests.packages.urllib3.disable_warnings()
        res = requests.get(url=url, verify=False, headers=self.headers).text
        regex1 = re.compile(r'window.open\("(.*?)",')
        __url1 = regex1.findall(res)
        regex2 = re.compile(r'url = (.*?)\"')
        __url2 = regex2.findall(res)
        regex3 = re.compile(r'newdomain="(.*?)";')
        __url3 = regex3.findall(res)
        regex4 = re.compile(r'window.location = "(.*?)";')
        __url4 = regex4.findall(res)
        regex5 = re.compile('location.href = "(.*?)";')
        __url5 = regex5.findall(res)
        regex6 = re.compile('window.location="(.*?)"')
        __url6 = regex6.findall(res)
        regex7 = re.compile("window.location = '(.*?)';")
        __url7 = regex7.findall(res)
        regex8 = re.compile('URL=(.*?)"')
        __url8 = regex8.findall(res)
        regex9 = re.compile('window.location.href="(.*?)"')
        __url9 = regex9.findall(res)
        regex10 = re.compile(r"window.location='(.*?)';")
        __url10 = regex10.findall(res)
        regex11 = re.compile(r'url=(.*?)\"')
        __url11 = regex11.findall(res)
        regex12 = re.compile('window.top.location.replace\("(.*?)"\);')
        __url12 = regex12.findall(res)
        regex13 = re.compile('top.location.href="(.*?)"')
        __url13 = regex13.findall(res)
        regex14 = re.compile(' action="(.*?)"')
        __url14 = regex14.findall(res)
        regex15 = re.compile('window.location.href = "(.*?)"')
        __url15 = regex15.findall(res)
        regex16 = re.compile("window.top.location.href='(.*?)'")
        __url16 = regex16.findall(res)
        regex17 = re.compile("window.location.href='(.*?)'")
        __url17 = regex17.findall(res)
        regex18 = re.compile("location.href='(.*?)';")
        __url18 = regex18.findall(res)
        regex19 = re.compile('window.location.href =  "(.*?)"')
        __url19 = regex19.findall(res)
        regex20 = re.compile('location.href="(.*)"')
        __url20 = regex20.findall(res)
        if __url1:
            stat, data = self.links_test(self.url_re(url, __url1))
            return stat, data
        elif __url2:  # 12 23
            stat, data = self.links_test(self.url_re(url, __url2))
            return stat, data
        elif __url3:
            stat, data = self.links_test(self.url_re(url, __url3))
            return stat, data
        elif __url4:
            stat, data = self.links_test(self.url_re(url, __url4))
            return stat, data
        elif __url5:
            stat, data = self.links_test(self.url_re(url, __url5))
            return stat, data
        elif __url6:
            stat, data = self.links_test(self.url_re(url, __url6))
            return stat, data
        elif __url7:
            stat, data = self.links_test(self.url_re(url, __url7))
            return stat, data
        elif __url8:
            stat, data = self.links_test(self.url_re(url, __url8))
            return stat, data
        elif __url9:
            stat, data = self.links_test(self.url_re(url, __url9))
            return stat, data
        elif __url10:
            stat, data = self.links_test(self.url_re(url, __url10))
            return stat, data
        elif __url11:
            stat, data = self.links_test(self.url_re(url, __url11))
            return stat, data
        elif __url12:
            stat, data = self.links_test(self.url_re(url, __url12))
            return stat, data
        elif __url13:
            stat, data = self.links_test(self.url_re(url, __url13))
            return stat, data
        elif __url14:
            stat, data = self.links_test(self.url_re(url, __url14))
            return stat, data
        elif __url15:
            stat, data = self.links_test(self.url_re(url, __url15))
            return stat, data
        elif __url16:
            stat, data = self.links_test(self.url_re(url, __url16))
            return stat, data
        elif __url17:
            stat, data = self.links_test(self.url_re(url, __url17))
            return stat, data
        elif __url18:
            stat, data = self.links_test(self.url_re(url, __url18))
            return stat, data
        elif __url19:
            stat, data = self.links_test(self.url_re(url, __url19))
            return stat, data
        elif __url20:
            stat, data = self.links_test(self.url_re(url, __url20))
            return stat, data
        else:
            pass
        for i in src:
            if "app." in i:
                url = url + i
                stat, data = self.links_test(url)
                return stat, data
        stat, data = self.links_test(url)
        return stat, data


def main(urll):
    CRAW().result(urll)

#
# if __name__ == '__main__':
#     main("index-https://www.eco-city.gov.cn/")

if __name__ == '__main__':
     # http://www.cigem.cn
    pool = Pool(10)
    for i in range(1, len(sys.argv)):
        pool.apply_async(main, args=(sys.argv[i],))
    pool.close()
    pool.join()



