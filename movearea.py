'''
中国象棋软件着法区域类型
'''

from config import *
from board import *


class MoveArea(View, ttk.Frame):

    canvawidth = 200
    canvasheight = 500
    cellwidth = 70
    cellheight = 30
    cellbd = 6

    def __init__(self, master, model):
        View.__init__(self, model)
        ttk.Frame.__init__(self, master, padding=2)

        self.create_vars()
        self.createwidgets()
        self.createlayout()
        self.createbindings()
        self.updateview()
        
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
                text=self.infovars['Title'].get()).pack(fill=X)
            topfrm.pack(side=TOP)

        def create_midfrm():
            
            def __initdraw():
                self.mvcanvas.create_oval(self.cellwidth//2+self.cellbd, self.cellbd,
                        self.cellwidth+self.cellwidth//2-self.cellbd,
                        self.cellheight-self.cellbd, width=2, outline='red')
                self.mvcanvas.create_text(self.cellwidth, self.cellheight//2, text='开始')
                
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
                    master, text=name, width=7,
                    command=com, relief=GROOVE).pack(side=sid) #, SUNKEN

            def create_buttonfrm(bottomfrm):
                buttonfrm = ttk.Frame(bottomfrm, padding=0)
                buttdate = [
                    ('最后局面', lambda: self.onEndKey(None),
                     RIGHT), ('下一着', lambda: self.onDownKey(None), RIGHT),
                    ('变  着', lambda: self.onRightKey(None),
                     RIGHT), 
                    ('上一着', lambda: self.onUpKey(None),
                     RIGHT), ('开始局面', lambda: self.onHomeKey(None),
                               RIGHT),          
                    ('对换位置', lambda: self.board.changeside('rotate'),
                     LEFT),
                    ('左右对称', lambda: self.board.changeside('symmetry'),
                     LEFT), ('对换棋局', lambda: self.board.changeside(),
                               LEFT)
                ]
                for name, com, sid in buttdate:
                    __button(buttonfrm, name, com, sid)
                Label(buttonfrm, text='  ').pack(side=LEFT)
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
        self.bind('<Left>', self.onUpKey)
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
                self.mvcanvas.create_line(
                        precol*self.cellwidth+self.cellwidth//2-self.cellbd 
                        if isother else col*self.cellwidth,
                        row*self.cellheight-self.cellbd,
                        col*self.cellwidth-self.cellwidth//2+self.cellbd
                        if isother else col*self.cellwidth,
                        row*self.cellheight+self.cellbd)
                recid = self.mvcanvas.create_rectangle(
                        col*self.cellwidth-self.cellwidth//2+self.cellbd,
                        row*self.cellheight+self.cellbd,
                        col*self.cellwidth+self.cellwidth//2-self.cellbd,
                        (row+1)*self.cellheight-self.cellbd,
                        width=1)
                strid = self.mvcanvas.create_text(col*self.cellwidth,
                        row*self.cellheight+self.cellheight//2, text=move.zhstr)
                self.mvid[recid] = self.mvid[strid] = move
                if move.next_:
                    __mvstr(move.next_)
                if move.other:
                    __mvstr(move.other, True)
            
            self.canvasheight = (self.board.maxrow + 2) * self.cellheight
            self.canvawidth = (self.board.maxcol + 2) * self.cellwidth
            self.mvcanvas.config(scrollregion=(0, 0, self.canvawidth, self.canvasheight))
            for i in range(1, self.board.maxrow, 2):
                self.mvcanvas.create_text(self.cellwidth//4,
                        i*self.cellheight+self.cellheight//2,
                        text='{:3d}'.format((i+1) // 2))  # 字中心点
                if (i+1) // 2 % 2 == 0:
                    self.mvcanvas.create_line(0, (i+2)*self.cellheight,
                        (self.board.maxcol + 2) * self.cellwidth,
                        (i+2)*self.cellheight, fill='red')
            self.mvid = {}
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
