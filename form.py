'''
中国象棋软件窗口类型
'''

from walkarea import *
from bdcanvas import *

        
class MainForm(View, ttk.Frame):
    # 棋盘与棋子视图类  

    def __init__(self, master, name, models):
        View.__init__(self, models)
        ttk.Frame.__init__(self, master, padding=2)
        
        self.config = Config_ET(name)
        self.create_widgets(models)
        for model in models:
            model.loadviews([self._bdcanvas, self._walkarea])        
        self.create_layout()
        self.create_bindings()
        self.makemenu()
        
    def create_widgets(self, models):
        self._bdcanvas = BdCanvas(self, models, imgpath + bdimgnames['栎木'], 
                                imgpath + pimgpaths['木刻']) # 
        self._walkarea = WalkArea(self, models)
        
    def create_layout(self):        
        self.pack()

    def create_bindings(self):
        self.bind_all('<Tab>', self.notdone)
        self.bind_all('<Control_L>', self.onCtrlleftKey)
        self.bind_all('<Control_R>', self.onCtrlrightKey)
        #self.onCtrlleftKey(None)    
        
    def onCtrlleftKey(self, event):
        self._bdcanvas.focus_set()
        
    def onCtrlrightKey(self, event):
        self._walkarea.focus_set()
             
    def copyfen(self):
        pyperclip.copy(self.board.getfen())
        
    def pastefen(self):
        self.chessboard.setfen(pyperclip.paste())
    
    def getfilename(self, gettype='open'):
        extension = '.pgn'
        types = [('pgn棋谱文件', '.pgn')]
        if gettype == 'open':
            return basename(askopenfilename(defaultextension=extension, filetypes=types))
        elif gettype == 'saveas':
            return basename(asksaveasfilename(defaultextension=extension, filetypes=types))
        
    def openpgn(self, isnew=False):
        def __asksave(): # True, False非取消, None取消
            return askyesnocancel('开始另一个对局',
                                '是否需要保存当前的棋局？')
        
        save = __asksave()
        if save is None:
            return
        elif save: 
            self.savepgn()
        
        filename = 'new.pgn' if isnew else self.getfilename('open')
        if filename is None:
            return
        try:
            with open(filename, 'r') as file:
                self.chessboard.setpgn(file.read())
        except:
            pass
        
    def savepgn(self, isother=False):
    
        if isother:
            filename = self.getfilename('saveas')
            if filename is None:
                return
            self.config.getelement('lastname').text = filename
        else:
            filename = self.config.getelement('lastname').text 

        with open(filename, 'w') as file:
            file.write(self.chessboard.getpgn())
        self.master.title('中国象棋_by cjp : %s ' % filename)
        #self.makemenu(self.win)
            
    def trimlastpgn(self):
        #PgnfileForm('整理近期pgn文件', self.config.filenames)
        pass

    def lookpgn(self):
        #PgnForm('查看当前棋面的文本棋谱', self.board.getapgn())
        pass
        
    def edittag(self):
        #TagForm('编辑对局信息', self.board.info) 
        pass
    
    def setoption(self):
        '''
        def saveoption():
            self.et.bdimgname = self.bdvar.get()
            self.et.pimgpath = self.pvar.get()
            if self.others[0].get():
                self.et.sound = 'yes'
            else:
                self.et.sound = 'no'
            if self.others[1].get():
                self.et.cartoon = 'yes'
            else:
                self.et.cartoon = 'no'
            self.et.saveconfig(self.et.configfilename)
            self.loadimgs(self.et.bdimgname, self.et.pimgpath) # 载入图像
            self.repgn(self.et.pgnfilename) 
            tp.destroy    

        def __displayoption():
        
            frms, lfrm = [], []        
            tp = Toplevel(self.win)                    
            tp.title('选项设置') 
            for i, sd in enumerate([TOP, BOTTOM]):
                frms.append(Frame(tp))
                frms[i].pack(side=sd, padx=5, pady=5)         
            frm0 = Frame(frms[0])
            frm0.pack(side=TOP) #, padx=2, pady=2
            for i, sd in enumerate([LEFT, RIGHT]):
                lfrm.append(LabelFrame(frm0, relief=GROOVE, text=['棋盘', '棋子'][i], labelanchor='nw'))
                lfrm[i].pack(side=sd, padx=5, pady=5, expand=YES, fill=BOTH)      

            self.bdvar = StringVar()
            for bf in bdimgnames:
                Radiobutton(lfrm[0], text=bf+'      ', variable=self.bdvar,
                    value=bdimgnames[bf]).pack(anchor=NW)
            self.bdvar.set(self.et.bdimgname)
            self.pvar = StringVar()
            for pf in pimgpaths:
                Radiobutton(lfrm[1], text=pf+'       ', variable=self.pvar,
                    value=pimgpaths[pf]).pack(anchor=NW)
            self.pvar.set(self.et.pimgpath)        
                    
            lfrm1 = LabelFrame(frms[0], relief=GROOVE, text='其他',labelanchor='nw')
            lfrm1.pack(side=BOTTOM, padx=5, pady=5, expand=YES, fill=BOTH)        
            self.others = []
            for i, t in enumerate(['声音', '走棋动画']):
                var = IntVar()
                Checkbutton(lfrm1, text=t, variable=var).pack(anchor=NW)
                self.others.append(var)
            if self.et.opensound == 'yes':
                self.others[0].set(1) 
            if self.et.opencartoon == 'yes':
                self.others[1].set(1)
                
            Button(frms[1], text='关闭', width=8, command=tp.destroy).pack(side=RIGHT)
            Button(frms[1], text='确定', width=8, command=saveoption).pack(side=RIGHT)
            tp.focus_set()
            tp.grab_set()
            tp.wait_window()  

        __displayoption()
        '''
        pass

    def makemenu(self):
        # 生成主菜单
        '''
        lastpgns = []
        pgnfs = self.et.getpgnfs()
        for pgnf in pgnfs:
            lastpgns.append((pgnf, lambda f=pgnf: self.openpgn(False, f), 3))
        lastpgns.append('separator')
        lastpgns.append(('整理近期文件...', lambda :self.trimlastpgn(), 3))
        #for x in lastpgns: print(x)
        '''
        
        menuBar = [
            ('文件(F)', 
                   [('新的对局(N)', lambda :self.openpgn(True), 5),
                    ('打开(O)...', lambda :self.openpgn(), 3),
                    ('近期文件...', self.notdone, 3),
                    ('保存(S)', lambda :self.savepgn(), 3),
                    ('另存为(A)...', lambda :self.savepgn(True), 4),
                    'separator',
                    ('查看文本棋谱(V)', self.lookpgn, 7),
                    ('编辑标签(A)', self.edittag, 5),
                    'separator',
                    ('退出(X)', lambda :self.quitmain(), 3)],
             3),
            ('局面(B)', 
                   [('对换位置(F)', self.notdone, 5),
                    ('左右对称(M)', self.notdone, 5),
                    ('对换棋局(D)', self.notdone, 5),
                    'separator',
                    ('新窗口推演(A)', self.notdone, 6),
                    ('编辑局面(E)', self.notdone, 5),
                    'separator',
                    ('复制局面(C)', self.copyfen, 5),
                    ('粘贴局面(P)', self.pastefen, 5)],
             3),
            ('着法(M)', 
                   [('起始局面(S)', lambda :self.notdone, 5),
                    ('上一着(B)', lambda :self.notdone, 4),
                    ('下一着(F)', lambda :self.notdone, 4),
                    ('最后局面(E)', lambda :self.notdone, 5)],
             3),
            ('选项(O)', 
                   [('设置(O)...', self.setoption, 3),
                    'separator'],
             3),               
            ('帮助(A)',
                   [('关于(O)...', self.notdone, 3)],
             3)]
            
        def addMenuItems(menu, items):
            # 载入菜单子目，包括子菜单
            for item in items:
                if item == 'separator':
                    menu.add_separator({})
                elif type(item[1]) != list:
                    menu.add_command(label=item[0],
                                     command=item[1],
                                     underline=item[2])
                else:
                    pullover = Menu(menu, tearoff=False)
                    addMenuItems(pullover, item[1])
                    # 递归载入
                    menu.add_cascade(label=item[0],
                                     menu=pullover,
                                     underline=item[2])

        topMenu = Menu(self)
        self.master.config(menu=topMenu)
        for item in menuBar:
            aMenu = Menu(topMenu, tearoff=False)
            addMenuItems(aMenu, item[1])
            topMenu.add_cascade(label=item[0], menu=aMenu)
       
            
    def notdone(self, event):
        pass
        
    def quitmain(self):
        sys.exit()   
        
    def updateview(self):
        pass
        
        
