'''
中国象棋棋子类型 by-cjp
'''

BLACK_P = True
RED_P = False
TOP_SIDE = False
BOTTOM_SIDE = True
NumCols = 9
NumRows = 10
MinColNo = 0
MaxColNo = 8

# yapf: disable
colchars = 'abcdefghi'
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
 
BlankChar = '_'
CharToNames = {'K':'帅', 'A':'仕', 'B':'相', 'N':'马',
               'R':'车', 'C':'炮', 'P':'兵',
               'k':'将', 'a':'士', 'b':'象', 'n':'马',
               'r':'车', 'c':'炮', 'p':'卒', BlankChar: ''} # yapf: disable
# 全部棋子ch值与中文名称映射字典
PawnNames = {'兵', '卒'}
AdvisorBishopNames = {'仕', '相', '士', '象'}
StrongePieceNames = {'车', '马', '炮', '兵', '卒'}
LineMovePieceNames = {'帅', '将', '车', '炮', '兵', '卒'}
FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'
# 新棋局
     
           
class Seats(object):
    # 棋子位置类
    
    allseats = {seat for seat in range(90)}

    sideseats = {
        BOTTOM_SIDE: {seat for seat in range(45)},
        TOP_SIDE: {seat for seat in range(45, 90)}
    }

    kingseats = {
        BOTTOM_SIDE: {21, 22, 23, 12, 13, 14, 3, 4, 5},
        TOP_SIDE: {84, 85, 86, 75, 76, 77, 66, 67, 68}
    }

    advisorseats = {
        BOTTOM_SIDE: {21, 23, 13, 3, 5},
        TOP_SIDE: {84, 86, 76, 66, 68}
    }

    bishopseats = {
        BOTTOM_SIDE: {2, 6, 18, 22, 26, 38, 42},
        TOP_SIDE: {47, 51, 63, 67, 71, 83, 87}
    }

    pawnseats = {
        TOP_SIDE:
        sideseats[BOTTOM_SIDE] |
        {45, 47, 49, 51, 53, 54, 56, 58, 60, 62},
        BOTTOM_SIDE:
        sideseats[TOP_SIDE] |
        {27, 29, 31, 33, 35, 36, 38, 40, 42, 44}
    }

    def getrow(self, seat):
        return seat // NumCols

    def getcol(self, seat):
        return seat % NumCols

    def seat(self, index):
        return index
        
    def getseat(self, row, col):
        return row * NumCols + col
    
    def rotateseat(self, seat):
        return 89 - seat

    def symmetryseat(self, seat):
        return (seat // NumCols + 1) * NumCols - seat % NumCols - 1

    def issamecol(self, seat, othseat):
        return self.getcol(seat) == self.getcol(othseat)

    def getsamecolseats(self, seat, othseat):
        step = NumCols if seat < othseat else -NumCols
        return [s for s in range(seat + step, othseat, step)]

    def kingmvseats(self, seat):
        return {seat + 1, seat - 1, seat + NumCols, seat - NumCols}

    def advisormvseats(self, seat):
        return {seat + NumCols + 1, seat + NumCols - 1,
                seat - NumCols + 1, seat - NumCols - 1}

    def bishopmv_censeats(self, seat):
        '获取移动、象心行列值'
        mvseats = [seat + 2 * NumCols + 2, seat - 2 * NumCols + 2, 
                    seat + 2 * NumCols - 2, seat - 2 * NumCols - 2]
        if self.getcol(seat) == MaxColNo:
            mvseats = mvseats[2:]
        elif self.getcol(seat) == MinColNo:
            mvseats = mvseats[:2]        
        return {s: (seat + s) // 2 for s in mvseats}

    def knightmv_legseats(self, seat):
        '获取移动、马腿行列值'

        def __leg(first, to):
            x = to - first
            if x > NumCols + 2:
                return first + NumCols
            elif x < -NumCols - 2:
                return first - NumCols
            elif x == NumCols + 2 or x == -NumCols + 2:
                return first + 1
            else:
                return first - 1
            
        col = self.getcol(seat)
        mvseats = [seat + NumCols + 2, seat - NumCols + 2,
                    seat + 2 * NumCols + 1, seat - 2 * NumCols + 1,
                    seat + 2 * NumCols - 1, seat - 2 * NumCols - 1,
                    seat + NumCols - 2, seat - NumCols - 2]
        if col == MaxColNo:
            mvseats = mvseats[4:]
        elif col == MaxColNo - 1:
            mvseats = mvseats[2:]
        elif col == MinColNo:
            mvseats = mvseats[:4]
        elif col == MinColNo + 1:
            mvseats = mvseats[:6]
        return {s: __leg(seat, s) for s in mvseats}

    def rookcannonmvseat_lines(self, seat):
        '车炮可走的四个方向位置'
        return (
            [c for c in range(seat - 1, self.getrow(seat) * NumCols-1, -1)],
            # 左边位置列表
            [r for r in range(seat - NumCols, -1, -NumCols)],
            # 下边位置列表
            [c for c in range(seat + 1, (self.getrow(seat)+1) * NumCols)],
            # 右边位置列表
            [r for r in range(seat + NumCols, 90, NumCols)]) 
            # 上边位置列表

    def pawnmvseats(self, seat):
        mvseats = [seat + 1, seat + NumCols, seat - NumCols, seat - 1]
        if self.getcol(seat) == MaxColNo:
            mvseats = mvseats[1:]
        elif self.getcol(seat) == MinColNo:
            mvseats = mvseats[:3]
        return mvseats

                
Seats = Seats() # 单例对象
        
     
class Piece(object):
    '棋子类'
    def __init__(self, char):
        self.__color = BLACK_P if char.islower() else RED_P
        self.__char = char

    def __str__(self):
        return self.name

    @property
    def color(self):
        return self.__color

    @property
    def char(self):
        return self.__char

    @property
    def name(self):
        return CharToNames[self.__char]

    @property
    def isStronge(self):
        return self.name in StrongePieceNames

    def getallseats(self, board):
        '全部活动范围集合(默认：车马炮的活动范围)'
        return Seats.allseats

    def intersectionseats(self, mvseats, board):
        '棋子规则移动范围与全部移动范围的交集，再筛除本方棋子占用范围'
        return {
            seat
            for seat in (self.getallseats(board) & set(mvseats))
            if board.getcolor(seat) != self.color
        }

    def getmvseats(self, board):
        '筛除棋子特殊规则后的有效活动范围集合'
        return {}


class BlankPie(Piece):

    def __bool__(self):
        return False
        
    @property
    def color(self):
        return None

    def setseat(self, seat):
        pass


class King(Piece):
    def getallseats(self, board):
        return Seats.kingseats[board.getside(self.color)]

    def getmvseats(self, board):
        return self.intersectionseats(
            Seats.kingmvseats(board.getseat(self)), board)


class Advisor(Piece):
    def getallseats(self, board):
        return Seats.advisorseats[board.getside(self.color)]

    def getmvseats(self, board):
        return self.intersectionseats(
            Seats.advisormvseats(board.getseat(self)), board)


class Bishop(Piece):
    def getallseats(self, board):
        return Seats.bishopseats[board.getside(self.color)]

    def getmvseats(self, board):
        move_centreseats = Seats.bishopmv_censeats(board.getseat(self))
        return {
            seat
            for seat in self.intersectionseats(move_centreseats.keys(), board)
            if board.isblank(move_centreseats[seat])
        }


class Knight(Piece):
    def getmvseats(self, board):
        move_legseats = Seats.knightmv_legseats(board.getseat(self))
        return {
            seat
            for seat in self.intersectionseats(move_legseats.keys(), board)
            if board.isblank(move_legseats[seat])
        }


class Rook(Piece):
    def getmvseats(self, board):
        result = set()
        lines = Seats.rookcannonmvseat_lines(board.getseat(self))
        for seatline in lines:
            for seat in seatline:
                if board.isblank(seat):
                    result.add(seat)
                else:
                    if board.getcolor(seat) != self.color:
                        result.add(seat)
                    break
        return result


class Cannon(Piece):
    def getmvseats(self, board):
        result = set()
        lines = Seats.rookcannonmvseat_lines(board.getseat(self))
        for seatline in lines:
            skip = False
            for seat in seatline:
                if not skip:
                    if board.isblank(seat):
                        result.add(seat)
                    else:  # 该位置有棋子
                        skip = True
                elif not board.isblank(seat):
                    if board.getcolor(seat) != self.color:
                        result.add(seat)
                    break
        return result


class Pawn(Piece):
    def getallseats(self, board):
        return Seats.pawnseats[board.getside(self.color)]

    def getmvseats(self, board):
        result = set()
        seat = board.getseat(self)
        row = Seats.getrow(seat)
        isbottomside = board.isbottomside(self.color)
        for s in self.intersectionseats(Seats.pawnmvseats(seat), board):
            r = Seats.getrow(s)
            if (isbottomside and r >= row) or (not isbottomside and r <= row):
                result.add(s)
        return result


class Pieces(object):
    '一副棋子类'
    Chars = ['K', 'A', 'A', 'B', 'B', 'N', 'N', 'R', 'R',
                'C', 'C', 'P', 'P', 'P', 'P', 'P',
            'k', 'a', 'a', 'b', 'b', 'n', 'n', 'r', 'r',
                'c', 'c', 'p', 'p', 'p', 'p', 'p'] # yapf: disable
    # 全部棋子ch值列表
    CharPieces = {'K': King, 'A': Advisor, 'B': Bishop, 'N': Knight,
                    'R': Rook, 'C': Cannon, 'P': Pawn} # yapf: disable
    # 棋子类字典

    def __init__(self):
        self.__pieces = [
            self.CharPieces[char.upper()](char) for char in self.Chars
        ]

    def __str__(self):
        return str([str(piece) for piece in self.__pieces])
        
    def getkingpiece(self, color):
        return self.__pieces[0 if color == RED_P else 16]

    def getothsidepiece(self, piece):
        return self.__pieces[(self.__pieces.index(piece) + 16) % 32]

    def allpieces(self):
        return self.__pieces

    def seatpieces(self, seatchars):
        result = {}
        chars = self.Chars.copy()
        for seat, char in seatchars.items():
            if char == BlankChar:
                continue
            for i, ch in enumerate(chars):
                if char == ch:
                    result[seat] = self.__pieces[i]
                    chars[i] = ''
                    break
        return result
        

BlankPie = BlankPie(BlankChar)  # 单例对象


class Move(object):
    '象棋着法树节点类'
        
    def __init__(self, prev=None):
        self.prev = prev
        self.fseat = 0
        self.tseat = 0
        self.remark = ''
        
        self.next_ = None
        self.other = None
        self.stepno = 0 # 着法深度
        self.othcol = 0 # 变着广度
        
        self.maxcol = 0 # 图中列位置（需结合board确定）
        self.zhstr = '' if prev else '1.开始' # 中文描述（需结合board确定）
        
    def __str__(self):
        return '{}_{}({}) [{} {}] {}'.format(self.stepno, self.othcol, self.maxcol,
                self.fseat, self.tseat, self.zhstr) 

    def ICCSzhstr(self, fmt):
        return ('' if self.stepno == 0 else
                '{0}{1}{2}{3}'.format(
                    colchars[Seats.getcol(self.fseat)],
                    Seats.getrow(self.fseat),
                    colchars[Seats.getcol(self.tseat)],
                    Seats.getrow(self.tseat))) if fmt == 'ICCS' else self.zhstr         
            
    def setseat_ICCS(self, ICCSstr):
        fcol, frow, tcol, trow = ICCSstr
        self.fseat = Seats.getseat(int(frow), colchars.index(fcol))
        self.tseat = Seats.getseat(int(trow), colchars.index(tcol))
    
    def setnext(self, next_):
        next_.stepno = self.stepno + 1
        next_.othcol = self.othcol # 变着层数
        self.next_ = next_
        
    def setother(self, other):
        other.stepno = self.stepno # 与premove的步数相同
        other.othcol = self.othcol + 1 # 变着层数
        self.other = other
                           
 
         
#