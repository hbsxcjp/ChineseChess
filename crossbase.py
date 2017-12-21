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
                
                
class CrossInt(object):
    # 交叉整数类  
    sideseats = {BOTTOM_SIDE: {i for i in range(45)},
                    TOP_SIDE: {j for j in range(45, 90)}}

    allseats = sideseats[BOTTOM_SIDE] | sideseats[TOP_SIDE]

    kingseats = {BOTTOM_SIDE: {3, 4, 5, 12, 13, 14, 21, 22, 23},
                    TOP_SIDE: {66, 67, 68, 75, 76, 77, 84, 85, 86}}
        
    advisorseats = {BOTTOM_SIDE: {3, 5, 13, 21, 23},
                    TOP_SIDE: {66, 68, 76, 84, 86}}  
                        
    bishopseats = {BOTTOM_SIDE: {2, 6, 18, 22, 26, 38, 42},
                    TOP_SIDE: {47, 51, 63, 67, 71, 83, 87}}

    pawnseats = {TOP_SIDE: sideseats[BOTTOM_SIDE] | {45, 47, 49, 51, 53,
                                                    54, 56, 58, 60, 62},
                    BOTTOM_SIDE: sideseats[TOP_SIDE] | {27, 29, 31, 33, 35,
                                                        36, 38, 40, 42, 44}}

    @classmethod
    def getindex(cls, seat):
        return seat
        
    @classmethod
    def getseat(cls, index):
        return index
        
    @classmethod
    def mergeseat(cls, row, col): 
        return row * 9 + col
        
    @classmethod
    def getrow(cls, seat): 
        return seat // 9
        
    @classmethod
    def getcol(cls, seat):
        return seat % 9
        
    @classmethod
    def issamecol(cls, seat, otherseat):
        return seat % 9 == otherseat % 9
        
    @classmethod
    def getsamecolseats(cls, seat, otherseat):
        step = 9 if seat < otherseat else -1
        return list(range(seat + step, otherseat, step))
        
    @classmethod
    def getrotateseat(cls, seat):
        return abs(seat - 89)
        
    @classmethod
    def getsymmetryseat(cls, seat):
        return (seat // 9 + 1) * 9 - seat % 9 - 1
        
    @classmethod
    def interseats(cls, moveseats, seat, piece, board):
        return {seat for seat in moveseats if board.getside(seat) != piece.side}
        
    @classmethod
    def getkingmoveseats(cls, seat, piece, board):    
        __kingmovs = {3:(4, 12), 4:(3, 5, 13), 5:(4, 14),
                     12:(3, 13, 21), 13:(4, 12, 14, 22), 14:(5, 13, 23),
                     21:(12, 22), 22:(13, 21, 23), 23:(14, 22),
                     66:(67, 75), 67:(66, 68, 76), 68:(67, 77),
                     75:(66, 76, 84), 76:(67, 75, 77, 85), 77:(68, 76, 86),
                     84:(75, 85), 85:(76, 84, 86), 86:(77, 85)}
                        
        return cls.interseats(__kingmovs[seat], seat, piece, board)
        
    @classmethod
    def getadvisormoveseats(cls, seat, piece, board):    
        __advisormovs = {3:(13,), 5:(13,), 21:(13,), 23:(13,),
                         13:(3, 5, 21, 23),
                         66:(76,), 68:(76,), 84:(76,), 86:(76,),
                         76:(66, 68, 84, 86)}
                        
        return cls.interseats(__advisormovs[seat], seat, piece, board)
        
    @classmethod
    def getbishopmoveseats(cls, seat, piece, board):
        __bishopmovs = {2:(18, 22), 6:(22, 26), 18:(2, 38),
                         22:(2, 6, 38, 42), 26:(6, 42),
                         38:(18, 22), 42:(22, 26),
                         47:(63, 67), 51:(67, 71), 63:(47, 83),
                         67:(47, 51, 83, 87), 71:(51, 87),
                         83:(63, 67), 87:(67, 71)}
                         
        seats = {s for s in __bishopmovs[seat] if board.isblank((s+seat)//2)}
        return cls.interseats(seats, seat, piece, board)

    @classmethod
    def getknightmoveseats(cls, seat, piece, board): 

        legoffset = {-19: -9, -17: -9, 17: 9, 19: 9,
                   -11: -1, 7: -1, -7: 1, 11: 1}
        # 马移动偏移量:马腿偏移量
        offset = {-19, -17, -11, -7, 7, 11, 17, 19}
        # 马可走位置偏移量 
        offset_c = {0: {-17, -7, 11, 19},
                      1: {-19, -17, -7, 11, 17, 19},
                      7: {-19, -17, -11, 7, 17, 19},
                      8: {-19, -11, 7, 17}}
        offset_r = {0: {7, 11, 17,19},
                      1: {-11, -7, 7, 11, 17, 19},
                      8: {-19, -17, -11, -7, 7, 11},
                      9: {-19, -17, -11, -7}}                 
        # 两者交集 seat%9(0,1,7,8) & seat//9(0,1,8,9)，筛除外溢位置    

        def __knightmovs_seatandlegs(seat):
            return [(seat+offset, seat+legoffset[offset]) for offset
                    in (offset_c.get(cls.getcol(seat), offset)
                    & offset_r.get(cls.getrow(seat), offset))]     
        
        seats = {s for s, leg in __knightmovs_seatandlegs(seat) if board.isblank(leg)}
        return cls.interseats(seats, seat, piece, board)
                
    @classmethod
    def rookcannonmove_lines(cls, seat):
        # 车炮可走的四个方向位置        
        r = cls.getrow(seat)
        return [range(seat-1, r*9-1, -1), range(seat+1, (r+1)*9),
                range(seat-9, -1, -9), range(seat+9, 90, 9)]       
        
    @classmethod
    def getrookmoveseats(cls, seat, piece, board):                    
        seats = set()
        lines = cls.rookcannonmove_lines(seat)       
        for seatline in lines:
            for s in seatline:
                seats.add(s)
                if not board.isblank(s):
                    break
        return cls.interseats(seats, seat, piece, board)
        
    @classmethod
    def getcannonmoveseats(cls, seat, piece, board):
        seats = set()
        lines = cls.rookcannonmove_lines(seat)
        for seatline in lines:
            skip = False
            for s in seatline:
                if not skip:
                    if board.isblank(s): 
                        seats.add(s)
                    else: # 该位置有棋子
                        skip = True
                elif not board.isblank(s):
                    seats.add(s)
                    break
        return cls.interseats(seats, seat, piece, board)
        
    @classmethod
    def getpawnmoveseats(cls, seat, piece, board):
        row, col = cls.getrow(seat), cls.getcol(seat)       
        isbottomside = board.isbottomside(piece.side)
        river = isbottomside == (row > MaxRowNo_B) # 已过河界
        
        offset_c = 9 if isbottomside else -9
        offsets = {offset_c, -1, 1} if river else {offset_c}
        if river:
            if col == MinColNo:
                offsets.remove(-1)
            elif col == MaxColNo:
                offsets.remove(1)
            if ((isbottomside and row == MaxRowNo_T) or
                (not isbottomside and row == MinRowNo_B)):
                offsets.remove(offset_c)
        seats = {seat + offset for offset in offsets}
        return cls.interseats(seats, seat, piece, board)
        
        
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
        
#Cross = CrossInt
Cross = CrossTuple                    
# 调用交叉转换类型，可更换

        
def multrepl(text, xdict):
    # 一次替换多个子字符串（字典定义）（方法来源于PythonCook）
    rx = re.compile('|'.join(map(re.escape, xdict))) # 模式
    def one_xlat(match):
        return xdict[match.group(0)] # 替换值
    return rx.sub(one_xlat, text)  # 执行替换
    
        
        