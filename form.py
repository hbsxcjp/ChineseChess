'''
中国象棋软件主窗口类型
'''

from bdcanvas import *
from movearea import *
from subform import *

#dir = './/'
#ext = '.bin'
#title = '棋谱文件'


class MainForm(View, ttk.Frame):
    '棋盘与棋子视图类'

    def __init__(self, master, config, filename):
        self.board = Board(filename)
        View.__init__(self, self.board)
        ttk.Frame.__init__(self, master, padding=2)

        self.config = config
        self.createwidgets(self.board)
        self.createlayout()
        self.createbindings()

        self.makemenu()
        self.master.protocol('WM_DELETE_WINDOW', self.quitmain)
        self.board.loadviews([self, self.bdcanvas, self.movearea]) #
        #self.updateview()

    def createwidgets(self, board):
        self.bdcanvas = BdCanvas(self, board)
        self.movearea = MoveArea(self, board)
        self.aboutForm = None

    def createlayout(self):
        self.pack()

    def createbindings(self):
        self.bind_all('<Control_L>', self.onCtrlleftKey)
        self.bind_all('<Control_R>', self.onCtrlrightKey)
        self.onCtrlleftKey(None)

    def onCtrlleftKey(self, event):
        self.bdcanvas.focus_set()

    def onCtrlrightKey(self, event):
        self.movearea.focus_set()

    def copyfen(self):
        pyperclip.copy(self.board.getfen())

    def pastefen(self):
        self.board.setfen(pyperclip.paste())

    def __getopenfilename(self):
        return (askopenfilename(
            initialdir=dir,
            title='打开棋局文件',
            defaultextension=ext,
            filetypes=[(title, ext)]))

    def __getsaveasfilename(self):
        return (asksaveasfilename(
            initialdir=dir,
            title='保存棋局文件',
            defaultextension=ext,
            filetypes=[(title, ext)]))

    def __settitle(self, title):
        self.master.title('{}{}'.format(title, ' --中国象棋'))

    def __asksave(self, title):
        result = askyesnocancel(title, '是否需要保存当前的棋局？')
        if result == True:
            self.savethis(self.config.getelement('lastfilename').text)
        return result

    def opennew(self):
        if self.__asksave('打开棋局文件') is None:
            return
        self.config.setelement('lastfilename', '')
        self.board.set('')

    def openother(self):
        if self.__asksave('打开棋局文件') is None:
            return
        filename = self.__getopenfilename()
        if filename:
            self.config.setelement('lastfilename', filename)
            self.board.set(readstr(filename))

    def savethis(self, filename):
        if filename:
            self.config.setelement('lastfilename', filename)
            with open(filename, 'w') as file:
                file.write(self.board.get())
            self.updateview()
        else:
            self.saveother()

    def saveother(self):
        filename = self.__getsaveasfilename()
        if filename:
            self.savethis(filename)

    def last(self):
        #PgnfileForm('整理近期文件', self.config.filenames)
        pass

    def deduce(self):
        #新窗口推演
        pass

    def modifyfen(self):
        #编辑局面
        pass

    def setoption(self):

        pass

    def about(self):
        if self.aboutForm is None:
            self.aboutForm = AboutForm(self)
        else:
            self.aboutForm.deiconify()

    def quitmain(self):
        if self.__asksave('退出对局') is not None:
            self.config.save()
            self.quit()

    def makemenu(self):
        '生成主菜单'
        menuBar = [
            ('文件(F)',
                   [('新的对局(N)', self.opennew, 5),
                    ('打开(O)...', self.openother, 3),
                    #('近期文件...', self.last, 3),
                    ('保存(S)', self.savethis, 3),
                    ('另存为(A)...', self.saveother, 4),
                    'separator',
                    ('查看文本棋谱(V)',lambda: PgnForm(self, self.board.get()), 7),
                    ('编辑标签(A)', lambda: TagForm(self, self.board.info), 5),
                    'separator',
                    ('退出(X)', self.quitmain, 3)],
             3),
            ('局面(B)',
                   [('对换位置(F)', lambda: self.board.changeside('rotate'), 5),
                    ('左右对称(M)', lambda: self.board.changeside('symmetry'), 5),
                    ('对换棋局(D)', self.board.changeside, 5),
                    'separator',
                    #('新窗口推演(A)', self.deduce, 6),
                    #('编辑局面(E)', self.modifyfen, 5),
                    #'separator',
                    ('复制局面(C)', lambda: pyperclip.copy(self.board.get()), 5)],
             3),
            ('着法(M)',
                   [('起始局面(S)', lambda: self.movearea.onHomeKey(None), 5),
                    ('上一着(B)', lambda: self.movearea.onUpKey(None), 4),
                    ('下一着(F)', lambda: self.movearea.onDownKey(None), 4),
                    ('最后局面(E)', lambda: self.movearea.onEndKey(None), 5)],
             3),
            ('帮助(A)',
                   [('关于(O)...', self.about, 3)],
             3)] # yapf: disable
        '''
            ('选项(O)',
                   [('设置(O)...', self.setoption, 3),
                    'separator'],
             3),
        '''
            
        def addMenuItems(menu, items):
            '载入菜单子目，包括子菜单'
            for item in items:
                if item == 'separator':
                    menu.add_separator({})
                elif type(item[1]) != list:
                    menu.add_command(
                        label=item[0], command=item[1], underline=item[2])
                else:
                    pullover = Menu(menu, tearoff=False)
                    addMenuItems(pullover, item[1])
                    # 递归载入
                    menu.add_cascade(
                        label=item[0], menu=pullover, underline=item[2])

        topMenu = Menu(self)
        self.master.config(menu=topMenu)
        for item in menuBar:
            aMenu = Menu(topMenu, tearoff=False)
            addMenuItems(aMenu, item[1])
            topMenu.add_cascade(label=item[0], menu=aMenu)

    def updateview(self):
        '更新视图（由数据模型发起）'
        self.__settitle(self.board.filename) 
        #self.config.getelement('lastfilename').text


#
