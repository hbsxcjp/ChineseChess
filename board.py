'''
中国象棋棋盘类型
'''

import base
from piece import *


TOP_SIDE = True
BOTTOM_SIDE = False

NumCols = 9
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


# yapf: disable
NumToChinese = {RED_P: {1:'一', 2:'二', 3:'三', 4:'四', 5:'五',
                    6:'六', 7:'七', 8:'八', 9:'九'}, # 数字转换成中文
                BLACK_P: {1:'１', 2:'２', 3:'３', 4:'４', 5:'５',
                    6:'６', 7:'７', 8:'８', 9:'９'}}
ChineseToNum = {'一':1, '二':2, '三':3, '四':4, '五':5,
                '六':6, '七':7, '八':8, '九':9, # 中文转换成数字
                '１':1, '２':2, '３':3, '４':4, '５':5,
                '６':6, '７':7, '８':8, '９':9,
                '前':0, '中':1, '后':-1, # 走棋文字转换成数字
                '进':1, '退':-1, '平':0 }
# yapf: enable

 
class Board(object):
    '棋盘类'
    
    sideseats = {
        BOTTOM_SIDE: {(row, col)
                      for row in range(MinRowNo_B, MaxRowNo_B + 1)
                      for col in range(NumCols)},
        TOP_SIDE: {(row, col)
                   for row in range(MinRowNo_T, MaxRowNo_T + 1)
                   for col in range(NumCols)}
    }

    allseats = sideseats[BOTTOM_SIDE] | sideseats[TOP_SIDE]

    kingseats = {
        BOTTOM_SIDE: {(row, col)
                      for row in range(MinRow_KB, MaxRow_KB + 1)
                      for col in range(MinCol_K, MaxCol_K + 1)},
        TOP_SIDE: {(row, col)
                   for row in range(MinRow_KT, MaxRow_KT + 1)
                   for col in range(MinCol_K, MaxCol_K + 1)}
    }

    advisorseats = {
        BOTTOM_SIDE: {(row, col)
                      for row, col in kingseats[BOTTOM_SIDE]
                      if (row + col) % 2 == 1},
        TOP_SIDE: {(row, col)
                   for row, col in kingseats[TOP_SIDE] if (row + col) % 2 == 0}
    }

    bishopseats = {
        BOTTOM_SIDE: {(row, col)
                      for row, col in sideseats[BOTTOM_SIDE]
                      if (row % 2 == 0) and (row - col) in (2, -2, -6)},
        TOP_SIDE: {(row, col)
                   for row, col in sideseats[TOP_SIDE]
                   if (row % 2 == 1) and (row - col) in (-1, 3, 7)}
    }

    pawnseats = {
        TOP_SIDE:
        sideseats[BOTTOM_SIDE] |
        ({(row, col)
          for row in range(MinRowNo_T, MinRowNo_T + 2)
          for col in range(MinColNo, MaxColNo + 1, 2)}),
        BOTTOM_SIDE:
        sideseats[TOP_SIDE] |
        ({(row, col)
          for row in range(MaxRowNo_B - 1, MaxRowNo_B + 1)
          for col in range(MinColNo, MaxColNo + 1, 2)})
    }
    
    #sorted_allseats = sorted(allseats)

    @classmethod
    def getindex(cls, seat):
        #return cls.sorted_allseats.index(seat)
        return seat[0]*9 + seat[1]

    @classmethod
    def getseat(cls, index):
        #return cls.sorted_allseats[index]
        return (index//9, index%9)

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
        step = 1 if row < otherseat[0] else -1
        return [(r, col) for r in range(row + step, otherseat[0], step)]

    @classmethod
    def getrotateseat(cls, seat):
        row, col = seat
        return (abs(row - MaxRowNo_T), abs(col - MaxColNo))

    @classmethod
    def getsymmetryseat(cls, seat):
        row, col = seat
        return (row, abs(col - MaxColNo))

    @classmethod
    def getkingmoveseats(cls, seat):
        row, col = seat
        return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}

    @classmethod
    def getadvisormoveseats(cls, seat):
        row, col = seat
        return {(row + 1, col + 1), (row - 1, col + 1), (row - 1, col - 1),
                (row + 1, col - 1)}

    @classmethod
    def getbishopmove_centreseats(cls, seat):
        '获取移动、象心行列值'
        row, col = seat
        moveseats = {(row + 2, col + 2), (row - 2, col + 2),
                     (row - 2, col - 2), (row + 2, col - 2)}
        return {(r, c): ((row + r) // 2, (col + c) // 2) for r, c in moveseats}

    @classmethod
    def getknightmove_legseats(cls, seat):
        '获取移动、马腿行列值'

        def __legx(first, to):
            x = to - first
            return first + ((x // 2) if abs(x) == 2 else 0)

        row, col = seat
        moveseats = {(row + 2, col - 1), (row + 2, col + 1),
                     (row + 1, col + 2), (row - 1, col + 2), (row - 2,
                                                              col + 1),
                     (row - 2, col - 1), (row - 1, col - 2), (row + 1,
                                                              col - 2)}
        return {(r, c): (__legx(row, r), __legx(col, c)) for r, c in moveseats}

    @classmethod
    def rookcannonmoveseat_lines(cls, seat):
        '车炮可走的四个方向位置'
        row, col = seat
        return (
            [(row, c) for c in range(col - 1, MinColNo - 1, -1)],  # 左边位置列表
            [(r, col) for r in range(row - 1, MinRowNo_B - 1, -1)],  # 下边位置列表
            [(row, c) for c in range(col + 1, MaxColNo + 1)],  # 右边位置列表
            [(r, col) for r in range(row + 1, MaxRowNo_T + 1)])  # 上边位置列表

    @classmethod
    def getpawnmoveseats(cls, seat):
        row, col = seat
        return {(row, col + 1), (row, col - 1), (row - 1, col), (row + 1, col)}

    def __init__(self, fen=''):
        self.seat_pies = dict.fromkeys(self.allseats, BlankPie)
        self.pieces = Pieces()
        self.bottomside = BLACK_P
        if fen:
            self.setfen(fen)

    def __str__(self):

        def __getname(piece):
            rookcannonpawn_name = {'车': '車', '马': '馬', '炮': '砲'}
            name = piece.name
            return (rookcannonpawn_name.get(name, name)
                    if piece.color == BLACK_P else name)

        def __fillingname():
            linestr = [
                list(line.strip()) for line in base.blankboard.strip().splitlines()
            ]
            for piece in self.getlivepieces():
                seat = piece.seat
                linestr[(MaxRowNo_T - self.getrow(seat)) *
                        2][self.getcol(seat) * 2] = __getname(piece)
            return [''.join(line) for line in linestr]

        frontstr = '\n'
        return '{}{}{}'.format(frontstr, frontstr.join(__fillingname()), '\n')

    def clear(self):
        for seat in self.allseats:
            self.seat_pies[seat] = BlankPie
        self.pieces.clear()

    def setpiece(self, seat, piece):
        self.seat_pies[seat] = piece
        piece.setseat(seat)

    def movepiece(self, fromseat, toseat, backpiece=BlankPie):
        eatpiece = self.seat_pies[toseat]
        eatpiece.setseat(None)
        self.setpiece(toseat, self.seat_pies[fromseat])
        self.setpiece(fromseat, backpiece)
        return eatpiece

    def setbottomside(self):
        self.bottomside = (RED_P if self.getrow(
            self.getkingseat(RED_P)) < MaxRowNo_B else BLACK_P)

    def isbottomside(self, color):
        return BOTTOM_SIDE == self.getboardside(color)

    def isblank(self, seat):
        return not bool(self.seat_pies[seat]) # is BlankPie

    def getpiece(self, seat):
        return self.seat_pies[seat]

    def getcolorside(self, seat):
        return self.seat_pies[seat].color

    def getboardside(self, color):
        return BOTTOM_SIDE if self.bottomside == color else TOP_SIDE

    def getkingpiece(self, color):
        return self.pieces.getkingpiece(color)

    def getkingseat(self, color):
        return self.getkingpiece(color).seat

    def getlivepieces(self):
        return self.pieces.getlivepieces()

    def geteatedpieces(self):
        return self.pieces.geteatedpieces()

    def getlivesidepieces(self, color):
        return {piece for piece in self.getlivepieces() if piece.color == color}

    def getlivesidenamepieces(self, color, name):
        return {
            piece
            for piece in self.getlivesidepieces(color) if piece.name == name
        }

    def getlivesidenamecolpieces(self, color, name, col):
        return {
            piece
            for piece in self.getlivesidenamepieces(color, name)
            if self.getcol(piece.seat) == col
        }

    def iskilled(self, color):
        othercolor = not color
        kingseat, otherseat = self.getkingseat(color), self.getkingseat(
            othercolor)
        if self.issamecol(kingseat, otherseat):  # 将帅是否对面
            if all([
                    self.isblank(seat)
                    for seat in self.getsamecolseats(kingseat, otherseat)
            ]):
                return True
        for piece in self.getlivesidepieces(othercolor):
            if piece.isStronge and (kingseat in piece.getmoveseats(self)):
                return True
        return False

    def canmoveseats(self, piece):
        '获取棋子可走的位置, 不能被将军'
        result = []
        fromseat, color = piece.seat, piece.color
        for toseat in piece.getmoveseats(self):
            topiece = self.movepiece(fromseat, toseat)
            if not self.iskilled(color):
                result.append(toseat)
            self.movepiece(toseat, fromseat, topiece)
        return result
        
    def isdied(self, color):
        return not any([
            self.canmoveseats(piece) for piece in self.getlivesidepieces(color)
        ])

    def loadseatpieces(self, seatpieces):
        self.clear()
        [self.setpiece(seat, piece) for seat, piece in seatpieces.items()]
        self.setbottomside()

    def setfen(self, fen):
        def __numtolines():
            '数字字符: 下划线字符串'
            numtolines = {}
            for i in range(1, 10):
                numtolines[str(i)] = '_' * i
            return numtolines

        def __isvalid(charls):
            '判断棋子列表是否有效'
            if len(charls) != 90:
                return False, 'len(charls) != 90' #'棋局的位置个数不等于90，有误！'
            chars = [c for c in charls if c != BlankChar]
            if len(chars) > 32:
                return False, 'len(chars) > 32' #'全部的棋子个数大于32个，有误！'
            for c in chars:
                if chars.count(c) > Pieces.Chars.count(c):
                    return False, 'chars.count(c) > Pieces.Chars.count(c)'
                    #'棋子: %s 的个数大于规定个数，有误！' % c
            return True, ''

        fenstr = ''.join(fen.split('/')[::-1])
        charls = list(base.multrepl(fenstr, __numtolines()))

        isvalid, info = __isvalid(charls)
        #print(fen, len(fen))
        assert isvalid, info

        seatchars = {self.getseat(n): char for n, char in enumerate(charls)}
        self.loadseatpieces(self.pieces.getseatpieces(seatchars))

    def getfen(self, piecechars=None):
        def __linetonums():
            '下划线字符串对应数字字符元组 列表'
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
            
        if not piecechars:
            piecechars = [
                piece.char for seat, piece in sorted(self.seat_pies.items())
            ]
        charls = [
            piecechars[rowno * NumCols:(rowno + 1) * NumCols]
            for rowno in range(NumRows)
        ]
        fen = '/'.join([''.join(chars) for chars in charls[::-1]])
        for _str, nstr in __linetonums():
            fen = fen.replace(_str, nstr)
        return fen
        
    def __sortpawnseats(self, isbottomside, pawnseats):
        '多兵排序'
        result = []
        pawnseatdict = {self.getcol(seat): [] for seat in pawnseats}
        for seat in pawnseats:
            pawnseatdict[self.getcol(seat)].append(seat)  # 列内排序
        for col, seats in sorted(pawnseatdict.items()):
            if len(seats) > 1:
                result.extend(seats)  # 按列排序
        return result[::-1] if isbottomside else result

    def chinese_moveseats(self, color, chinese):
        '根据中文纵线着法描述取得源、目标位置: (fromseat, toseat)'

        def __chcol_col(zhcol):
            return (NumCols - ChineseToNum[zhcol]
                    if isbottomside else ChineseToNum[zhcol] - 1)

        def __movzh_movdir(movchar):
            '根据中文行走方向取得棋子的内部数据方向（进：1，退：-1，平：0）'
            return ChineseToNum[movchar] * (1 if isbottomside else -1)

        def __indexname_fromseat(index, name, seats):
            if name in PawnNames:
                seats = self.__sortpawnseats(isbottomside, seats)  # 获取多兵的列
                if len(seats) > 3:
                    index -= 1  # 修正index
            elif isbottomside:
                seats = seats[::-1]
            return seats[index]

        def __linename_toseat(fromseat, movdir, tocol, tochar):
            '获取直线走子toseat'
            row, col = self.getrow(fromseat), self.getcol(fromseat)
            return ((row, tocol)
                    if movdir == 0 else (
                        row + movdir * ChineseToNum[tochar], col))

        def __obliquename_toseat(fromseat, movdir, tocol, isAdvisorBishop):
            '获取斜线走子：仕、相、马toseat'
            row, col = self.getrow(fromseat), self.getcol(fromseat)
            step = tocol - col  # 相距1或2列
            inc = abs(step) if isAdvisorBishop else (2
                                                     if abs(step) == 1 else 1)
            return (row + movdir * inc, tocol)

        isbottomside = self.isbottomside(color)
        name = chinese[0]
        if name in CharToNames.values():
            seats = sorted([
                piece.seat
                for piece in self.getlivesidenamecolpieces(
                    color, name, __chcol_col(chinese[1]))
            ])
            assert bool(seats), ('没有找到棋子 => %s color:%s name: %s\n%s' %
                                 (chinese, color, name, self))

            index = (-1 if (len(seats) == 2 and name in AdvisorBishopNames
                            and ((chinese[2] == '退') == isbottomside)) else 0)
            # 排除：士、象同列时不分前后，以进、退区分棋子
            fromseat = seats[index]
        else:
            # 未获得棋子, 查找某个排序（前后中一二三四五）某方某个名称棋子
            index, name = ChineseToNum[chinese[0]], chinese[1]
            seats = sorted(
                [pie.seat for pie in self.getlivesidenamepieces(color, name)])
            assert len(seats) >= 2, 'color: %s name: %s 棋子列表少于2个! \n%s' % (color,
                                                                          name,
                                                                          self)
            fromseat = __indexname_fromseat(index, name, seats)

        movdir = __movzh_movdir(chinese[2])
        tocol = __chcol_col(chinese[3])
        toseat = (__linename_toseat(fromseat, movdir, tocol, chinese[3])
                  if name in LineMovePieceNames else __obliquename_toseat(
                      fromseat, movdir, tocol, name in AdvisorBishopNames))
        #assert chinese == self.moveseats_chinese(fromseat, toseat), ('棋谱着法: %s   生成着法: %s 不等！' % (chinese, self.moveseats_chinese(fromseat, toseat)))

        return (fromseat, toseat)

    def moveseats_chinese(self, fromseat, toseat):
        '根据源、目标位置: (fromseat, toseat)取得中文纵线着法描述'
        def __col_chcol(color, col):
            return NumToChinese[color][NumCols - col
                                      if isbottomside else col + 1]

        frompiece = self.getpiece(fromseat)
        color, name = frompiece.color, frompiece.name
        isbottomside = self.isbottomside(color)
        fromrow, fromcol = self.getrow(fromseat), self.getcol(fromseat)
        seats = sorted([
            pie.seat
            for pie in self.getlivesidenamecolpieces(color, name, fromcol)
        ])
        length = len(seats)
        if length > 1 and name in StrongePieceNames:
            if name in PawnNames:
                seats = self.__sortpawnseats(
                    isbottomside,
                    sorted([
                        pie.seat
                        for pie in self.getlivesidenamepieces(color, name)
                    ]))
                length = len(seats)
            elif isbottomside:  # '车', '马', '炮'
                seats = seats[::-1]
            indexstr = {2: '前后', 3: '前中后'}.get(length, '一二三四五')
            firstStr = indexstr[seats.index(fromseat)] + name
        else:
            #仕(士)和相(象)不用“前”和“后”区别，因为能退的一定在前，能进的一定在后
            firstStr = name + __col_chcol(color, fromcol)

        torow, tocol = self.getrow(toseat), self.getcol(toseat)
        chcol = __col_chcol(color, tocol)
        tochar = ('平' if torow == fromrow else
                  ('进' if isbottomside == (torow > fromrow) else '退'))
        tochcol = (chcol if torow == fromrow or name not in LineMovePieceNames
                   else NumToChinese[color][abs(torow - fromrow)])
        lastStr = tochar + tochcol

        '''
        assert (fromseat, toseat) == self.chinese_moveseats(
            color, firstStr + lastStr), '棋谱着法: %s 生成着法: %s 不等！' % (
                (fromseat, toseat),
                self.chinese_moveseats(color, firstStr + lastStr))
        '''
        
        return '{}{}'.format(firstStr, lastStr)

    
#
