'''
中国象棋棋谱转换类型
'''

import cProfile
import struct


piechars = 'RNBAKABNRCCPPPPPrnbakabnrccppppp' # QiziXY设定的棋子顺序 
colchars = 'abcdefghi'

headfmt = '2B2BL8B32BH2B2L4B8H64p64p64p16p16p16p16p64p16p16p32p16p16p4P128P'#206个元素
headstruct = struct.Struct(headfmt)
nodestruct1 = struct.Struct('4B')
nodestruct2 = struct.Struct('L')
def remarkstruct(size):
    return struct.Struct('{}s'.format(size))
    
    
def tostr(bstr): 
    return bstr.decode('GB2312')  # encoding=GB2312 GB18030 utf-8 GBK
    

def subbyte(a, b):
    return (a - b + 25600) % 256
    
    
class Head(object):
    'XQF象棋文件头类'
    
    def __init__(self, data):
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
        self.fKeys = self.__calkeys()

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
        FEN = '{} {} - - 0 0'.format(afen, 'b' if self.WhoPlay == 1 else 'r')
        
        playtype = {0: '全局', 1: '开局', 2: '中局', 3: '残局'}
        playresult = {0: '未知', 1: '红胜', 2: '黑胜', 3: '和棋'}
        result = ('[棋谱名称 "{}"]\n[比赛名称 "{}"]\n[比赛时间 "{}"]\n[比赛地点 "{}"]\n' +
                '[红方姓名 "{}"]\n[黑方姓名 "{}"]\n[对局类型 "{}"]\n[开局类型 "{}"]\n' +
                '[棋谱评论员 "{}"]\n[文件作者 "{}"]\n[比赛结果 "{}"]\n[XQF版本 "{}"]\n' +
                '[FEN "{}"]').format(
                self.TitleA, self.MatchName, self.MatchTime, self.MatchAddr,
                self.RedPlayer, self.BlkPlayer, playtype[self.CodeA], self.TimeRule,
                self.RMKWriter, self.Author, playresult[self.PlayResult], self.Version,
                FEN)
        return result
        
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
    
    def __init__(self, stepno):
        self.stepno = stepno
        self.XYf = 0 # 本步棋的起始位置XY
        self.XYt = 0 # 本步棋的目的位置XY
        self.ChildTag = 0
        self.RemarkSize = 0
        self.Remark = ''
        
        
class XQFFile(object):
    'XQF象棋文件类'
            
    def __str__(self):
        return '[文件名 "{}"]\n{}\n{}'.format(self.name, self.head, self.nodestr)

    def readnodestr(self, filename):    

        def __readnode(stepno):
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
                    unbytestr = __readbytes(4)
                    if unbytestr == 0:
                        node.RemarkSize = 0
                    else:  # 还原注解的大小
                        node.RemarkSize = nodestruct2.unpack(unbytestr)[0] - KeyRMKSize
                                
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
                if node.RemarkSize > 0: # 如果有注解
                    __readremark()                    
                    
            def __tocoord(xy):
                'XQF位置转换为坐标序号'    
                return '{}{}'.format(colchars[xy // 10], xy % 10)

            node = Node(stepno)
            __readdata()            
            if stepno > 0: # 第0个为根节点，不需要
                self.nodestr += '{0}{1} '.format(
                        __tocoord(node.XYf), __tocoord(node.XYt))
            if node.Remark:
                self.nodestr += '{' + node.Remark + '}\n'
            
            if (node.ChildTag & 0x80) != 0: # 有左子树
                __readnode(stepno + 1)
            if (node.ChildTag & 0x40) != 0: # 有右子树
                self.nodestr += '【{}. '.format(stepno)  # ≤≤◤╠ 
                __readnode(stepno)
                self.nodestr += '】 ' # ≥≥ ◢ ╣
                
        with open(filename, 'rb') as fileobj:
            self.name = filename
            self.nodestr = ''
            self.head = Head(headstruct.unpack(fileobj.read(1024))) # 象棋文件头
            KeyXY, KeyXYf, KeyXYt, KeyRMKSize, F32Keys = self.head.fKeys            
            __readnode(0)
            
            
def main():
    filenames = ['将族屏风马先负过宫炮.XQF',
                '- 北京张强 (和) 上海胡荣华 (1993.4.27于南京).xqf',
                '布局陷阱--飞相局对金钩炮.XQF',
                '4四量拨千斤.XQF',
                '05WY0001.XQF'] #
    xqfile = XQFFile()
    for fn in filenames:
        xqfile.readnodestr(fn)
        print(xqfile, '\n')
        '''
        for k, v in xqfile.head.__dict__.items():
            print(k, v)
        print('')
        '''        
            
if __name__ == '__main__':

    #cProfile.run('main()')
    main()
    
#