'''
中国象棋棋子类型 by-cjp
'''

BLACK_P = True
RED_P = False
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
     
 
class Piece(object):
    '棋子类'
    def __init__(self, char):
        self.__color = BLACK_P if char.islower() else RED_P
        self.__char = char
        self.__seat = None

    def __str__(self):
        return self.name

    @property
    def color(self):
        return self.__color

    @property
    def char(self):
        return self.__char

    @property
    def seat(self):
        return self.__seat

    @property
    def name(self):
        return CharToNames[self.__char]

    @property
    def isStronge(self):
        return self.name in StrongePieceNames

    def setseat(self, seat):
        self.__seat = seat

    def getallseats(self, board):
        '全部活动范围集合(默认：车马炮的活动范围)'
        return board.allseats

    def intersectionseats(self, mvseats, board):
        '棋子规则移动范围与全部移动范围的交集，再筛除本方棋子占用范围'
        return {
            seat
            for seat in (self.getallseats(board) & mvseats)
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
        return board.kingseats[board.getside(self.color)]

    def getmvseats(self, board):
        return self.intersectionseats(
            board.getkingmvseats(self.seat), board)


class Advisor(Piece):
    def getallseats(self, board):
        return board.advisorseats[board.getside(self.color)]

    def getmvseats(self, board):
        return self.intersectionseats(
            board.getadvisormvseats(self.seat), board)


class Bishop(Piece):
    def getallseats(self, board):
        return board.bishopseats[board.getside(self.color)]

    def getmvseats(self, board):
        move_centreseats = board.getbishopmove_centreseats(self.seat)
        return {
            seat
            for seat in self.intersectionseats(move_centreseats.keys(), board)
            if board.isblank(move_centreseats[seat])
        }


class Knight(Piece):
    def getmvseats(self, board):
        move_legseats = board.getknightmove_legseats(self.seat)
        return {
            seat
            for seat in self.intersectionseats(move_legseats.keys(), board)
            if board.isblank(move_legseats[seat])
        }


class Rook(Piece):
    def getmvseats(self, board):
        result = set()
        lines = board.rookcannonmoveseat_lines(self.seat)
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
        lines = board.rookcannonmoveseat_lines(self.seat)
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
        return board.pawnseats[board.getside(self.color)]

    def getmvseats(self, board):
        row = self.seat[0]
        isbottomside = board.isbottomside(self.color)
        return {
            (r, c)
            for r, c in self.intersectionseats(
                board.getpawnmvseats(self.seat), board)
            if (isbottomside and r >= row) or (not isbottomside and r <= row)
        }


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

    def clear(self):
        [piece.setseat(None) for piece in self.__pieces]

    def getseatpieces(self, seatchars):
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

    def getkingpiece(self, color):
        return self.__pieces[0 if color == RED_P else 16]

    def getothersidepiece(self, piece):
        n = self.__pieces.index(piece)
        return self.__pieces[(n + 16) if n < 16 else (n - 16)]

    def getlivepieces(self):
        return [piece for piece in self.__pieces if bool(piece.seat)] # is not None

    def geteatedpieces(self):
        return [piece for piece in self.__pieces if not bool(piece.seat)] # is None

    def setpieimgids(self, imgids):
        for n, piece in enumerate(self.__pieces):
            piece.imgid = imgids[n]


BlankPie = BlankPie(BlankChar)


class Move(object):
    '象棋着法树节点类'
        
    def __init__(self, prev=None, fseat=(0, 0), tseat=(0, 0), remark='', zhstr=''):
        self.prev = prev
        self.fseat = fseat
        self.tseat = tseat
        self.remark = remark
        
        self.next_ = None
        self.other = None
        self.stepno = 0 # 着法深度
        self.othcol = 0 # 变着广度
        
        self.maxcol = 0 # 图中列位置（需结合board确定）
        self.zhstr = zhstr if not prev else '1.开始' # 中文描述（需结合board确定）
        
    def __str__(self):
        return '{}_{}({}) [{} {}] {}'.format(self.stepno, self.othcol, self.maxcol,
                self.fseat, self.tseat, self.zhstr)
        
    @property
    def binint(self):
        return (self.fseat[0] * 10 + self.fseat[1],
                self.tseat[0] * 10 + self.tseat[1])
                
    def ICCSzhstr(self, fmt):
        return ('' if self.stepno == 0 else
                '{0}{1}{2}{3}'.format(colchars[self.fseat[1]], self.fseat[0],
                    colchars[self.tseat[1]], self.tseat[0])) if fmt == 'ICCS' else self.zhstr
         
    def setseat_i(self, fi, ti):
        self.fseat, self.tseat = (fi // 10, fi % 10), (ti // 10, ti % 10)
            
    def setseat_ICCS(self, ICCSstr):
        fl, fw, tl, tw = ICCSstr
        self.fseat = (int(fw), colchars.index(fl))
        self.tseat = (int(tw), colchars.index(tl))
    
    def setnext(self, next_):
        next_.stepno = self.stepno + 1
        next_.othcol = self.othcol # 变着层数
        self.next_ = next_
        
    def setother(self, other):
        other.stepno = self.stepno # 与premove的步数相同
        other.othcol = self.othcol + 1 # 变着层数
        self.other = other
            
        
        
#