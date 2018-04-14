'''
中国象棋软件着法区域类型
'''

MoveWidth=200
MoveHeight=200

from config import *
from board import *


class MoveArea(View, ttk.Frame):
    def __init__(self, master, model):
        View.__init__(self, model)
        ttk.Frame.__init__(self, master, padding=2)

        self.createwidgets()
        self.createlayout()
        self.createbindings()
        self.updateview()

    def createwidgets(self):
    
        def create_topfrm():
            topfrm = ttk.Frame(self, padding=2, width=210)#
            Label(
                topfrm, text=self.board.info['Title']).pack()
                # font='Helvetica -14 bold' 
            topfrm.pack(side=TOP)  # 顶部区域 , fill=X side=TOP

        def create_midfrm():
            #midfrm = ttk.Frame(self, padding=2)
            midfrm = LabelFrame(
                self,
                relief=GROOVE,
                text=' 图示着法 ',
                padx=2,
                pady=2,
                labelanchor='nw')
            vbar = Scrollbar(midfrm, orient=VERTICAL)
            hbar = Scrollbar(midfrm, orient=HORIZONTAL)            
            mvcanvas = Canvas(
                midfrm,
                relief=SUNKEN,
                width=MoveWidth,
                height=MoveHeight,
                scrollregion=(0, 0, MoveWidth*2, MoveHeight*2),
                #highlightthickness=0,
                yscrollcommand=vbar.set,
                xscrollcommand=hbar.set)  # width=13
            vbar.config(command=mvcanvas.yview)
            hbar.config(command=mvcanvas.xview)
            self.mvcanvas = mvcanvas                
            vbar.pack(side=RIGHT, fill=Y)
            hbar.pack(side=BOTTOM, fill=X)            
            mvcanvas.pack(side=LEFT) #fill=BOTH
            midfrm.pack(expand=YES, fill=BOTH) #  

        def create_bottomfrm():
        
            def __button(master, name, wid, com, sid):
                Button(
                    master, text=name, width=wid,
                    command=com, relief=GROOVE).pack(side=sid) #, SUNKEN

            def create_botleftfrm(bottomfrm):
                botleftfrm = ttk.Frame(bottomfrm, padding=1)
                buttdate = [
                    ('对换位置', 8, lambda: self.board.changeside('rotate'),
                     BOTTOM),
                    ('左右对称', 8, lambda: self.board.changeside('symmetry'),
                     BOTTOM), ('对换棋局', 8, lambda: self.board.changeside(),
                               BOTTOM), ('打印棋局', 8, lambda: print(self.board),
                                         BOTTOM)
                ]
                for name, wid, com, sid in buttdate:
                    __button(botleftfrm, name, wid, com, sid)
                botleftfrm.pack(side=LEFT)  #, fill=BOTH, expand=YES
                
            def create_botrightfrm(bottomfrm):
                botrightfrm = ttk.Frame(bottomfrm, padding=1)
                buttdate = [
                    ('最后局面', 8, lambda: self.onEndKey(None),
                     BOTTOM), ('下一着', 8, lambda: self.onDownKey(None), BOTTOM),
                    ('上一着', 8, lambda: self.onUpKey(None),
                     BOTTOM), ('起始局面', 8, lambda: self.onHomeKey(None),
                               BOTTOM)
                ]
                for name, wid, com, sid in buttdate:
                    __button(botrightfrm, name, wid, com, sid)
                botrightfrm.pack(side=RIGHT)  #, fill=BOTH, expand=YES
                
            def create_botmidfrm(bottomfrm):
                remfrm = LabelFrame(
                    bottomfrm,
                    relief=GROOVE,
                    text=' 评注：',
                    padx=2,
                    pady=2,
                    labelanchor='nw')
                self.remarktext = Text(
                    remfrm,
                    padx=2,
                    pady=1,
                    height=6,
                    width=30,
                    relief=GROOVE,
                    font=('Consolas', '10'))
                self.remarktext.pack()  # side=TOP, expand=YES, fill=BOTH
                remfrm.pack(expand=YES, fill=BOTH)  # 底部区域
                
            bottomfrm = ttk.Frame(self, padding=1)
            create_botleftfrm(bottomfrm)
            create_botrightfrm(bottomfrm)
            create_botmidfrm(bottomfrm)
            bottomfrm.pack(side=BOTTOM)  # 顶部区域

        create_topfrm()  # 先打包的最后被裁切
        create_bottomfrm()
        create_midfrm()
        
    def createlayout(self):
        self.pack(side=RIGHT, expand=YES, fill=Y)  # BOTH

    def createbindings(self):
        self.bind('<Up>', self.onUpKey)
        self.bind('<Down>', self.onDownKey)
        self.bind('<Prior>', self.onPgupKey)
        self.bind('<Next>', self.onPgdnKey)
        self.bind('<Home>', self.onHomeKey)
        self.bind('<End>', self.onEndKey)
        self.mvcanvas.bind('<Double-1>',
                              self.onMouseLeftclick)  # 用buttom-1不成功！

    def onUpKey(self, event):
        self.board.movestep(-1)

    def onDownKey(self, event):
        self.board.movestep()

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
            '''
            boutstr = self.walks.getboutstrs_ltbox() #getboutstr(True)
            boutstr.insert(0, '=====开始======')
            self.listvar.set(boutstr)
            '''
            pass

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
