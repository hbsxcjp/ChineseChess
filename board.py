'''
中国象棋棋盘类型
'''

from base import *
from piece import *


class Board(object):
    '棋盘类'

    def __init__(self, filename=''):
        self.seats = []
        self.pieces = Pieces()
        self.rootmove = None
        self.readfile(filename)

    def __str__(self):

        def __getname(piece):
            rookcannonpawn_name = {'车': '車', '马': '馬', '炮': '砲'}
            name = piece.name
            return (rookcannonpawn_name.get(name, name)
                    if piece.color == BLACK_P else name)

        linestr = [
            list(line.strip()) for line in blankboard.strip().splitlines()
        ]
        for piece in self.getlivepieces():
            seat = self.getseat(piece)
            linestr[(9 - Seats.getrow(seat)) *
                    2][Seats.getcol(seat) * 2] = __getname(piece)
        return '\n{}\n'.format('\n'.join([''.join(line) for line in linestr]))
        
    def __infostr(self):
        return '\n'.join(['[{} "{}"]'.format(key, self.info[key])
                    for key in sorted(self.info)])   
       
    def __repr__(self):
    
        def __setchar(move):
            firstcol = move.maxcol * 5
            linestr[move.stepno * 2][firstcol: firstcol + 4] = move.zhstr            
            if move.remark:              
                remstrs.append('({:3d},{:3d}): {{{}}}'.format(
                        move.stepno, move.maxcol, move.remark))                
            if move.next_:
                linestr[move.stepno * 2 + 1][firstcol + 1: firstcol + 3] = [' ↓', ' ']
                __setchar(move.next_)
            if move.other:
                linef = firstcol + 4
                linel = move.other.maxcol * 5
                linestr[move.stepno * 2][linef: linel] = '…' * (linel - linef)
                __setchar(move.other)
            
        linestr = [['　' for _ in range((self.maxcol + 1) * 5)]
                    for _ in range((self.maxrow + 1) * 2)]
        remstrs = []
        __setchar(self.rootmove)
            
        totalstr = '着法深度：{}, 变着广度：{}, 视图宽度：{}\n'.format(
                    self.maxrow, self.othcol, self.maxcol)
        walkstr = '\n'.join([''.join(line) for line in linestr])
        remstr = '\n'.join(remstrs)
        return '\n'.join([self.__infostr(), str(self), totalstr, walkstr, remstr])
        
    def __clearinfomove(self):
        self.info = {'Author': '',
                    'Black': '',
                    'BlackTeam': '',
                    'Date': '',
                    'ECCO': '',
                    'Event': '',
                    'FEN': FEN,
                    'Format': 'zh',
                    'Game': 'Chinese Chess',
                    'Opening': '',
                    'PlayType': '',
                    'RMKWriter': '',
                    'Red': '',
                    'RedTeam': '',
                    'Result': '',
                    'Round': '',
                    'Site': '',
                    'Title': '',
                    'Variation': '',
                    'Version': ''}
        self.rootmove = Move()
        self.curmove = self.rootmove
        self.firstcolor = RED_P 
        self.movcount = -1 # 消除根节点
        self.remcount = 0 # 注解数量
        self.remlenmax = 0 # 注解最大长度
        self.othcol = 0 # 存储最大变着层数
        self.maxrow = 0 # 存储最大着法深度
        self.maxcol = 0 # 存储视图最大列数         

    def isbottomside(self, color):
        return self.bottomside == color

    def isblank(self, seat):
        return self.seats[seat] is BlankPie

    def getseat(self, piece):
        return self.seats.index(piece)

    def getpiece(self, seat):
        return self.seats[seat]

    def getcolor(self, seat):
        return self.seats[seat].color

    def getside(self, color):
        return BOTTOM_SIDE if self.bottomside == color else TOP_SIDE

    def getkingpiece(self, color):
        return self.pieces.getkingpiece(color)

    def getkingseat(self, color):
        return self.getseat(self.getkingpiece(color))

    def getlivepieces(self):
        return [piece for piece in self.seats if piece is not BlankPie]

    def getlivesidepieces(self, color):
        return [piece for piece in self.getlivepieces() if piece.color == color]

    def getsidenameseats(self, color, name):
        return [
            self.getseat(piece)
            for piece in self.getlivesidepieces(color) if piece.name == name
        ]

    def getsidenamecolseats(self, color, name, col):
        return [
            seat
            for seat in self.getsidenameseats(color, name)
            if Seats.getcol(seat) == col
        ]

    def geteatedpieces(self):
        return set(self.pieces.allpieces()) - set(self.getlivepieces())

    def iskilled(self, color):
        othercolor = not color
        kingseat = self.getkingseat(color)
        otherseat = self.getkingseat(othercolor)
        if Seats.issamecol(kingseat, otherseat):  # 将帅是否对面
            if all([
                    self.isblank(seat)
                    for seat in Seats.getsamecolseats(kingseat, otherseat)
            ]):
                return True
        for piece in self.getlivesidepieces(othercolor):
            if piece.isStronge and (kingseat in piece.getmvseats(self)):
                return True
        return False

    def canmvseats(self, fseat):
        '获取棋子可走的位置, 不能被将军'
        result = []
        piece = self.getpiece(fseat)
        color = piece.color
        for tseat in piece.getmvseats(self):
            topiece = self.__go(fseat, tseat)
            if not self.iskilled(color):
                result.append(tseat)
            self.__back(fseat, tseat, topiece)
        return result
        
    def isdied(self, color):
        for piece in self.getlivesidepieces(color):
            if self.canmvseats(self.getseat(piece)):
                return False
        return True

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

    def setmvseat(self, move):
        '根据中文纵线着法描述取得源、目标位置: (fseat, tseat)'

        def __zhcol_col(zhcol):
            return (NumCols - ChineseToNum[zhcol]
                    if isbottomside else ChineseToNum[zhcol] - 1)

        color, zhstr = self.curcolor, move.zhstr
        isbottomside = self.isbottomside(color)
        name = zhstr[0]
        if name in CharToNames.values():
            seats = self.getsidenamecolseats(color, name, __zhcol_col(zhstr[1]))
            assert bool(seats), ('没有找到棋子 => %s color:%s name: %s\n%s' %
                                 (zhstr, color, name, self))

            index = (-1 if (len(seats) == 2 and name in AdvisorBishopNames
                            and ((zhstr[2] == '退') == isbottomside)) else 0)
            # 排除：士、象同列时不分前后，以进、退区分棋子
            fseat = seats[index]
        else:
            # 未获得棋子, 查找某个排序（前后中一二三四五）某方某个名称棋子
            index, name = ChineseToNum[zhstr[0]], zhstr[1]
            seats = self.getsidenameseats(color, name)
            assert len(seats) >= 2, 'color: %s name: %s 棋子列表少于2个! \n%s' % (     color, name, self)
            
            if name in PawnNames:
                seats = self.__sortpawnseats(isbottomside, seats)  # 获取多兵的列
                if len(seats) > 3:
                    index -= 1  # 修正index
            elif isbottomside:
                seats = seats[::-1]
            fseat = seats[index]

        movdir = ChineseToNum[zhstr[2]] * (1 if isbottomside else -1)
        # '根据中文行走方向取得棋子的内部数据方向（进：1，退：-1，平：0）'
        tocol = __zhcol_col(zhstr[3])
        if name in LineMovePieceNames:
            #'获取直线走子toseat'
            row = Seats.getrow(fseat)
            move.tseat = (Seats.getseat(row, tocol) if movdir == 0
                            else Seats.getseat(row + movdir * ChineseToNum[zhstr[3]],
                            Seats.getcol(fseat)))           
        else:
            #'获取斜线走子：仕、相、马toseat'
            step = tocol - Seats.getcol(fseat)  # 相距1或2列            
            inc = abs(step) if name in AdvisorBishopNames else (2
                                                     if abs(step) == 1 else 1)
            move.tseat = Seats.getseat(Seats.getrow(fseat) + movdir * inc, tocol)
        move.fseat = fseat
        '''
        self.setzhstr(move)
        assert zhstr == move.zhstr, ('棋谱着法: %s   生成着法: %s 不等！' % (
                zhstr, move.zhstr))
        '''        
        
    def setzhstr(self, move):
        '根据源、目标位置: (fseat, tseat)取得中文纵线着法描述'
        def __col_chcol(color, col):
            return NumToChinese[color][NumCols - col
                                      if isbottomside else col + 1]

        fseat, tseat = move.fseat, move.tseat
        frompiece = self.getpiece(fseat)
        color, name = frompiece.color, frompiece.name        
        isbottomside = self.isbottomside(color)
        fromrow, fromcol = Seats.getrow(fseat), Seats.getcol(fseat)
        seats = self.getsidenamecolseats(color, name, fromcol)
        length = len(seats)
        if length > 1 and name in StrongePieceNames:
            if name in PawnNames:
                seats = self.__sortpawnseats(
                    isbottomside,
                    self.getsidenameseats(color, name))
                length = len(seats)
            elif isbottomside:  # '车', '马', '炮'
                seats = seats[::-1]
            indexstr = {2: '前后', 3: '前中后'}.get(length, '一二三四五')
            firstStr = indexstr[seats.index(fseat)] + name
        else:
            #仕(士)和相(象)不用“前”和“后”区别，因为能退的一定在前，能进的一定在后
            firstStr = name + __col_chcol(color, fromcol)

        torow, tocol = Seats.getrow(tseat), Seats.getcol(tseat)
        chcol = __col_chcol(color, tocol)
        tochar = ('平' if torow == fromrow else
                  ('进' if isbottomside == (torow > fromrow) else '退'))
        tochcol = (chcol if torow == fromrow or name not in LineMovePieceNames
                   else NumToChinese[color][abs(torow - fromrow)])
        lastStr = tochar + tochcol
        move.zhstr = '{}{}'.format(firstStr, lastStr)
        '''
        self.setmvseat(move) # 不能成功断言，可能与curcolor值有关？2018.4.26
        assert (fseat, tseat) == (move.fseat, move.tseat), ('棋谱着法: %s   生成着法: %s 不等！' % ((fseat, tseat), (move.fseat, move.tseat)))
        '''
            
    @property
    def curcolor(self):
        return self.firstcolor if (
                self.curmove.stepno % 2 == 0) else not self.firstcolor

    @property
    def isstart(self):
        return self.curmove is self.rootmove
                
    @property
    def islast(self):
        return self.curmove.next_ is None
                
    def getprevmoves(self, move=None):
        if not move:
            move = self.curmove
        result = [move]
        while move.prev is not None:
            result.append(move.prev)
            move = move.prev
        return result[::-1]
                
    def __go(self, fseat, tseat):
        eatpiece = self.seats[tseat]
        self.seats[tseat] = self.seats[fseat]
        self.seats[fseat] = BlankPie
        return eatpiece

    def __back(self, fseat, tseat, backpiece):
        self.seats[fseat] = self.seats[tseat]
        self.seats[tseat] = backpiece
                
    def movego(self, move):
        move.eatpiece = self.__go(move.fseat, move.tseat)
        self.curmove = move
            
    def moveback(self):
        self.__back(self.curmove.fseat, self.curmove.tseat, 
                self.curmove.eatpiece)
        self.curmove = self.curmove.prev
        
    def moveother(self):
        '移动到当前节点的另一变着'
        if self.curmove.other is None:
            return        
        tomove = self.curmove.other   
        self.moveback()
        self.movego(tomove)
        self.notifyviews()

    def movefirst(self, updateview=False):
        moved = False
        while self.curmove is not self.rootmove:
            self.moveback()
            moved = True
        if moved and updateview:
            self.notifyviews()
    
    def movelast(self):
        moved = False
        while self.curmove.next_ is not None:
            self.movego(self.curmove.next_)
            moved = True
        if moved:
            self.notifyviews()
        
    def movestep(self, inc=1):
    
        def __movegoto():
            if self.curmove.next_ is None:
                return
            self.movego(self.curmove.next_)
            return True
            
        def __movebackto():
            if self.curmove.prev is None:
                return
            self.moveback()
            return True
        
        movefun = __movebackto if inc < 0 else __movegoto
        if any([movefun() for _ in range(abs(inc))]):
            self.notifyviews()
        
    def movethis(self, move):
        if move is self.curmove:
            return
        self.movefirst()
        [self.movego(mv) for mv in self.getprevmoves(move)]
        self.notifyviews()
            
    def addmove(self, fseat, tseat, remark='', isother=False):
        move = Move(self.curmove.prev if isother else self.curmove)
        move.fseat = fseat
        move.tseat = tseat
        move.remark = remark
        self.setzhstr(move)
        if isother:
            self.curmove.setother(move)
            self.moveother()
        else:
            self.curmove.setnext(move)
            self.movestep()
        self.__setmvinfo()
                
    def cutnext(self):
        self.curmove.next_ = None

    def cutother(self):
        if self.curmove.other:
            self.curmove.other = self.curmove.other.other

    def __fen(self, piecechars=None):
        def __linetonums():
            '下划线字符串对应数字字符元组 列表'
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
            
        if not piecechars:
            piecechars = [piece.char for piece in self.seats]
        charls = [
            piecechars[rowno * NumCols:(rowno + 1) * NumCols]
            for rowno in range(NumRows)
        ]
        _fen = '/'.join([''.join(chars) for chars in charls[::-1]])
        for _str, nstr in __linetonums():
            _fen = _fen.replace(_str, nstr)
        return _fen
        
    def __mergefen(self, _fen, whoplay):
        return '{} {} - - 0 0'.format(_fen, 'b' if whoplay else 'r')
        
    def getfen(self):    
        assignmove = self.curmove
        self.movefirst()
        fen = self.__mergefen(self.__fen(), self.curcolor == BLACK_P)
        self.movethis(assignmove)
        assert self.info['FEN'] == fen, '\n原始:{}\n生成:{}'.format(self.info['FEN'], fen)
        return fen

    def __setseatpieces(self, seatpieces):
        self.seats = [BlankPie] * NumCols * NumRows
        for seat, piece in seatpieces.items():
            self.seats[seat] = piece
        self.bottomside = (RED_P if Seats.getrow(
            self.getkingseat(RED_P)) < 3 else BLACK_P)

    def setfen(self, fen=''):
    
        def __setfen(_fen):
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

            fenstr = ''.join(_fen.split('/')[::-1])
            charls = list(multrepl(fenstr, __numtolines()))

            isvalid, info = __isvalid(charls)
            #print(_fen, len(_fen))
            assert isvalid, info

            seatchars = {Seats.seat(n): char for n, char in enumerate(charls)}
            self.__setseatpieces(self.pieces.seatpieces(seatchars))

        if not fen:
            fen = self.info['FEN']
        else:
            self.info['FEN'] = fen
        afens = fen.split(' ')
        __setfen(afens[0])
        self.firstcolor = BLACK_P if (afens[1] == 'b') else RED_P
        self.curmove = self.rootmove
        self.notifyviews()

    def changeside(self, changetype='exchange'):
        
        def __changeseat(transfun):            
            '根据transfun改置每个move的fseat,tseat'
            
            def __seat(move):
                move.fseat = transfun(move.fseat)
                move.tseat = transfun(move.tseat)
                if move.next_:
                    __seat(move.next_)
                if move.other:
                    __seat(move.other)
        
            if self.rootmove.next_:
                __seat(self.rootmove.next_) # 驱动调用递归函数
                    
        curmove = self.curmove
        self.movefirst()
        if changetype == 'exchange':
            self.firstcolor = not self.firstcolor
            seatpieces = {self.getseat(piece): self.pieces.getothsidepiece(piece)
                    for piece in self.getlivepieces()}
        else:
            transfun = (Seats.rotateseat if changetype == 'rotate'
                    else Seats.symmetryseat)
            __changeseat(transfun)
            seatpieces = {transfun(self.getseat(piece)): piece
                    for piece in self.getlivepieces()}
        self.__setseatpieces(seatpieces)
        if changetype != 'rotate':
            self.__setmvinfo()
        if curmove is not self.rootmove:
            self.movethis(curmove)
        else:
            self.notifyviews()
        
    def __setcounts(self, move):
        self.movcount += 1
        if move.remark:
            self.remcount += 1
            self.remlenmax = max(self.remlenmax, len(move.remark))
                    
    def __readxqf(self, filename):    
        
        def __tostr(bstr):
            return bstr.decode('GBK', errors='ignore').strip()
            
        def __subbyte(a, b):
            return (a - b + 1024) % 256
            
        def __readinfo(data):
        
            def __calkey(bKey, cKey):
                return (((((bKey*bKey)*3+9)*3+8)*2+1)*3+8) * cKey % 256 # 保持为<256
                
            piechars = 'RNBAKABNRCCPPPPPrnbakabnrccppppp' # QiziXY设定的棋子顺序 
            #self.Signature = data[:2] # 2字节 文件标记 'XQ' = $5158;
            self.info['Version_xqf'] = data[2] # 版本号
            headKeyMask = data[3] # 加密掩码
            #self.ProductId = data[4] # 4字节 产品号(厂商的产品号)
            headKeyOrA = data[5] #
            headKeyOrB = data[6] #
            headKeyOrC = data[7] #
            headKeyOrD = data[8] #
            headKeysSum = data[9] # 加密的钥匙和
            headKeyXY = data[10] # 棋子布局位置钥匙       
            headKeyXYf = data[11] # 棋谱起点钥匙
            headKeyXYt = data[12] # 棋谱终点钥匙
            #// = 16 bytes
            headQiziXY = list(data[13:45]) # 32个棋子的原始位置
            #// 用单字节坐标表示, 将字节变为十进制数, 十位数为X(0-8)个位数为Y(0-9),
            #// 棋盘的左下角为原点(0, 0). 32个棋子的位置从1到32依次为:
            #// 红: 车马相士帅士相马车炮炮兵兵兵兵兵 (位置从右到左, 从下到上)
            #// 黑: 车马象士将士象马车炮炮卒卒卒卒卒 (位置从右到左, 从下到上)        
            #// = 48 bytes
            #self.PlayStepNo = data[45] # 棋谱文件的开始步数
            headWhoPlay = data[46] # 该谁下 0-红先, 1-黑先
            headPlayResult = data[47] # 最终结果 0-未知, 1-红胜 2-黑胜, 3-和棋
            #self.PlayNodes = data[48] # 本棋谱一共记录了多少步
            #self.PTreePos = data[49] # 对弈树在文件中的起始位置
            #self.Reserved1 = data[50:54] # : array [1..4] of dTByte;        
            #// = 64 bytes
            headCodeA = data[54] # 对局类型(开,中,残等)
            #self.CodeB = data[55] # 另外的类型
            #self.CodeC = data[56] #
            #self.CodeD = data[57] #
            #self.CodeE = data[58] #
            #self.CodeF = data[59] #
            #self.CodeH = data[60] #
            #self.CodeG = data[61] #
            #// = 80  bytes
            self.info['Title'] = __tostr(data[62]) # 标题
            #self.TitleB = __tostr(data[63]) #
            #// = 208 bytes
            self.info['Event'] = __tostr(data[64]) # 比赛名称
            self.info['Date'] = __tostr(data[65]) # 比赛时间
            self.info['Site'] = __tostr(data[66]) # 比赛地点
            self.info['Red'] = __tostr(data[67]) # 红方姓名
            self.info['Black'] = __tostr(data[68]) # 黑方姓名
            #// = 336 bytes
            self.info['Opening'] = __tostr(data[69]) # 开局类型
            #self.RedTime = __tostr(data[70]) #
            #self.BlkTime = __tostr(data[71]) #
            #self.Reservedh = __tostr(data[72]) #        
            #// = 464 bytes
            self.info['RMKWriter'] = __tostr(data[73]) # 棋谱评论员
            self.info['Author'] = __tostr(data[74]) # 文件的作者
            
            '''
            if self.Signature != (0x58, 0x51):
                print('文件标记不对。xqfinfo.Signature != (0x58, 0x51)')
            if (headKeysSum + headKeyXY + headKeyXYf + headKeyXYt) % 256 != 0:
                print('检查密码校验和不对，不等于0。')
            if self.info['Version_xqf'] > 18: 
                print('这是一个高版本的XQF文件，您需要更高版本的XQStudio来读取这个文件')
            '''            
            if self.info['Version_xqf'] <= 10: # 兼容1.0以前的版本
                KeyXY = 0
                KeyXYf = 0
                KeyXYt = 0
                KeyRMKSize = 0
            else:
                KeyXY = __calkey(headKeyXY, headKeyXY)
                KeyXYf = __calkey(headKeyXYf, KeyXY)
                KeyXYt = __calkey(headKeyXYt, KeyXYf)
                KeyRMKSize = ((headKeysSum * 256 + headKeyXY) % 65536 % 32000) + 767
                if self.info['Version_xqf'] >= 12: # 棋子位置循环移动
                    for i, xy in enumerate(headQiziXY[:]):
                        headQiziXY[(i + KeyXY + 1) % 32] = xy
                for i in range(32): # 棋子位置解密           
                    headQiziXY[i] = __subbyte(headQiziXY[i], KeyXY)
                    # 保持为8位无符号整数，<256
                    
            KeyBytes = [(headKeysSum & headKeyMask) | headKeyOrA,
                        (headKeyXY & headKeyMask) | headKeyOrB,
                        (headKeyXYf & headKeyMask) | headKeyOrC,
                        (headKeyXYt & headKeyMask) | headKeyOrD]
            F32Keys = [ord(c) & KeyBytes[i % 4]
                        for i, c in enumerate('[(C) Copyright Mr. Dong Shiwei.]')]
                        
            piecechars = ['_'] * 90
            for i, xy in enumerate(headQiziXY):
                if xy < 90:
                    piecechars[xy%10*9 + xy//10] = piechars[i]
                    # 用单字节坐标表示, 将字节变为十进制数, 
                    # 十位数为X(0-8),个位数为Y(0-9),棋盘的左下角为原点(0, 0)
            self.info['FEN'] = self.__mergefen(
                    self.__fen(piecechars), headWhoPlay)
            
            self.info['PlayType'] = {0: '全局', 1: '开局', 2: '中局', 3: '残局'}[headCodeA]
            self.info['Result'] = {0: '未知', 1: '红胜',
                    2: '黑胜', 3: '和棋'}[headPlayResult]            
            return (KeyXYf, KeyXYt, KeyRMKSize, F32Keys)            

        def __readmove(move):
            '递归添加着法节点'
            
            def __strstruct(size):
                return struct.Struct('{}s'.format(size))                        
                    
            def __bytetoseat(a, b):
                xy = __subbyte(a, b)
                return Seats.getseat(xy % 10, xy // 10) #(xy % 10, xy // 10)
                    
            def __readbytes(size):
                pos = fileobj.tell()
                bytestr = fileobj.read(size)                
                if self.info['Version_xqf'] <= 10:
                    return bytestr 
                else: # '字节串解密'
                    barr = bytearray(len(bytestr))  # 字节数组才能赋值，字节串不能赋值
                    for i, b in enumerate(bytestr):
                        barr[i] = __subbyte(int(b), F32Keys[(pos + i) % 32])
                    return barr
                    
            def __readremarksize():
                bytestr = __readbytes(4)
                return movestruct2.unpack(bytestr)[0] - KeyRMKSize
                
            data = movestruct1.unpack(__readbytes(4))
            # 一步棋的起点和终点有简单的加密计算，读入时需要还原
            move.fseat = __bytetoseat(data[0], 0X18 + KeyXYf) # 一步棋的起点
            move.tseat = __bytetoseat(data[1], 0X20 + KeyXYt) # 一步棋的终点
            ChildTag = data[2]
            
            RemarkSize = 0
            if self.info['Version_xqf'] <= 0x0A:
                b = 0
                if (ChildTag & 0xF0) != 0: 
                    b = b | 0x80
                if (ChildTag & 0x0F) != 0: 
                    b = b | 0x40
                ChildTag = b
                RemarkSize = __readremarksize()
            else:
                ChildTag = ChildTag & 0xE0
                if (ChildTag & 0x20) != 0:                        
                    RemarkSize = __readremarksize()
                    
            if RemarkSize > 0: # 如果有注解
                bytestr = __readbytes(RemarkSize)
                remark = __tostr(__strstruct(RemarkSize).unpack(bytestr)[0])
                if remark:
                    move.remark = remark
            self.__setcounts(move) # 设置内部计数值
            
            if (ChildTag & 0x80) != 0: # 有左子树
                move.setnext(Move(move))
                __readmove(move.next_)
            if (ChildTag & 0x40) != 0: # 有右子树
                move.setother(Move(move.prev))
                __readmove(move.other)

        infofmt = '2B2BL8B32BH2B2L4B8H64p64p64p16p16p16p16p64p16p16p32p16p16p528B'
        #206个元素
        infostruct = struct.Struct(infofmt)
        #print('infostruct：', struct.calcsize(infofmt))
        movestruct1 = struct.Struct('4B')
        movestruct2 = struct.Struct('L')
        with open(filename, 'rb') as fileobj:
            self.__init__()
            bytestr = infostruct.unpack(fileobj.read(1024))
            KeyXYf, KeyXYt, KeyRMKSize, F32Keys = __readinfo(bytestr)
            __readmove(self.rootmove)
        self.info['Version_xqf'] = str(self.info['Version_xqf'])

    def __readbin(self, filename):
    
        def __readmove(move):
            hasothernextrem, fi, ti = movestruct1.unpack(fileobj.read(3))
            move.fseat, move.tseat = fi, ti
            if hasothernextrem & 0x20:
                rlength = movestruct2.unpack(fileobj.read(2))[0]
                move.remark = fileobj.read(rlength).decode()
            self.__setcounts(move) # 设置内部计数值
            if hasothernextrem & 0x80:
                move.setother(Move(move.prev))
                __readmove(move.other)
            if hasothernextrem & 0x40:
                move.setnext(Move(move))
                __readmove(move.next_)
                
        movestruct1 = struct.Struct('3B')
        movestruct2 = struct.Struct('H')
        with open(filename, 'rb') as fileobj:
            self.__init__()
            count = struct.Struct('B').unpack(fileobj.read(1))[0]
            infoks = struct.Struct('{}B'.format(count)).unpack(fileobj.read(count))
            infovstruct = struct.Struct(('{}s' * count).format(*infoks))
            infovs = infovstruct.unpack(fileobj.read(sum(infoks)))
            for n, key in enumerate(sorted(self.info)):
                self.info[key] = infovs[n].decode()
            __readmove(self.rootmove)
            
    def __readxml(self, filename):
            
        def __readelem(elem, i, move):
            move.stepno = int(elem[i].tag[1:]) # 元素名
            if move.stepno > 0:
                nstr = elem[i].text.strip()
                if fmt == 'ICCS':
                    move.setseat_ICCS(nstr)
                else:
                    move.zhstr = nstr
            move.remark = elem[i].tail.strip()
            
            self.__setcounts(move) # 设置内部计数值         

            if len(elem[i]) > 0: # 有子元素(变着)
                move.setother(Move(move.prev))
                __readelem(elem[i], 0, move.other)
            i += 1
            if len(elem) > i:
                move.setnext(Move(move))
                __readelem(elem, i, move.next_)
                
        etree = ET.ElementTree(ET.Element('root'), filename)
        rootelem = etree.getroot()
        infoelem = rootelem.find('info')
        for elem in infoelem.getchildren():
            text = elem.text.strip() if elem.text else ''
            self.info[elem.tag] = text
            
        fmt = self.info['Format']
        movelem = rootelem.find('moves')
        if len(movelem) > 0:
            __readelem(movelem, 0, self.rootmove)
            
    def __readpgn(self, filename):
    
        def __readmove_ICCSzh(movestr, fmt):                    
        
            def __readmoves(move, mvstr, isother):  # 非递归                
                lastmove = move
                for i, (mstr, remark) in enumerate(moverg.findall(mvstr)):
                    newmove = Move(move.prev if isother else move)
                    if fmt == 'ICCS':
                        newmove.setseat_ICCS(mstr)
                    elif fmt == 'zh':
                        newmove.zhstr = mstr
                    if remark:
                        newmove.remark = remark                        
                    self.__setcounts(newmove) # 设置内部计数值
                    if isother and (i == 0): # 第一步为变着
                        lastmove.setother(newmove)
                    else:
                        lastmove.setnext(newmove)
                    lastmove = newmove
                return lastmove
                
            moverg = re.compile(' ([^\.\{\}\s]{4})(?:\s+\{([\s\S]*?)\})?')
            # 走棋信息 (?:pattern)匹配pattern,但不获取匹配结果;  注解[\s\S]*?: 非贪婪
            resultstr = re.findall('\s(1-0|0-1|1/2-1/2|\*)\s?', movestr)
            if resultstr:
                self.info['Result'] = resultstr[0]  # 棋局结果
            remark = re.findall('\{([\s\S]*?)\}', infostr)
            if remark:
                self.rootmove.remark = remark[0]
            self.__setcounts(self.rootmove) # 设置内部计数值
            othmoves = [self.rootmove]
            isother = False
            thismove = None
            leftstrs = re.split('\(\d+\.', movestr) # 如果注解里存在‘\(\d+\.’的情况，则可能会有误差
            while leftstrs:
                thismove = othmoves[-1] if isother else othmoves.pop()
                if not re.search('\) ', leftstrs[0]):
                    # 如果注解里存在‘\) ’的情况，则可能会有误差                  
                    othmoves.append(__readmoves(thismove, leftstrs.pop(0), isother))
                    isother = True
                else:
                    lftstr, leftstrs[0] = re.split('\) ', leftstrs[0], maxsplit=1)
                    __readmoves(thismove, lftstr, isother)
                    isother = False                    
            
        def __readmove_cc(movestr):
            
            def __readmove(move, row, col, isother=False):
                zhstr = moverg.findall(moves[row][col])                
                if zhstr:
                    newmove = Move(move.prev if isother else move)
                    newmove.stepno = row
                    newmove.zhstr = zhstr[0][:4]
                    newmove.remark = rems.get((row, col), '')
                    self.__setcounts(newmove) # 设置内部计数值
                    if isother:
                        move.setother(newmove)
                    else:
                        move.setnext(newmove)    
                    if zhstr[0][4] == '…':
                        __readmove(newmove, row, col+1, True)
                elif isother:
                    while moves[row][col][0] == '…':
                        col += 1
                    __readmove(move, row, col, True)
                if zhstr and row < len(moves)-1 and moves[row+1]:
                    __readmove(newmove, row+1, col)
                        
            movestr, p, remstr = movestr.partition('\n(')
            moves, rems = [], {}
            if movestr:
                mstrrg = re.compile('.{5}')
                moverg = re.compile('([^…　]{4}[…　])')
                moves = [mstrrg.findall(linestr) for linestr
                        in [line for i, line in enumerate(movestr.split('\n')) if i % 2 == 0]]
            if remstr:
                remrg = re.compile('\(\s*(\d+),\s*(\d+)\): \{([\s\S]*?)\}')
                rems = {(int(rowstr), int(colstr)): remark
                        for rowstr, colstr, remark in remrg.findall('(' + remstr)}
                self.rootmove.remark = rems.get((0, 0), '')
            self.__setcounts(self.rootmove) # 设置内部计数值
            if len(moves) > 1:
                __readmove(self.rootmove, 1, 0)
            
        infostr, p, movestr = open(filename).read().partition('\n1.')
        for key, value in re.findall('\[(\w+) "(.*)"\]', infostr):
            self.info[key] = value
        # 读取info内容（在已设置原始key上可能会有增加）
        fmt = self.info['Format']
        if fmt == 'cc':
            __readmove_cc(movestr)
        else:
            __readmove_ICCSzh(movestr, fmt)
        
    def __setmvinfo(self, haszhstr=False):
    
        '根据board设置树节点的zhstr或seat'
        def __set(move):
            setfunc(move)            
            move.maxcol = self.maxcol # 在视图中的列数
            self.othcol = max(self.othcol, move.othcol)
            self.maxrow = max(self.maxrow, move.stepno)
            self.movego(move)
            if move.next_:
                __set(move.next_)
            self.moveback()
            if move.other:
                self.maxcol += 1
                __set(move.other)
        
        setfunc = self.setmvseat if haszhstr else self.setzhstr
        self.othcol = 0 # 存储最大变着层数
        self.maxrow = 0 # 存储最大着法深度
        self.maxcol = 0 # 存储视图最大列数
        if self.rootmove.next_: # and self.movcount < 300: # 步数太多则太慢
            __set(self.rootmove.next_) # 驱动调用递归函数            
                    
    def readfile(self, filename):
    
        self.__clearinfomove()
        if not (filename and os.path.exists(filename) and os.path.isfile(filename)):
            return
        self.dirname = os.path.splitdrive(os.path.dirname(filename))[1]
        self.filename = os.path.splitext(os.path.basename(filename))[0]
        ext = os.path.splitext(os.path.basename(filename))[1]
        if ext == '.xqf':
            self.__readxqf(filename) 
        elif ext == '.bin':
            self.__readbin(filename)
        elif ext == '.xml':
            self.__readxml(filename)
        elif ext == '.pgn':
            self.__readpgn(filename)
            
        self.setfen()
        self.__setmvinfo(ext in {'.xml', '.pgn'}
                and self.info['Format'] in {'zh', 'cc'})
            
    def __saveasbin(self, filename):
    
        def __addmoves(move):
            rembytes = move.remark.strip().encode()
            hasothernextrem = ((0x80 if move.other else 0) |
                                (0x40 if move.next_ else 0) |
                                (0x20 if rembytes else 0))
            resbytes.extend(movestruct1.pack(hasothernextrem, move.fseat, move.tseat))
            if rembytes:
                resbytes.extend(movestruct2.pack(len(rembytes)))
                resbytes.extend(rembytes)  # rbytes已经是字节串，不需要再pack
            if move.other:
                __addmoves(move.other)
            if move.next_:
                __addmoves(move.next_)
    
        resbytes = bytearray()
        infobytes = [value.encode() for key, value in sorted(self.info.items())]
        lenbytes = [len(infob) for infob in infobytes]
        resbytes.extend([len(lenbytes)]) # info条目数
        resbytes.extend(lenbytes)
        resbytes.extend(b''.join(infobytes))
            
        movestruct1 = struct.Struct('3B')
        movestruct2 = struct.Struct('H')
        __addmoves(self.rootmove)
        try:
            open(filename, 'wb').write(resbytes)
        except:
            print('错误：写入 {} 文件不成功！'.format(filename))

    def __saveasxml(self, filename, fmt):
            
        def __createlem(name, value='', remark=''):
            newelem = ET.Element(name) # 元素名
            newelem.text = value
            newelem.tail = remark
            return newelem
            
        def __addelem(elem, move, fmt):
            rem = move.remark.strip()
            thissub = __createlem('m{0:02d}'.format(move.stepno),
                    move.ICCSzhstr(fmt), rem)
            if move.other: # 有变着
                __addelem(thissub, move.other, fmt)                
            elem.append(thissub)
            if move.next_:
                __addelem(elem, move.next_, fmt)
                
        self.info['Format'] = fmt
        rootelem = ET.Element('root')
        infoelem = __createlem('info')
        for name, value in sorted(self.info.items()):
            infoelem.append(__createlem(name, value))
        rootelem.append(infoelem)
        
        movelem = __createlem('moves')
        __addelem(movelem, self.rootmove, fmt)
        rootelem.append(movelem)
        xmlindent(rootelem)  # 美化
        ET.ElementTree(rootelem).write(filename, encoding='utf-8')
        
    def __saveaspgn(self, filename, fmt):
    
        def __movestr(fmt):
               
            def __remarkstr(move):
                rem = move.remark
                return '' if not rem else '\n{{{}}}\n'.format(rem)
            
            def __addstrl(move, isother=False):
                prestr = ('({0}. {1}'.format((move.stepno + 1) // 2, 
                        '... ' if move.stepno % 2 == 0 else '')
                        if isother else
                        (' ' if move.stepno % 2 == 0 else 
                        '{}. '.format((move.stepno + 1) // 2)))
                movestrl.append('{0}{1} {2}'.format(prestr,
                        move.ICCSzhstr(fmt), __remarkstr(move)))                
                if move.other:
                    __addstrl(move.other, True)
                    movestrl.append(') ')                   
                if move.next_:
                    __addstrl(move.next_)
        
            movestrl = [__remarkstr(self.rootmove)]
            if self.rootmove.next_:
                __addstrl(self.rootmove.next_)          
            return movestrl
            
        self.info['Format'] = fmt
        open(filename, 'w').write(repr(self) if fmt == 'cc' else 
                '\n'.join([self.__infostr(), ''.join(__movestr(fmt))]))
                    
    def writefile(self, filename, ext, fmt='ICCS'):
        if ext == '.bin':
            self.__saveasbin(filename)
        elif ext == '.xml':
            self.__saveasxml(filename, fmt)
        elif ext == '.pgn':
            self.__saveaspgn(filename, fmt)

    def transdir(self, dirfrom, dirto, text, fmt):
               
        def __transdir(dirfrom, dirto, text, fmt):
            fcount = dcount = 0
            if not os.path.exists(dirto):
                os.mkdir(dirto)
            for subname in os.listdir(dirfrom):
                subname = os.path.normcase(subname)
                pathfrom = os.path.join(dirfrom, subname)          
                pathto = os.path.join(dirto, subname)
                if os.path.isfile(pathfrom): # 文件
                    extension = os.path.splitext(os.path.basename(pathfrom))[1]
                    if extension in ('.xqf', '.bin', '.xml', '.pgn'):
                        board = Board(pathfrom)                        
                        filenameto = os.path.join(dirto, 
                                os.path.splitext(os.path.basename(pathfrom))[0] + text)
                        count[0] += board.movcount
                        count[1] += board.remcount
                        count[2] = max(count[2], board.remlenmax)
                        dirtoboard.append((filenameto, text, fmt, board))
                        fcount += 1
                    elif extension == '.txt':
                        data = open(pathfrom).read()
                        open(pathto, 'w').write(data)
                        fcount += 1
                else:
                    below = __transdir(pathfrom, pathto, text, fmt)
                    fcount += below[0]
                    dcount += below[1]
                    dcount += 1
            return (fcount, dcount)
            
        count = [0, 0, 0]
        dirtoboard = []
        fcount, dcount = __transdir(dirfrom, dirto, text, fmt)
        #'''
        for filenameto, text, fmt, board in dirtoboard:
            board.writefile(filenameto, text, fmt)            
        print('{}==>：{}_{} 共有{}个文件，{}个目录转换成功！'.format(
                dirfrom, text, fmt, fcount, dcount))
        print('着法数量：{}，注释数量：{}, 注释最大长度：{}'.format(
                count[0], count[1], count[2]))
        #'''
        
    def loadviews(self, views):
        self.views = views
        self.notifyviews()

    def notifyviews(self):
        '通知视图更新'
        if not hasattr(self, 'views'):
            return
        for view in self.views:
            view.updateview()

    
def testtransdir():
    dirfrom = ['c:\\棋谱文件\\示例文件',#
                'c:\\棋谱文件\\象棋杀着大全',
                'c:\\棋谱文件\\疑难文件',
                'c:\\棋谱文件\\中国象棋棋谱大全'
                ]
    fexts = ['.xqf', '.bin', '.xml', '.pgn']
    texts = ['.bin', '.xml', '.pgn']
    fmts = ['ICCS', 'zh', 'cc']
    
    bd = Board()
    for dir in dirfrom[:2]:    
        for fext in fexts[1:3]:
            for text in texts[1:3]:
                if text == fext:
                    continue
                for fmt in fmts[1:2]: # 设置输入文件格式  
                    bd.transdir(dir+fext, dir+text, text, fmt)
           
            
if __name__ == '__main__':

    import time
    start = time.time()
    
    testtransdir()    
    #cProfile.run("testtransdir()")
    #'.db' 生产的db文件超过1G，不具备可操作性.        
    
    end = time.time()
    print('usetime: %0.3fs' % (end - start))
    
    #shutil.rmtree('C:\\中国象棋棋谱大全')
    pass
    
    
#
