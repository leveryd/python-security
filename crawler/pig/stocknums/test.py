#-*- encoding:utf-8 -*-

import xlrd
import os
import requests
from collections import defaultdict
import xlrd
from selenium import webdriver
import types
import re
from redis import Redis
from pymongo import MongoClient
import time
import threading
# from Queue import Queue
import Queue

def get_data():
    data = xlrd.open_workbook('mRNAdata.xls')
    table = data.sheets()[0]
    col_values = table.col_values(7)
    col_len = len(col_values)
    print col_len - 11
    sum_float = 0
    for i in xrange(11, col_len):
        # print type(col_values[i])
        if type(col_values[i]) == types.FloatType:
            sum_float += 1
            print i, 'is float'
    print sum_float
    print col_len - 17

def test():
	url = 'http://www.ncbi.nlm.nih.gov/gene/34'
	# url = 'http://www.ncbi.nlm.nih.gov/gene/?term=ACADM'
	driver = webdriver.PhantomJS()
	driver.get(url)
	try:
            # relate_articles = driver.find_element_by_xpath('//*[@id="padded_content"]/div[5]/div[2]/div[4]/div[2]/div[1]/div/ol')
            # relate_articles = driver.find_element_by_css_selector('#padded_content > div.rprt.full-rprt > div.rprt-body > div.rprt-section.gene-bibliography > div.rprt-section-body > div:nth-child(1) > div > ol')
            # a = driver.find_element_by_css_selector('#padded_content > div.rprt.full-rprt > div.rprt-body > div.rprt-section.gene-bibliography > div.rprt-section-body > div:nth-child(1) > div > ol')
            relate_articles = driver.find_elements_by_class_name('generef-link')
	except Exception, e:
            print 'get relate_articles error'
            print str(e)

	# print type(a)
	try:
            if relate_articles[0]:
                relate_articles_nums = len(relate_articles[0].find_elements_by_tag_name('li'))
                print 'relate_articles_li:', relate_articles_nums
                print type(relate_articles_nums)
	except Exception, e:
            print 'len error'
            print str(e)

	pattern = re.compile(ur'See all (\d+) citations in')
	result = pattern.search(driver.page_source)
	if result:
		relate_articles_nums = result.group(1)
	print result.group(1)
	print type(relate_articles_nums)

def test_gene_type():
	url = 'http://www.ncbi.nlm.nih.gov/gene/?term=RPL38'
	driver = webdriver.PhantomJS()
	driver.get(url)

	try:
            result_element = driver.find_element_by_xpath('//*[@id="padded_content"]/div[4]/div/h2')
	except Exception, e:
            print str(e)
            print traceback.print_exc()

	line_numbers = 20
	if len(result_element.text) < 15:
            tmp_text = result_element.text.split()
            line_numbers = int(tmp_text[1])

	for line in xrange(line_numbers):
            line += 1
            xpath = '//*[@id="gene-tabular-docsum"]/div[2]/table/tbody/tr[' + str(line) + ']/td[2]/em'
            exists_homo_sapiens = driver.find_element_by_xpath(xpath)

            if exists_homo_sapiens.text == 'Homo sapiens':
                    xpath = '//*[@id="gene-tabular-docsum"]/div[2]/table/tbody/tr[' + str(line) + ']/td[1]/div[2]/a'
                    get_gene_href = driver.find_element_by_xpath(xpath)
                    second_url = get_gene_href.get_attribute('href')
                    print second_url
                    if second_url:
                            driver.get(second_url)
                            print driver.current_url
                            # handle_full_report(driver, gene_name, 'second')
                    else:
                            print 'second url none'
                    break



