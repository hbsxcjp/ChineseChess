'''
中国象棋用户类型
'''

from chessboard import *       
from form import *  

                
class User(object):
    # 玩家类    
    
    def __init__(self, sn=1, name='cjp'):
        self.sn = sn
        self.name = name
        self.chessboard = ChessBoard()        
        self.creatwin()    
            
    def creatwin(self):    
        self.application = Tk()
        #self.application.title('中国象棋')
        #TkUtil.set_application_icons(application, os.path.join(
        #        os.path.dirname(os.path.realpath(__file__)), "images"))        
        self.mainform = MainForm(self.application, self.name,
                [self.chessboard, self.chessboard.board, self.chessboard.walks])
                
                
                