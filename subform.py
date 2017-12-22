'''
中国象棋软件子窗口类型
'''

from config_et import *
     
       
class PopForm(Toplevel):

    def __init__(self, master, title, buttoninfos):
        super().__init__(master)
        self.title(title)        
        self.__createbuttons(buttoninfos)        
        self.focus_set()
        #self.grab_set()
        #self.wait_window()
    
    def __createbuttons(self, buttoninfos):
        frm = Frame(self)
        for txt, cmd, sid in buttoninfos:
            Button(frm, text=txt, width=8, command=cmd).pack(side=sid)
        frm.pack(side=BOTTOM)
        
    def __createinterfrm(self):
        pass
        

class PgnForm(PopForm):

    def __init__(self, master, pgn=''):
        buttoninfos = [['关闭', self.destroy, RIGHT], ['复制', self.copypgn, RIGHT]]
        super().__init__(master, '查看当前棋局的文本棋谱', buttoninfos)
        self.pgn = pgn
        self.__createinterfrm()
        
    def __createinterfrm(self):
        pgnfrm = Frame(self)        
        sbar = Scrollbar(pgnfrm)
        text = Text(pgnfrm, relief=SUNKEN)        
        sbar.config(command=text.yview)
        text.config(yscrollcommand=sbar.set)        
        pgnfrm.pack(side=TOP, expand=YES, fill=BOTH)
        sbar.pack(side=RIGHT, fill=Y)
        text.pack(side=LEFT, padx=5, pady=5, expand=YES, fill=BOTH)
        text.insert('1.0', self.pgn)        
        
    def copypgn(self):
        pyperclip.copy(self.pgn) 
           
    
class TagForm(PopForm):

    cate_tags = {' 开局 ': {'Opening': '开局', 'ECCO': '资料库?', 'Variation': '变例'},
            ' 比赛 ': {'Game': '名称', 'Event': '赛事', 'Round': '轮次', 'Format': '格式',
                        'Date': '日期', 'Site': '地点', 'Result': '结果'},
            ' 红方 ': {'RedTeam': '队伍', 'Red': '选手'},
            ' 黑方 ': {'BlackTeam': '队伍', 'Black': '选手'}}

    def __init__(self, master, info):
        buttoninfos = [['关闭', self.destroy, RIGHT], ['确定', self.saveinfo, RIGHT]]
        super().__init__(master, '编辑对局信息', buttoninfos)
        self.info = info
        self.__createinterfrm()    
        
    def __createinterfrm(self):
        self.infovars = {}
        for cate, tags in self.cate_tags.items():
            frm = Frame(self)
            lbfrm = LabelFrame(frm, relief=GROOVE, text=cate, labelanchor='nw')
            i = 0
            for tag, name in tags.items():
                Label(lbfrm, text=name).grid(row=i, column=0, padx=2, pady=2)
                entry = Entry(lbfrm)
                entry.grid(row=i, column=1, padx=2, pady=2)
                var = StringVar()
                entry.config(textvariable=var)
                var.set(self.info.get(tag, ''))
                self.infovars[tag] = var
                i = i + 1
            lbfrm.pack(side=TOP, padx=5, pady=5) #, expand=YES, fill=BOTH
            frm.pack(side=TOP) #, padx=2, pady=2
        
    def saveinfo(self):
        for tag, var in self.infovars.items():
            self.info[tag] = var.get()
        self.master.chessboard.info = self.info
        self.destroy()


'''
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

class AboutForm(Toplevel):

    def __init__(self, master):
        super().__init__(master)
        self.withdraw()
        self.title('关于这个软件')
        self.create_ui()
        self.reposition()
        self.resizable(False, False)
        self.deiconify()
        if self.winfo_viewable():
            self.transient(master)
        self.wait_visibility()
        
    def create_ui(self):
        self.deslabel = ttk.Label(self, text='这是一个中国象棋打谱的软件。\n\n\n')
        self.closebutton = Button(self, text='关闭', command=self.close)
        self.deslabel.pack(anchor=N, expand=True, fill=BOTH)
        self.closebutton.pack(anchor=S)
        self.protocol("WM_DELETE_WINDOW", self.close)
        self.bind("<Alt-c>", self.close)
        self.bind("<Escape>", self.close)
        self.bind("<Expose>", self.reposition)
        
    def reposition(self, event=None):
        if self.master is not None:
            self.geometry("+{}+{}".format(self.master.winfo_rootx() + 250,
                self.master.winfo_rooty() + 100))
                
    def close(self, event=None):
        self.withdraw()


            