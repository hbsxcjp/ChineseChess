'中国象棋棋盘位置交叉类型'

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
    '交叉元组类'
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
    
    def getindex(self, seat):
        return sorted(self.allseats).index(seat)        
    
    def getseat(self, index):
        return sorted(self.allseats)[index]
    
    def mergeseat(self, row, col): 
        return (row, col)
    
    def getrow(self, seat):
        return seat[0]        
    
    def getcol(self, seat):
        return seat[1]        
    
    def issamecol(self, seat, otherseat):
        return seat[1] == otherseat[1]
    
    def getsamecolseats(self, seat, otherseat):
        row, col = seat
        otherrow, othercol = otherseat        
        step = 1 if row < otherrow else -1
        return [(r, col) for r in range(row + step, otherrow, step)]        
    
    def getrotateseat(self, seat):
        row, col = seat
        return (abs(row - MaxRowNo_T), abs(col - MaxColNo))        
    
    def getsymmetryseat(self, seat):
        row, col = seat
        return (row, abs(col - MaxColNo))
        
    def getkingmoveseats(self, seat):
        row, col = seat
        return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}
    
    def getadvisormoveseats(self, seat):
        row, col = seat
        return {(row + 1, col + 1), (row - 1, col + 1),
                (row - 1, col - 1), (row + 1, col - 1)}
    
    def getbishopmove_centreseats(self, seat):           
        '获取移动、象心行列值'
        row, col = seat
        moveseats = {(row + 2, col + 2), (row - 2, col + 2),
                    (row - 2, col - 2), (row + 2, col - 2)}
        return {(r, c): ((row+r)//2, (col+c)//2) for r, c in moveseats}
    
    def getknightmove_legseats(self, seat):    
        '获取移动、马腿行列值'
        def __legx(first, to):            
            x = to - first  
            return first + ((x // 2) if abs(x) == 2 else 0)
            
        row, col = seat
        moveseats = {(row + 2, col - 1), (row + 2, col + 1),
                    (row + 1, col + 2), (row - 1, col + 2),
                    (row - 2, col + 1), (row - 2, col - 1),
                    (row - 1, col - 2), (row + 1, col - 2)}                
        return {(r, c): (__legx(row, r), __legx(col, c)) for r, c in moveseats}
    
    def rookcannonmoveseat_lines(self, seat):
        '车炮可走的四个方向位置'        
        row, col = seat
        return ([(row, c) for c in range(col - 1, MinColNo - 1, -1)], # 左边位置列表
                [(r, col) for r in range(row - 1, MinRowNo_B - 1, -1)], # 下边位置列表
                [(row, c) for c in range(col + 1, MaxColNo + 1)], # 右边位置列表
                [(r, col) for r in range(row + 1, MaxRowNo_T + 1)]) # 上边位置列表
    
    def getpawnmoveseats(self, seat):
        row, col = seat
        return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}            


CrossT = CrossTuple()
# 调用交叉转换类型，可更换

        
def multrepl(text, xdict):
    '一次替换多个子字符串（字典定义）（方法来源于PythonCook）'
    rx = re.compile('|'.join(map(re.escape, xdict))) # 模式
    def one_xlat(match):
        return xdict[match.group(0)] # 替换值
    return rx.sub(one_xlat, text)  # 执行替换
    
        
        