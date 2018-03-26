'中国象棋棋子着法类型-树结构'

from board import Model

class MoveNode(object):
    '象棋着法树节点类'
    colchars = 'abcdefghi'
        
    def __init__(self, prev=None):
        self.stepno = 0
        self.fseat = (0, 0)
        self.tseat = (0, 0)
        self.prev = prev
        self.next_ = None
        self.other = None
        self.remark = ''
        
    @property
    def coordstr(self):
        if self.stepno == 0:
            return ''
        return '{0}{1}{2}{3}'.format(self.colchars[self.fseat[1]], self.fseat[0],
                self.colchars[self.tseat[1]], self.tseat[0])    

    @property
    def coordint(self):
        return (self.fseat[0] * 10 + self.fseat[1],
                self.tseat[0] * 10 + self.tseat[1])
                
    def setseat_s(self, coordstr):
        fl, fw, tl, tw = coordstr
        self.fseat = (int(fw), self.colchars.index(fl))
        self.tseat = (int(tw), self.colchars.index(tl))

    def setseat_i(self, fi, ti):
        self.fseat = (fi // 10, fi % 10)
        self.tseat = (ti // 10, ti % 10)

    def setnext(self, next_):
        self.next_ = next_
        self.next_.stepno = self.stepno + 1
        
    def setother(self, other):
        self.other = other
        self.other.stepno = self.stepno # 与premove的步数相同

      
class Walks(Model):
    '棋谱着法类-树结构'    
        
    def __init__(self, chessfile, board):
        super().__init__()
        self.chessfile = chessfile
        self.board = board
        self.currentmvnode = chessfile.rootmvnode
        self.cureatpiece = None
        #self.__lineboutnum = 3  # 生成pgn文件的着法文本每行回合数

    def getprevmoves(self, mvnode):
        result = [mvnode]
        while result[-1].prev is not self.chessfile.rootmvnode:
            result.append(result[-1].prev)
        return result # reversed()
                
    def getnextmoves(self, mvnode):
        result = [mvnode]
        while result[-1].next_ is not None:
            result.append(result[-1].next_)
        return result
                
    def cutfollow(self):
        self.currentmvnode.next_ = None

    def movebackto(self, mvnode):
        while (self.currentmvnode is not mvnode
                and self.currentmvnode is not self.chessfile.rootmvnode):
            self.board.movepiece(self.currentmvnode.tseat, 
                    self.currentmvnode.fseat, self.cureatpiece)
            self.currentmvnode = self.currentmvnode.prev
        self.notifyviews()
        
    def movegoto(self, mvnode):
        while (self.currentmvnode is not mvnode
                and self.currentmvnode.next_ is not None):
            self.currentmvnode = self.currentmvnode.next_   
            self.cureatpiece = self.board.movepiece(self.currentmvnode.fseat, 
                    self.currentmvnode.tseat, self.cureatpiece)
        self.notifyviews()

    def moveoffset(self, inc=1):
        if inc > 0:
            self.movegoto(self.getnextmoves(self.currentmvnode)[i])
        elif inc < 0:
            self.movebackto(self.getprevmoves(self.currentmvnode)[i-1])        
        self.notifyviews()

    def moveother():
        if self.currentmvnode.other is None:
            return
        othermvnode = self.currentmvnode.other
        self.movebackto(self.currentmvnode.prev)
        self.movegoto(othermvnode)
        self.notifyviews()
        
    def movefirst(self):
        self.moveto(self.chessfile.rootmvnode)
    
    def movelast(self):
        self.movegoto(None)
        
   '''        
    class Walk(object):
        '象棋着法树节点类'            
        
        def __init__(self, move, board):
            '构造一步着法'
            self.move = move
            
            fromseat, toseat = move.fseat, move.tseat
            
            
            canmoveseats = board.canmoveseats(board.getpiece(fromseat))
            assert toseat in canmoveseats, (
                '走法不符合规则，可能自己被将军、将帅会面！\nfrom: {}\nto: {}\ncanmove: {}\n{}'.
                format(fromseat, toseat, sorted(canmoveseats), board))
            
            def go():
                self.eatpiece = board.movepiece(fromseat, toseat)

            def back():
                board.movepiece(toseat, fromseat, self.eatpiece)

            self.go = go
            self.back = back            
            self.description = board.moveseats_chinese(fromseat, toseat)            

        def __str__(self):
            return self.description
            
    def __str__(self):
        result = []
        remarkes = self.remarkes()
        line_n = self.__lineboutnum * 2
        for n, boutstr in enumerate(self.__getboutstrs()):
            result.append(boutstr)
            colnum = (n + 1) % line_n  # 求得需要填充空格的着数
            if colnum == 0:
                result.append('\n')
            remark = remarkes[n].strip()
            if remark:
                result.append(' {0}\n{1}'.format(
                    remark, ' ' * (colnum // 2 * (13+9) + (colnum % 2 * 13))))
                # [13, 9, 13, 9, 13, 9, 13, 9...]
        return ''.join(result)
        
    def __getboutstrs(self):
        '着法字符串转换集合成带序号的回合字符串'
        return ['{0:>3d}. {1!s}'.format(n // 2 + 1, walk)
                if n % 2 == 0 else
                ' {0!s}'.format(walk)
                for n, walk in enumerate(self.__walks)]
    
    def getboutstrs_ltbox(self):
        boutstrs = self.__getboutstrs()
        for n, remark in enumerate(self.remarkes()):
            if remark.strip():
                boutstrs[n] += '☆'
            if n % 2 == 1:
                boutstrs[n] = '    {0}'.format(boutstrs[n])
        return boutstrs
                
    def setstrcolumn(self, lineboutnum):
        self.__lineboutnum = lineboutnum # (boutnum % 4) if (boutnum % 4) != 0 else 4
    '''
    
    '''
    @property
    def length(self):
        return len(self.__walks)
    
    @property
    def isempty(self):
        return self.__rootwalk is None #self.length == 0

    @property
    def isstart(self):
        return self.current < 0

    @property
    def islast(self):
        return self.current == self.length - 1

    def currentwalk(self):
        return self.__walks[self.current]    
    
    def currentseat(self):
        #return (self.currentmvnode.fseat, self.currentmvnode.tseat)
        pass

    def mvnodeseats(self):
        #return [(walk.fromseat, walk.toseat) for walk in self.__walks]
        pass

    def remarkes(self):
        #return [walk.remark for walk in self.__walks]
        pass
    '''
        
#
