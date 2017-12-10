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


class CrossTuple(object):
    # 交叉元组类  
    siderowcols = {BOTTOM_SIDE: {(row, col) for row in range(MinRowNo_B, MaxRowNo_B + 1) 
                        for col in range(NumCols)},
                    TOP_SIDE: {(row, col) for row in range(MinRowNo_T, MaxRowNo_T + 1)
                        for col in range(NumCols)}}

    allrowcols = siderowcols[BOTTOM_SIDE] | siderowcols[TOP_SIDE]

    kingrowcols = {BOTTOM_SIDE: {(row, col) for row in range(MinRow_KB, 
                        MaxRow_KB + 1) for col in range(MinCol_K, MaxCol_K + 1)},
                    TOP_SIDE: {(row, col) for row in range(MinRow_KT, 
                        MaxRow_KT + 1) for col in range(MinCol_K, MaxCol_K + 1)}}
        
    advisorrowcols = {BOTTOM_SIDE: {(row, col) for row, col in kingrowcols[BOTTOM_SIDE]
                        if (row + col) % 2 == 1},
                    TOP_SIDE: {(row, col) for row, col in kingrowcols[TOP_SIDE]
                        if (row + col) % 2 == 0}}  
                        
    bishoprowcols = {BOTTOM_SIDE: {(row, col) for row, col in siderowcols[BOTTOM_SIDE]
                        if (row % 2 == 0) and (row - col) in (2, -2, -6)},
                    TOP_SIDE: {(row, col) for row, col in siderowcols[TOP_SIDE]
                        if (row % 2 == 1) and (row - col) in (-1, 3, 7)}}

    pawnrowcols = {TOP_SIDE: siderowcols[BOTTOM_SIDE] | ({(row, col) 
                        for row in range(MinRowNo_T, MinRowNo_T + 2)
                        for col in range(MinColNo, MaxColNo + 1, 2)}),
                    BOTTOM_SIDE: siderowcols[TOP_SIDE] | ({(row, col) 
                        for row in range(MaxRowNo_B - 1, MaxRowNo_B + 1)
                        for col in range(MinColNo, MaxColNo + 1, 2)})}


    @classmethod
    def getindex(cls, rowcol):
        #return rowcol[0] * 9 + rowcol[1]
        return sorted(cls.allrowcols).index(rowcol)
        
    @classmethod
    def getrowcol(cls, index):
        #return (index // 9, index % 9) 
        return sorted(cls.allrowcols)[index]      
        
    @classmethod
    def getrotaterowcol(cls, rowcol):
        row, col = rowcol
        return (abs(row - MaxRowNo_T), abs(col - MaxColNo))
        
    @classmethod
    def getsymmetryrowcol(cls, rowcol):
        row, col = rowcol
        return (row, abs(col - MaxColNo))
        
    @classmethod
    def interrowcols(cls, moverowcols, rowcol, piece, board):
        return {rowcol for rowcol in (piece.getallrowcols(board) & moverowcols)
                if board.getside(rowcol) != piece.side}
        
    @classmethod
    def getkingmoverowcols(cls, rowcol, piece, board):
        row, col = rowcol
        moverowcols = {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}
        return cls.interrowcols(moverowcols, rowcol, piece, board)
        
    @classmethod
    def getadvisormoverowcols(cls, rowcol, piece, board):
        row, col = rowcol
        moverowcols = {(row + 1, col + 1), (row - 1, col + 1),
                        (row - 1, col - 1), (row + 1, col - 1)}
        return cls.interrowcols(moverowcols, rowcol, piece, board)
        
    @classmethod
    def getbishopmoverowcols(cls, rowcol, piece, board):           
        # 获取象心、移动行列值集合
        def __cenx(first, to):
            return (first + to) // 2
            
        row, col = rowcol
        moverowcols = {(row + 2, col + 2), (row - 2, col + 2),
                        (row - 2, col - 2), (row + 2, col - 2)}
        rowcols = cls.interrowcols(moverowcols, rowcol, piece, board)
        return {(brow, bcol) for brow, bcol in rowcols
                    if board.isblank((__cenx(row, brow), __cenx(col, bcol)))}

    @classmethod
    def getknightmoverowcols(cls, rowcol, piece, board):    
        # 获取马腿、移动行列值字典
        def __legx(first, to):            
            x = to - first  
            return first + ((x // 2) if abs(x) == 2 else 0)
            
        def __getkninghtmoverowcols(row, col):
            return {(row + 2, col - 1), (row + 2, col + 1),
                    (row + 1, col + 2), (row - 1, col + 2),
                    (row - 2, col + 1), (row - 2, col - 1),
                    (row - 1, col - 2), (row + 1, col - 2)}                
            
        row, col = rowcol
        moverowcols = __getkninghtmoverowcols(row, col)
        rowcols = cls.interrowcols(moverowcols, rowcol, piece, board)           
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
    def getrookmoverowcols(cls, rowcol, piece, board):                    
        result = set()
        lines = cls.rookcannonmove_lines(rowcol)       
        for rowcolline in lines:
            for rc in rowcolline:
                if board.isblank(rc):
                    result.add(rc)
                else:
                    if board.getside(rc) != piece.side:
                        result.add(rc)
                    break
        return result 
        
    @classmethod
    def getcannonmoverowcols(cls, rowcol, piece, board):
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
                        board.getside(rc) != piece.side):
                    result.add(rc)
                    break
        return result 
        
    @classmethod
    def getpawnmoverowcols(cls, rowcol, piece, board):
        row, col = rowcol
        isbottomside = board.isbottomside(piece.side)
        moverowcols = {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}
        rowcols = cls.interrowcols(moverowcols, rowcol, piece, board)        
        return {(prow, pcol) for prow, pcol in rowcols
                if (isbottomside and prow >= row) or (not isbottomside and prow <= row)}
        
        
class Model(object):
        
    def loadviews(self, views):
        self.__views = views
        
    def notifyviews(self):
        # 通知视图更新
        for view in self.__views:
            view.updateview()
 
class View(object):

    def __init__(self, models):        
        self.chessboard, self.board, self.walks = models
        
    def updateview(self):
        # 更新视图（由数据模型发起）
        pass
        

Cross = CrossTuple                    
# 调用交叉转换类型，可更换

        
def multrepl(text, xdict):
    # 一次替换多个子字符串（字典定义）（方法来源于PythonCook）
    rx = re.compile('|'.join(map(re.escape, xdict))) # 模式
    def one_xlat(match):
        return xdict[match.group(0)] # 替换值
    return rx.sub(one_xlat, text)  # 执行替换
    
        
        