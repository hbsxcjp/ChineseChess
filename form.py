'''
中国象棋软件主窗口类型
'''

from walkarea import *
from bdcanvas import *
from subform import *

pgndir = './pgn/'
pgnext = '.pgn'
pgntitle = 'pgn棋谱文件'


class MainForm(View, ttk.Frame):
    '棋盘与棋子视图类'

    def __init__(self, master, config, models):
        View.__init__(self, models)
        ttk.Frame.__init__(self, master, padding=2)

        self.config = config
        self.createwidgets(models)
        self.createlayout()
        self.createbindings()

        for model in models:
            model.loadviews([self, self.bdcanvas, self.walkarea])
        self.makemenu()
        self.master.protocol('WM_DELETE_WINDOW', self.quitmain)
        self.updateview()

    def createwidgets(self, models):
        self.bdcanvas = BdCanvas(self, models)
        self.walkarea = WalkArea(self, models)
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
        self.walkarea.focus_set()

    def copyfen(self):
        pyperclip.copy(self.board.getfen())

    def pastefen(self):
        self.chessboard.setfen(pyperclip.paste())

    def __getopenfilename(self):
        return (askopenfilename(
            initialdir=pgndir,
            title='打开棋局文件',
            defaultextension=pgnext,
            filetypes=[(pgntitle, pgnext)]))

    def __getsaveasfilename(self):
        return (asksaveasfilename(
            initialdir=pgndir,
            title='保存棋局文件',
            defaultextension=pgnext,
            filetypes=[(pgntitle, pgnext)]))

    def __settitle(self, title):
        self.master.title('{}{}'.format(title, ' --中国象棋'))

    def __asksavepgn(self, title):
        result = askyesnocancel(title, '是否需要保存当前的棋局？')
        if result == True:
            self.savethispgn(self.config.getelement('lastpgnfilename').text)
        return result

    def opennewpgn(self):
        if self.__asksavepgn('打开棋局文件') is None:
            return
        self.config.setelement('lastpgnfilename', '')
        self.chessboard.setpgn('')

    def openotherpgn(self):
        if self.__asksavepgn('打开棋局文件') is None:
            return
        filename = self.__getopenfilename()
        if filename:
            self.config.setelement('lastpgnfilename', filename)
            with open(filename, 'r') as file:
                self.chessboard.setpgn(file.read())

    def savethispgn(self, filename):
        if filename:
            self.config.setelement('lastpgnfilename', filename)
            with open(filename, 'w') as file:
                file.write(self.chessboard.getpgn())
            self.updateview()
        else:
            self.saveotherpgn()

    def saveotherpgn(self):
        filename = self.__getsaveasfilename()
        if filename:
            self.savethispgn(filename)

    def lastpgn(self):
        #PgnfileForm('整理近期pgn文件', self.config.filenames)
        pass

    def deducepgn(self):
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
        if self.__asksavepgn('退出对局') is not None:
            self.config.save()
            self.quit()

    def makemenu(self):
        '生成主菜单'
        menuBar = [
            ('文件(F)',
                   [('新的对局(N)', self.opennewpgn, 5),
                    ('打开(O)...', self.openotherpgn, 3),
                    #('近期文件...', self.lastpgn, 3),
                    ('保存(S)', self.savethispgn, 3),
                    ('另存为(A)...', self.saveotherpgn, 4),
                    'separator',
                    ('查看文本棋谱(V)',lambda: PgnForm(self, self.chessboard.getpgn()), 7),
                    ('编辑标签(A)', lambda: TagForm(self, self.chessboard.info), 5),
                    'separator',
                    ('退出(X)', self.quitmain, 3)],
             3),
            ('局面(B)',
                   [('对换位置(F)', lambda: self.chessboard.changeside('rotate'), 5),
                    ('左右对称(M)', lambda: self.chessboard.changeside('symmetry'), 5),
                    ('对换棋局(D)', self.chessboard.changeside, 5),
                    'separator',
                    #('新窗口推演(A)', self.deducepgn, 6),
                    #('编辑局面(E)', self.modifyfen, 5),
                    #'separator',
                    ('复制局面(C)', lambda: pyperclip.copy(self.chessboard.getpgn()), 5)],
             3),
            ('着法(M)',
                   [('起始局面(S)', lambda: self.walkarea.onHomeKey(None), 5),
                    ('上一着(B)', lambda: self.walkarea.onUpKey(None), 4),
                    ('下一着(F)', lambda: self.walkarea.onDownKey(None), 4),
                    ('最后局面(E)', lambda: self.walkarea.onEndKey(None), 5)],
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
        self.__settitle(self.config.getelement('lastpgnfilename').text)


#
