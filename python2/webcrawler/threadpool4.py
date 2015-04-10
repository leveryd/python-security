# -*- coding:utf-8 -*-
# !/usr/bin/env python

import os
import threading
import Queue
# import xlrd
import requests

# global variable
Gene_queue = Queue.Queue()
Html_queue = Queue.Queue()
# Finished_thread_queue = Queue.Queue()


class ThreadManager:
    def __init__(self, work_queue_size, thread_pool_size):
        self.work_queue = Queue.Queue()
        self.thread_pool = []
        self.__init_work_queue(work_queue_size)
        self.__init_thread_pool(thread_pool_size)

    def __init_work_queue(self, work_queue_size):
        print 'work_queue_size: ', work_queue_size
        for i in xrange(work_queue_size):
            self.work_queue.put((get_html_data, Gene_queue.get()))

    def __init_thread_pool(self, thread_pool_size):
        for i in xrange(thread_pool_size):
            thread = Thread(self.work_queue)
            self.thread_pool.append(thread)

    def wait_all_threads_done(self):
        tmp_len = len(self.thread_pool)
        for i in xrange(tmp_len):
            if self.thread_pool[i].is_alive():
                print 'wait', self.thread_pool[i].name, 'terminate'
                self.thread_pool[i].join()
                print self.thread_pool[i].name, 'is terminated'
            else:
                print self.thread_pool[i].name, 'is not a live process'


class Thread(threading.Thread):
    def __init__(self, work_queue):
        threading.Thread.__init__(self)
        self.work_queue = work_queue
        self.setDaemon(True)
        self.start()

    def run(self):
        while True:
            try:
                func, args = self.work_queue.get(block=False)
                func(args)
            except Queue.Empty:
                print 'thread', self.name, 'cause empty'
                break
            except Exception, e:
                print 'thread start error'
                print e.message
                break


def get_data_from_excel():
    url = 'http://www.baidu.com'
    global Gene_queue
    for i in xrange(100):
        Gene_queue.put(url)


def get_html_data(gene_name):
    response = requests.get(gene_name)
    global Html_queue
    Html_queue.put(response.text)


if __name__ == '__main__':
    os.system('printf "\033c"')

    get_data_from_excel()
    print Gene_queue.qsize()
    thread_manager = ThreadManager(Gene_queue.qsize(), 20)
    thread_manager.wait_all_threads_done()

    print 'Html_queue size:', Html_queue.qsize()
