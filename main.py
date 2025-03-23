import win32gui
import win32process
import psutil as ps
import time as tm
import asyncio
from datetime import *
import sqlite3
import sys

conn = sqlite3.connect('process_table.db')
cursor = conn.cursor()


# allData = list()
# curlen = 0
def is_process_has_visible_window(pid):
        def callback(hwnd, hwnds):
            if win32gui.IsWindowVisible(hwnd):
                _, found_pid = win32process.GetWindowThreadProcessId(hwnd)
                if found_pid == pid:
                    hwnds.append(hwnd)
            return True

        hwnds = []
        win32gui.EnumWindows(callback, hwnds)
        return len(hwnds) > 0

iterNum = 0
while True:
    iterNum += 1
    dat = list(ps.process_iter())
    data = list()
    for x in dat:
        if is_process_has_visible_window(x.pid):
            data.append(x)
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dataSet (
            id INTEGER PRIMARY KEY,
            pid INTEGER,
            process_name TEXT,
            time_start TEXT,
            closed TEXT DEFAULT 'RUNNING',
            time_close TEXT DEFAULT NULL
            
        )
        ''')
    conn.commit()

        
    rows = cursor.fetchall()
    # if not rows:
    #     continue
    cursor.execute('''SELECT * FROM dataSet''')
    rows = cursor.fetchall()
    for x in data:   
        insertList = 0
        for k in range(0, len(rows)):
            if rows[k][2] == x.name() and x.pid == rows[k][1]:
                insertList = 1
                break
        if insertList == 0:
            cursor.execute('''
                    INSERT INTO dataSet(pid, process_name, time_start) VALUES(?, ?, ?)
                    ''', (x.pid, x.name(), str(datetime.now()) ))
        # print(x.pid, x.name(), x.create_time(), str(datetime.now()))
        conn.commit()
       
    
    cursor.execute('''SELECT * FROM dataSet''')
    rows = cursor.fetchall()
    
    for i in rows:
        inList = 0
        for x in data:
            if i[2] ==  x.name() and x.pid == i[1]:
                inList = 1
                break
        if inList == 0 and i[4] == 'RUNNING':
            cursor.execute(f'''UPDATE dataSet
                               SET closed = 'CLOSED',
                               time_close = '{str(datetime.now())}' 
                               WHERE id = {i[0]}''')
            conn.commit()
                    
    

    if not rows:
        print('*')
    if iterNum % 5 == 0:
        print(f"ITERATION INDEX: {iterNum}")
        for row in rows:
            print(row)
        print('\n')
    tm.sleep(1)
 
