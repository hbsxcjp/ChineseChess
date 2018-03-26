'''
中国象棋用户类型
'''

from config_et import Config
from chessfile import ChessFile
from chessboard import ChessBoard
from form import MainForm


filename = 'C:\\360Downloads\\棋谱文件\\示例文件.xml\\第01局.xml'


class User(object):
    '玩家类'

    def __init__(self, sn=1, name='cjp'):
        self.sn = sn
        self.name = name
        self.config = Config(name)
        self.chessboard = ChessBoard(ChessFile(filename))       
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
