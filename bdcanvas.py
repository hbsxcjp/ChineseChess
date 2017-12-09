'''
中国象棋软件棋盘类型
'''

from config_et import *
from crossbase import *
from walk import *


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

PondText = {BLACK_SIDE: '黑方吃子', RED_SIDE: '红方吃子'}
TagLength = (BorderWidth - (NumCols - 1) * PieBdWidth) // NumCols

EatpieStartXY = PieBdWidth * 2 + PieWidth // 2
EatpieStepX = PieWidth * 2 // 3
EatpieStepY = PieBdWidth + PieWidth
EatpieEndY = EatpieStartXY + 3 * EatpieStepY
EatpieEndX = EatpieStartXY + 3 * EatpieStepX            
              
                    
class BdCanvas(View, Canvas):
    # 棋盘与棋子
    def __init__(self, master, models, bdimgname, pimgpath):
        View.__init__(self, models)
        Canvas.__init__(self, master, width=CanvasWidth, height=CanvasHeight)
        
        self.create_widgets(bdimgname, pimgpath)
        self.create_layout()
        self.create_bindings()
        self.init_sel()
        
    def init_sel(self):
        self.sel_rowcol = (0, 0)
        self.selfrom_rowcol = None    

    def __canvas_texts(self):
        def __textxys(bottomside=RED_SIDE):
            # 图形框内文字坐标
            PondTopTextX, PondTopTextY = ImgBdStartX // 2, CanvasHeight // 2 - PieHeight // 2
            PondBottomTextX, PondBottomTextY = ImgBdStartX // 2, CanvasHeight // 2 + PieHeight // 2
            PondTopText = PondText[CrossTrans.gettopside(bottomside)]
            PondBottomText = PondText[bottomside]
            textxys = [(PondTopTextX, PondTopTextY, PondTopText), 
                        (PondBottomTextX, PondBottomTextY, PondBottomText)]
            for i in range(NumCols):
                textx = ImgBdStartX + i * (TagLength + PieBdWidth) + TagLength // 2
                textxys.append((textx, ImgBdStartY // 2,
                    WalkConvert.NumToChinese[CrossTrans.gettopside(bottomside)][i+1]))
                textxys.append((textx, CanvasHeight - ImgBdStartY // 2, 
                        WalkConvert.NumToChinese[bottomside][NumCols-i]))
            return textxys

        self.delete('side_tag')
        for x, y, astr in __textxys(self.board.bottomside):
            self.create_text(x, y, font=('Consolas', '10'), text=astr, tag='side_tag')
            
    def create_widgets(self, bdimgname, pimgpath):                  
                
        def __canvas_rects():
            def __rectxys():
                # 图形框坐标
                TopPondXY = (PieBdWidth, PieBdWidth, ImgBdStartX - PieBdWidth * 2,
                            CanvasHeight // 2 - PieBdWidth * 3)
                BottomPondXY = (PieBdWidth, CanvasHeight // 2 + PieBdWidth * 3,
                            ImgBdStartX - PieBdWidth * 2, CanvasHeight - PieBdWidth)
                rectxys = [TopPondXY, BottomPondXY]   
                TopNumY0, TopNumY1 = PieBdWidth, ImgBdStartY - PieBdWidth
                BottomNumY0, BottomNumY1 = (ImgBdStartY + BoardHeight + PieBdWidth, 
                            CanvasHeight - PieBdWidth)
                for i in range(NumCols):
                    rectx = ImgBdStartX + i * (TagLength + PieBdWidth)
                    rectxys.append((rectx, TopNumY0, rectx + TagLength, TopNumY1))
                    rectxys.append((rectx, BottomNumY0, rectx + TagLength, BottomNumY1))
                return rectxys

            for x0, y0, x1, y1 in __rectxys():
                self.create_rectangle(x0, y0, x1, y1, outline='gray60', width=1)
                
        def __create_imgs(bdimgname, pimgpath):                     
            self.imgs = [] # 棋盘、棋子、痕迹图像，tag='bd','pie','from','to', 'trace', 
            self.pieimgids = {} # 存储棋子图像的imgid
            self.imgs.append(PhotoImage(file=bdimgname))
            self.create_image(ImgBdStartX, ImgBdStartY, image=self.imgs[-1],
                        anchor=NW, tag='bd')  # 载入棋盘图像 
                        
            self.imgs.append(PhotoImage(file = pimgpath + imgflnames['trace']))
            self.create_image(OutsideXY, image=self.imgs[-1], tag='from')
            self.create_image(OutsideXY, image=self.imgs[-1], tag='to')
            
            for pie in self.board.pieces.pieces:
                self.imgs.append(PhotoImage(file = pimgpath + imgflnames[pie.char]))
                pie.imgid = self.create_image(OutsideXY, image=self.imgs[-1], tag='pie')
                
            for side, char in {RED_SIDE: 'KK', BLACK_SIDE: 'kk'}.items():
                self.imgs.append(PhotoImage(file = pimgpath + imgflnames[char]))
                self.board.pieces.getkingpiece(side).eatimgid = self.create_image(OutsideXY,
                        image=self.imgs[-1], tag='pie')                    
        
        __canvas_rects()
        __create_imgs(bdimgname, pimgpath)
        #print([(str(pie), pie.imgid) for pie in self.board.pieces.pieces])
        
        
    def create_layout(self):
        self.pack(side=LEFT)

    def create_bindings(self):
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
        self.bind('<ButtonPress-1>', self.onMouseLeftclick) # 绑定点击事件
        
    def xy_rowcol(self, x, y):
        return (NumRows - abs(y + PieHeight // 2 - BoardStartY) // PieHeight - 1,
                abs(x + PieWidth // 2 - BoardStartX) // PieWidth)

    def rowcol_xy(self, rowcol):
        row, col = rowcol
        return (BoardStartX + col * PieWidth,
                BoardStartY + (NumRows - row - 1) * PieHeight)

    def getoval_xy(self, rowcol):
        # 根据row, col取得画圆用的坐标值
        x, y = self.rowcol_xy(rowcol)
        return (x - OvalRadius, y - OvalRadius, x + OvalRadius, y + OvalRadius)
        
    def geteatpie_xy(self, side, n=-1):
        # 获取被杀棋子的存放位置, ran=True则随机位置存放（需要模型数据）
        isbottomside = self.board.isbottomside(side)
        if n >= 0:
            kr, kc = n // 4, n % 4
            x = EatpieStartXY + kc * EatpieStepX
            EatpieEndY = EatpieStartXY + kr * EatpieStepY
            y = (CanvasHeight - EatpieEndY) if isbottomside else  EatpieEndY
        else:
            x = randint(EatpieStartXY, EatpieEndX)
            miny, maxy = ((CanvasHeight - EatpieEndY, CanvasHeight - EatpieStartXY)
                    if isbottomside else (EatpieStartXY, EatpieEndY))
            y = randint(miny, maxy)
        return (x, y)
        
    def onLeftKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0], 
                self.sel_rowcol[1]-1 if self.sel_rowcol[1] > MinColNo else MaxColNo))
        
    def onRightKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0], 
                self.sel_rowcol[1]+1 if self.sel_rowcol[1] < MaxColNo else MinColNo))
       
    def onUpKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0]+1
                if self.sel_rowcol[0] < MaxRowNo_T else MinRowNo_B, self.sel_rowcol[1]))
        
    def onDownKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0]-1
                if self.sel_rowcol[0] > MinRowNo_B else MaxRowNo_T, self.sel_rowcol[1]))
        
    def onHomeKey(self, event): 
        self.setsel_rowcol((MaxRowNo_T, self.sel_rowcol[1]))
        
    def onEndKey(self, event): 
        self.setsel_rowcol((MinRowNo_B, self.sel_rowcol[1]))
        
    def onDeleteKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0], MinColNo))
        
    def onPgdnKey(self, event): 
        self.setsel_rowcol((self.sel_rowcol[0], MaxColNo))
        
    def setsel_rowcol(self, rowcol):
        self.sel_rowcol = rowcol
        self.coords('to' if self.selfrom_rowcol else 'from', self.rowcol_xy(rowcol))

    def onMouseLeftclick(self, event):
        # 接收棋盘点击信息
        self.focus_set()
        if (event.x < ImgBdStartX or ImgBdStartY > event.y
                or event.y > CanvasHeight - ImgBdStartY):
            return
        self.onspaceKey(event, True) # 调用空格按键函数

    def onspaceKey(self, event, mouseclick=False):  
        def __drawselfrom_rowcol():   
            self.selfrom_rowcol = self.sel_rowcol
            self.delete('walk')
            self.coords('to', OutsideXY)
            self.coords('from', self.rowcol_xy(self.selfrom_rowcol))
            for rowcol in self.board.canmoverowcols(self.selfrom_rowcol):                
                self.create_oval(self.getoval_xy(rowcol), outline='blue', fill='blue', tag='walk')
            self.tag_raise('walk', 'pie')
            playsound('CLICK') # 5: 选择声音
                    
        def __movepie(fromrowcol, torowcol): 
            def __change():
                if askyesno('提示', '改变当前着法，'
                    '将删除原棋局的全部后续着法！\n是否删除？'):
                    self.walks.cutfollow()
                    return True
                return False
            
            if torowcol in self.board.canmoverowcols(fromrowcol):
                if self.walks.islast or __change():
                    self.walks.append(self.chessboard.createwalk(fromrowcol, torowcol))
                    self.walks.location(1)  # 更新视图
                    self.selfrom_rowcol = None                    
            else:
                playsound('ILLEGAL') # 点击位置不正确声音
        
        currentside = self.walks.currentside
        if self.board.isdied(currentside): # 已被将死 
            return
        if mouseclick:
            self.setsel_rowcol(self.xy_rowcol(event.x, event.y))
        if self.board.getside(self.sel_rowcol) == currentside:
            __drawselfrom_rowcol()
        elif self.selfrom_rowcol:
            __movepie(self.selfrom_rowcol, self.sel_rowcol)

    def updateview(self):
        def __drawallpies():
            livecrosses = self.board.getlivecrosses()
            [self.coords(pie.imgid, self.rowcol_xy(rowcol)) for rowcol, pie
                    in livecrosses.items()]
            eatpies = set(self.board.pieces.pieces) - set(livecrosses.values())          
            for side in [RED_SIDE, BLACK_SIDE]:
                eatpieimgids = sorted([pie.imgid for pie in eatpies if pie.side == side])
                [self.coords(imgid, self.geteatpie_xy(CrossTrans.getotherside(side), n))
                        for n, imgid in enumerate(eatpieimgids)]
            
        def __drawtraces():
            if self.walks.isstart:
                fromxy, toxy = OutsideXY, OutsideXY
            else:
                fromrowcol, torowcol = self.walks.currentwalk().moverowcol
                fromxy, toxy = self.rowcol_xy(fromrowcol), self.rowcol_xy(torowcol)
            self.delete('walk')
            self.coords('from', fromxy)
            self.coords('to', toxy)
            
        def __moveeffect():
            currentside = self.walks.currentside
            kingrowcol = self.board.getkingrowcol(currentside)
            if self.board.isdied(currentside): # 将死后，将帅图像更改
                kingpie = self.board.pieces.getkingpiece(currentside)
                self.coords(kingpie.imgid, OutsideXY)
                self.coords(kingpie.eatimgid, self.rowcol_xy(kingrowcol))
                playsound('WIN')
            elif self.board.iskilled(currentside): # 走棋后，将军
                color = 'black' if currentside == RED_SIDE else 'red'
                self.create_oval(self.getoval_xy(kingrowcol),
                        outline=color, fill=color, tag='walk') # , width=4
                playsound('CHECK2')
            elif not self.walks.isstart:
                eatpiece = self.walks.currentwalk().eatpiece
                playsound('MOVE' if eatpiece is BlankPie else
                            ('CAPTURE2' if eatpiece.isStronge else 'CAPTURE')) 
            
        self.__canvas_texts()
        if self.board.getkingrowcol(RED_SIDE):
            __drawallpies()
            __drawtraces()
            __moveeffect()
        else:
            print('将帅不在棋盘上？')

       