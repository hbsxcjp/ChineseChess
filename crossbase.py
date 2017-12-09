'''
中国象棋棋盘位置交叉转换类型
'''

import re


BLACK_SIDE = True
RED_SIDE = False

TOP_SIDE = True
BOTTOM_SIDE = False

NumCols =  9
NumRows = 10

MinCol_K = 3
MaxCol_K = 5
MinRow_KB = 0
MaxRow_KB = 2
MinRow_KT = 7
MaxRow_KT = 9

MinColNo = 0
MaxColNo = 8
MinRowNo_B = 0
MaxRowNo_B = 4
MinRowNo_T = 5
MaxRowNo_T = 9


side_rowcols = {BOTTOM_SIDE: {(row, col) for row in range(MinRowNo_B, MaxRowNo_B + 1) 
                    for col in range(NumCols)},
                TOP_SIDE: {(row, col) for row in range(MinRowNo_T, MaxRowNo_T + 1)
                    for col in range(NumCols)}}

all_rowcols = side_rowcols[BOTTOM_SIDE] | side_rowcols[TOP_SIDE]

king_rowcols = {BOTTOM_SIDE: {(row, col) for row in range(MinRow_KB, 
                    MaxRow_KB + 1) for col in range(MinCol_K, MaxCol_K + 1)},
                TOP_SIDE: {(row, col) for row in range(MinRow_KT, 
                    MaxRow_KT + 1) for col in range(MinCol_K, MaxCol_K + 1)}}
    
advisor_rowcols = {BOTTOM_SIDE: {(row, col) for row, col in king_rowcols[BOTTOM_SIDE]
                    if (row + col) % 2 == 1},
                TOP_SIDE: {(row, col) for row, col in king_rowcols[TOP_SIDE]
                    if (row + col) % 2 == 0}}  
                    
bishop_rowcols = {BOTTOM_SIDE: {(row, col) for row, col in side_rowcols[BOTTOM_SIDE]
                    if (row % 2 == 0) and (row - col) in (2, -2, -6)},
                TOP_SIDE: {(row, col) for row, col in side_rowcols[TOP_SIDE]
                    if (row % 2 == 1) and (row - col) in (-1, 3, 7)}}

pawn_rowcols = {TOP_SIDE: side_rowcols[BOTTOM_SIDE] | ({(row, col) 
                    for row in range(MinRowNo_T, MinRowNo_T + 2)
                    for col in range(MinColNo, MaxColNo + 1, 2)}),
                BOTTOM_SIDE: side_rowcols[TOP_SIDE] | ({(row, col) 
                    for row in range(MaxRowNo_B - 1, MaxRowNo_B + 1)
                    for col in range(MinColNo, MaxColNo + 1, 2)})}


