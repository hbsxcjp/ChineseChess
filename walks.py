'中国象棋棋子着法类型'


from board import *            


class Walks(Model):
    '棋谱着法类'
            
    class Walk(object):
        '着法类'
        
        def __init__(self, fromseat, toseat, remark, board):
            '构造一步着法'
            #'''
            canmoveseats = board.canmoveseats(board.getpiece(fromseat))
            assert toseat in canmoveseats, ('走法不符合规则，可能自己被将军、将帅会面！\nfrom: {}\nto: {}\ncanmove: {}\n{}'.format(fromseat, toseat, sorted(canmoveseats), board))
            #'''        
            
            def go():
                self.eatpiece = board.movepiece(fromseat, toseat)
                
            def back():
                board.movepiece(toseat, fromseat, self.eatpiece)
                
            self.go = go
            self.back = back
            self.fromseat = fromseat
            self.toseat = toseat
            self.remark = remark
            self.description = board.moveseats_chinese(fromseat, toseat)
            
        def __str__(self):
            return self.description
        
            
    def __init__(self):
        super().__init__()
        self.__lineboutnum = 3  # 生成pgn文件的着法文本每行回合数
        self.clear()
        
    def clear(self):
        self.cursor = -1  # 着法序号 范围：0 ~ length        
        self.__walks = []
        
    def __str__(self):    
        line_n = self.__lineboutnum * 2
        blanknums = [13, 10, 13, 10, 13, 10, 13, 10]
        boutstrls = []
        for n, strwalk in enumerate(self.getboutstr()):
            boutstrls.append(strwalk)
            colnum = (n + 1) % line_n # 求得需要填充空格的着数
            if colnum == 0:
                boutstrls.append('\n')
            remark = self.__walks[n].remark.strip()
            if remark:                
                boutstrls.append(' {0}\n{1}'.format(remark, 
                    ' ' * sum(blanknums[:colnum])))
        return ''.join(boutstrls)
    
    def getboutstr(self, align=False):
        '着法字符串转换成带序号的回合字符串'
        width = 9 if align else 5 # 是否对齐
        result = []
        for n, walk in enumerate(self.__walks):
            strwalk = walk.description
            tag = '☆' if walk.remark else ''
            boutstr = ('{0:>{1}}'.format(strwalk, width) if n % 2 == 1
                    else '{0:>3d}. {1}'.format(n // 2 + 1, strwalk))
            if align:
                bstr = '{0}{1}'.format(boutstr, tag)
            result.append(boutstr)
        return result        
        
    def setstrcolumn(self, boutnum):
        self.__lineboutnum = (boutnum % 4) if (boutnum % 4) != 0 else 4

    def setcurrentside(self, side):
        self.currentside = side
            
    def transcurrentside(self):
        self.setcurrentside(not self.currentside)
            
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

    def currentwalk(self):
        return self.__walks[self.cursor]
      
    def curmoveseat(self):
        walk = self.currentwalk()
        return (walk.fromseat, walk.toseat)
        
    def cureatpiece(self):
        return self.currentwalk().eatpiece

    def curremark(self):
        return self.currentwalk().remark.strip()
        
    def moveseats(self):
        return [(walk.fromseat, walk.toseat) for walk in self.__walks]
        
    def remarkes(self):
        return [walk.remark for walk in self.__walks]
    
    def append(self, fromseat, toseat, remark, board):
        self.__walks.append(self.Walk(fromseat, toseat, remark, board))
        
    def cutfollow(self):
        self.__walks = self.__walks[:self.cursor + 1]
        
    def move(self, inc):
                
        def __forward():
            if self.isempty or self.islast:
                return
            self.cursor += 1
            self.currentwalk().go()
            self.transcurrentside()
                
        def __backward():
            if self.isstart:
                return
            self.currentwalk().back()
            self.transcurrentside()
            self.cursor -= 1

        function = __forward if inc > 0 else __backward
        [function() for _ in range(abs(inc))]
 
    def move_refresh(self, inc):
        self.move(inc)
        self.notifyviews()
        

#        