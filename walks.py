'中国象棋棋子着法类型'

from board import *


class Walks(Model):
    '棋谱着法类'

    class Walk(object):
        '着法类'

        def __init__(self, fromseat, toseat, remark, board):
            '构造一步着法'
            '''
            canmoveseats = board.canmoveseats(board.getpiece(fromseat))
            assert toseat in canmoveseats, (
                '走法不符合规则，可能自己被将军、将帅会面！\nfrom: {}\nto: {}\ncanmove: {}\n{}'.
                format(fromseat, toseat, sorted(canmoveseats), board))
            '''

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
        self.__walks = []
        self.cursor = -1  # 着法序号 范围：0 ~ length
        
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

    def setcurrentside(self, color):
        self.currentside = color

    def transcurrentside(self):
        self.setcurrentside(other_color(self.currentside))

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

    def cutfollow(self):
        self.__walks = self.__walks[:self.cursor + 1]

    def move(self, inc=1):
        def __go():
            if self.isempty or self.islast:
                return
            self.cursor += 1
            self.currentwalk().go()
            self.transcurrentside()

        def __back():
            if self.isstart:
                return
            self.currentwalk().back()
            self.transcurrentside()
            self.cursor -= 1

        function = __go if inc > 0 else __back
        [function() for _ in range(abs(inc))]

    def move_refresh(self, inc=1):
        self.move(inc)
        self.notifyviews()

    def append(self, fromseat, toseat, remark, board):
        self.__walks.append(self.Walk(fromseat, toseat, remark, board))
        self.move()

    def loadmoveseats(self, moveseats, remarkes, board):
        self.clear()
        for n, (fromseat, toseat) in enumerate(moveseats):
            self.append(fromseat, toseat, remarkes[n], board)
        self.move(-self.length)


#
