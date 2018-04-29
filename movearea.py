'''
中国象棋软件着法区域类型
'''

from config import *
from board import *

cellwidth = 80
cellheight = 40
cellbd = 8


class MoveArea(View, ttk.Frame):

    #canvawidth = 200
    #canvasheight = 500
    def __init__(self, master, model):
        View.__init__(self, model)
        ttk.Frame.__init__(self, master, padding=2)

        self.create_vars()
        self.createwidgets()
        self.createlayout()
        self.createbindings()
        #self.updateview()
        
    def create_vars(self):
        self.infovars = {}
        for name, value in self.board.info.items():
            var = StringVar()
            var.set(value)
            self.infovars[name] = var
        
    def createwidgets(self):
    
        def create_topfrm():
            topfrm = ttk.Frame(self, padding=2)
            Label(topfrm, # font='Helvetica -14 bold' 
                text='{} {}'.format(self.board.filename,
                self.infovars['Title'].get())).pack(fill=X) # , font='Helvetica -14 bold'
            topfrm.pack(side=TOP)

        def create_midfrm():            
            midfrm = LabelFrame(
                self,
                relief=GROOVE,
                text=' 棋谱着法 ',
                padx=2,
                pady=1,
                labelanchor='nw')
            self.vbar = Scrollbar(midfrm, orient=VERTICAL)
            self.hbar = Scrollbar(midfrm, orient=HORIZONTAL)            
            self.mvcanvas = Canvas(
                midfrm,
                relief=SUNKEN,
                width=442,
                height=508,
                #scrollregion=(0, 0, canvawidth*2, canvasheight*2),
                highlightthickness=2,
                yscrollcommand=self.vbar.set,
                xscrollcommand=self.hbar.set)
            self.remtxt = Text(midfrm, width=60, height=2)
            self.vbar.config(command=self.mvcanvas.yview)
            self.hbar.config(command=self.mvcanvas.xview)
            self.remtxt.pack(side=BOTTOM)
            self.vbar.pack(side=RIGHT, fill=Y)
            self.hbar.pack(side=BOTTOM, fill=X)            
            self.mvcanvas.pack()#,side=LEFT expand=YES, fill=BOTH
            midfrm.pack()#side=TOP,expand=YES fill=BOTH

        def create_bottomfrm():
        
            def __button(master, name, com, sid):
                Button(
                    master, text=name, width=5,
                    command=com, relief=GROOVE).pack(side=sid) #, SUNKEN

            def create_buttonfrm(bottomfrm):
                buttonfrm = ttk.Frame(bottomfrm, padding=0)
                buttdate = [
                    ('结尾', lambda: self.onEndKey(None),
                     RIGHT), 
                    ('前进', lambda: self.onDownKey(None), RIGHT),
                    ('右变', lambda: self.onRightKey(None),
                     RIGHT), 
                    ('左变', lambda: self.onLeftKey(None),
                     RIGHT), 
                    ('后退', lambda: self.onUpKey(None),
                     RIGHT), 
                    ('开始', lambda: self.onHomeKey(None),
                               RIGHT),          
                    #('换位', lambda: self.board.changeside('rotate'), LEFT), # 预留
                    ('换位', lambda: self.board.changeside('rotate'),
                     LEFT),
                    ('左右', lambda: self.board.changeside('symmetry'),
                     LEFT), 
                    ('换棋', lambda: self.board.changeside(),
                               LEFT)
                ]
                for name, com, sid in buttdate:
                    __button(buttonfrm, name, com, sid)
                Label(buttonfrm, text='      ').pack(side=LEFT)
                buttonfrm.pack(side=RIGHT)     
            
            bottomfrm = ttk.Frame(self, padding=1)
            create_buttonfrm(bottomfrm)
            bottomfrm.pack(side=BOTTOM)  # 顶部区域

        create_topfrm()  # 先打包的最后被裁切
        create_bottomfrm()
        create_midfrm()
        
    def createlayout(self):
        self.pack(side=RIGHT)  #Y, expand=YES, fill=BOTH 

    def createbindings(self):
        self.bind('<Up>', self.onUpKey)
        self.bind('<Down>', self.onDownKey)
        self.bind('<Left>', self.onLeftKey)
        self.bind('<Right>', self.onRightKey)
        self.bind('<Prior>', self.onPgupKey)
        self.bind('<Next>', self.onPgdnKey)
        self.bind('<Home>', self.onHomeKey)
        self.bind('<End>', self.onEndKey)
        self.mvcanvas.bind('<ButtonPress-1>',
                              self.onMouseLeftclick)  # Double-1

    def onUpKey(self, event):
        self.board.movestep(-1)

    def onDownKey(self, event):
        self.board.movestep()

    def onLeftKey(self, event):
        curmove = self.board.curmove
        if (curmove.prev and curmove.prev.next_ is not curmove):
            tomove = curmove.prev.next_
            while tomove.other and tomove.other is not curmove:
                tomove = tomove.other
            self.board.moveback()
            self.board.movego(tomove)
            self.board.notifyviews()
            
    def onRightKey(self, event):
        self.board.moveother()
        
    def onPgupKey(self, event):
        self.board.movestep(-10)

    def onPgdnKey(self, event):
        self.board.movestep(10)

    def onHomeKey(self, event):
        self.board.movefirst(True)

    def onEndKey(self, event):
        self.board.movelast()

    def onMouseLeftclick(self, event):
        # 接收点击信息
        self.focus_set()
        canx, cany = self.mvcanvas.canvasx(event.x), self.mvcanvas.canvasy(event.y)
        curid = self.mvcanvas.find_closest(canx, cany)
        if not (curid and curid[0] in self.mvid):
            return
        self.board.movethis(self.mvid[curid[0]])
        
    def updateview(self):
    
        def __drawinfo():
            info = self.board.info
            infotext = [
                info.get('Event', ''), '{}  {}  {}'.format(
                    info.get('Red', ''), info.get('Result', ''),
                    info.get('Black', '')), '{} 奕于 {}'.format(
                        info.get('Date', ''), info.get('Site', ''))
            ]
            #for n, label in enumerate(self.infolabel):
            #    label.config(text=infotext[n])

        def __drawmvstr():    
        
            def __mvstr(move, isother=False):
                row, col = move.stepno, move.maxcol + 1
                precol = move.prev.maxcol + 1 if isother else col
                wid = 2 if move in prevmoves else 1
                lineid = self.mvcanvas.create_line(
                        precol*cellwidth+cellwidth//2-cellbd 
                        if isother else col*cellwidth,
                        row*cellheight-cellbd,
                        col*cellwidth-cellwidth//2+cellbd
                        if isother else col*cellwidth,
                        row*cellheight+cellbd,
                        width=wid)
                recid = self.mvcanvas.create_rectangle(
                        col*cellwidth-cellwidth//2+cellbd,
                        row*cellheight+cellbd,
                        col*cellwidth+cellwidth//2-cellbd,
                        (row+1)*cellheight-cellbd,
                        width=wid,
                        fill='gray70' if move is self.board.curmove else '')
                strid = self.mvcanvas.create_text(col*cellwidth,
                        row*cellheight+cellheight//2,
                        text=move.zhstr, font='-size 10')
                self.mvid[recid] = self.mvid[strid] = move
                if move.next_:
                    __mvstr(move.next_)
                if move.other:
                    __mvstr(move.other, True)
            
            self.mvcanvas.delete('all')
            canvasheight = (self.board.maxrow + 2) * cellheight
            canvawidth = (self.board.maxcol + 2) * cellwidth
            self.mvcanvas.config(scrollregion=(0, 0, canvawidth, canvasheight))
            for i in range(1, self.board.maxrow, 2):
                self.mvcanvas.create_text(cellwidth//4,
                        i*cellheight+cellheight//2,
                        text='{:3d}'.format((i+1) // 2), font='Helvetica -14')
                if (i+1) // 2 % 2 == 0:
                    self.mvcanvas.create_line(0, (i+2)*cellheight,
                        (self.board.maxcol + 2) * cellwidth,
                        (i+2)*cellheight, fill='gray70')
                        
            self.mvid = {}
            recid = self.mvcanvas.create_oval(cellwidth//2+cellbd,
                        cellbd,
                        cellwidth+cellwidth//2-cellbd,
                        cellheight-cellbd, width=2, fill='gray70') # , outline='red'
            strid = self.mvcanvas.create_text(cellwidth, cellheight//2,
                    text='开始', font='-size 10')
            self.mvid[recid] = self.mvid[strid] = self.board.rootmove
            prevmoves = set(self.board.getprevmoves())
            if self.board.rootmove.next_:
                __mvstr(self.board.rootmove.next_)
                
            self.remtxt.delete('1.0', 'end')
            if self.board.curmove.remark:
                self.remtxt.insert('1.0', self.board.curmove.remark)
            self.mvcanvas.xview_moveto((self.board.curmove.maxcol-4)/(self.board.maxcol+2))
            self.mvcanvas.yview_moveto((self.board.curmove.stepno-10)/(self.board.maxrow+2))
            # 移动到一个比例
            
            '''
            #print(self.hbar.get())
            #print(self.vbar.get())

            hpos, vpos = self.hbar.get(), self.vbar.get()
            rowpos = self.board.curmove.stepno/(self.board.maxrow+2)
            colpos = self.board.curmove.maxcol/(self.board.maxcol+2)
            if colpos > hpos + 4/(self.board.maxcol+2):
                self.mvcanvas.xview_moveto(hpos+1/(self.board.maxcol+2))
            elif colpos < hpos - 4/(self.board.maxcol+2):
                self.mvcanvas.xview_moveto(hpos-1/(self.board.maxcol+2))
            if rowpos > vpos + 12/(self.board.maxrow+2):
                self.mvcanvas.yview_moveto(vpos+2/(self.board.maxrow+2)) # 移动到一个比例
            elif rowpos > vpos - 12/(self.board.maxcol+2):
                self.mvcanvas.yview_moveto(vpos-2/(self.board.maxrow+2))
            '''
            

        __drawinfo()
        __drawmvstr()


#
