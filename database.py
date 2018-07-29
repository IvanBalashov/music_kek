import sqlite3
import threading

class SQLighter:

    def __init__(self, database):
        self.connection = sqlite3.connect(database, check_same_thread=False)
        self.cursor = self.connection.cursor()
        self.lock = threading.Lock()

    def select_all(self):
        with self.connection:
            return self.cursor.execute('SELECT * FROM files').fetchall()

    def add_file(self, file_id, file_name, url):
        with self.connection:
            return self.cursor.execute('INSERT INTO files(file_id,file_name,url) VALUES (?,?,?)',(file_id, file_name, url, ))

    def select_by_fileid(self, fileid):
        with self.connection:
            return self.cursor.execute('SELECT * FROM files WHERE file_id = (?)',(fileid, )).fetchall()[0]

    def check_exist_file(self, url):
        with self.connection:
            try:
                self.lock.acquire(True)
                tmp = self.cursor.execute('SELECT file_id FROM files WHERE url = (?)',(url, )).fetchall()
                if len(tmp) == 0:
                    return False
                else:
                    return True
            finally:
                self.lock.release()

    def select_by_url(self, url):
        with self.connection:
            return self.cursor.execute('SELECT file_id FROM files WHERE url =(?)',(url, )).fetchall()[0]

    def select_single(self, rownum):
        with self.connection:
            return self.cursor.execute('SELECT * FROM files WHERE id = (?)', (rownum, )).fetchall()[0]

    def count_rows(self):
        with self.connection:
            result = self.cursor.execute('SELECT * FROM files').fetchall()
            return len(result)

    def close(self):
        self.connection.close()
