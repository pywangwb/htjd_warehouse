#! usr/bin/python
# -*- coding: utf-8 -*-

import pymysql
import logging
import redis
import time
import sys
import re
from DBUtils.PooledDB import PooledDB
import math
import logging.handlers
defaultencoding = 'utf-8'

class Logs():
    def __init__(self,_log_):
        self.log=_log_

    #反馈日至函数
    def log1(self):
        logger = logging.getLogger()
        formater = logging.Formatter('%(asctime)s,%(levelname)-12s:%(message)s')

        names = 'rm_%s.log' % (self.log)
        file_handler = logging.FileHandler(names)
        file_handler.setFormatter(formater)

        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.formatter = formater

        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        logger.setLevel(logging.DEBUG)
        return logger

    def log(self):
        LOGGING_MSG_FORMAT = '[%(asctime)s] [%(levelname)s] [%(module)s] [%(funcName)s] [%(lineno)d] %(message)s'
        LOGGING_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
        logging.basicConfig(level=logging.DEBUG, format=LOGGING_MSG_FORMAT, datefmt=LOGGING_DATE_FORMAT)
        log = logging.getLogger()
        crawl_time = int(time.time())
        timeArray1 = time.localtime(crawl_time)
        otherStyleTime1 = time.strftime("%Y%m%d%H%M%S", timeArray1)
        logger = logging.handlers.TimedRotatingFileHandler(otherStyleTime1 + ".log", 'D', 1, 0)
        logger.setFormatter(logging.Formatter(LOGGING_MSG_FORMAT))
        log.addHandler(logger)
        console = logging.StreamHandler()
        console.setLevel(logging.INFO)
        console.setFormatter(logging.Formatter(LOGGING_MSG_FORMAT))
        log.addHandler(console)
        return log

