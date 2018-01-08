'''
中国象棋软件棋盘类型
'''

from config_et import *
from cross import *
from walks import *

BorderWidth = 521
BoardHeight = 577
BorderBdWidth = 32
PieWidth = 57
PieHeight = 57
PieBdWidth = 4

ImgBdStartX = PieBdWidth * 5 + PieWidth * 3
ImgBdStartY = 30
BoardStartX = ImgBdStartX + BorderBdWidth
BoardStartY = ImgBdStartY + BorderBdWidth
CanvasWidth = ImgBdStartX + BorderWidth
CanvasHeight = ImgBdStartY * 2 + BoardHeight

OvalRadius = 8
OutsideXY = (-1000, -1000)

TagLength = (BorderWidth - (NumCols - 1) * PieBdWidth) // NumCols

EatpieStartXY = PieBdWidth * 2 + PieWidth // 2
EatpieStepX = PieWidth * 2 // 3
EatpieStepY = PieBdWidth + PieWidth
EatpieEndY = EatpieStartXY + 3 * EatpieStepY
EatpieEndX = EatpieStartXY + 3 * EatpieStepX


class BdCanvas(View, Canvas):
    '棋盘与棋子'
    def __init__(self, master, models):
        View.__init__(self, models)
        Canvas.__init__(self, master, width=CanvasWidth, height=CanvasHeight)

        self.createwidgets()
        self.createlayout()
        self.createbindings()
        self.initseat()
        self.updateview()

    def initseat(self):
        self.locatedseat = (0, 0)
        self.selectedseat = None

    def __canvastexts(self):
        def __textxys(bottomside=RED_SIDE):
            '图形框内文字坐标'
            PondTopTextX, PondTopTextY = ImgBdStartX // 2, CanvasHeight // 2 - PieHeight // 2
            PondBottomTextX, PondBottomTextY = ImgBdStartX // 2, CanvasHeight // 2 + PieHeight // 2
            PondTopText = PondText[not bottomside]
            PondBottomText = PondText[bottomside]
            textxys = [(PondTopTextX, PondTopTextY, PondTopText),
                       (PondBottomTextX, PondBottomTextY, PondBottomText)]
            for i in range(NumCols):
                textx = ImgBdStartX + i * (
                    TagLength + PieBdWidth) + TagLength // 2
                textxys.append((textx, ImgBdStartY // 2,
                                NumToChinese[not bottomside][i + 1]))
                textxys.append((textx, CanvasHeight - ImgBdStartY // 2,
                                NumToChinese[bottomside][NumCols - i]))
            return textxys

        PondText = {BLACK_SIDE: '黑方吃子', RED_SIDE: '红方吃子'}
        self.delete('side_tag')
        for x, y, astr in __textxys(self.board.bottomside):
            self.create_text(
                x, y, font=('Consolas', '10'), text=astr, tag='side_tag')

    def createwidgets(self):
        def __canvasrects():
            def __rectxys():
                # 图形框坐标
                TopPondXY = (PieBdWidth, PieBdWidth,
                             ImgBdStartX - PieBdWidth * 2,
                             CanvasHeight // 2 - PieBdWidth * 3)
                BottomPondXY = (PieBdWidth, CanvasHeight // 2 + PieBdWidth * 3,
                                ImgBdStartX - PieBdWidth * 2,
                                CanvasHeight - PieBdWidth)
                rectxys = [TopPondXY, BottomPondXY]
                TopNumY0, TopNumY1 = PieBdWidth, ImgBdStartY - PieBdWidth
                BottomNumY0, BottomNumY1 = (
                    ImgBdStartY + BoardHeight + PieBdWidth,
                    CanvasHeight - PieBdWidth)
                for i in range(NumCols):
                    rectx = ImgBdStartX + i * (TagLength + PieBdWidth)
                    rectxys.append((rectx, TopNumY0, rectx + TagLength,
                                    TopNumY1))
                    rectxys.append((rectx, BottomNumY0, rectx + TagLength,
                                    BottomNumY1))
                return rectxys

            for x0, y0, x1, y1 in __rectxys():
                self.create_rectangle(
                    x0, y0, x1, y1, outline='gray60', width=1)

        def __createimgs(bdimgname, pimgpath):
            self.imgs = []  # 棋盘、棋子、痕迹图像，tag='bd','pie','from','to', 'trace',
            self.pieimgids = {}  # 存储棋子图像的imgid
            #print('棋盘图像文件：', bdimgname)
            self.imgs.append(PhotoImage(file=bdimgname))
            self.create_image(
                ImgBdStartX,
                ImgBdStartY,
                image=self.imgs[-1],
                anchor=NW,
                tag='bd')  # 载入棋盘图像

            self.imgs.append(
                PhotoImage(file=pimgpath + Config.imgflnames['trace']))
            self.create_image(OutsideXY, image=self.imgs[-1], tag='from')
            self.create_image(OutsideXY, image=self.imgs[-1], tag='to')

            pieimgids = []
            for char in Pieces.Chars:
                self.imgs.append(
                    PhotoImage(file=pimgpath + Config.imgflnames[char]))
                pieimgids.append(
                    self.create_image(
                        OutsideXY, image=self.imgs[-1], tag='pie'))
            self.board.pieces.setpieimgids(pieimgids)

            for side, char in {RED_SIDE: 'KING', BLACK_SIDE: 'king'}.items():
                self.imgs.append(
                    PhotoImage(file=pimgpath + Config.imgflnames[char]))
                self.board.getkingpiece(side).eatimgid = self.create_image(
                    OutsideXY, image=self.imgs[-1], tag='pie')

        bdimgname = self.master.config.getelement('bdimgname').text
        pimgpath = self.master.config.getelement('pimgpath').text
        __canvasrects()
        __createimgs(bdimgname, pimgpath)

    def createlayout(self):
        self.pack(side=LEFT)

    def createbindings(self):
        #self.bind('<FocusIn>', self.onFocusIn)
        self.bind('<Left>', self.onLeftKey)
        self.bind('<Right>', self.onRightKey)
        self.bind('<Up>', self.onUpKey)
        self.bind('<Down>', self.onDownKey)
        self.bind('<Home>', self.onHomeKey)
        self.bind('<End>', self.onEndKey)
        self.bind('<Delete>', self.onDeleteKey)
        self.bind('<Next>', self.onPgdnKey)
        self.bind('<space>', self.onspaceKey)
        self.bind('<Return>', self.onspaceKey)
        self.bind('<ButtonPress-1>', self.onMouseLeftclick)  # 绑定点击事件

    def xy_seat(self, x, y):
        return (
            NumRows - abs(y + PieHeight // 2 - BoardStartY) // PieHeight - 1,
            abs(x + PieWidth // 2 - BoardStartX) // PieWidth)

    def seat_xy(self, seat):
        row, col = CrossT.getrow(seat), CrossT.getcol(seat)
        return (BoardStartX + col * PieWidth,
                BoardStartY + (NumRows - row - 1) * PieHeight)

    def getoval_xy(self, seat):
        '根据row, col取得画圆用的坐标值'
        x, y = self.seat_xy(seat)
        return (x - OvalRadius, y - OvalRadius, x + OvalRadius, y + OvalRadius)

    def geteatpie_xy(self, side, n=-1):
        '获取被杀棋子的存放位置, ran=True则随机位置存放（需要模型数据）'
        isbottomside = self.board.isbottomside(side)
        if n >= 0:
            kr, kc = n // 4, n % 4
            x = EatpieStartXY + kc * EatpieStepX
            EatpieEndY = EatpieStartXY + kr * EatpieStepY
            y = (CanvasHeight - EatpieEndY) if isbottomside else EatpieEndY
        else:
            x = randint(EatpieStartXY, EatpieEndX)
            miny, maxy = ((CanvasHeight - EatpieEndY,
                           CanvasHeight - EatpieStartXY)
                          if isbottomside else (EatpieStartXY, EatpieEndY))
            y = randint(miny, maxy)
        return (x, y)

    def onLeftKey(self, event):
        col = CrossT.getcol(self.locatedseat)
        self.setlocatedseat((
                CrossT.getrow(self.locatedseat), col - 1
                if col > MinColNo else MaxColNo))

    def onRightKey(self, event):
        col = CrossT.getcol(self.locatedseat)
        self.setlocatedseat((
                CrossT.getrow(self.locatedseat), col + 1
                if col < MaxColNo else MinColNo))

    def onUpKey(self, event):
        row = CrossT.getrow(self.locatedseat)
        self.setlocatedseat((row + 1 if row < MaxRowNo_T else MinRowNo_B,
                             CrossT.getcol(self.locatedseat)))

    def onDownKey(self, event):
        row = CrossT.getrow(self.locatedseat)
        self.setlocatedseat((row - 1 if row > MinRowNo_B else MaxRowNo_T,
                             CrossT.getcol(self.locatedseat)))

    def onHomeKey(self, event):
        self.setlocatedseat((MaxRowNo_T, CrossT.getcol(self.locatedseat)))

    def onEndKey(self, event):
        self.setlocatedseat((MinRowNo_B, CrossT.getcol(self.locatedseat)))

    def onDeleteKey(self, event):
        self.setlocatedseat((CrossT.getrow(self.locatedseat), MinColNo))

    def onPgdnKey(self, event):
        self.setlocatedseat((CrossT.getrow(self.locatedseat), MaxColNo))

    def setlocatedseat(self, seat):
        self.locatedseat = seat
        self.coords('to' if self.selectedseat else 'from', self.seat_xy(seat))

    def onMouseLeftclick(self, event):
        self.focus_set()
        if (event.x < ImgBdStartX or ImgBdStartY > event.y
                or event.y > CanvasHeight - ImgBdStartY):
            return
        self.onspaceKey(event, True)  # 调用空格按键函数

    def onspaceKey(self, event, mouseclick=False):
        def __drawselectedseat():
            self.selectedseat = self.locatedseat
            self.delete('walk')
            self.coords('to', OutsideXY)
            self.coords('from', self.seat_xy(self.selectedseat))
            for seat in self.board.canmoveseats(
                    self.board.getpiece(self.selectedseat)):
                self.create_oval(
                    self.getoval_xy(seat),
                    outline='blue',
                    fill='blue',
                    tag='walk')
            self.tag_raise('walk', 'pie')
            playsound('CLICK')  # 5: 选择声音

        def __movepie(fromseat, toseat):
            def __change():
                if askyesno('提示', '改变当前着法，' '将删除原棋局的全部后续着法！\n是否删除？'):
                    self.walks.cutfollow()
                    return True

            if toseat in self.board.canmoveseats(
                    self.board.getpiece(fromseat)):
                if self.walks.islast or __change():
                    self.walks.append(fromseat, toseat, '',
                                      self.chessboard.board)
                    self.walks.notifyviews()
                    self.selectedseat = None
            else:
                playsound('ILLEGAL')  # 点击位置不正确声音

        currentside = self.walks.currentside
        if self.board.isdied(currentside):  # 已被将死
            return
        if mouseclick:
            self.setlocatedseat(self.xy_seat(event.x, event.y))
        if self.board.getside(self.locatedseat) == currentside:
            __drawselectedseat()
        elif self.selectedseat:
            __movepie(self.selectedseat, self.locatedseat)
        

    def updateview(self):
        def __drawallpies():
            livepieces = self.board.getlivepieces()
            #livecrosses =
            [
                self.coords(pie.imgid, self.seat_xy(pie.seat))
                for pie  #seat, 
                in livepieces
            ]  #livecrosses.items()]
            eatpies = self.board.geteatedpieces()
            for side in [RED_SIDE, BLACK_SIDE]:
                eatpieimgids = sorted(
                    [pie.imgid for pie in eatpies if pie.side == side])
                [
                    self.coords(imgid, self.geteatpie_xy(not side, n))
                    for n, imgid in enumerate(eatpieimgids)
                ]

        def __drawtraces():
            if self.walks.isstart:
                fromxy, toxy = OutsideXY, OutsideXY
            else:
                fromseat, toseat = self.walks.curmoveseat()
                fromxy, toxy = self.seat_xy(fromseat), self.seat_xy(toseat)
            self.delete('walk')
            self.coords('from', fromxy)
            self.coords('to', toxy)

        def __moveeffect():
            currentside = self.walks.currentside
            kingseat = self.board.getkingseat(currentside)
            kingpie = self.board.getkingpiece(currentside)
            otherkingpie = self.board.getkingpiece(not currentside)
            self.coords(kingpie.eatimgid, OutsideXY)
            self.coords(otherkingpie.eatimgid, OutsideXY)
            if self.board.isdied(currentside):  # 将死后，将帅图像更改
                self.coords(kingpie.imgid, OutsideXY)
                self.coords(kingpie.eatimgid, self.seat_xy(kingseat))
                playsound('WIN')
            elif self.board.iskilled(currentside):  # 走棋后，将军
                color = 'black' if currentside == RED_SIDE else 'red'
                self.create_oval(
                    self.getoval_xy(kingseat),
                    outline=color,
                    fill=color,
                    tag='walk')  # , width=4
                playsound('CHECK2')
            elif not self.walks.isstart:
                eatpiece = self.walks.cureatpiece()
                playsound('MOVE' if eatpiece is BlankPie else (
                    'CAPTURE2' if eatpiece.isStronge else 'CAPTURE'))

        assert self.board.getkingseat(RED_SIDE), '将帅不在棋盘上？'
        self.__canvastexts()
        __drawallpies()
        __drawtraces()
        __moveeffect()


#
