'''
中国象棋棋谱文件基础信息
'''

import os, sys, re
import cProfile
import struct
import xml.etree.ElementTree as ET
import pyperclip
import winsound
#import itertools
#import sqlite3
#import chardet, shutil

from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import *
from PIL.ImageTk import PhotoImage
#from os.path import *
#from random import randint

    
blankboard = '''
┏━┯━┯━┯━┯━┯━┯━┯━┓
┃　│　│　│╲│╱│　│　│　┃
┠─┼─┼─┼─╳─┼─┼─┼─┨
┃　│　│　│╱│╲│　│　│　┃
┠─╬─┼─┼─┼─┼─┼─╬─┨
┃　│　│　│　│　│　│　│　┃
┠─┼─╬─┼─╬─┼─╬─┼─┨
┃　│　│　│　│　│　│　│　┃
┠─┴─┴─┴─┴─┴─┴─┴─┨
┃　　　　　　　　　　　　　　　┃
┠─┬─┬─┬─┬─┬─┬─┬─┨
┃　│　│　│　│　│　│　│　┃
┠─┼─╬─┼─╬─┼─╬─┼─┨
┃　│　│　│　│　│　│　│　┃
┠─╬─┼─┼─┼─┼─┼─╬─┨
┃　│　│　│╲│╱│　│　│　┃
┠─┼─┼─┼─╳─┼─┼─┼─┨
┃　│　│　│╱│╲│　│　│　┃
┗━┷━┷━┷━┷━┷━┷━┷━┛
'''
# yapf: disable
# 边框粗线
        
def multrepl(text, xdict):
    '一次替换多个子字符串（字典定义）（方法来源于PythonCook）'
    rx = re.compile('|'.join(map(re.escape, xdict)))  # 模式
    def one_xlat(match):
        return xdict[match.group(0)]  # 替换值
    return rx.sub(one_xlat, text)  # 执行替换


def xmlindent(elem, islast=False, level=0):
    'Get pretty look 取得漂亮的外观'
    def __isblank(text):
        return not text or not text.expandtabs(4).strip()

    def __addblank(text):
        return '{}{}'.format(text.expandtabs(4).strip(), tabstr)

    def __cuttab(tail, islast):
        return tail[:-1] if islast else tail

    tabstr = '\n' + level * '\t'
    if len(elem):
        elem.text = '{}\t'.format(
            tabstr if __isblank(elem.text) else __addblank(elem.text))
    for n, e in enumerate(elem):
        xmlindent(e, bool(len(elem) - 1 == n), level + 1)
    elem.tail = __cuttab(
        tabstr if __isblank(elem.tail) else __addblank(elem.tail), islast)
        

def set_application_icons(application, path):
    """Sets the application/window icon for all top-level windows.
    Assumes that the application has two icons in the given path,
    icon_16x16.gif and icon_32x32.gif. (Does nothing on Mac OS X.)
    """
    icon32 = PhotoImage(file=os.path.join(path, "icon_32x32.gif"))
    icon16 = PhotoImage(file=os.path.join(path, "icon_16x16.gif"))
    application.tk.call("wm", "iconphoto", application, "-default", icon32,
                        icon16)
                        

def playsound(soundname):
    soundpath = './SOUNDS/'  # 声音文件目录
    winsound.PlaySound(soundpath + soundname + '.WAV', winsound.SND_ASYNC)


class View(object):
    def __init__(self, model):
        self.chessboard = model
        self.board = self.chessboard.board

    def updateview(self):
        # 更新视图（由数据模型发起）
        pass

        
initdbsql = '''
    BEGIN;
    CREATE TABLE IF NOT EXISTS manual(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dirname TEXT,
                filename TEXT,
                content TEXT);
    CREATE TABLE IF NOT EXISTS chessmanual(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                dirname TEXT NOT NULL,
                filename TEXT NOT NULL,
                remark TEXT,
                Author TEXT,
                Black TEXT,
                BlackTeam TEXT,
                Date TEXT,
                ECCO TEXT,
                Event TEXT,
                FEN TEXT,
                Format TEXT,
                Game TEXT,
                Opening TEXT,
                PlayType TEXT,
                RMKWriter TEXT,
                Red TEXT,
                RedTeam TEXT,
                Result TEXT,
                Round TEXT,
                Site TEXT,
                Title TEXT,
                Variation TEXT,
                Version TEXT);
    CREATE TABLE IF NOT EXISTS moves(
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                manid INTEGER NOT NULL,
                previd INTEGER NOT NULL,
                stepno INTEGER NOT NULL,
                coordstr TEXT NOT NULL,
                remark TEXT);
    CREATE TABLE IF NOT EXISTS relation(
                ancid INTEGER NOT NULL,                
                movid INTEGER NOT NULL);
    CREATE INDEX IF NOT EXISTS movid_index ON relation (movid); --非常重要！
    CREATE TRIGGER IF NOT EXISTS insert_manual  
        BEFORE INSERT
        ON manual
        WHEN (SELECT id FROM manual 
            WHERE dirname=new.dirname AND filename=new.filename) NOTNULL
        BEGIN
            DELETE FROM manual WHERE dirname=new.dirname AND filename=new.filename;
        END;
    CREATE TRIGGER IF NOT EXISTS insert_chessmanual  
        BEFORE INSERT
        ON chessmanual
        WHEN (SELECT id FROM chessmanual 
            WHERE dirname=new.dirname AND filename=new.filename) NOTNULL
        BEGIN
            DELETE FROM chessmanual WHERE dirname=new.dirname AND filename=new.filename;
        END;
    CREATE TRIGGER IF NOT EXISTS insert_moves
        AFTER INSERT
        ON moves
        BEGIN
            INSERT INTO relation SELECT ancid, new.id FROM relation WHERE movid=new.previd;
            INSERT INTO relation VALUES (new.id, new.id);
        END;
    CREATE TRIGGER IF NOT EXISTS delete_moves
        AFTER DELETE
        ON moves
        WHEN (SELECT movid FROM relation WHERE ancid=new.id) NOTNULL 
        BEGIN
            DELETE FROM moves WHERE id in (SELECT movid FROM relation WHERE ancid=new.id);
            DELETE FROM relation WHERE ancid in (SELECT movid FROM relation
                            WHERE ancid=new.id);
        END;
    '''
    

    
