'''
中国象棋用户类型
'''

from config import Config # 配置
from chessboard import ChessBoard # 模型
from form import MainForm # 视图


filename = '.\\棋谱文件\\示例文件.xml\\第01局.xml'


class User(object):
    '玩家类'

    def __init__(self, sn=1, name='cjp'):
        self.sn = sn
        self.name = name
        self.config = Config(name)
        self.chessboard = ChessBoard(filename)       
        self.creatwin()
        
    def creatwin(self):
        self.application = Tk()
        #self.application.title('中国象棋')
        #TkUtil.set_application_icons(application, os.path.join(
        #        os.path.dirname(os.path.realpath(__file__)), "images"))
        self.mainform = MainForm(
            self.application, self.config,
            [self.chessboard, self.chessboard.board, self.chessboard.walks])


#
