#!/usr/bin/env python3
# file: mysql.py
# author: walker

"""
Changelogs

2018.07.10: Add Function insert
2018.06.24: Add Function query, update
2018.03.21: init

"""

import pymysql

class MySQL():

    def __init__(self, host, port, user, passwd, db):
        self.db = pymysql.connect(
            host = host,
            port = port,
            user = user,
            passwd = passwd,
            db = db,
            charset = 'utf8',
        )
        self.cur = self.db.cursor()
        # Create the cursor

    def cmd(self, sql):
        ctype = sql.split()[0]
        if ctype.lower() == 'select':
            #print sql
            self.cur.execute(sql)
            head = self.cur.description
            data = self.cur.fetchall()
            #<type 'tuple'>
            return head, data
        else:
            result = self.cur.execute(sql)
            self.db.commit()
            return result

    def query(self, sql):
        '''
        Only use select method

        '''
        ctype = sql.split()[0]
        if ctype.lower() == 'select':
            head, data = self.cmd(sql)
            rsp = []
            for row in data:
                d = {}
                for n, r in enumerate(row):
                    d[head[n][0]] = r
                rsp.append(d)
            return rsp
        else:
            raise NotImplementedError('Only use select method')

    def insert(self, table, data, _type=0):
        '''
        Insert data from dict list
            type = 0, INSERT INTO
            type = 1, INSERt IGNORE INTO
            type = 2, REPLACE INTO

        '''
        type_dict = {
            0: 'INSERT INTO',
            1: 'INSERT IGNORE INTO',
            2: 'REPLACE INTO',
        }
        if not data: 
            raise RuntimeError('No data')
            
        cols = [n for n in data[0].keys()]
        col = ','.join(['`{}`'.format(n) for n in cols])
        sql = '{} {} ({}) VALUE\n'.format(type_dict[_type], table, col)
        rows = []
        for n in data:
            row = []
            for c in cols:
                row.append("'{}'".format(n[c]))
            rows.append('({})'.format(','.join(row)))
            if len(rows) >= 1000:
                sql += ',\n'.join(rows)
                self.cmd(sql)
                sql = '{} {} ({}) VALUE\n'.format(type_dict[_type], table, col)
                rows = []
        sql += ',\n'.join(rows)
        self.cmd(sql)

    def update(self, table, key, data):
    
        ''' 
        Update data with case
            table   : database table
            key     : primary key
            data    : data list constituted by dict
        
        '''
        _ids = [n[key] for n in data]
        item =[ n for n in data[0].keys()]
        item.remove(key)
        sql = 'UPDATE {} SET\n'.format(table)
        sqls = []
        for t in item:
            case = '{} = CASE {}\n'.format(t, key)
            line = []
            for n in data:
                _key = n[key]
                _item = n[t]
                if isinstance(_item, int) or isinstance(_item, float):
                    c = 'WHEN {} THEN {}'
                else:
                    c = 'WHEN {} THEN \'{}\''
                c = c.format(_key, _item)
                line.append(c)
            case += '\n'.join(line)
            case += '\nEND'
            sqls.append(case)
        sql += ',\n'.join(sqls)
        sql += '\nWHERE {} IN ({})'.format(key, ','.join([str(n) for n in _ids]))
        return self.cmd(sql)

    def delete(self, table, data):
        '''
        Delete data
            table  : database tables
            data   : data list constituted by dict
        '''
        sql = 'DELETE FROM {} WHERE\n'.format(table)
        conds = []
        for n in data:
            cond = []
            for key, val in n.items():
                if isinstance(val, int) or isinstance(val, float):
                    s = '`{}`={}'.format(key, val)
                else:
                    s = '`{}`=\'{}\''.format(key, val)
                cond.append(s)
            t = ' AND '.join(cond)
            conds.append('({})'.format(t))
        sql += ' OR\n'.join(conds)
        return self.cmd(sql)
        
    def close(self):
        self.db.close()

