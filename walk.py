'''
中国象棋棋子着法类型
'''

from board import *


class Walk(object):
    # 着法类
    
    def __init__(self, go, back, description, remark):
        # 构造一步着法
        assert callable(go) and callable(back), '参数不是可运行的！'
        self.go = go
        self.back = back
        self.description = description
        self.remark = remark
    
    def __str__(self):
        return self.description
    
    @property
    def moveseat(self):
        return (self.fromseat, self.toseat)
        
    @property
    def eatpiece(self):
        return self.back.eatpiece
        

class Walks(Model):
    # 棋谱着法类
    
    def __init__(self):
        super().__init__()
        self.__lineboutnum = 3  # 生成pgn文件的着法文本每行回合数
        self.clear()
        
    def clear(self):
        self.cursor = -1  # 着法序号 范围：0 ~ length        
        self.__walks = []
        
    def __str__(self):
        # 着法字符串        
        line_n = self.__lineboutnum * 2
        blanknums = [13, 10, 13, 10, 13, 10, 13, 10]
        boutstrls = []
        for n, strwalk in enumerate(self.getboutstr()):
            boutstrls.append(strwalk)
            colnum = (n + 1) % line_n # 求得需要填充空格的着数
            if colnum == 0:
                boutstrls.append('\n')
            remark = self.getremark(n)
            if remark:                
                boutstrls.append(' {0}\n{1}'.format(remark, 
                    ' ' * sum(blanknums[:colnum])))
        return ''.join(boutstrls)
    
    def getboutstr(self, align=False):
        # 着法字符串转换成带序号的回合字符串
        width = 9 if align else 5 # 是否对齐
        result = []
        for n, strwalk in enumerate(self.descriptiones):
            tag = '☆' if self.getremark(n) else ''
            boutstr = ('{0:>{1}}'.format(strwalk, width) if n % 2 == 1
                    else '{0:>3d}. {1}'.format(n // 2 + 1, strwalk))
            if align:
                bstr = '{0}{1}'.format(boutstr, tag)
            result.append(boutstr)
        return result        
        
    def setstrcolumn(self, boutnum):
        # 设置着法文本每行回合数(最多4栏)
        self.__lineboutnum = (boutnum % 4) if (boutnum % 4) != 0 else 4

    def setcurrentside(self, side):
        self.currentside = side
            
    @property
    def descriptiones(self):
        return [walk.description for walk in self.__walks]
    
    @property
    def remarkes(self):
        return [walk.remark for walk in self.__walks]
    
    @property
    def length(self):
        return len(self.__walks)
        
    @property
    def isempty(self):
        return self.length == 0

    @property
    def isstart(self):
        return self.cursor < 0

    @property
    def islast(self):
        return self.cursor == self.length - 1

    def getremark(self, n):
        return self.__walks[n].remark.strip()
        
    def currentwalk(self):
        if not self.isempty and not self.isstart:
            return self.__walks[self.cursor]
      
    def moveseats(self):
        return [(walk.fromseat, walk.toseat) for walk in self.__walks]
        
    def append(self, walk):
        self.__walks.append(walk)
        
    def cutfollow(self):
        self.__walks = self.__walks[:self.cursor + 1]
        
    def move(self, inc, refresh=True):
                
        def __forward():
            if self.isempty or self.islast:
                return
            self.cursor += 1
            self.currentwalk().go()
                
        def __backward():
            if self.isstart:
                return
            self.currentwalk().back()
            self.cursor -= 1            

        function = __forward if inc > 0 else __backward
        [function() for _ in range(abs(inc))]       
        if refresh:
            self.notifyviews()
 
    def movestart(self, refresh=True):
        self.move(-self.length, refresh)

    def movelast(self, refresh=True):
        self.move(self.length, refresh)

    def loadmoveseats(self, moveseats, remarkes, chessboard):
        self.clear()
        for n, (fromseat, toseat) in enumerate(moveseats):        
            self.append(chessboard.createwalk(fromseat, toseat, '', remarkes[n]))
            self.move(1, False)      
   

class WalkConvert(object):
    # 着法记录转换类

    NumToChinese = {RED_SIDE: {1:'一', 2:'二', 3:'三', 4:'四', 5:'五',
                        6:'六', 7:'七', 8:'八', 9:'九'}, # 数字转换成中文
                    BLACK_SIDE: {1:'１', 2:'２', 3:'３', 4:'４', 5:'５',
                        6:'６', 7:'７', 8:'８', 9:'９'}}
    ChineseToNum = {'一':1, '二':2, '三':3, '四':4, '五':5,
                    '六':6, '七':7, '八':8, '九':9, # 中文转换成数字
                    '１':1, '２':2, '３':3, '４':4, '５':5,
                    '６':6, '７':7, '８':8, '９':9,
                    '前':0, '中':1, '后':-1, # 走棋文字转换成数字
                    '进':1, '退':-1, '平':0 }
    ColChars = 'abcdefghi'    
        
    def __sortpawnseats(self, isbottomside, pawnseats):
        # 多兵排序
        result = []
        pawnseatdict = {Cross.getcol(seat): [] for seat in pawnseats}
        for seat in pawnseats:
            pawnseatdict[Cross.getcol(seat)].append(seat) # 列内排序
        for col, seats in sorted(pawnseatdict.items()):    
            if len(seats) > 1:
                result.extend(seats) # 按列排序，
        return result[::-1] if isbottomside else result
        
    def chinese_moveseats(self, side, chinese, board):
        # 根据中文纵线着法描述取得源、目标位置: (fromseat, toseat)
                    
        def __chcol_col(isbottomside, zhcol):
            return (NumCols-self.ChineseToNum[zhcol] if isbottomside
                    else self.ChineseToNum[zhcol]-1)
            
        def __movzh_movdir(isbottomside, movchar):
            # 根据中文行走方向取得棋子的内部数据方向（进：1，退：-1，平：0）
            return self.ChineseToNum[movchar] * (1 if isbottomside else -1)
            
        def __indexname_fromseat(index, name, seats, isbottomside):
            if name in PawnNames: 
                seats = self.__sortpawnseats(isbottomside, seats) # 获取多兵的列
                if len(seats) > 3:
                    index -= 1  # 修正index
            elif isbottomside:
                seats = seats[::-1]
            return seats[index]
                    
        def __linename_toseat(fromseat, movdir, tocol, tochar):
            # 获取直线走子toseat
            row, col = Cross.getrow(fromseat), Cross.getcol(fromseat)
            return (Cross.mergeseat(row, tocol) if movdir == 0 else
                    Cross.mergeseat(row + movdir * self.ChineseToNum[tochar], col))

        def __obliquename_toseat(fromseat, movdir, tocol, isAdvisorBishop):
            # 获取斜线走子：仕、相、马toseat
            row, col = Cross.getrow(fromseat), Cross.getcol(fromseat)
            step = tocol - col  # 相距1或2列
            inc = abs(step) if isAdvisorBishop else (2 if abs(step) == 1 else 1)
            return Cross.mergeseat(row + movdir * inc, tocol)
            
        isbottomside = board.isbottomside(side)
        name = chinese[0]
        if name in CharToNames.values():
            seats = sorted(board.getlivesidenamecolcrosses(side, name, 
                    __chcol_col(isbottomside, chinese[1])).keys())
            assert bool(seats), ('没有找到棋子 => %s side:%s name: %s\n%s' % 
                            (chinese, side, name, board))

            index = (-1 if (len(seats) == 2 and name in AdvisorBishopNames
                            and ((chinese[2] == '退') == isbottomside)) else 0)
            # 排除：士、象同列时不分前后，以进、退区分棋子
            fromseat = seats[index] 
        else:
            # 未获得棋子, 查找某个排序（前后中一二三四五）某方某个名称棋子
            index, name = self.ChineseToNum[chinese[0]], chinese[1]
            seats = sorted(board.getlivesidenamecrosses(side, name).keys())
            assert len(seats) >= 2, 'side: %s name: %s 棋子列表少于2个! \n%s' % (
                        side, name, self)
            
            fromseat = __indexname_fromseat(index, name, seats, isbottomside)
        
        movdir = __movzh_movdir(isbottomside, chinese[2])
        tocol = __chcol_col(isbottomside, chinese[3])
        toseat = (__linename_toseat(fromseat, movdir, tocol, chinese[3])
                    if name in LineMovePieceNames else
                        __obliquename_toseat(fromseat, movdir, tocol,
                        name in AdvisorBishopNames))
        
        assert chinese == self.moveseats_chinese(fromseat, toseat, board), ('棋谱着法: %s   生成着法: %s 不等！' % (chinese, self.moveseats_chinese(fromseat, toseat, board))) 

        return (fromseat, toseat)
        
    def moveseats_chinese(self, fromseat, toseat, board):
        # 根据源、目标位置: (fromseat, toseat)取得中文纵线着法描述
        def __col_chcol(side, isbottomside, col):
            return self.NumToChinese[side][NumCols-col if isbottomside else col+1]
                
        frompiece = board.getpiece(fromseat)
        side, name = frompiece.side, frompiece.name
        isbottomside = board.isbottomside(side)
        fromrow, fromcol = Cross.getrow(fromseat), Cross.getcol(fromseat)
        seats = sorted(board.getlivesidenamecolcrosses(side, name, fromcol).keys())
        length = len(seats)
        if length > 1 and name in StrongePieceNames:
            if name in PawnNames:
                seats = self.__sortpawnseats(isbottomside, 
                        sorted(board.getlivesidenamecrosses(side, name).keys()))
                length = len(seats)
            elif isbottomside: # '车', '马', '炮'            
                seats = seats[::-1]
            indexstr = {2: '前后', 3: '前中后'}.get(length, '一二三四五')
            firstStr = indexstr[seats.index(fromseat)] + name
        else: 
            #仕(士)和相(象)不用“前”和“后”区别，因为能退的一定在前，能进的一定在后
            firstStr = name + __col_chcol(side, isbottomside, fromcol)
        
        torow, tocol = Cross.getrow(toseat), Cross.getcol(toseat)
        chcol = __col_chcol(side, isbottomside, tocol)
        tochar = ('平' if torow == fromrow else
                    ('进' if isbottomside == (torow > fromrow) else '退'))
        tochcol = (chcol if torow == fromrow or name not in LineMovePieceNames
                        else self.NumToChinese[side][abs(torow - fromrow)])
        lastStr = tochar + tochcol
        
        #assert (fromseat, toseat) == self.chinese_moveseats(side, firstStr + lastStr, board), '棋谱着法: %s 生成着法: %s 不等！' % ((fromseat, toseat), self.chinese_moveseats(side, firstStr + lastStr, board))
        
        return '{}{}'.format(firstStr, lastStr)
        
    def coord_moveseat(self, coord):
        # 根据坐标字符串取得移动位置        
        return ((int(coord[1]), self.ColChars.index(coord[0])),
                (int(coord[3]), self.ColChars.index(coord[2])))

    def moveseat_coord(self, moveseat):
        # 根据移动位置取得坐标字符串
        fromseat, toseat = moveseat
        fromrow, fromcol = Cross.getrow(fromseat), Cross.getcol(fromseat)
        torow, tocol = Cross.getrow(toseat), Cross.getcol(toseat)
        return '{}{}{}{}'.format(self.ColChars[fromcol], str(fromrow),
                    self.ColChars[tocol], str(torow))

                    
WalkConvert = WalkConvert()
# 全局唯一的着法转换对象
                
                