'''
中国象棋棋谱类型
'''

from walk import *       

        
class ChessBoard(Model):
    # 棋局类（含一副棋盘、棋子、棋谱）
    
    FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'
    # 新棋局 
     
    def __init__(self):
        super().__init__()
        self.board = Board()
        self.walks = Walks()
        self.info = {}  # 信息: pgn标签...
        self.remark = ''
        
    def __str__(self):
        # 棋盘字符串函数
        return '{}\n{}'.format(str(self.board), str(self.walks))

    def __repr__(self):
        pass    
        
    def createwalk(self, fromrowcol, torowcol, description='', remark=''):
        # 生成一步着法命令
        def go():
            assert torowcol in self.board.canmoverowcols(fromrowcol), ('该走法不符合规则，或者可能自己被将军、将帅会面！\nfrom: %s\nto: %s\ncanmove: %s\n%s' % 
                (fromrowcol, torowcol, sorted(self.board.canmoverowcols(fromrowcol)), self.board))
            
            back.eatpiece = self.board.movepiece(fromrowcol, torowcol)
            # 给函数back添加一个属性:被吃棋子!
            self.walks.setcurrentside(Piece.getotherside(self.walks.currentside))
            
        def back():
            self.board.movepiece(torowcol, fromrowcol, back.eatpiece)
            self.walks.setcurrentside(Piece.getotherside(self.walks.currentside))
            
        if not description:
            description = WalkConvert.moverowcols_chinese(fromrowcol,
                    torowcol, self.board)
        walk = Walk(go, back, description, remark)
        walk.fromrowcol, walk.torowcol = fromrowcol, torowcol
        return walk
     
    def getfen(self):
        # 将一个棋盘局面写入FEN格式串
        def __linetonums():
            # 下划线字符串对应数字字符元组 列表
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
    
        piecechars = [piece.char for rc, piece in sorted(self.board.crosses.items())]
        chars = [piecechars[rowno * NumCols: (rowno + 1) * NumCols]
                    for rowno in range(NumRows)]
        afen = '/'.join([''.join(char) for char in chars[::-1]])
        for _str, nstr in __linetonums():
            afen = afen.replace(_str, nstr)
        sidechar = 'b' if self.walks.currentside == BLACK_SIDE else 'r'
        return '{} {} {} {} {} {}'.format(afen, sidechar, '-', '-', '0', '0')

    def setfen(self, fen):                
        afens = fen.split()
        self.walks.setcurrentside(BLACK_SIDE
                if (len(afens) > 1 and afens[1] == 'b') else RED_SIDE) 
        self.board.loadpieces(fen)
        
    def getpgn(self):
        # 将一个棋局着棋过程，写入pgn字符串
        cursor = self.walks.cursor        
        self.walks.movestart(False)
        
        strinfo = '\n'.join(['[{} "{}"]'.format(key, self.info[key])
                    for key in self.info])
        sfen, gfen = self.info.get('FEN'), self.getfen()
        if sfen:
            assert sfen.split()[0] == gfen.split()[0], '\n棋谱FEN：%s, \n生成FEN: %s' % (sfen.split()[0], gfen.split()[0])                        
        self.info['FEN'] = gfen
        
        self.walks.movelast(False)
        return '{}\n{}\n{}\n'.format(strinfo, self.remark, str(self.walks))      
        
    def setpgn(self, pgn=''):
        # 将一个pgn棋局文件载入棋局
        
        def __getinfo():
            infolist = re.findall('\[(\w+) "(.*)"\]', pgn)
            for aline in infolist:
                self.info[aline[0]] = aline[1]  # 棋局信息（pgn标签）                
            s = re.findall('\]\s+(\{[\s\S]*\})?\s+1\. ', pgn)
            if len(s) > 0:
                self.remark = s[0]  # 棋谱评注                
            s = re.findall('\s(1-0|0-1|1/2-1/2|\*)\s?', pgn)
            if len(s) > 0:
                self.info['Result'] = s[0]    # 棋局结果
        
        def __getwalktuple():
            s = '(\d+)\. (\S{4})\s+(\{.*\})?\s*(\S{4})?\s+(\{.*\})?'            
            return re.findall(s, pgn)  # 走棋信息, 字符串元组
            
        def __getwalkdeses(walktuple):
            walkdeses = []
            walkremarks = []
            if pgn:
                for bout in __getwalktuple():
                    walkdeses.extend([bout[1], bout[3]])
                    walkremarks.extend([bout[2], bout[4]])                
            return  walkdeses, walkremarks
            
        def __createwalks(walkdeses_walkremarks):
            walkdeses, walkremarks = walkdeses_walkremarks
            self.walks.clear()
            for n, des in enumerate(walkdeses):
                # 生成多步着法命令列表
                if des:
                    (fromrowcol, torowcol) = WalkConvert.chinese_moverowcols(
                            self.walks.currentside, des, self.board)
                    self.walks.append(self.createwalk(fromrowcol, torowcol,
                            des, walkremarks[n]))
                    self.walks.move(1, False)
            self.walks.movestart(False)            
        
        __getinfo()
        self.setfen(self.info.get('FEN', self.FEN))        
        __createwalks(__getwalkdeses(__getwalktuple()))        
        
        if hasattr(self, 'views'):
            self.notifyviews()
    
    def changeside(self, changetype='exchange'):
    
        def __crosses_moverowcols(transrowcolfun):
            crosses = {transrowcolfun(rowcol): piece
                    for rowcol, piece in self.board.getlivecrosses().items()}
            moverowcols = [(transrowcolfun(fromrowcol), transrowcolfun(torowcol))
                    for fromrowcol, torowcol in self.walks.moverowcols()]
            return crosses, moverowcols
                    
        offset = self.walks.cursor + 1 - self.walks.length 
        remarkes = self.walks.remarkes  # 备注里如有棋子走法，则未作更改？        
        self.walks.movestart(False)        
        if changetype == 'rotate': # 交换场地
            crosses, moverowcols = __crosses_moverowcols(Cross.getrotaterowcol)
        elif changetype == 'symmetry': # 左右交换
            crosses, moverowcols = __crosses_moverowcols(Cross.getsymmetryrowcol)
        else: # 对换棋局
            self.walks.currentside = Piece.getotherside(self.walks.currentside)
            crosses, moverowcols = ({rowcol: self.board.pieces.getothersidepiece(piece)
                            for rowcol, piece in self.board.getlivecrosses().items()},
                            self.walks.moverowcols())
            
        self.board.clear()
        [self.board.setpiece(rowcol, piece) for rowcol, piece in crosses.items()]
        self.board.setbottomside()
        
        self.walks.clear()
        for n, (fromrowcol, torowcol) in enumerate(moverowcols):        
            self.walks.append(self.createwalk(fromrowcol, torowcol, '', remarkes[n]))
            self.walks.move(1, False)
        self.walks.move(offset, False)
        
        self.notifyviews()


        