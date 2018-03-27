'中国象棋棋子着法类型-树结构'

from board import Model
from piece import BlankPie


class Walks(Model):
    '棋谱着法类-树结构'    
        
    def __init__(self, board, chessfile):
        super().__init__()
        self.board = board
        self.chessfile = chessfile
        self.currentnode = chessfile.rootnode
        self.cureatpiece = BlankPie
        #self.__lineboutnum = 3  # 生成pgn文件的着法文本每行回合数
        
    def __str__(self):    
        def __adddesc(node):
            if not node:
                return
            descls.append(node.desc)
            __adddesc(node.next_)
            __adddesc(node.other)    
                
        self.setdesc(self.chessfile.rootnode.next_) # 驱动调用递归函数
        descls = []
        __adddesc(self.chessfile.rootnode.next_)
        return ' '.join(descls)

    def setdesc(self, node):
        if not node:
            return
        node.desc = self.board.moveseats_chinese(node.fseat, node.tseat)
        eatpiece = self.board.movepiece(node.fseat, node.tseat)
        self.setdesc(node.next_)
        self.board.movepiece(node.tseat, node.fseat, eatpiece)
        self.setdesc(node.other)
    
    @property
    def currentside(self):
        self.currentside = color

    def __transside(self):
        self.__setside(other_color(self.currentside))
        
    def getprevmoves(self, node):
        result = []
        while result[-1].prev is not self.chessfile.rootnode:
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
        
    '''                            
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
        
#
