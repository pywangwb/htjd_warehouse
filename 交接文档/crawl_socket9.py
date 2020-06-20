#!usr/bin/python
# -*- coding: utf-8 -*-
import re
import socket
import sys
import time
import logging
import redis
import threading
from concurrent.futures import ThreadPoolExecutor
import gevent
from gevent import socket,monkey
monkey.patch_all(thread=False)
import threading
import queue




class Monitor(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.browser_type = ''

        self.host_dict = dict()
        self.domain_id = ''

        self.connpool = redis.ConnectionPool(host='localhost', port=6379, decode_responses=True, db=6)
        self.rc = redis.Redis(connection_pool=self.connpool)

        self.nums = 0
        self.lock = threading.RLock()
        self.time = None

        self.q=queue.Queue()

    def listen(self):
        self.time = time.time()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(('192.168.0.20', 8886))

        for i in range(5):
            t = ThreadNum(queue)
            t.setDaemon(True)
            t.start()

        with ThreadPoolExecutor(12) as excutor:
            while True:
                buf, addr = sock.recvfrom(3072)

                # gevent.spawn(self.storage(buf))
                # excutor.submit(self.storage(buf))

                self.nums += 1
                self.rc.lpush('syslog::data', str(buf))


if __name__ == '__main__':
    monitor = Monitor()
    monitor.listen()
