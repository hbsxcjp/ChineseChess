'中国象棋棋子着法类型-树结构'

from board import Model
from piece import BlankPie


class MoveNode(object):
    '象棋着法树节点类'
    colchars = 'abcdefghi'
        
    def __init__(self, prev=None):
        self.stepno = 0 # 着法图中的行位置
        self.fseat = (0, 0)
        self.tseat = (0, 0)
        self.prev = prev
        self.next_ = None
        self.other = None
        self.remark = ''
        self.desc = ''
        self.othcol = 0 # 着法图中的列位置
        
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
        
    def __init__(self, board, rootnode):
        super().__init__()
        self.board = board
        self.rootnode = rootnode
        self.currentnode = rootnode
        self.cureatpiece = BlankPie
        
    def __str__(self):
    
        def __setchar(node):
            firstcol = node.othcol * 5
            linestr[node.stepno * 2][firstcol: firstcol + 4] = node.desc
            if node.next_:
                linestr[node.stepno * 2 + 1][firstcol + 1: firstcol + 3] = [' ↓', ' ']
                __setchar(node.next_)
            if node.other:
                linef = firstcol + 4
                linel = node.other.othcol * 5
                linestr[node.stepno * 2][linef: linel] = '…' * (linel - linef)
                __setchar(node.other)
            
        self.setdesc()
        linestr = [['　' for _ in range((self.othcol + 1) * 5)]
                    for _ in range((self.maxrow + 1) * 2)]
        __setchar(self.rootnode)
        return '\n'.join([''.join(line) for line in linestr])

    def setdesc(self):
    
        def __setdesc(node):
            node.desc = self.board.moveseats_chinese(node.fseat, node.tseat)
            self.maxrow = max(self.maxrow, node.stepno)
            node.othcol = self.othcol # 存储节点的列数
            eatpiece = self.board.movepiece(node.fseat, node.tseat)
            if node.next_:
                __setdesc(node.next_)
            self.board.movepiece(node.tseat, node.fseat, eatpiece)
            if node.other:
                self.othcol += 1
                __setdesc(node.other)
    
        self.maxrow = 0 # 存储最大行数
        self.othcol = 0 # 存储最大列数
        self.rootnode.desc = '　开始　'
        __setdesc(self.rootnode.next_) # 驱动调用递归函数
        
    def getprevmoves(self, node):
        result = []
        while result[-1].prev is not self.rootnode:
            result.append(result[-1].prev)
        return reversed(result)
                
    def getnextmoves(self, node):
        result = [node]
        while result[-1].next_ is not None:
            result.append(result[-1].next_)
        return result
                
    def moveforward(self, inc=1):
        for _ in range(inc):
            if self.currentnode.next_ is None:
                break
            self.currentnode = self.currentnode.next_   
            self.cureatpiece = self.board.movepiece(self.currentnode.fseat, 
                    self.currentnode.tseat)
        self.notifyviews()            

    def movebackward(self, inc=1):                    
        for _ in range(inc):
            if self.currentnode.prev is None:
                break
            self.board.movepiece(self.currentnode.tseat, 
                    self.currentnode.fseat, self.cureatpiece)
            self.currentnode = self.currentnode.prev
        self.notifyviews()

    def moveother(self):
        '移动到当前节点的另一变着'
        if self.currentnode.other is None:
            return        
        self.board.movepiece(self.currentnode.tseat, 
                self.currentnode.fseat, self.cureatpiece)
        self.board.movepiece(self.currentnode.other.fseat, 
                        self.currentnode.other.tseat)
        self.currentnode = self.currentnode.other
        self.notifyviews()

    def movefirst(self):
        self.movebackward(len(self.getprevmoves(self.currentnode))+1)
    
    def movelast(self):
        self.moveforward(len(self.getnextmoves(self.currentnode)))
        
    def moveassign(self, node):
        self.movefirst()
        for node in self.getprevmoves(node):
            self.board.movepiece(node.fseat, node.tseat)
        self.cureatpiece = self.board.movepiece(node.fseat, node.tseat)
        self.currentnode = node
        self.notifyviews()
            
    def cutfollow(self):
        self.currentnode.next_ = None

    def addnext(self, node):
        self.currentnode.next_ = node
        self.moveforward()
        
    def addother(self, node):
        self.currentnode.other = node
        self.moveother()
        
        
#