def handle_full_report(driver, gene_name, sign, url):
    try:
            driver.get(url)
    except httplib.BadStatusLine:
            print 'request full report url error'
            return
    try:
            gene_type = driver.find_element_by_xpath('//*[@id="summaryDl"]/dd[5]')
    except:
            print '\n' + sign + ' error url:', driver.current_url  + ' ' + gene_name + ' ' + 'Get gene_type error' +  ' ' + url + '\n'
            return
    try:
            exon_count = driver.find_element_by_xpath('//*[@id="padded_content"]/div[5]/div[2]/div[2]/div[2]/div/dl/dd')
    except:
            print '\nerror url:', driver.current_url  + '\t' + gene_name + 'get exon_count erro' + '\n'
            return

    try:
            relate_articles = driver.find_elements_by_class_name('generef-link')
            # relate_articles = driver.find_element_by_xpath('//*[@id="padded_content"]/div[5]/div[2]/div[4]/div[2]/div[1]/div/ol')
    except Exception, e:
            print 'get relate_articles error'
            print str(e)

    relate_articles_nums = 0
    try:
            if relate_articles[0]:
                    relate_articles_nums = unicode(len(relate_articles[0].find_elements_by_tag_name('li')))
    except Exception, e:
            print 'get relate_article_len error'
            print str(e)

    pattern = re.compile(ur'See all (\d+) citations in')
    result = pattern.search(driver.page_source)
    if result:
            relate_articles_nums = result.group(1)

    try:
            print 'gene_type:', gene_type.text + '\t' +  'exon_count:' + exon_count.text + '\t' + 'article_nums:', relate_articles_nums
            # OUTPUT_QUEUE.put(gene_name + ' ' + gene_type.text + ' ' + exon_count.text + ' ' + relate_articles_nums)
    except Exception, e:
            print str(e)
            print driver.current_url
    return

def handle_data(gene_name, driver):
    base_url = 'http://www.ncbi.nlm.nih.gov/gene/?term='
    first_url = base_url + gene_name

    response = requests.get(first_url)
    if len(re.findall(ur'Full Report', response.text)) > 0:
        handle_full_report(driver, gene_name, 'first', first_url)
        print 'excute handle_full_report'
        return

    driver.get(first_url)
    """
    try:
            result_element = driver.find_element_by_xpath('//*[@id="padded_content"]/div[4]/div/h2')
    except Exception, e:
            print str(e)
            print 'get result_element error, gene_name:', gene_name ,  ' error url:', driver.current_url
            # print traceback.print_exc()
    line_numbers = 20
    try:
            if len(result_element.text) < 15:
                    tmp_text = result_element.text.split()
                    line_numbers = int(tmp_text[1])
    except Exception, e:
            print str(e)
            print driver.current_url

    """
    line_numbers = 20
    for line in xrange(line_numbers):
        line += 1
        xpath = '//*[@id="gene-tabular-docsum"]/div[2]/table/tbody/tr[' + str(line) + ']/td[2]/em'
        try:
                exists_homo_sapiens = driver.find_element_by_xpath(xpath)
        except Exception, e:
                continue
                # print

        if exists_homo_sapiens.text == 'Homo sapiens':
            xpath = '//*[@id="gene-tabular-docsum"]/div[2]/table/tbody/tr[' + str(line) + ']/td[1]/div[2]/a'
            get_gene_href = driver.find_element_by_xpath(xpath)
            second_url = get_gene_href.get_attribute('href')
            if second_url:
                    # driver.get(second_url)
                    handle_full_report(driver, gene_name, 'second', second_url)
            else:
                    print 'second url none'
            break

def test15():
    server = MongoClient('localhost', 27017)
    db = server.guba_data
    lack_queue = Queue.Queue()
    line_num = 1
    for stock_num in open('stocknums.txt', 'r'):
        stocknum = 'db' + stock_num.strip()
        collec = db[stocknum]
        if collec.count() == 0:
            print stock_num.strip(), 'is not exist'
            lack_queue.put(stock_num)
            # print line_num
        line_num += 1

    print lack_queue.qsize()


def test14():
    server = MongoClient('localhost', 27018)
    db = server.guba
    lack_queue = Queue.Queue()
    line_num = 1
    for stock_num in open('stocknum_04.txt', 'r'):
        stocknum = 'db' + stock_num.strip()
        collec = db[stocknum]
        # print collec.count()
        if collec.count() == 0:
            print stock_num.strip(), 'is not exist'
            lack_queue.put(stock_num)
            print line_num
        line_num += 1

    print lack_queue.qsize()


if __name__ == '__main__':
    os.system('printf "\033c"')

    test14()
