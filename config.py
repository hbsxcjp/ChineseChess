'''
中国象棋软件配置类型
'''

from base import *


class Config(object):
    # yapf: disable
    pimgpaths = {'木刻': 'WOOD/', '精致': 'POLISH/',
                 '光泽': 'DELICATE/', '卡通': 'COMIC/'}
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
                  'KING':'RKM.GIF', 'king':'BKM.GIF', 'trace':'OOS.GIF'}
    # 上一步选中痕迹图像, 将帅被将死的图像

    publicdata = [
            ('option',
                    [('face',
                        [('pimg', [(imgname, 'text_' + path) for imgname, path
                                        in pimgpaths.items()]),
                        ('bdimg', [(bdimgname, 'text_' + filename)
                            for bdimgname, filename in bdimgnames.items()])])])]

    userdata = [
        ('file',
               [('lastfile', [])]),
        ('option',
               [('action', {'openlast': 'yes'}),
                ('sound', {'open': 'yes'}),
                ('cartoon', {'open': 'no'}),
                ('face', {'imgpath': './IMAGES_L/',
                        'pimgpath': './IMAGES_L/WOOD/',
                        'bdimgname': './IMAGES_L/WOOD.JPG'})])]
    # 条目格式：[('name', 'text_xxx', {}, [], 'tail_xxx')，...],
    #           'name'元素名,'text_'元素文本，{}属性，[]子元素，'tail_'元素尾巴
    # yapf: enable

    def __init__(self, username):
        self.username = username
        try:
            self.etree = ET.ElementTree(file='config.xml')
        except:
            self.etree = ET.ElementTree(ET.Element('root'))
            allusrelem = ET.SubElement(self.etree.getroot(), '所有用户')
            self.iniconfig(allusrelem, self.publicdata)
        if self.etree.find(username) is None:
            usrelem = ET.SubElement(self.etree.getroot(), username)
            self.iniconfig(usrelem, self.userdata)
            self.save()

    def getelement(self, tag):
        return self.etree.find('{}//{}'.format(self.username, tag))

    def getallelement(self, tag):
        return self.etree.findall('{}//{}'.format(self.username, tag))

    def setelement(self, tag, value):
        self.getelement(tag).text = value

    def iniconfig(self, elem, items):
        for item in items:
            subelem = ET.Element(item[0]) # 元素名
            if len(item) > 1:  # 除元素名外，还有其他内容
                for it in item[1:]:
                    if type(it) == str:
                        if it[:5] == 'text_':  # 元素文本
                            subelem.text = it[5:]
                        elif it[:5] == 'tail_':  # 元素尾巴
                            subelem.tail = it[5:]
                    elif type(it) == dict:  # 属性
                        for name, value in it.items():
                            subelem.set(name, value)
                    elif type(it) == list:  # 子元素
                        self.iniconfig(subelem, it)
            elem.append(subelem)

    def save(self):
        xmlindent(self.etree.getroot())
        self.etree.write('config.xml', encoding='utf-8')


#
