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
        self.__board = Board()
        self.__walks = Walks()
        self.info = {}  # 信息: pgn标签...
        self.remark = ''
        
    def __str__(self):
        # 棋盘字符串函数
        return '{}\n{}'.format(str(self.__board), str(self.__walks))

    def __repr__(self):
        pass
    
    @property
    def board(self):
        return self.__board
    
    @property
    def walks(self):
        return self.__walks
        
    def createwalk(self, fromrowcol, torowcol, description='', remark=''):
        # 生成一步着法命令
        def go():
            assert torowcol in self.__board.canmoverowcols(fromrowcol), ('该走法不符合规则，或者可能自己被将军、将帅会面！\nfrom: %s\nto: %s\ncanmove: %s\n%s' % 
                (fromrowcol, torowcol, sorted(self.__board.canmoverowcols(fromrowcol)), self.__board))
            
            back.eatpiece = self.__board.movepiece(fromrowcol, torowcol)
            # 给函数back添加一个属性:被吃棋子!
            self.__walks.setcurrentside(CrossTrans.getotherside(self.__walks.currentside))
            
        def back():
            self.__board.movepiece(torowcol, fromrowcol, back.eatpiece)
            self.__walks.setcurrentside(CrossTrans.getotherside(self.__walks.currentside))
            
        if not description:
            description = WalkConvert.moverowcols_chinese(fromrowcol,
                    torowcol, self.__board)
        walk = Walk(go, back, description, remark)
        walk.fromrowcol, walk.torowcol = fromrowcol, torowcol
        return walk
     
    def getfen(self):
        # 将一个棋盘局面写入FEN格式串
        def __linetonums():
            # 下划线字符串对应数字字符元组 列表
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
    
        piecechars = [piece.char for rc, piece in sorted(self.__board.crosses.items())]
        chars = [piecechars[rowno * NumCols: (rowno + 1) * NumCols]
                    for rowno in range(NumRows)]
        afen = '/'.join([''.join(char) for char in chars[::-1]])
        for _str, nstr in __linetonums():
            afen = afen.replace(_str, nstr)
        sidechar = 'b' if self.__walks.currentside == BLACK_SIDE else 'r'
        return '{} {} {} {} {} {}'.format(afen, sidechar, '-', '-', '0', '0')

    def setfen(self, fen):                
        afens = fen.split()
        self.__walks.setcurrentside(BLACK_SIDE
                if (len(afens) > 1 and afens[1] == 'b') else RED_SIDE) 
        self.__walks.clear()
        self.__board.loadpieces(fen)
        
    def getpgn(self):
        # 将一个棋局着棋过程，写入pgn字符串
        number = self.__walks.number        
        self.__walks.location(Walks.StartNumber, False)
        
        strinfo = '\n'.join(['[{} "{}"]'.format(key, self.info[key])
                    for key in self.info])
        sfen, gfen = self.info.get('FEN'), self.getfen()
        if sfen:
            assert sfen.split()[0] == gfen.split()[0], '\n棋谱FEN：%s, \n生成FEN: %s' % (sfen.split()[0], gfen.split()[0])                        
        self.info['FEN'] = gfen        
        self.__walks.location(number, False)        
        return '%s\n%s\n%s\n' % (strinfo, self.remark, str(self.__walks))      
        
    def setpgn(self, pgn=''):
        # 将一个pgn棋局文件载入棋局 
        walkdeses = []
        walkremarks = []        
        if pgn:
            infolist = re.findall('\[(\w+) "(.*)"\]', pgn)
            for aline in infolist:
                self.info[aline[0]] = aline[1]  # 棋局信息（pgn标签）
                
            s = re.findall('\]\s+(\{[\s\S]*\})?\s+1\. ', pgn)
            if len(s) > 0:
                self.remark = s[0]  # 棋谱评注
                
            s = re.findall('\s(1-0|0-1|1/2-1/2|\*)\s?', pgn)
            if len(s) > 0:
                self.info['Result'] = s[0]    # 棋局结果
                
            s = '(\d+)\. (\S{4})\s+(\{.*\})?\s*(\S{4})?\s+(\{.*\})?'
            walktuple = re.findall(s, pgn)  # 走棋信息, 字符串元组
            
            for bout in walktuple:
                walkdeses.extend([bout[1], bout[3]])
                walkremarks.extend([bout[2], bout[4]])
                
        self.setfen(self.info.get('FEN', self.FEN))
        for n, des in enumerate(walkdeses):
            # 生成多步着法命令列表
            if des:
                (fromrowcol, torowcol) = WalkConvert.chinese_moverowcols(
                        self.__walks.currentside, des, self.__board)
                self.__walks.append(self.createwalk(fromrowcol, torowcol,
                        des, walkremarks[n]))
                self.__walks.forward(False)
        self.__walks.location(Walks.StartNumber)        
    
    def changeside(self, changetype='exchange'):
        number = self.__walks.number        
        remarkes = self.__walks.remarkes  # 备注里如有棋子走法，则未作更改？        
        self.__walks.location(Walks.StartNumber)
        
        if changetype == 'rotate': # 交换场地
            crosses = {CrossTrans.getrotaterowcol(rowcol): piece
                    for rowcol, piece in self.board.getlivecrosses().items()}
            moverowcols = [(CrossTrans.getrotaterowcol(fromrowcol),
                            CrossTrans.getrotaterowcol(torowcol))
                            for fromrowcol, torowcol in self.__walks.moverowcols()]
        elif changetype == 'symmetry': # 左右交换
            crosses = {CrossTrans.getsymmetryrowcol(rowcol): piece
                for rowcol, piece in self.board.getlivecrosses().items()}
            moverowcols = [(CrossTrans.getsymmetryrowcol(fromrowcol),
                            CrossTrans.getsymmetryrowcol(torowcol))
                            for fromrowcol, torowcol in self.__walks.moverowcols()]
        else: # 对换棋局
            self.__walks.currentside = CrossTuple.getotherside(self.__walks.currentside)
            crosses = {rowcol: self.board.pieces.getothersidepiece(piece)
                for rowcol, piece in self.board.getlivecrosses().items()}
            moverowcols = self.__walks.moverowcols()
        [self.board.setpiece(rowcol, BlankPie) for rowcol in self.board.crosses.keys()]
        [self.board.setpiece(rowcol, piece) for rowcol, piece in crosses.items()]
        self.board.setbottomside()
        
        self.__walks.clear()
        for n, (fromrowcol, torowcol) in enumerate(moverowcols):        
            self.__walks.append(self.createwalk(fromrowcol, torowcol, '', remarkes[n]))
            self.__walks.forward(False)
        self.__walks.location(number)


        