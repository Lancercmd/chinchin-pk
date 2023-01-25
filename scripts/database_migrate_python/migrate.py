import os
import sqlite3
import json


class Sql():

    def __init__(self):
        sql_dir = os.path.join(os.path.dirname(__file__), '../../src/data-v2')
        if not os.path.exists(sql_dir):
            os.makedirs(sql_dir)
        sql_path = os.path.join(sql_dir, 'data.sqlite')
        if os.path.exists(sql_path):
            # throw error
            raise Exception('data.sqlite file already exists')
        # connect sqlite database and create table
        conn = sqlite3.connect(sql_path)
        cursor = conn.cursor()
        self.conn = conn
        self.cursor = cursor

    def __create_table(self):
        return 'create table if not exists `users` (`qq` bigint, `length` float, `daily_lock_count` integer, `daily_pk_count` integer, `daily_glue_count` integer, `register_time` varchar(255), `latest_daily_lock` varchar(255), `latest_daily_pk` varchar(255), `latest_daily_glue` varchar(255), `pk_time` varchar(255), `pked_time` varchar(255), `glueing_time` varchar(255), `glued_time` varchar(255), `locked_time` varchar(255), primary key (`qq`));'

    def __insert_single_data(self, json: dict):
        return f'insert into `users` (`daily_glue_count`, `daily_lock_count`, `daily_pk_count`, `glued_time`, `glueing_time`, `latest_daily_glue`, `latest_daily_lock`, `latest_daily_pk`, `length`, `locked_time`, `pk_time`, `pked_time`, `qq`, `register_time`) values ({json["daily_glue_count"]}, {json["daily_lock_count"]}, {json["daily_pk_count"]}, "{json["glued_time"]}", "{json["glueing_time"]}", "{json["latest_daily_glue"]}", "{json["latest_daily_lock"]}", "{json["latest_daily_pk"]}", {json["length"]}, "{json["locked_time"]}", "{json["pk_time"]}", "{json["pked_time"]}", {json["qq"]}, "{json["register_time"]}");'

    def connect_sql(self):
        self.cursor.execute(self.__create_table())
        self.conn.commit()
        print('create table suscess')
        return self

    def insert_all_data(self):
        from_data_dir = os.path.join(
            os.path.dirname(__file__), '../../src/data')
        # copy all data to backup
        backup_dir = os.path.join(os.path.dirname(
            __file__), '../../src/data-v1-backup')
        # delete and create
        if os.path.exists(backup_dir):
            os.system(f'rm -rf {backup_dir}')
            os.makedirs(backup_dir)
        print('backup data to data-v1-backup')
        os.system(f'cp -r {from_data_dir}/ {backup_dir}/')
        # read all json file and insert data to sqlite database
        files = os.listdir(from_data_dir)
        for file in files:
            if not file.endswith('.json'):
                return
            with open(os.path.join(from_data_dir, file), 'r', encoding='utf-8') as f:
                json_data = json.load(f)
                sql = self.__insert_single_data(json_data)
                self.cursor.execute(sql)
                self.conn.commit()
                # print insert suscess
                current_idx = files.index(file)
                print(f'insert {file} suscess ({current_idx}/{len(files)})')
        print('insert all data suscess, please check the data.sqlite file')
        return self


if __name__ == '__main__':
    sql = Sql()
    sql.connect_sql().insert_all_data()
