# -*- coding: utf-8 -*-
import sqlite3

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def select_all(self):
        """ Получаем все строки """
        with self.connection:
            return self.cursor.execute('SELECT * FROM files').fetchall()

    def add_file(self, file_id, file_name, url):
        with self.connection:
            return self.cursor.execute('INSERT INTO files [(file_id, file_name, url] VALUES (?,?,?)',(file_id, file_name, url,))

    def select_by_fileid(self, fileid):
        with self.connection:
            return self.cursor.execute('SELECT * FROM files WHERE file_id = ?',(fileid,)).fetchall()[0]

    def check_exist_file(self, url):
        with self.connection:
            tmp = self.cursor.execute('SELECT * FROM files WHERE url = ?',(url,)).fetchall()[0]
            if len(tmp) == 0:
                return False
            else:
                return True

    def select_by_url(self, url):
        with self.connection:
            return self.cursor.execute('SELECT file_id FROM files WHERE url = ?',(url,)).fetchall()[0]

    def select_single(self, rownum):
        """ Получаем одну строку с номером rownum """
        with self.connection:
            return self.cursor.execute('SELECT * FROM files WHERE id = ?', (rownum,)).fetchall()[0]

    def count_rows(self):
        """ Считаем количество строк """
        with self.connection:
            result = self.cursor.execute('SELECT * FROM files').fetchall()
            return len(result)

    def close(self):
        """ Закрываем текущее соединение с БД """
        self.connection.close()