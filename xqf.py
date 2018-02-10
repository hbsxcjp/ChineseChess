'''
中国象棋棋谱转换类型
'''

import cProfile, os, sys, glob
import struct, shutil, chardet
import codecs
    

piechars = 'RNBAKABNRCCPPPPPrnbakabnrccppppp' # QiziXY设定的棋子顺序 
colchars = 'abcdefghi'

headfmt = '2B2BL8B32BH2B2L4B8H64p64p64p16p16p16p16p64p16p16p32p16p16p4P128P'#206个元素
headstruct = struct.Struct(headfmt)
nodestruct1 = struct.Struct('4B')
nodestruct2 = struct.Struct('L')
def remarkstruct(size):
    return struct.Struct('{}s'.format(size))
    
    
def tostr(bstr):
    try:  # encoding=GB2312 GB18030 utf-8 GBK
        return bstr.decode('GBK', errors='ignore')
    except:
        coding = chardet.detect(bstr)
        return bstr.decode(coding['encoding'], errors='ignore')
        

def subbyte(a, b):
    return (a - b + 1024) % 256
    
    
class Head(object):
    'XQF象棋文件头类'
    
    def __init__(self, filename, data):
        self.name = os.path.basename(filename)
        self.Signature = data[:2] # 2字节 文件标记 'XQ' = $5158;
        self.Version = data[2] # 版本号
        self.KeyMask = data[3] # 加密掩码
        #self.ProductId = data[4] # 4字节 产品号(厂商的产品号)
        self.KeyOrA = data[5] #
        self.KeyOrB = data[6] #
        self.KeyOrC = data[7] #
        self.KeyOrD = data[8] #
        self.KeysSum = data[9] # 加密的钥匙和
        self.KeyXY = data[10] # 棋子布局位置钥匙       
        self.KeyXYf = data[11] # 棋谱起点钥匙
        self.KeyXYt = data[12] # 棋谱终点钥匙
        #// = 16 bytes
        self.QiziXY = list(data[13:45]) # 32个棋子的原始位置
        #// 用单字节坐标表示, 将字节变为十进制数, 十位数为X(0-8)个位数为Y(0-9),
        #// 棋盘的左下角为原点(0, 0). 32个棋子的位置从1到32依次为:
        #// 红: 车马相士帅士相马车炮炮兵兵兵兵兵 (位置从右到左, 从下到上)
        #// 黑: 车马象士将士象马车炮炮卒卒卒卒卒 (位置从右到左, 从下到上)        
        #// = 48 bytes
        #self.PlayStepNo = data[45] # 棋谱文件的开始步数
        self.WhoPlay = data[46] # 该谁下 0-红先, 1-黑先
        self.PlayResult = data[47] # 最终结果 0-未知, 1-红胜 2-黑胜, 3-和棋
        #self.PlayNodes = data[48] # 本棋谱一共记录了多少步
        #self.PTreePos = data[49] # 对弈树在文件中的起始位置
        #self.Reserved1 = data[50:54] # : array [1..4] of dTByte;        
        #// = 64 bytes
        self.CodeA = data[54] # 对局类型(开,中,残等)
        #self.CodeB = data[55] # 另外的类型
        #self.CodeC = data[56] #
        #self.CodeD = data[57] #
        #self.CodeE = data[58] #
        #self.CodeF = data[59] #
        #self.CodeH = data[60] #
        #self.CodeG = data[61] #
        #// = 80  bytes
        self.TitleA = tostr(data[62]) # 标题
        self.TitleB = tostr(data[63]) #
        #// = 208 bytes
        self.MatchName = tostr(data[64]) # 比赛名称
        self.MatchTime = tostr(data[65]) # 比赛时间
        self.MatchAddr = tostr(data[66]) # 比赛地点
        self.RedPlayer = tostr(data[67]) # 红方姓名
        self.BlkPlayer = tostr(data[68]) # 黑方姓名
        #// = 336 bytes
        self.TimeRule = tostr(data[69]) # 开局类型
        #self.RedTime = tostr(data[70]) #
        #self.BlkTime = tostr(data[71]) #
        #self.Reservedh = tostr(data[72]) #        
        #// = 464 bytes
        self.RMKWriter = tostr(data[73]) # 棋谱评论员
        self.Author = tostr(data[74]) # 文件的作者
        
        '''
        if self.Signature != (0x58, 0x51):
            print('文件标记不对。xqfhead.Signature != (0x58, 0x51)')
        if (self.KeysSum + self.KeyXY + self.KeyXYf + self.KeyXYt) % 256 != 0:
            print('检查密码校验和不对，不等于0。')
        if self.Version > 18: 
            print('这是一个高版本的XQF文件，您需要更高版本的XQStudio来读取这个文件')
        '''            
        self.keys = self.__calkeys()

    def __str__(self):    
    
        def __linetonums():
            '下划线字符串对应数字字符元组 列表'
            return [('_' * i, str(i)) for i in range(9, 0, -1)]
            
        charls = [['_' for _ in range(9)] for row in range(10)]
        for i, xy in enumerate(self.QiziXY):
            if xy < 90:
                charls[xy%10][(8 - xy//10) if i < 16 else xy//10] = piechars[i]
        afen = '/'.join([''.join(chars) for chars in charls[::-1]])
        for _str, nstr in __linetonums():
            afen = afen.replace(_str, nstr)
        self.FEN = '{} {} - - 0 0'.format(afen, 'b' if self.WhoPlay == 1 else 'r')        
        
        self.playtype = {0: '全局', 1: '开局', 2: '中局', 3: '残局'}[self.CodeA]
        self.playresult = {0: '未知', 1: '红胜', 2: '黑胜', 3: '和棋'}[self.PlayResult]
        
        return ('''[Filename "{self.name}"]\n[Game "Chinese Chess"]\n[Event "{self.MatchName}"]\n[Date "{self.MatchTime}"]\n[Site "{self.MatchAddr}"]\n[Round ""]\n[Red "{self.RedPlayer}"]\n[RedTeam ""]\n[Black "{self.BlkPlayer}"]\n[BlackTeam ""]\n[Opening "{self.TimeRule}"]\n[Variation ""]\n[ECCO ""]\n[Result "{self.playresult}"]\n[FEN "{self.FEN}"]\n[Format "ICCS"]\n[棋谱名称 "{self.TitleA}"]\n[对局类型 "{self.playtype}"]\n[棋谱评论员 "{self.RMKWriter}"]\n[文件作者 "{self.Author}"]\n[XQF版本 "{self.Version}"]''').format(self=self)
        
    def __calkeys(self):
        '根据文件头密码因子计算真正的加密密码'
        
        def __calkey(bKey, cKey):
            return (((((bKey*bKey)*3+9)*3+8)*2+1)*3+8) * cKey % 256 # 保持为<256
            
        if self.Version <= 10: # 兼容1.0以前的版本
            KeyXY = 0
            KeyXYf = 0
            KeyXYt = 0
            KeyRMKSize = 0
        else:
            KeyXY = __calkey(self.KeyXY, self.KeyXY)
            KeyXYf = __calkey(self.KeyXYf, KeyXY)
            KeyXYt = __calkey(self.KeyXYt, KeyXYf)
            KeyRMKSize = ((self.KeysSum * 256 + self.KeyXY) % 65536 % 32000) + 767
            if self.Version >= 12: # 棋子位置循环移动
                for i, xy in enumerate(self.QiziXY[:]):
                    self.QiziXY[(i + KeyXY + 1) % 32] = xy
            for i in range(32): # 棋子位置解密           
                self.QiziXY[i] = subbyte(self.QiziXY[i], KeyXY)
                # 保持为8位无符号整数，<256
                
        KeyBytes = [(self.KeysSum & self.KeyMask) | self.KeyOrA,
                    (self.KeyXY & self.KeyMask) | self.KeyOrB,
                    (self.KeyXYf & self.KeyMask) | self.KeyOrC,
                    (self.KeyXYt & self.KeyMask) | self.KeyOrD]
        F32Keys = [ord(c) & KeyBytes[i % 4]
                    for i, c in enumerate('[(C) Copyright Mr. Dong Shiwei.]')]
        return (KeyXY, KeyXYf, KeyXYt, KeyRMKSize, F32Keys)
        
                 
class Node(object):
    'XQF象棋着法树节点类'
    
    def __init__(self, prenode):
        self.ChildTag = 0
        self.RemarkSize = 0
        
        self.stepno = 0
        self.XYf = 0 # 本步棋的起始位置XY
        self.XYt = 0 # 本步棋的目的位置XY
        self.Remark = ''
        self.prenode = prenode
        self.nextnode = None
        self.othernode = None
        
    def setnext(self, nextnode):
        self.nextnode = nextnode
        self.nextnode.stepno = self.stepno + 1
        
    def setother(self, othernode):
        self.othernode = othernode
        self.othernode.stepno = self.stepno
        
        
class XQFFile(object):
    'XQF象棋文件类'
    
    def __init__(self):
        self.head = None
        self.rootnode = None
        self.nodestr = ''
        self.nodestrl = []
        
    def __str__(self):
        return '{}\n{}'.format(self.head, self.nodestr)

    def __setnodestrl(self, node, isother=False):
    
        def __remarkstr():
            remarkstr = '' if not node.Remark else node.Remark.strip()
            return '' if not remarkstr else '\n{{{}}}\n '.format(remarkstr)
        
        def __mergestr():                        
            if not isother:
                prestr = ('' if node.stepno % 2 == 0 else 
                        '{}. '.format((node.stepno + 1) // 2))
            else:
                prestr = '({0}. {1}'.format((node.stepno + 1) // 2, 
                        '... ' if node.stepno % 2 == 0 else '')           
            xyf, xyt = node.XYf, node.XYt
            bodystr = '{0}{1}{2}{3} '.format(colchars[xyf // 10], xyf % 10,
                        colchars[xyt // 10], xyt % 10) # XQF位置转换为坐标序号
            return '{0}{1}{2}'.format(prestr, bodystr, __remarkstr())
            
        if node.prenode is None: # 根节点 
            self.nodestrl.append(__remarkstr())
        else:
            self.nodestrl.append(__mergestr())
            
        if node.othernode:
            self.__setnodestrl(node.othernode, True)
            self.nodestrl.append(') ')
        
        if node.nextnode:
            self.__setnodestrl(node.nextnode)
        
    def readfile(self, filename):    

        def __readnode(node):
            '递归添加着法节点'
            
            def __readdata():
                    
                def __readbytes(size):
                    pos = fileobj.tell()
                    bytestr = fileobj.read(size)
                    
                    if len(bytestr) != size: # 文件最后一个节点注解标志位为1，但无注解情形
                        return 0
                    if self.head.Version <= 10:
                        return bytestr 
                    else: # '字节串解密'
                        barr = bytearray(len(bytestr))  # 字节数组才能赋值，字节串不能赋值
                        for i, b in enumerate(bytestr):
                            barr[i] = subbyte(int(b), F32Keys[(pos + i) % 32])
                        return barr
                        
                def __readnodehead():
                    data = nodestruct1.unpack(__readbytes(4))                    
                    # 一步棋的起点和终点有简单的加密计算，读入时需要还原
                    node.XYf = subbyte(data[0], 0X18 + KeyXYf) # 一步棋的起点
                    node.XYt = subbyte(data[1], 0X20 + KeyXYt) # 一步棋的终点
                    node.ChildTag = data[2]
                
                def __readremarksize():
                    bytestr = __readbytes(4)
                    if bytestr == 0:
                        node.RemarkSize = 0
                    else:  # 还原注解的大小
                        node.RemarkSize = nodestruct2.unpack(bytestr)[0] - KeyRMKSize
                                
                def __readremark():
                    bytestr = __readbytes(node.RemarkSize)
                    remarks = remarkstruct(node.RemarkSize)
                    node.Remark = tostr(remarks.unpack(bytestr)[0])
                    
                __readnodehead()
                if self.head.Version <= 0x0A:
                    b = 0
                    if (node.ChildTag & 0xF0) != 0: 
                        b = b | 0x80
                    if (node.ChildTag & 0x0F) != 0: 
                        b = b | 0x40
                    node.ChildTag = b
                    __readremarksize()
                else:
                    node.ChildTag = node.ChildTag & 0xE0
                    if (node.ChildTag & 0x20) != 0:                        
                        __readremarksize()
                if node.RemarkSize > 0: # 如果有注解 and node.RemarkSize < 2048
                    __readremark()
                    
            __readdata()
            if (node.ChildTag & 0x80) != 0: # 有左子树
                nextnode = Node(node)
                node.setnext(nextnode)
                __readnode(nextnode)
            if (node.ChildTag & 0x40) != 0: # 有右子树
                othernode = Node(node)
                node.setother(othernode)
                __readnode(othernode)
        
        with open(filename, 'rb') as fileobj:            
            bytestr = headstruct.unpack(fileobj.read(1024))
            self.head = Head(filename, bytestr)
            KeyXY, KeyXYf, KeyXYt, KeyRMKSize, F32Keys = self.head.keys
            
            self.rootnode = Node(None)
            __readnode(self.rootnode)
            
        self.nodestrl = []
        self.__setnodestrl(self.rootnode)            
        self.nodestr = ''.join(self.nodestrl)    
   
    def transdir(self, dirfrom, dirto):
        fcount = dcount = 0
        if not os.path.exists(dirto):
            os.mkdir(dirto)
        for subname in os.listdir(dirfrom):
            subname = os.path.normcase(subname)
            pathfrom = os.path.join(dirfrom, subname)
            pathto = os.path.join(dirto, subname)
            if os.path.isfile(pathfrom): # 文件
                data = ''
                filename, extension = os.path.splitext(subname)
                try:
                    if extension == '.xqf':
                        self.readfile(pathfrom)
                        data = str(self)
                        pathto = os.path.join(dirto, filename + '.pgn')
                    elif extension == '.txt':
                        data = open(pathfrom).read()
                    if data:
                        codecs.open(pathto, 'w', encoding='utf-8').write(data) #  
                        fcount += 1
                except:
                    print('转换文件不成功：', pathfrom)
            else:
                try:
                    below = self.transdir(pathfrom, pathto)
                    fcount += below[0]
                    dcount += below[1]
                    dcount += 1
                except:
                    print('转换目录不成功：', pathfrom)
        return (fcount, dcount)
    
    
def transdir(i):

    dirfrom = ['C:\\示例文件XQF',
                'C:\\象棋杀着大全',
                'C:\\疑难文件xqf\\第21届五羊杯赛对局选（评注版）',
                'C:\疑难文件xqf',
                'C:\\360安全浏览器下载\\中国象棋棋谱大全'
                ]
    dirto = ['C:\\示例文件XQF_pgn',
                'C:\\象棋杀着大全_pgn',
                'C:\\疑难文件xqf_pgn\\第21届五羊杯赛对局选（评注版）',
                'C:\疑难文件xqf_pgn',
                'C:\\中国象棋棋谱大全_pgn'
                ]
    
    xqfile = XQFFile()
    fc, dc = xqfile.transdir(dirfrom[i], dirto[i])
    print('文件数: {} 目录数: {}'.format(fc, dc))
    
    
def transfile(i):

    dirfrom = 'C:\\疑难文件xqf'
    dirto = 'C:\\疑难文件xqf_pgn'
    filenames = ['将族屏风马先负过宫炮.XQF',
                '飞相局【卒7进1】.XQF',
                '仙人指路全集（史上最全最新版）.XQF',
                '中炮对屏风马.XQF',
                '黑用开局库.XQF',
                '中炮【马8进7】.XQF',
                '5、第二轮 吕钦　红先胜 徐天红 2001.1.XQF'
                ]
    filenameto = filenames[i][:-4] + '.pgn'
    xqfile = XQFFile()
    xqfile.readfile(os.path.join(dirfrom, filenames[i]))    
    codecs.open(os.path.join(dirto, filenameto), 'w', encoding='utf-8').write(str(xqfile))
    
            
if __name__ == '__main__':

    import time
    start = time.time()
    
    #cProfile.run('transdir(2)')
    #cProfile.run('transfile(5)')
    
    transdir(3)
    #transfile(0)
    
    end = time.time()
    print('usetime: %0.4f' % (end - start))
    
    #shutil.rmtree('C:\\中国象棋棋谱大全')
    pass
    
#