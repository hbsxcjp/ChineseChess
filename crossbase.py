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
    sideseats = {BOTTOM_SIDE: {(row, col) for row in range(MinRowNo_B, MaxRowNo_B + 1) 
                        for col in range(NumCols)},
                    TOP_SIDE: {(row, col) for row in range(MinRowNo_T, MaxRowNo_T + 1)
                        for col in range(NumCols)}}

    allseats = sideseats[BOTTOM_SIDE] | sideseats[TOP_SIDE]

    kingseats = {BOTTOM_SIDE: {(row, col) for row in range(MinRow_KB, 
                        MaxRow_KB + 1) for col in range(MinCol_K, MaxCol_K + 1)},
                    TOP_SIDE: {(row, col) for row in range(MinRow_KT, 
                        MaxRow_KT + 1) for col in range(MinCol_K, MaxCol_K + 1)}}
        
    advisorseats = {BOTTOM_SIDE: {(row, col) for row, col in kingseats[BOTTOM_SIDE]
                        if (row + col) % 2 == 1},
                    TOP_SIDE: {(row, col) for row, col in kingseats[TOP_SIDE]
                        if (row + col) % 2 == 0}}  
                        
    bishopseats = {BOTTOM_SIDE: {(row, col) for row, col in sideseats[BOTTOM_SIDE]
                        if (row % 2 == 0) and (row - col) in (2, -2, -6)},
                    TOP_SIDE: {(row, col) for row, col in sideseats[TOP_SIDE]
                        if (row % 2 == 1) and (row - col) in (-1, 3, 7)}}

    pawnseats = {TOP_SIDE: sideseats[BOTTOM_SIDE] | ({(row, col) 
                        for row in range(MinRowNo_T, MinRowNo_T + 2)
                        for col in range(MinColNo, MaxColNo + 1, 2)}),
                    BOTTOM_SIDE: sideseats[TOP_SIDE] | ({(row, col) 
                        for row in range(MaxRowNo_B - 1, MaxRowNo_B + 1)
                        for col in range(MinColNo, MaxColNo + 1, 2)})}


    @classmethod
    def getindex(cls, seat):
        #return seat[0] * 9 + seat[1]
        return sorted(cls.allseats).index(seat)
        
    @classmethod
    def getseat(cls, index):
        #return (index // 9, index % 9) 
        return sorted(cls.allseats)[index]      
        
    @classmethod
    def mergeseat(cls, row, col): 
        return (row, col)    
        
    @classmethod
    def getrow(cls, seat):
        return seat[0]      
        
    @classmethod
    def getcol(cls, seat):
        return seat[1]      
        
    @classmethod
    def issamecol(cls, seat, otherseat):
        return seat[1] == otherseat[1]
        
    @classmethod
    def getsamecolseats(cls, seat, otherseat):
        row, col = seat
        otherrow, othercol = otherseat        
        step = 1 if row < otherrow else -1
        return [(r, col) for r in range(row + step, otherrow, step)]
        
    @classmethod
    def getrotateseat(cls, seat):
        row, col = seat
        return (abs(row - MaxRowNo_T), abs(col - MaxColNo))
        
    @classmethod
    def getsymmetryseat(cls, seat):
        row, col = seat
        return (row, abs(col - MaxColNo))
        
    @classmethod
    def interseats(cls, moveseats, seat, piece, board):
        return {seat for seat in (piece.getallseats(board) & moveseats)
                if board.getside(seat) != piece.side}
        
    @classmethod
    def getkingmoveseats(cls, seat, piece, board):
        def __kingmov(row, col):
            return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}
                        
        row, col = seat
        return cls.interseats(__kingmov(row, col), seat, piece, board)
        
    @classmethod
    def getadvisormoveseats(cls, seat, piece, board):
        def __advisormov(row, col):
            return {(row + 1, col + 1), (row - 1, col + 1),
                        (row - 1, col - 1), (row + 1, col - 1)}
                        
        row, col = seat
        return cls.interseats(__advisormov(row, col), seat, piece, board)
        
    @classmethod
    def getbishopmoveseats(cls, seat, piece, board):           
        # 获取象心、移动行列值集合
        def __cenx(first, to):
            return (first + to) // 2
            
        def __bishopmov(row, col):
            return {(row + 2, col + 2), (row - 2, col + 2),
                        (row - 2, col - 2), (row + 2, col - 2)}
                        
        row, col = seat
        seats = cls.interseats(__bishopmov(row, col), seat, piece, board)
        return {(brow, bcol) for brow, bcol in seats
                    if board.isblank((__cenx(row, brow), __cenx(col, bcol)))}

    @classmethod
    def getknightmoveseats(cls, seat, piece, board):    
        # 获取马腿、移动行列值字典
        def __legx(first, to):            
            x = to - first  
            return first + ((x // 2) if abs(x) == 2 else 0)
            
        def __kninghtmov(row, col):
            return {(row + 2, col - 1), (row + 2, col + 1),
                    (row + 1, col + 2), (row - 1, col + 2),
                    (row - 2, col + 1), (row - 2, col - 1),
                    (row - 1, col - 2), (row + 1, col - 2)}                
            
        row, col = seat
        seats = cls.interseats(__kninghtmov(row, col), seat, piece, board)           
        return {(krow, kcol) for krow, kcol in seats
                if board.isblank((__legx(row, krow), __legx(col, kcol)))}
                
    @classmethod
    def rookcannonmove_lines(cls, seat):
        # 车炮可走的四个方向位置        
        row, col = seat
        return ([(row, c) for c in range(col - 1, MinColNo - 1, -1)], # 左边位置列表
                [(r, col) for r in range(row - 1, MinRowNo_B - 1, -1)], # 下边位置列表
                [(row, c) for c in range(col + 1, MaxColNo + 1)], # 右边位置列表
                [(r, col) for r in range(row + 1, MaxRowNo_T + 1)]) # 上边位置列表        
        
    @classmethod
    def getrookmoveseats(cls, seat, piece, board):                    
        result = set()
        lines = cls.rookcannonmove_lines(seat)       
        for seatline in lines:
            for rc in seatline:
                if board.isblank(rc):
                    result.add(rc)
                else:
                    if board.getside(rc) != piece.side:
                        result.add(rc)
                    break
        return result 
        
    @classmethod
    def getcannonmoveseats(cls, seat, piece, board):
        result = set()
        lines = cls.rookcannonmove_lines(seat)
        for seatline in lines:
            skip = False
            for rc in seatline:
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
    def getpawnmoveseats(cls, seat, piece, board):
        def __pawnmov(row, col):
            return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}
            
        row, col = seat
        isbottomside = board.isbottomside(piece.side)
        seats = cls.interseats(__pawnmov(row, col), seat, piece, board)        
        return {(prow, pcol) for prow, pcol in seats
                if (isbottomside and prow >= row) or (not isbottomside and prow <= row)}
        
        
class Model(object):
        
    def loadviews(self, views):
        self.views = views
        
    def notifyviews(self):
        # 通知视图更新
        for view in self.views:
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
    
        
        