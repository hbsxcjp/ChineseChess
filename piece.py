'''
中国象棋棋子类型 by-cjp
'''

from crossbase import *


BlankChar = '_' 
Chars = ['K', 'A', 'A', 'B', 'B', 'N', 'N', 'R', 'R', 
            'C', 'C', 'P', 'P', 'P', 'P', 'P',
        'k', 'a', 'a', 'b', 'b', 'n', 'n', 'r', 'r',
            'c', 'c', 'p', 'p', 'p', 'p', 'p']
# 全部棋子ch值列表
    
CharToNames = {'K':'帅', 'A':'仕', 'B':'相', 'N':'马',
               'R':'车', 'C':'炮', 'P':'兵', 
               'k':'将', 'a':'士', 'b':'象', 'n':'马',
               'r':'车', 'c':'炮', 'p':'卒', BlankChar: ''}
# 全部棋子ch值与中文名称映射字典
PawnNames = {'兵', '卒'}
AdvisorBishopNames = {'仕', '相', '士', '象'}
FullMovePieceNames = {'车', '马', '炮'}
StrongePieceNames = {'车', '马', '炮', '兵', '卒'}
LineMovePieceNames = {'帅', '将', '车', '炮', '兵', '卒'}


class Piece(object):
    # 棋子类

    def __init__(self, char):
        self.__side = (None if char == BlankChar else
                        (BLACK_SIDE if char.islower() else RED_SIDE))
        self.__char = char
        
    def __str__(self):
        return self.name    
        
    @property
    def side(self):
        return self.__side
        
    @property
    def char(self):
        return self.__char        
     
    @property
    def name(self):
        return CharToNames[self.__char]
        
    @classmethod
    def isStronge(self):
        return self.name in StrongePieceNames        
        
    def getallrowcols(self, rowcol, board):  
        # 全部活动范围集合(默认：车马炮的活动范围)
        return all_rowcols
    
    def getmoverowcols(self, rowcol, board):
        # 当前棋子所处位置的有效活动范围集合
        return {}       
        

class King(Piece):

    def getallrowcols(self, rowcol, board):  
        return king_rowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getkingmove_rowcols(rowcol, self, board)
        
        
class Advisor(Piece):
    
    def getallrowcols(self, rowcol, board):  
        return advisor_rowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getadvisormove_rowcols(rowcol, self, board)        
        
        
class Bishop(Piece):

    def getallrowcols(self, rowcol, board):  
        return bishop_rowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getbishopmove_rowcols(rowcol, self, board)
                
        
class Knight(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getknightmove_rowcols(rowcol, self, board)

                
class Rook(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getrookmove_rowcols(rowcol, self, board)

        
class Cannon(Piece):
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getcannonmove_rowcols(rowcol, self, board)
 
        
class Pawn(Piece):
    
    def getallrowcols(self, rowcol, board):  
        return pawn_rowcols[board.getboardside(self.side)]
        
    def getmoverowcols(self, rowcol, board):
        return CrossTrans.getpawnmove_rowcols(rowcol, self, board)        
        
        
CharPieces = {'K': King, 'A': Advisor, 'B': Bishop, 'N': Knight,
            'R': Rook, 'C': Cannon, 'P': Pawn}
# 生成棋子类字典
BlankPie = Piece(BlankChar)    

        
class Pieces(object):
    # 一副棋子类    
    
    def __init__(self):    
        self.__pieces = [CharPieces[char.upper()](char) for char in Chars]
        
    def __str__(self):
        return str([str(piece) for piece in self.__pieces])
        
    @property
    def pieces(self):
        return self.__pieces

    def getpiece(self, char, board):
        if char == BlankChar:
            return BlankPie
        for pie in self.__pieces:
            if pie.char == char and pie not in board.getlivecrosses().values():
                return pie
        assert False, '找不到空闲的棋子: ' + char
        
    def getkingpiece(self, side):
        return self.__pieces[0 if side == RED_SIDE else 16]
        
    def getothersidepiece(self, piece):
        n = self.__pieces.index(piece)
        return self.__pieces[(n + 16) if piece.side == RED_SIDE else (n - 16)]        
        
    def getsidepieces(self, side):
        return self.__pieces[:16] if side == RED_SIDE else self.__pieces[16:]        

    def getpieimgids(self, side):
        return {pie.imgid for pie in self.__pieces if pie.side == side}
        
        
        