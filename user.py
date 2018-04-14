'''
中国象棋用户类型
'''


from form import * # 视图
filename = 'c:\\棋谱文件\\示例文件.xml\\布局陷阱--飞相局对金钩炮.xml' # 4四量拨千斤


class User(object):
    '玩家类'

    def __init__(self, sn=1, name='cjp'):
        self.sn = sn
        self.name = name
        self.config = Config(name)
        self.creatwin()
        
    def creatwin(self):
        self.application = Tk()
        #self.application.title('中国象棋')
        #TkUtil.set_application_icons(application, os.path.join(
        #        os.path.dirname(os.path.realpath(__file__)), "images"))
        self.mainform = MainForm(self.application, self.config, filename)


#