'''             
class PopForm(Toplevel):

    def __init__(self, master, title, buttoninfos, info):
        super().__init__(master, padding=2)
        self.title(title)
        self.info = info
        self.__create_buttons(buttoninfos)
        self.__create_interfrm()
        self.focus_set()
        self.grab_set()
        self.wait_window()
    
    def __create_buttons(self, buttoninfos):
        frm = Frame(self)        
        for txt, cmd in buttoninfos:
            Button(frm, text=txt, width=8, command=cmd).pack(side=RIGHT)
        frm.pack(side=BOTTOM)
        
    def __create_interfrm(self):
        pass

    
class TagForm(PopForm):

    def __init__(self, master, title, buttoninfos, info):
        buttoninfos = [['关闭', self.destroy, RIGHT], ['确定', self.saveinfo, RIGHT]]
        super().__init__(master, title, buttoninfos, info)
        self.infovars = {}      
        
    def __create_interfrm(self):
        side_forms = [BOTTOM, LEFT, TOP, TOP]
        category = [' 开局 ', ' 比赛 ', ' 红方 ', ' 黑方 ']
        tagnames_l = [['开局', '变例'],
                ['赛事', '轮次', '日期', '地点', '结果'],
                ['单位', '选手'], 
                ['单位', '选手']] 
        tags_l = [['Opening', 'ECCO'],
                ['Game', 'Event', 'Date', 'Site', 'Result'],
                ['Red', 'RedPlayer'], 
                ['Black',  'BlackPlayer']]

        for i, sd in enumerate(side_forms):
            frm = Frame(self)
            lbfrm = LabelFrame(frm, relief=GROOVE, text=category[i], labelanchor='nw')
            tags = tags_l[i]
            for j, label in enumerate(tagnames_l[i]):
                Label(lbfrm, text=Label).grid(row=j, column=0, padx=2, pady=2)
                entry = Entry(lbfrm)
                entry.grid(row=j, column=1, padx=2, pady=2)
                var = StringVar()
                entry.config(textvariable=var)
                var.set(self.info.get(tags[j], ''))
                self.infovars[tags[j]] = var            
            lbfrm.pack(side=TOP, padx=5, pady=5) #, expand=YES, fill=BOTH
            frm.pack(side=sd) #, padx=2, pady=2
        
    def saveinfo(self):
        for tag, var in self.infovars.items():
            self.info[tag] = var.get()
        self.destroy()
        
        
class PgnForm(PopForm):

    def __init__(self, master, title, pgn):
        buttoninfos = [['关闭', self.destroy, RIGHT], ['复制', self.copypgn, RIGHT]]
        super().__init__(master, padding=2)
        self.title(title)
        self.pgn = pgn    
        
    def __create_interfrm(self):
        sbar = Scrollbar(self)
        text = Text(self, relief=SUNKEN)
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=TOP, padx=5, pady=5, expand=YES, fill=BOTH)
        text.insert('1.0', self.pgn)
        
    def copypgn(self):
        pyperclip.copy(self.pgn)
        

class PgnfileForm(Toplevel):

    def __init__(self, master, filenames):
        buttoninfos = [['关闭', self.destroy, RIGHT],
                        ['删除', self.delfilenames, RIGHT],
                        ['全否', lambda :selectall(0), RIGHT],
                        ['全选', lambda :selectall(1), RIGHT]]
        super().__init__(master, '整理近期pgn文件', filenames)

    def __create_interfrm(self):
        self.lbfrm = LabelFrame(self, relief=GROOVE, text=' 近期文件 ', labelanchor='nw')
        self.filenamesvars = []        
        for filename in self.filenames:
            var = IntVar()
            Checkbutton(self.lbfrm, text=filename, variable=var).pack(anchor=NW)
            self.filenamesvars.append(var)

    def selectall(self, val):
        for var in self.filenamesvars:
            var.set(val)
            
    def delfilenames(self):
        filenames = []
        for i, var in enumerate(self.filenamesvars):
            if var.get() > 0:
                filenames.append(self.filenames[i])
        self.filenames = filenames        
        del self.lbfrm
        self.__create_interfrm()
'''

