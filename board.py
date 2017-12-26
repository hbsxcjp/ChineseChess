'''
中国象棋棋盘类型
'''

from piece import *

   
class Model(object):
        
    def loadviews(self, views):
        self.views = views
        
    def notifyviews(self):
        # 通知视图更新
        for view in self.views:
            view.updateview()
            

class View(object):

    def __init__(self, models):        
        self.chessboard, self.board, self.walks = models
        
    def updateview(self):
        # 更新视图（由数据模型发起）
        pass
        
        
class Board(Model):
    # 棋盘类
    
    def __init__(self):
        super().__init__()
        self.crosses = dict.fromkeys(Cross.allseats, BlankPie)
        self.pieces = Pieces()
        self.bottomside = BLACK_SIDE
        
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
        # 边框粗线
        
        def __getname(piece):
            rookcannonpawn_name = {'车': '車', '马': '馬', '炮': '砲'}
            name = piece.name
            return (rookcannonpawn_name.get(name, name)
                    if piece.side == BLACK_SIDE else name)
        
        def __fillingname():
            linestr = [list(line.strip()) for line in blankboard.strip().splitlines()]
            for seat, piece in self.getlivecrosses().items():
                linestr[(MaxRowNo_T - Cross.getrow(seat))*2][
                        Cross.getcol(seat)*2] = __getname(piece)
            return [''.join(line) for line in linestr]

        frontstr = '\n　　　　'
        return '{}{}{}'.format(frontstr, frontstr.join(__fillingname()), '\n')    
    
    def getboardside(self, side):
        return BOTTOM_SIDE if self.bottomside == side else TOP_SIDE
    
    def setbottomside(self):
        self.bottomside = (RED_SIDE
                if Cross.getrow(self.getkingseat(RED_SIDE)) < MaxRowNo_B else BLACK_SIDE)
    
    def isbottomside(self, side):
        return BOTTOM_SIDE == self.getboardside(side)
    
    def isblank(self, seat):
        return self.crosses[seat] is BlankPie
              
    def getpiece(self, seat):
        return self.crosses[seat]
    
    def getside(self, seat):
        return self.crosses[seat].side
    
    @classmethod
    def otherside(cls, side):        
        return TOP_SIDE if side == BOTTOM_SIDE else BOTTOM_SIDE
    
    def getkingpiece(self, side):    
        return self.pieces.getkingpiece(side)
        
    def getkingseat(self, side):
        for seat, pie in self.getlivesidenamecrosses(side,
                    self.getkingpiece(side).name).items():
            return seat
        #assert False, '没有发现棋子：{}'.format(str(self))        
        
    def clear(self):
        [self.setpiece(seat, BlankPie) for seat in self.crosses.keys()]
    
    def setpiece(self, seat, piece):
        self.crosses[seat] = piece

    def movepiece(self, fromseat, toseat, backpiece=BlankPie):
        eatpiece = self.crosses[toseat]
        self.setpiece(toseat, self.crosses[fromseat])
        self.setpiece(fromseat, backpiece)
        return eatpiece
        
    def getlivecrosses(self):
        return {seat: piece for seat, piece in self.crosses.items()
                if piece is not BlankPie}
    
    def geteatedpieces(self):
        return self.pieces.geteatedpieces(self.getlivecrosses().values())
    
    def getlivesidecrosses(self, side):
        return {seat: piece for seat, piece in self.getlivecrosses().items()
                if piece.side == side}
    
    def getlivesidenamecrosses(self, side, name):
        return {seat: piece for seat, piece in self.getlivesidecrosses(side).items()
                if piece.name == name}
                
    def getlivesidenamecolcrosses(self, side, name, col):
        return {seat: piece for seat, piece in
            self.getlivesidenamecrosses(side, name).items() if Cross.getcol(seat) == col}
        
    def iskilled(self, side):
        def __isfaced():
            if not Cross.issamecol(kingseat, otherseat):
                return False
            return all([self.isblank(seat)
                for seat in Cross.getsamecolseats(kingseat, otherseat)])      
            
        def __iskilled():
            for seat, piece in self.getlivesidecrosses(otherside).items():
                if (piece.isStronge and 
                        (kingseat in piece.getmoveseats(seat, self))):
                    return True
            return False
            
        otherside = Piece.otherside(side)
        kingseat, otherseat = self.getkingseat(side), self.getkingseat(otherside)
        return __isfaced() or __iskilled()
        
    def isdied(self, side):
        for seat, piece in self.getlivesidecrosses(side).items():
            if bool(self.canmoveseats(seat)):
                return False # 有子可走，避免被将
        return True

    def canmoveseats(self, fromseat):
        # 获取棋子可走的位置, 不能被将军
        result = []
        piece = self.getpiece(fromseat)
        side = piece.side
        #print(sorted(piece.getmoveseats(fromseat, self)))
        for toseat in piece.getmoveseats(fromseat, self):            
            topiece = self.movepiece(fromseat, toseat)            
            if not self.iskilled(side): 
                result.append(toseat)
            self.movepiece(toseat, fromseat, topiece)
        return result

    def loadcrosses(self, crosses):
        self.clear()
        [self.setpiece(seat, piece) for seat, piece in crosses.items()]
        self.setbottomside()
        
    def loadpieces(self, fen):
        def __numtolines():
            # 数字字符: 下划线字符串           
            numtolines = {}
            for i in range(1, 10):
                numtolines[str(i)] = '_' * i
            return numtolines
            
        def __isvalid(charls):
            # 判断棋子列表是否有效
            if len(charls) != 90:
                return False, '棋局的位置个数不等于90，有误！'
            chars = [c for c in charls if c != BlankChar]
            if len(chars) > 32:
                return False, '全部的棋子个数大于32个，有误！'
            for c in chars:
                if chars.count(c) > Pieces.Chars.count(c):
                    return False, '棋子: %s 的个数大于规定个数，有误！' % c
            return True, ''           
        
        afens = fen.split()
        fenstr = ''.join(afens[0].split('/')[::-1])
        charls = list(multrepl(fenstr, __numtolines()))
        
        assert __isvalid(charls)[0], __isvalid(charls)[1]
        
        self.clear()
        [self.setpiece(Cross.getseat(n), self.pieces.getunusedpiece(char, self)) 
                for n, char in enumerate(charls)]
        self.setbottomside()
        

#