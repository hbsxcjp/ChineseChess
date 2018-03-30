'''
中国象棋棋子类型 by-cjp
'''

from seats import *


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


class Piece(object):
    '棋子类'
    def __init__(self, char):
        self.__color = BLACK_Piece if char.islower() else RED_Piece
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
        return Seats.allseats

    def intersectionseats(self, moveseats, board):
        '棋子规则移动范围与全部移动范围的交集，再筛除本方棋子占用范围'
        return {
            seat
            for seat in (self.getallseats(board) & moveseats)
            if board.getcolorside(seat) != self.color
        }

    def getmoveseats(self, board):
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
        return Seats.kingseats[board.getboardside(self.color)]

    def getmoveseats(self, board):
        return self.intersectionseats(
            Seats.getkingmoveseats(self.seat), board)


class Advisor(Piece):
    def getallseats(self, board):
        return Seats.advisorseats[board.getboardside(self.color)]

    def getmoveseats(self, board):
        return self.intersectionseats(
            Seats.getadvisormoveseats(self.seat), board)


class Bishop(Piece):
    def getallseats(self, board):
        return Seats.bishopseats[board.getboardside(self.color)]

    def getmoveseats(self, board):
        move_centreseats = Seats.getbishopmove_centreseats(self.seat)
        return {
            seat
            for seat in self.intersectionseats(move_centreseats.keys(), board)
            if board.isblank(move_centreseats[seat])
        }


class Knight(Piece):
    def getmoveseats(self, board):
        move_legseats = Seats.getknightmove_legseats(self.seat)
        return {
            seat
            for seat in self.intersectionseats(move_legseats.keys(), board)
            if board.isblank(move_legseats[seat])
        }


class Rook(Piece):
    def getmoveseats(self, board):
        result = set()
        lines = Seats.rookcannonmoveseat_lines(self.seat)
        for seatline in lines:
            for seat in seatline:
                if board.isblank(seat):
                    result.add(seat)
                else:
                    if board.getcolorside(seat) != self.color:
                        result.add(seat)
                    break
        return result


class Cannon(Piece):
    def getmoveseats(self, board):
        result = set()
        lines = Seats.rookcannonmoveseat_lines(self.seat)
        for seatline in lines:
            skip = False
            for seat in seatline:
                if not skip:
                    if board.isblank(seat):
                        result.add(seat)
                    else:  # 该位置有棋子
                        skip = True
                elif not board.isblank(seat):
                    if board.getcolorside(seat) != self.color:
                        result.add(seat)
                    break
        return result


class Pawn(Piece):
    def getallseats(self, board):
        return Seats.pawnseats[board.getboardside(self.color)]

    def getmoveseats(self, board):
        row = self.seat[0]
        isbottomside = board.isbottomside(self.color)
        return {
            (r, c)
            for r, c in self.intersectionseats(
                Seats.getpawnmoveseats(self.seat), board)
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
        return self.__pieces[0 if color == RED_Piece else 16]

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