class Monitor():
    def __init__(self):
        crawl_time = int(time.time())
        timeArray1 = time.localtime(crawl_time)
        otherStyleTime1 = time.strftime("%Y%m%d", timeArray1)
        self.log = Logs(otherStyleTime1).log()

        self.host = '192.168.0.20'
        self.user = 'root'
        self.password = '123456'
        self.db = 'logsystem'
        self.port = 3306
        self.charset = 'utf8'
        pool = PooledDB(pymysql, 5, host=self.host, user=self.user, password=self.password, port=self.port,
                        charset=self.charset, database=self.db)
        self.conn = pool.connection()
        self.cursor = self.conn.cursor()

        self.browser_type = ''
        self.host_dict = dict()
        self.domain_id = ''
        self.datas = ''

        self.client_ = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True,db=6)
        self.rc = redis.Redis(connection_pool=self.client_)

        self.nums = 0
        self.stoptime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time() + 2))
        self.list2 = []
        self.upper=0
        self.rule=0
        self.http_user_agent=''

    def while_data(self):
        try:
            l=self.rc.llen('syslog::data')
            if l>0:
                return 'y',l
            else :
                return 'n',0
        except:
            return 'n',0

    def get_data(self,l):
        self.rule=l
        if self.rule>20:
            self.upper=20
        elif self.rule<=20:
            self.upper=math.ceil(self.rule/2)
        try:
            datas = self.rc.rpop('syslog::data')
            print(u"当前弹出来的数据是%s"%(datas))
            if datas!=None:
                self.log.warning("warning:%s" % (datas))
                self.re_my(datas)
        except BaseException as b:
            self.log.error("error:error is %s"%(b))

    def re_my(self, buf):
        now_time = int(time.time())
        time_Array = time.localtime(now_time)
        resnow_time = time.strftime("%Y-%m-%d %H:%M:%S", time_Array)
        datas = str(buf).split('nginx:', 1)
        screen_out = datas[-1].split(",", 11)
        if '.pdf' or '.doc' or'.jpg' or '.png' or '.gif' or '.css' or '.js' or '.ttf' or '.ppt' or 'docx' or '.xls' or '.xlsx' not in screen_out[5]:
            hosts = screen_out[1]
            host = hosts.replace(" ", "")
            try:
                times_s = screen_out[2][1:-1]
                enly_rime = str(times_s).split(' ', 1)
                timeArray = time.strptime(enly_rime[0], "%d/%b/%Y:%H:%M:%S")
                int_time = int(time.mktime(timeArray))
                timeArray = time.localtime(int_time)
                self.timeArray = timeArray
            except BaseException as e:
                print(e)

            otherStyleTime = time.strftime("%Y-%m-%d %H:%M:%S", self.timeArray)
            otherStyleTime_time = time.strftime("%H:%M:%S", self.timeArray)
            otherStyleTime_date = time.strftime("%Y-%m-%d", self.timeArray)

            try:
                regex = re.compile(r'".*?"')
                self.http_user_agent = regex.findall(str(datas[-1]))[-1]
            except:
                regex = str(datas).split(",", 11)
                self.http_user_agent = regex[-5] + "," + regex[-4]

            if "Chrome" in self.http_user_agent:
                self.browser_type = '谷歌内核浏览器'
                self.log.info(u"info:该浏览器为：谷歌内核浏览器")
            elif "Trident" in self.http_user_agent:
                self.browser_type = u'IE内核浏览器'
                self.log.info(u"info:该浏览器为：IE内核浏览器")
            elif "Safari" in self.http_user_agent:
                self.browser_type = '苹果内核浏览器'
                self.log.info(u"info:该浏览器为：苹果内核浏览器")
            elif "Firefox" in self.http_user_agent:
                self.browser_type = '火狐浏览器内核'
                self.log.info(u"info:该浏览器为:火狐浏览器内核")
            else:
                self.browser_type = '其他内核浏览器'
                self.log.info(u"info:该浏览器为：其他内核浏览器")
            self.totality_store( otherStyleTime, screen_out, host, resnow_time, otherStyleTime_date,
                                 otherStyleTime_time)

    def totality_store(self, otherStyleTime, screen_out, host, resnow_time, otherStyleTime_date,
                       otherStyleTime_time):
        self.log.info("info:host-%s"%(host))
        ho = self.host_dict.get(host,0)
        if ho == 0:
            try:
                self.log.info("info:my dict not have this host,The database skips if it doesn't")
                sql = "select id from log_domain_name where domain ='%s'" % (host)
                self.cursor.execute(sql)
                host_id = self.cursor.fetchone()[0]
                if host_id:
                    self.log.info("info:my dict not have this host, but database have this host")
                    self.nums+=1
                    self.host_dict[host] = host_id
                    if "'" in screen_out[-1]:
                        bytes_nums=screen_out[-1][0:-1]
                    else:
                        bytes_nums = screen_out[-1]
                    if  '"' in screen_out[5]:
                        screen_out_data=screen_out[5][1:-1]
                    elif "'" in screen_out[5]:
                        screen_out_data = screen_out[5][1:-1]
                    else:
                        screen_out_data=screen_out[5]
                    if "'" in screen_out[3]:
                        request=screen_out[3][1:-1]
                    elif '"' in screen_out[3]:
                        request=screen_out[3][1:-1]
                    else:
                        request=screen_out[3]
                    lis2 = (
                        'Python', resnow_time, otherStyleTime, request, self.browser_type, screen_out[-2],
                        otherStyleTime_date, screen_out[0], screen_out[4], screen_out_data, otherStyleTime_time,
                        bytes_nums, self.http_user_agent, host_id)
                    self.list2.append(lis2)
            except BaseException as b:
                self.log.error("error:matching ~~~%s"%(b))
                pass

        elif ho != 0:
            self.log.info("info:this host_id is %s"%(ho))
            host_id = ho
            if "'" in screen_out[-1]:
                bytes_nums = screen_out[-1][0:-1]
            elif '"' in screen_out[-1]:
                bytes_nums=screen_out[-1][0:-1]
            else:
                bytes_nums = screen_out[-1]

            if  '"' in screen_out[5]:
                screen_out_data = screen_out[5][1:-1]
            elif "'" in screen_out[5]:
                screen_out_data=screen_out[5][1:-1]
            else:
                screen_out_data = screen_out[5]

            if "'" in screen_out[3]:
                request = screen_out[3][1:-1]
            elif '"' in screen_out[3]:
                request = screen_out[3][1:-1]
            else:
                request = screen_out[3]

            lis2 = ('Python', resnow_time, otherStyleTime, request, self.browser_type, screen_out[-2],
                    otherStyleTime_date, screen_out[0], screen_out[4],screen_out_data, otherStyleTime_time,
                    bytes_nums, self.http_user_agent, host_id)
            self.nums+=1
            self.list2.append(lis2)
        thistime = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime(time.time()))

        if self.nums >= self.upper or thistime>self.stoptime:
            self.stoptime = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time()+2))
            self.in_stroge()

    def in_stroge(self):
        try:
            try:
                sql2 = "insert into log_visit_details" \
                       "(create_person,create_time,access_date,access_page,browser_type,cache_hit_status,date," \
                       "ip,request_state,source_request,time,traffic_bytes,user_agent,domain_id) " \
                       "values(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"
                self.cursor.executemany(sql2, self.list2)
            except BaseException as b:
                self.log.error("error:Storage exception!!!%s"%(b))
            self.conn.commit()
        except BaseException as b:
            self.log.error("error:Storage exception-----%s"%(b))
            pass
        self.nums = 0
        self.list2 = []