hastable = '''
    SELECT count(*) FROM sqlite_master
        WHERE type="table" AND name ="chessmanual"
    '''
#cur.execute(base.hastable)
#if cur.fetchone()[0] < 1:  # 全部sql语句调试好后再启用

insertmanual = '''
    INSERT INTO manual VALUES (?, ?, ?, ?)
    '''
insertinfo = '''
    INSERT INTO chessmanual VALUES 
        (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    '''
insertmove = '''
    INSERT INTO moves VALUES (?, ?, ?, ?, ?, ?)
    '''
getlastmanid = '''
    SELECT seq FROM sqlite_sequence WHERE name="chessmanual"
    '''
getlastmovid = '''
    SELECT seq FROM sqlite_sequence WHERE name="moves"
    '''
'''
class xqftodb(object):

    def tranxqftodb(self, dirnamefrom, dirto='.\\'):

        def __addinfomove():
        
            def __addmove(node, preid):
                self.moves.append((None, self.manid, preid, node.stepno,
                            node.coordstr, node.remark))
                self.lastmovid += 1
                node.movid = self.lastmovid # 重要!保存当前move的id
                if node.other:
                    __addmove(node.other, preid)
                if node.next_:
                    __addmove(node.next_, node.movid)
                    
            info = ([None, self.dirname, self.filename, self.rootnode.remark] + 
                    [value for key, value in sorted(self.info.items())])
            self.infos.append(info)
            self.manid += 1            
            __addmove(self.rootnode, 0)
            
        def __getinfomove(dirfrom):
            fcount = dcount = 0        
            for subname in os.listdir(dirfrom):
                subname = os.path.normcase(subname)
                pathfrom = os.path.join(dirfrom, subname)
                if os.path.isfile(pathfrom):
                    extension = os.path.splitext(os.path.basename(pathfrom))[1]
                    if extension == '.xqf':
                        self.__readxqf(pathfrom)
                        __addinfomove()
                        fcount += 1
                    elif extension == '.txt':
                        content = open(pathfrom).read()
                        cur.execute(base.insertmanual,
                                (None, os.path.splitdrive(dirfrom)[1], subname, content))
                        fcount += 1
                else:
                    below = __getinfomove(pathfrom)
                    fcount += below[0]
                    dcount += below[1]
                    dcount += 1
            return (fcount, dcount)

        #if not os.path.exists(dirto):
        #    os.mkdir(dirto)
        dbname = dirto + '\\chessmanual.db'
        #if os.path.exists(dbname):
        #    os.remove(dbname)
        con = sqlite3.connect(dbname)
        con.execute('PRAGMA synchronous = OFF')
        cur = con.cursor()
        cur.executescript(base.initdbsql) # 执行sql脚本，多个sql语句
        
        cur.execute(base.getlastmanid)
        res = cur.fetchone()
        self.manid = 0 if res is None else res[0]
        cur.execute(base.getlastmovid)
        res = cur.fetchone()
        self.lastmovid = 0 if res is None else res[0]
        
        self.infos = []
        self.moves = []
        fcount, dcount = __getinfomove(dirnamefrom)
        con.execute('BEGIN;')
        cur.executemany(base.insertinfo, self.infos)
        cur.executemany(base.insertmove, self.moves)
        
        cur.close()
        con.commit()
        con.close()
        return (fcount, dcount)   
   
'''

'''
try:  # encoding=GB2312 GB18030 utf-8 GBK
    return bstr.decode('GBK', errors='ignore')
except:
    coding = chardet.detect(bstr)
    print(coding)
    return bstr.decode(coding['encoding'], errors='ignore')                
'''
    
#                