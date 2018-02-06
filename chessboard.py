'''
中国象棋棋谱类型
'''

from walks import *


class ChessBoard(Model):
    '棋局类（含一副棋盘、棋子、棋谱）'

    FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'

    # 新棋局

    def __init__(self, pgn=''):
        super().__init__()
        self.board = Board()
        self.walks = Walks()
        self.info = {}  # 信息: pgn标签...
        self.remark = ''
        self.setpgn(pgn)

    def __str__(self):
        return '{}\n{}'.format(str(self.board), str(self.walks))

    def getfen(self):        
        sidechar = 'b' if self.walks.currentside == BLACK_Piece else 'r'
        return '{} {} {} {} {} {}'.format(self.board.getafen(), sidechar, '-', '-', '0', '0')

    def setfen(self, fen):
        afens = fen.split()
        self.walks.setcurrentside(
            BLACK_Piece if (len(afens) > 1 and afens[1] == 'b') else RED_Piece)
        self.board.loadafen(afens[0])

    def getpgn(self):
        # 将一个棋局着棋过程，写入pgn字符串
        offset = self.walks.cursor + 1
        self.walks.move(-offset)

        sfen, gfen = self.info.get('FEN'), self.getfen()
        if sfen:
            assert sfen.split()[0] == gfen.split()[
                0], '\n棋谱FEN：%s, \n生成FEN: %s' % (sfen.split()[0],
                                                 gfen.split()[0])
        self.info['FEN'] = gfen
        strinfo = '\n'.join(
            ['[{} "{}"]'.format(key, self.info[key]) for key in sorted(self.info)])
            
        self.walks.move(offset)
        return '{}\n{}\n{}\n'.format(strinfo, self.remark, str(self.walks))

    def setpgn(self, pgn=''):
        '将一个pgn棋局文件载入棋局'

        def __setinfo():
            infolist = re.findall('\[(\w+) "(.*)"\]', pgn)
            for key, value in infolist:
                self.info[key] = value  # 棋局信息（pgn标签）
            remark = re.findall('\]\s+(\{[\s\S]*\})?\s+1\. ', pgn)
            if remark:
                self.remark = remark[0]  # 棋谱评注
            result = re.findall('\s(1-0|0-1|1/2-1/2|\*)\s?', pgn)
            if result:
                self.info['Result'] = result[0]  # 棋局结果
            self.setfen(self.info.get('FEN', self.FEN))

        def __createwalks():
            #s = '(\d+)\. (\S{4})\s+(\{.*\})?\s*(\S{4})?\s+(\{.*\})?'
            s = '(\d+)\.\s+(\S{4})\s+(\{.*\})?\s*(\S{4})?\s*(\{.*\})?'
            description_remarks = re.findall(s, pgn)  # 走棋信息, 字符串元组

            descriptiones, remarks = [], []
            for n, des1, remark1, des2, remark2 in description_remarks:
                descriptiones.extend([des1, des2])
                remarks.extend([remark1, remark2])

            for n, des in enumerate(descriptiones):
                if des:
                    (fromseat, toseat) = self.board.chinese_moveseats(
                        self.walks.currentside, des)
                    self.walks.append(fromseat, toseat, remarks[n], self.board)
            self.walks.move(-self.walks.length)

        self.info = {}
        self.walks.clear()        
        if pgn:
            __setinfo()
            __createwalks()
        else:
            self.setfen(self.FEN)
        if hasattr(self, 'views'):
            self.notifyviews()

    def changeside(self, changetype='exchange'):
        def __seatpieces_moveseats(changetype):
            self.walks.move(-self.walks.length)
            if changetype == 'exchange':
                self.walks.transcurrentside()
                return ({
                    piece.seat: self.board.pieces.getothersidepiece(piece)
                    for piece in self.board.getlivepieces()
                }, self.walks.moveseats())
            else:
                if changetype == 'rotate':
                    transfun = Seats.getrotateseat
                elif changetype == 'symmetry':
                    transfun = Seats.getsymmetryseat
                return ({
                    transfun(piece.seat): piece
                    for piece in self.board.getlivepieces()
                }, [(transfun(fromseat), transfun(toseat))
                    for fromseat, toseat in self.walks.moveseats()])

        offset = self.walks.cursor + 1
        seatpieces, moveseats = __seatpieces_moveseats(changetype)

        self.board.loadseatpieces(seatpieces)
        self.walks.loadmoveseats(moveseats, self.walks.remarkes(), self.board)
        # 备注里如有棋子走法，则未作更改？
        self.walks.move(offset)

        self.notifyviews()


#
