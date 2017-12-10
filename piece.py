'''
中国象棋棋子类型 by-cjp
'''

from crossbase import *


BlankChar = '_' 
CharToNames = {'K':'帅', 'A':'仕', 'B':'相', 'N':'马',
               'R':'车', 'C':'炮', 'P':'兵', 
               'k':'将', 'a':'士', 'b':'象', 'n':'马',
               'r':'车', 'c':'炮', 'p':'卒', BlankChar: ''}
# 全部棋子ch值与中文名称映射字典
PawnNames = {'兵', '卒'}
AdvisorBishopNames = {'仕', '相', '士', '象'}
StrongePieceNames = {'车', '马', '炮', '兵', '卒'}
LineMovePieceNames = {'帅', '将', '车', '炮', '兵', '卒'}


class Piece(object):
    # 棋子类
    def __init__(self, char):
        self.__char = char
        
    def __str__(self):
        return self.name
        
    @property
    def side(self):
        return BLACK_SIDE if self.__char.islower() else RED_SIDE
        
    @property
    def char(self):
        return self.__char
     
    @property
    def name(self):
        return CharToNames[self.__char]
        
    @property
    def isStronge(self):
        return self.name in StrongePieceNames        
        
    @classmethod
    def getotherside(cls, side):        
        return RED_SIDE if side == BLACK_SIDE else BLACK_SIDE
        
    def getallrowcols(self,  board):  
        # 全部活动范围集合(默认：车马炮的活动范围)
        return Cross.allrowcols
    
    def getmoverowcols(self, rowcol, board):
        # 当前棋子所处位置的有效活动范围集合
        return {}
        
        
class BlankPie(Piece):

    @property
    def side(self):
        return None

        
class King(Piece):

    def getallrowcols(self,  board):  
        return Cross.kingrowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getkingmoverowcols(rowcol, self, board)
        
        
class Advisor(Piece):
    
    def getallrowcols(self,  board):  
        return Cross.advisorrowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getadvisormoverowcols(rowcol, self, board)        
        
        
class Bishop(Piece):

    def getallrowcols(self,  board):  
        return Cross.bishoprowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getbishopmoverowcols(rowcol, self, board)
                
        
class Knight(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getknightmoverowcols(rowcol, self, board)

                
class Rook(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getrookmoverowcols(rowcol, self, board)

        
class Cannon(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getcannonmoverowcols(rowcol, self, board)
 
        
class Pawn(Piece):
    
    def getallrowcols(self,  board):  
        return Cross.pawnrowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return Cross.getpawnmoverowcols(rowcol, self, board)
              
        
class Pieces(object):
    # 一副棋子类
    Chars = ['K', 'A', 'A', 'B', 'B', 'N', 'N', 'R', 'R', 
                'C', 'C', 'P', 'P', 'P', 'P', 'P',
            'k', 'a', 'a', 'b', 'b', 'n', 'n', 'r', 'r',
                'c', 'c', 'p', 'p', 'p', 'p', 'p']
    # 全部棋子ch值列表
    CharPieces = {'K': King, 'A': Advisor, 'B': Bishop, 'N': Knight,
                    'R': Rook, 'C': Cannon, 'P': Pawn}
    # 棋子类字典
    
    def __init__(self):    
        self.__pieces = [self.CharPieces[char.upper()](char) for char in self.Chars]
        
    def __str__(self):
        return str([str(piece) for piece in self.__pieces])
        
    def getpiece(self, char, board):
        if char == BlankChar:
            return BlankPie
        charpieces = list({piece for piece in self.__pieces if piece.char == char}
                        - set(board.getlivecrosses().values()))
        return charpieces[0]
        #assert False, '找不到空闲的棋子: ' + char        

    def getkingpiece(self, side):
        return self.__pieces[0 if side == RED_SIDE else 16]
        
    def getothersidepiece(self, piece):
        n = self.__pieces.index(piece)
        return self.__pieces[(n + 16) if n < 16 else (n - 16)]        
        
    def getotherpieces(self, livepieces):
        return set(self.__pieces) - set(livepieces)
    
    def setpieimgids(self, imgids):
        for n, piece in enumerate(self.__pieces):
            piece.imgid = imgids[n]
            
        
BlankPie = BlankPie(BlankChar)

 