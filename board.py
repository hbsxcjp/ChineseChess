'''
中国象棋棋盘类型
'''

import base
from piece import *

# yapf: disable
NumToChinese = {RED_Piece: {1:'一', 2:'二', 3:'三', 4:'四', 5:'五',
                    6:'六', 7:'七', 8:'八', 9:'九'}, # 数字转换成中文
                BLACK_Piece: {1:'１', 2:'２', 3:'３', 4:'４', 5:'５',
                    6:'６', 7:'７', 8:'８', 9:'９'}}
ChineseToNum = {'一':1, '二':2, '三':3, '四':4, '五':5,
                '六':6, '七':7, '八':8, '九':9, # 中文转换成数字
                '１':1, '２':2, '３':3, '４':4, '５':5,
                '６':6, '７':7, '８':8, '９':9,
                '前':0, '中':1, '后':-1, # 走棋文字转换成数字
                '进':1, '退':-1, '平':0 }
ColChars = 'abcdefghi'
# yapf: enable


class Board(object):
    '棋盘类'

    def __init__(self, fen):
        self.allseats = dict.fromkeys(Seats.allseats, BlankPie)
        self.pieces = Pieces()
        self.bottomside = BLACK_Piece
        self.setfen(fen)

    def __str__(self):
        blankboard = '''
┏━┯━┯━┯━┯━┯━┯━┯━┓
┃　│　│　│╲│╱│　│　│　┃
┠─┼─┼─┼─╳─┼─┼─┼─┨
┃　│　│　│╱│╲│　│　│　┃
┠─╬─┼─┼─┼─┼─┼─╬─┨
┃　│　│　│　│　│　│　│　┃
┠─┼─╬─┼─╬─┼─╬─┼─┨
┃　│　│　│　│　│　│　│　┃
┠─┴─┴─┴─┴─┴─┴─┴─┨
┃　　　　　　　　　　　　　　　┃
┠─┬─┬─┬─┬─┬─┬─┬─┨
┃　│　│　│　│　│　│　│　┃
┠─┼─╬─┼─╬─┼─╬─┼─┨
┃　│　│　│　│　│　│　│　┃
┠─╬─┼─┼─┼─┼─┼─╬─┨
┃　│　│　│╲│╱│　│　│　┃
┠─┼─┼─┼─╳─┼─┼─┼─┨
┃　│　│　│╱│╲│　│　│　┃
┗━┷━┷━┷━┷━┷━┷━┷━┛
'''
        # yapf: disable
        # 边框粗线

        def __getname(piece):
            rookcannonpawn_name = {'车': '車', '马': '馬', '炮': '砲'}
            name = piece.name
            return (rookcannonpawn_name.get(name, name)
                    if piece.color == BLACK_Piece else name)

        def __fillingname():
            linestr = [
                list(line.strip()) for line in blankboard.strip().splitlines()
            ]
            for piece in self.getlivepieces():
                seat = piece.seat
                linestr[(MaxRowNo_T - Seats.getrow(seat)) *
                        2][Seats.getcol(seat) * 2] = __getname(piece)
            return [''.join(line) for line in linestr]

        frontstr = '\n'
        return '{}{}{}'.format(frontstr, frontstr.join(__fillingname()), '\n')

    def clear(self):
        for seat in self.allseats:
            self.allseats[seat] = BlankPie
        self.pieces.clear()

    def setpiece(self, seat, piece):
        self.allseats[seat] = piece
        piece.setseat(seat)

    def movepiece(self, fromseat, toseat, backpiece=BlankPie):
        eatpiece = self.allseats[toseat]
        eatpiece.setseat(None)
        self.setpiece(toseat, self.allseats[fromseat])
        self.setpiece(fromseat, backpiece)
        return eatpiece

    def setbottomside(self):
        self.bottomside = (RED_Piece if Seats.getrow(
            self.getkingseat(RED_Piece)) < MaxRowNo_B else BLACK_Piece)

    def isbottomside(self, color):
        return BOTTOM_SIDE == self.getboardside(color)

    def isblank(self, seat):
        return not bool(self.allseats[seat]) # is BlankPie

    def getpiece(self, seat):
        return self.allseats[seat]

    def getcolorside(self, seat):
        return self.allseats[seat].color

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
            if Seats.getcol(piece.seat) == col
        }

    def iskilled(self, color):
        othercolor = other_color(color)
        kingseat, otherseat = self.getkingseat(color), self.getkingseat(
            othercolor)
        if Seats.issamecol(kingseat, otherseat):  # 将帅是否对面
            if all([
                    self.isblank(seat)
                    for seat in Seats.getsamecolseats(kingseat, otherseat)
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

        seatchars = {Seats.getseat(n): char for n, char in enumerate(charls)}
        self.loadseatpieces(self.pieces.getseatpieces(seatchars))

    def getfen(self):
        def __linetonums():
            '下划线字符串对应数字字符元组 列表'
            return [('_' * i, str(i)) for i in range(9, 0, -1)]

        piecechars = [
            piece.char for seat, piece in sorted(self.allseats.items())
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
        pawnseatdict = {Seats.getcol(seat): [] for seat in pawnseats}
        for seat in pawnseats:
            pawnseatdict[Seats.getcol(seat)].append(seat)  # 列内排序
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
            row, col = Seats.getrow(fromseat), Seats.getcol(fromseat)
            return ((row, tocol)
                    if movdir == 0 else (
                        row + movdir * ChineseToNum[tochar], col))

        def __obliquename_toseat(fromseat, movdir, tocol, isAdvisorBishop):
            '获取斜线走子：仕、相、马toseat'
            row, col = Seats.getrow(fromseat), Seats.getcol(fromseat)
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
        fromrow, fromcol = Seats.getrow(fromseat), Seats.getcol(fromseat)
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

        torow, tocol = Seats.getrow(toseat), Seats.getcol(toseat)
        chcol = __col_chcol(color, tocol)
        tochar = ('平' if torow == fromrow else
                  ('进' if isbottomside == (torow > fromrow) else '退'))
        tochcol = (chcol if torow == fromrow or name not in LineMovePieceNames
                   else NumToChinese[color][abs(torow - fromrow)])
        lastStr = tochar + tochcol

        assert (fromseat, toseat) == self.chinese_moveseats(
            color, firstStr + lastStr), '棋谱着法: %s 生成着法: %s 不等！' % (
                (fromseat, toseat),
                self.chinese_moveseats(color, firstStr + lastStr))

        return '{}{}'.format(firstStr, lastStr)

    def coord_moveseat(self, coord):
        '根据坐标字符串取得移动位置'
        return ((int(coord[1]), ColChars.index(coord[0])), (int(coord[3]),
                                                            ColChars.index(
                                                                coord[2])))

    def moveseat_coord(self, moveseat):
        '根据移动位置取得坐标字符串'
        fromseat, toseat = moveseat
        fromrow, fromcol = Seats.getrow(fromseat), Seats.getcol(fromseat)
        torow, tocol = Seats.getrow(toseat), Seats.getcol(toseat)
        return '{}{}{}{}'.format(ColChars[fromcol], str(fromrow),
                                 ColChars[tocol], str(torow))


#