class CrossTuple(object):
    # 交叉元组类  

    @classmethod
    def getindex(cls, rowcol):
        return rowcol[0] * 9 + rowcol[1]
        
    @classmethod
    def getrowcol(cls, index):
        return (index // 9, index % 9)           
        
    @classmethod
    def getotherside(cls, side):        
        return RED_SIDE if side == BLACK_SIDE else BLACK_SIDE
        
    @classmethod
    def gettopside(cls, side):        
        return TOP_SIDE if side == BOTTOM_SIDE else BOTTOM_SIDE
        
    @classmethod
    def getrotaterowcol(cls, rowcol):
        row, col = rowcol
        return (abs(row - 9), abs(col - 8))
        
    @classmethod
    def getsymmetryrowcol(cls, rowcol):
        row, col = rowcol
        return (row, abs(col - 8))
 
    @classmethod
    def getkingmove_rowcols(cls, rowcol, piece, board):
        row, col = rowcol
        rowcols = (king_rowcols[board.getboardside(piece.side)] &
                {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)})
        return {rowcol for rowcol in rowcols if board.canmovepiece(rowcol, piece)}
        
    @classmethod
    def getadvisormove_rowcols(cls, rowcol, piece, board):
        row, col = rowcol
        rowcols = (advisor_rowcols[board.getboardside(piece.side)] &
                {(row + 1, col + 1), (row - 1, col + 1),
                (row - 1, col - 1), (row + 1, col - 1)})
        return {rowcol for rowcol in rowcols if board.canmovepiece(rowcol, piece)}                       
    @classmethod
    def getbishopmove_rowcols(cls, rowcol, piece, board):           
        # 获取象心、移动行列值集合
        def __cenx(first, to):
            return (first + to) // 2
            
        row, col = rowcol
        rowcols = {rowcol for rowcol in 
                    (bishop_rowcols[board.getboardside(piece.side)] &
                    {(row + 2, col + 2), (row - 2, col + 2),
                    (row - 2, col - 2), (row + 2, col - 2)})
                    if board.canmovepiece(rowcol, piece)}
        return {(brow, bcol) for brow, bcol in rowcols
                    if board.isblank((__cenx(row, brow), __cenx(col, bcol)))}

    @classmethod
    def getknightmove_rowcols(cls, rowcol, piece, board):    
        # 获取马腿、移动行列值字典
        def __legx(first, to):            
            x = to - first  
            return first + ((x // 2) if abs(x) == 2 else 0)
            
        def __getkinghtmove_rowcols(row, col):
            return {(row + 2, col - 1), (row + 2, col + 1),
                    (row + 1, col + 2), (row - 1, col + 2),
                    (row - 2, col + 1), (row - 2, col - 1),
                    (row - 1, col - 2), (row + 1, col - 2)}                
            
        row, col = rowcol
        rowcols = {rowcol for rowcol in 
                    (all_rowcols & __getkinghtmove_rowcols(row, col))
                    if board.canmovepiece(rowcol, piece)}
        return {(krow, kcol) for krow, kcol in rowcols
                if board.isblank((__legx(row, krow), __legx(col, kcol)))}
                
    @classmethod
    def rookcannonmove_lines(cls, rowcol):
        # 车炮可走的四个方向位置        
        row, col = rowcol
        ltcols = [(row, c) for c in range(col - 1, MinColNo - 1, -1)] # 左边位置列表
        ltrows = [(r, col) for r in range(row - 1, MinRowNo_B - 1, -1)] # 下边位置列表
        gtcols = [(row, c) for c in range(col + 1, MaxColNo + 1)] # 右边位置列表
        gtrows = [(r, col) for r in range(row + 1, MaxRowNo_T + 1)] # 上边位置列表        
        return ltcols, ltrows, gtcols, gtrows        
        
    @classmethod
    def getrookmove_rowcols(cls, rowcol, piece, board):                    
        result = set()
        lines = cls.rookcannonmove_lines(rowcol)       
        for rowcolline in lines:
            for rc in rowcolline:
                if board.isblank(rc):
                    result.add(rc)
                else:
                    if board.canmovepiece(rc, piece):
                        result.add(rc)
                    break
        #print('{}{}: {}'.format(piece, rowcol, result))
        return result 
        
    @classmethod
    def getcannonmove_rowcols(cls, rowcol, piece, board):
        result = set()
        lines = cls.rookcannonmove_lines(rowcol)
        for rowcolline in lines:
            skip = False
            for rc in rowcolline:
                if not skip:
                    if board.isblank(rc): 
                        result.add(rc)                     
                    else: # 该位置有棋子
                        skip = True
                elif (not board.isblank(rc) and 
                        board.canmovepiece(rc, piece)):
                    result.add(rc)
                    break
        #print('{}{}: {}'.format(piece, rowcol, result))
        return result 
        
    @classmethod
    def getpawnmove_rowcols(cls, rowcol, piece, board):
        result = set()
        row, col = rowcol
        isbottomside = board.isbottomside(piece.side)
        rowcols = {rowcol for rowcol in 
                    (pawn_rowcols[board.getboardside(piece.side)] &
                    {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)})
                    if board.canmovepiece(rowcol, piece)}
        for prow, pcol in rowcols:
            if (isbottomside and prow >= row) or (not isbottomside and prow <= row):
                result.add((prow, pcol))
        return result
        
        
# 调用交叉转换类型，可更换
CrossTrans = CrossTuple                    

        
def multrepl(text, xdict):
    # 一次替换多个子字符串（字典定义）（方法来源于PythonCook）
    rx = re.compile('|'.join(map(re.escape, xdict))) # 模式
    def one_xlat(match):
        return xdict[match.group(0)] # 替换值
    return rx.sub(one_xlat, text)  # 执行替换
    
        
class Model(object):
    # 数据模型基类
    #def __init__(self, views=[]):
    #    self.loadviews(views)
        
    def loadviews(self, views):
        self.__views = views
        
    def notifyviews(self):
        # 通知视图更新
        for view in self.__views:
            view.updateview()
            #print(type(self))
 
class View(object):

    def __init__(self, models):        
        self.chessboard, self.board, self.walks = models
        
    def updateview(self):
        # 更新视图（由数据模型发起）
        pass
        

        