'''
中国象棋软件着法区域类型
'''

from config import *
from board import *


class MoveArea(View, ttk.Frame):

    #canvawidth = 200
    #canvasheight = 500
    cellwidth = 82
    cellheight = 40
    cellbd = 8

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
                text=self.infovars['Title'].get()).pack(fill=X) # , font='Helvetica -14 bold'
            topfrm.pack(side=TOP)

        def create_midfrm():
            
            def __initdraw():
                self.mvcanvas.create_oval(self.cellwidth//2+self.cellbd, self.cellbd,
                        self.cellwidth+self.cellwidth//2-self.cellbd,
                        self.cellheight-self.cellbd, width=2) # , outline='red'
                self.mvcanvas.create_text(self.cellwidth, self.cellheight//2, text='开始', font='-size 10')
                
            midfrm = LabelFrame(
                self,
                relief=GROOVE,
                text=' 棋谱着法 ',
                padx=2,
                pady=1,
                labelanchor='nw')
            vbar = Scrollbar(midfrm, orient=VERTICAL)
            hbar = Scrollbar(midfrm, orient=HORIZONTAL)            
            self.mvcanvas = Canvas(
                midfrm,
                relief=SUNKEN,
                width=456,
                height=536,
                #scrollregion=(0, 0, self.canvawidth*2, self.canvasheight*2),
                highlightthickness=2,
                yscrollcommand=vbar.set,
                xscrollcommand=hbar.set) 
            vbar.config(command=self.mvcanvas.yview)
            hbar.config(command=self.mvcanvas.xview)               
            vbar.pack(side=RIGHT, fill=Y)
            hbar.pack(side=BOTTOM, fill=X)            
            self.mvcanvas.pack()#,side=LEFT expand=YES, fill=BOTH
            __initdraw()
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
                     RIGHT), ('前进', lambda: self.onDownKey(None), RIGHT),
                    ('右变', lambda: self.onRightKey(None),
                     RIGHT), 
                    ('左变', lambda: self.onLeftKey(None),
                     RIGHT), 
                    ('后退', lambda: self.onUpKey(None),
                     RIGHT), ('开始', lambda: self.onHomeKey(None),
                               RIGHT),          
                    ('换位', lambda: self.board.changeside('rotate'),
                     LEFT), # 预留
                    ('换位', lambda: self.board.changeside('rotate'),
                     LEFT),
                    ('左右', lambda: self.board.changeside('symmetry'),
                     LEFT), ('换棋', lambda: self.board.changeside(),
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
        self.mvcanvas.bind('<Button-1>',
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
            self.board.movebackward()
            self.board.movegoto(tomove)
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
                        precol*self.cellwidth+self.cellwidth//2-self.cellbd 
                        if isother else col*self.cellwidth,
                        row*self.cellheight-self.cellbd,
                        col*self.cellwidth-self.cellwidth//2+self.cellbd
                        if isother else col*self.cellwidth,
                        row*self.cellheight+self.cellbd,
                        width=wid, tag='mv')
                recid = self.mvcanvas.create_rectangle(
                        col*self.cellwidth-self.cellwidth//2+self.cellbd,
                        row*self.cellheight+self.cellbd,
                        col*self.cellwidth+self.cellwidth//2-self.cellbd,
                        (row+1)*self.cellheight-self.cellbd,
                        width=wid, tag='mv')
                strid = self.mvcanvas.create_text(col*self.cellwidth,
                        row*self.cellheight+self.cellheight//2, text=move.zhstr, font='-size 10', tag='mv')
                self.mvid[recid] = self.mvid[strid] = move
                if move.next_:
                    __mvstr(move.next_)
                if move.other:
                    __mvstr(move.other, True)
            
            self.mvcanvas.delete('mv')
            self.canvasheight = (self.board.maxrow + 2) * self.cellheight
            self.canvawidth = (self.board.maxcol + 2) * self.cellwidth
            self.mvcanvas.config(scrollregion=(0, 0, self.canvawidth, self.canvasheight))
            for i in range(1, self.board.maxrow, 2):
                self.mvcanvas.create_text(self.cellwidth//4,
                        i*self.cellheight+self.cellheight//2,
                        text='{:3d}'.format((i+1) // 2), font='Helvetica -14', tag='mv')  # 字中心点
                if (i+1) // 2 % 2 == 0:
                    self.mvcanvas.create_line(0, (i+2)*self.cellheight,
                        (self.board.maxcol + 2) * self.cellwidth,
                        (i+2)*self.cellheight, fill='red', tag='mv')
            self.mvid = {}
            prevmoves = set(self.board.getprevmoves(self.board.curmove))
            if self.board.rootmove.next_:
                __mvstr(self.board.rootmove.next_)
                

        def __drawselection():
            '''
            no = self.walks.cursor + 1
            wklb = self.walklistbox
            wklb.selection_clear(0, wklb.size())
            wklb.selection_set(no)
            wklb.see(no)
            '''
            pass

        def __drawremark():
            '''
            self.remarktext.delete('1.0', END)
            if not self.walks.isstart:
                self.remarktext.insert('1.0', self.walks.curremark())
            '''
            pass

        __drawinfo()
        __drawmvstr()
        __drawselection()
        __drawremark()


#