def mains():
    monitor = Monitor()
    while True:
        lens, l = monitor.while_data()
        if lens == 'y':
            monitor.get_data(l)

if __name__ == '__main__':
    mains()
    # datas='<190>Mar  5 00:18:56 localhost.localdomain nginx: 2408:84e5:108d:a8e:99fe:fa08:9230:306,www.weihai.gov.cn,[05/Mar/2020:00:18:56 +0800],GET //picture/2301/1905201107108301302.png HTTP/1.1,200,http://zfgjj.weihai.gov.cn/jrobot/search.do?pagemode=result&appid=1&q=%E8%AF%B7%E8%BE%93%E5%85%A5%E5%85%B3%E9%94%AE%E5%AD%97%E5%85%AC%E7%A7%AF%E9%87%91%E6%8F%90%E5%8F%96&webid=86&style=22&ck=0&pos=title%2Ccontent,Mozilla/5.0 (Linux; U; Android 8.1.0; zh-cn; OPPO R11 Build/OPM1.171019.011) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/53.0.2785.134 Mobile Safari/537.36 OppoBrowser/10.5.0.4,-,HIT,81'
    #     datas='<190>Mar  4 18:42:19 localhost.localdomain nginx: 2409:890c:db40:cae:68ac:f235:87e5:eda9,www.weihai.gov.cn,[04/Mar/2020:18:42:19 +0800],GET /vc/vc/interface/visit.jsp?type=3&i_webid=59&i_columnid=42568&i_articleid=2158414&url=http://www.whncfp.gov.cn/art/2019/10/23/art_42568_2158414.html HTTP/1.1,200,http://www.whncfp.gov.cn/module/visitcount/visit.jsp?type=3&i_webid=59&i_columnid=42568&i_articleid=2158414,CMCC M850A_LTE/V1 Linux/3.18.31 Android/7.1.2 Release/10.1.2017 Browser/AppleWebKit537.36 Mobile Safari/537.36 System/Android/7.1.2,-,-,2421'
    # monitor = Monitor().re_my(datas)

    # strs='<190>Feb 28 14:19:38 localhost.localdomain nginx: 2408:8606:2600:1:1ab:b88c:ebc6:6cc8,www.sge.com.cn,[28/Feb/2020:14:19:38 +0800],GET /static/css/images/ui-bg_flat_75_ffffff_40x100.png HTTP/1.1,404,https://www.sge.com.cn/static/css/jquery-ui.css,Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/69.0.3497.81 Safari/537.36 QQBrowser/4.5.122.400,-,-,134'
    # monitor=Monitor()
    # monitor.re_my(strs)

