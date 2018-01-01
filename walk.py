'''
中国象棋棋子着法类型
'''

from board import *


class Walk(object):
    # 着法类
    
    def __init__(self, go, back, remark):
        # 构造一步着法
        assert callable(go) and callable(back), '参数不是可运行的！'
        self.go = go
        self.back = back
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
            
    def transcurrentside(self):
        self.currentside = Piece.otherside(self.currentside)
        
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
        return self.__walks[self.cursor]
      
    def moveseats(self):
        return [(walk.fromseat, walk.toseat) for walk in self.__walks]
        
    def append(self, walk):
        self.__walks.append(walk)
        
    def cutfollow(self):
        self.__walks = self.__walks[:self.cursor + 1]
        
    def move(self, inc):
                
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
 
    def move_refresh(self, inc):
        self.move(inc)
        self.notifyviews()


#            