'''
中国象棋软件配置类型
'''

import os
import sys

from os.path import *
from random import randint

import pyperclip
import itertools
import xml.etree.ElementTree as ET
import winsound

from tkinter import *
import tkinter.ttk as ttk
from tkinter.filedialog import askopenfilename, asksaveasfilename
from tkinter.messagebox import *
from PIL.ImageTk import PhotoImage


imgpath = '.\\IMAGES_L\\' 
pimgpath = '.\\IMAGES_L\\WOOD\\'
bdimgname = '.\\IMAGES_L\\WOOD.JPG'
# 默认的图像目录、文件
                            
pimgpaths = {'木刻': 'WOOD\\', '精致': 'POLISH\\',
             '光泽': 'DELICATE\\', '卡通': 'COMIC\\'} 
            # 棋子图像目录                                                
bdimgnames = {'栎木': 'WOOD.JPG', '白色大理石': 'WHITE.JPG', 
              '再生纸': 'SHEET.JPG', '画布': 'CANVAS.JPG', 
              '水滴': 'DROPS.JPG', '绿色大理石': 'GREEN.JPG',
              '浅红象棋': 'QIANHONG.GIF'} 
            # 棋盘图像文件名
imgflnames = {'P':'RP.GIF', 'N':'RN.GIF', 'C':'RC.GIF',
              'R':'RR.GIF', 'B':'RB.GIF', 'A':'RA.GIF',
              'K':'RK.GIF', # 95:'OO.GIF', 
            # 红色棋子图像文件名
              'p':'BP.GIF', 'n':'BN.GIF', 'c':'BC.GIF',
              'r':'BR.GIF', 'b':'BB.GIF', 'a':'BA.GIF',
              'k':'BK.GIF', 
              'KK':'RKM.GIF', 'kk':'BKM.GIF', 'trace':'OOS.GIF'}
            # 上一步选中痕迹图像, 将帅被将死的图像


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
    # 播放声音
    soundpath = '.\\SOUNDS\\' # 声音文件目录
    winsound.PlaySound(soundpath + soundname + '.WAV', winsound.SND_ASYNC)
    

class Config_ET(object):

    publicdata = [
            ('option', 
                    [('face', 
                        [('pimg', [(imgname, 'text_' + path) for imgname, path
                                        in pimgpaths.items()]),
                        ('bdimg', [(bdimgname, 'text_' + filename)
                            for bdimgname, filename in bdimgnames.items()])])])]
    
    userdata = [
        ('file', 
               [('pgnfile', [('lastname', )])]),
        ('option', #'text_option.text',
               [('action', [('openlastpgn', 'text_yes')]),
                ('sound', [('isopen', 'text_yes')]),
                ('cartoon', [('isopen', 'text_no')]),
                ('face', [('imgpath', 'text_' + imgpath)],
                        [('pimgpath', 'text_' + pimgpath)],
                        [('bdimgname', 'text_' + bdimgname)])])]
    # 条目格式：[('str', 'text_xxx', {}, [], 'tail_xxx')，...], 'str'必须在第一个位置
    
    def __init__(self, username):
        self.username = username
        try:
            self.etree = ET.ElementTree(file='.\\config.xml')
        except:       
            self.etree = ET.ElementTree(ET.Element('root'))
            self.iniconfig('所有用户', Config_ET.publicdata)
        if self.etree.find(self.username) is None:
            self.iniconfig(self.username, Config_ET.userdata)            
            
    def getelement(self, tag):
        return self.etree.find('{}//{}'.format(self.username, tag))
  
    def getallelement(self, tag):
        return self.etree.findall('{}//{}'.format(self.username, tag)) 
  
    def setelement(self, tag, value):
        self.getelement(tag).text = value
  
    def indent(self, elem, islast=False, level=0):
        # Get pretty look 取得漂亮的外观

        def __isblank(text):
            return not text or not text.expandtabs(4).strip()
        
        def __addblank(text):
            return '{}{}'.format(text.expandtabs(4).strip(), tabstr)        
      
        def __cuttab(tail, islast):
            return tail[:-1] if islast else tail
        
        tabstr = '\n' + level * '\t'         
        if len(elem):
            elem.text = '{}\t'.format(tabstr if __isblank(elem.text)
                                    else __addblank(elem.text))               
        for n, e in enumerate(elem):
            self.indent(e, bool(len(elem)-1 == n), level+1)                
        elem.tail = __cuttab(tabstr if __isblank(elem.tail)
                            else __addblank(elem.tail), islast)       
        
    def iniconfig(self, username, data):
    
        def __addelem(elem, items):
            for item in items:
                subelem = ET.Element(item[0])
                if len(item) > 1:  # 除元素名外，还有其他内容
                    for it in item[1:]:
                        if type(it) == str:
                            if it[:5] == 'text_': # 元素文本
                                subelem.text = it[5:]
                            elif it[:5] == 'tail_': # 元素尾巴
                                subelem.tail = it[5:]
                        elif type(it) == dict: # 属性
                            for name, value in it.items():
                                subelem.set(name, value)
                        elif type(it) == list:  # 子元素
                            __addelem(subelem, it)
                elem.append(subelem)

        root = self.etree.getroot()
        __addelem(ET.SubElement(root, username), data)       
            
    def save(self):
        # 存储设置选项
        self.indent(self.etree.getroot())
        self.etree.write('config.xml', encoding='utf-8')             


        