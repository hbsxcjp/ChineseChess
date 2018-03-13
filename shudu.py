'''
数独游戏

一个数独谜题通常包含有9x9=81个单元格，每个单元格仅能填写一个值。
对一个未完成的数独题，有些单元格中已经填入了值，另外的单元格则为空，等待解题者来完成。

习惯上，横为行，纵为列。行由横向的9个单元格组成，而列由纵向的9个单元格组成。
这里用大写英文字母和数字分别表示行和列。例如，单元格[G6]指的是行G和第6列交界处的单元格。
区块指的是起始于特定位置的9个相邻的单元格组。
任何一行，一列或一个区块都是一个单元。每个单元都必须包含全部但不重复的数字1到9。

数独的技巧，可大分为直观法及候选数法两种。
直观法的特性：
1. 相对而言，能解出的谜题较简单。
2. 主要的技巧：唯一解法、基础摒除法、区块摒除法、唯余解法、矩形摒除法、单元摒除法。
候选数法的特性：
1. 需先建立候选数列表，需经过一段相当的时间才会出现第1个解。
3. 需使用高阶直观法技巧或有计算机辅助时的首要解题方法。
4. 相对而言，能解出的谜题较复杂。
5. 主要的技巧：唯一候选数法(Singles Candidature)、隐性唯一候选数法(Hidden Singles Candidature)、 区块删减法(Locked Candidates)、数对删减法(Naked Pairs)、隐性数对删减法(Hidden Pairs)、 三链数删减法(Naked Triples)、隐性三链数删减法(Hidden Triples)、矩形顶点删减法(X-Wing)、 三链列删减法(Swordfish)、关键数删减法(Colors, Colouring)、关连数删减法(Forcing chains)。

'''

import cProfile, re, os, sys, itertools, copy

global count
count = 0


class ShuDu(object):
    '数独类'
    rowchars = 'ABCDEFGHI'
    colchars = '123456789'
    nums = {1, 2, 3, 4, 5, 6, 7, 8, 9}
    
    allseats = [y*9+x for x in range(9) for y in range(9)] # 81项
    row_seats = [[y*9+x for x in range(9)] for y in range(9)] # 9行
    col_seats = [[y*9+x for y in range(9)] for x in range(9)] # 9列
    blk_seats = [[(r*3+y)*9+c*3+x for y in range(3) for x in range(3)]
                for r in range(3) for c in range(3)] # 9块    
    rcb_seats = row_seats + col_seats + blk_seats # 27单元(行、列、块)
                
    def __init__(self, no_nums):
        self.seat_nums = {seat: [0, self.nums.copy()] for seat in self.allseats}
        self.no = int(no_nums[0])
        [self.__setnum(i, int(num))
            for i, num in enumerate(no_nums[1:]) if num]
        self.calculate()
        
    def __str__(self):
        blankboard0 = '''
            ┏━┯━┯━┳━┯━┯━┳━┯━┯━┓
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┣━┿━┿━╋━┿━┿━╋━┿━┿━┫
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┣━┿━┿━╋━┿━┿━╋━┿━┿━┫
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┠─┼─┼─╂─┼─┼─╂─┼─┼─┨
            ┃　│　│　┃　│　│　┃　│　│　┃
            ┗━┷━┷━┻━┷━┷━┻━┷━┷━┛
        ''' # yapf: disable
        # 边框粗线
        blankboard1 = '''
            ╔═╤═╤═╦═╤═╤═╦═╤═╤═╗
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╠═╪═╪═╬═╪═╪═╬═╪═╪═╣
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╠═╪═╪═╬═╪═╪═╬═╪═╪═╣
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╟─┼─┼─╫─┼─┼─╫─┼─┼─╢
            ║　│　│　║　│　│　║　│　│　║
            ╚═╧═╧═╩═╧═╧═╩═╧═╧═╝
        ''' # yapf: disable
        # 边框双线
        numchs = {1:'１', 2:'２', 3:'３', 4:'４', 5:'５',
                    6:'６', 7:'７', 8:'８', 9:'９'}
        linestr = [list(line.strip())
                    for line in blankboard0.strip().splitlines()]
        for seat, nums in self.seat_nums.items():                
            if nums[0] > 0:
                linestr[seat//9*2+1][seat%9*2+1] = numchs[nums[0]]
        linestrs = [''.join(line) for line in linestr]
        return '{}  (已填数字：{}个)\n{}\n\n'.format(self.no,
                self.numcount(), '\n'.join(linestrs))
                    
    def __setnum(self, seat, num):
        y, x = seat // 9, seat % 9
        self.seat_nums[seat] = [num, set()]
        r_seats = self.row_seats[y] + self.col_seats[x] + self.blk_seats[y//3*3+x//3]
        r_seats.remove(seat)
        for r_seat in r_seats:
            if not self.seat_nums[r_seat][0]:
                self.seat_nums[r_seat][1] -= {num}

    def __getcannums(self, rcb_seat):
        cannums = []
        [cannums.extend(self.seat_nums[seat][1]) for seat in rcb_seat]
        return cannums

    def __getnum_seats(self, num, rcb_seat):
        return {seat for seat in rcb_seat if num in self.seat_nums[seat][1]}
                    
    def __getnums_seats(self, nums, rcb_seat):
        numseats = set()
        for num in nums:
            numseats |= self.__getnum_seats(num, rcb_seat)
        return numseats
        
    def __getnum_seats_dict(self, nums, rcb_seat):
        return {num: self.__getnum_seats(num, rcb_seat) for num in nums}
                        
    def calculate(self):
    
        def __onlyone():
            ''' 唯一数法
                如果发现某个格子中只有一个可用候选数，那么这个格子必然是这个数字
            '''    
            searched = bool([self.__setnum(seat, list(nums[1])[0])
                            for seat, nums in self.seat_nums.items()
                            if len(nums[1]) == 1])
            '''
                隐含唯一数法
                如果发现某一行某一列或某个九宫有一个候选数只出现在一个格子里面，那么这个格子必然是这个数字
            '''                  
            if not self.right():
                return
            for rcb_seat in self.rcb_seats:
                cannums = self.__getcannums(rcb_seat)
                for num in self.nums:
                    if cannums.count(num) == 1:
                        _seats = self.__getnum_seats(num, rcb_seat)
                        if not _seats: # crack试填可能会产生逻辑错误
                            return
                        self.__setnum(list(_seats)[0], num)
                        searched = True
            if searched:
                __onlyone()
            
        def __relatednums():
            ''' 
                数对法 如果发现某一行某一列或某个九宫有两个格子只使用了两个候选数，那么这两个格子必然正好是这两个数字，那么在这个单元（行，列，或九宫）中，其它格子不会出现这两个候选数
                三链数法        如果发现某一行某一列或某个九宫有三个格子只使用了三个候选数，那么这三个格子必然正好是这三个数字，那么在这个单元（行，列，或九宫）中，其它格子不会出现这三个候选数
                四链数法  如果我们发现某一行某一列或某个九宫有四个格子只使用了四个候选数，那么这四个格子必然正好是这四个数字，那么在这个单元（行，列，或九宫）中，其它格子不会出现这四个候选数
                隐含数对法          如果我们发现某一行某一列或某个九宫中有两个候选数只出现在两个格子中，那么这两个格子必然正好是这两个数字，那么这两格子中其他候选数可以删除
                隐含三链数法  如果我们发现某一行某一列或某个九宫中有三个候选数只出现在三个格子中，那么这三个格子必然正好是这三个数字，那么这三格子中其他候选数可以删除
                隐含四链数法  如果我们发现某一行某一列或某个九宫中有四个候选数只出现在四个格子中，那么这四个格子必然正好是这四个数字，那么这四格子中其他候选数可以删除
            '''
            __onlyone()
            if not self.right():
                return
            searched = False            
            time_num_seats = []
            for i, rcb_seat in enumerate(self.rcb_seats):
                cannums = self.__getcannums(rcb_seat)
                for time in range(2, 5): 
                    _nums = {num for num in self.nums if cannums.count(num) == time}
                    for _timenums in itertools.combinations(_nums, time): # 取time个数的组合
                        timeseats = self.__getnums_seats(_timenums, rcb_seat)
                        if len(timeseats) == time: # 数对法, 数字个数与空格数相同
                            _othernums = self.nums.difference(_timenums)
                            _thisnums = set(_timenums)
                            for seat in rcb_seat:
                                oldlen = len(self.seat_nums[seat][1])
                                self.seat_nums[seat][1] -= (_othernums
                                        if seat in timeseats else _thisnums)
                                if oldlen > len(self.seat_nums[seat][1]):
                                    #print('数对法: 查找处理成功')
                                    searched = True
                    if time < 4 and _nums and i < 18: # 区域删减法, 找行、列
                        time_num_seats.append(self.__getnum_seats_dict(_nums, rcb_seat))
            '''
                区域删减法
                    如果发现某一候选数在某一单元(行，列，九宫）中完全处在同另外一个单元的交集中，
                    那么在另外一个单元中，不在交集中的这个候选数必然可以删除
            '''
            for num_seats in time_num_seats: # 区域删减法, 行、列与块核对是否有交集
                for num, timeseats in num_seats.items():
                    for j, rcb_seat in enumerate(self.blk_seats):
                        if timeseats.issubset(rcb_seat):
                            for seat in set(rcb_seat).difference(timeseats):
                                if num in self.seat_nums[seat][1]:
                                    self.seat_nums[seat][1] -= {num}
                                    #print('区域删减法: 有交集的单元其他空格排除此数, 查找处理成功')
                                    searched = True
                            break
            if searched:
                __relatednums()
            
        def __rectangle():    
            '''
                矩形删减法
                    如果某个候选数在某两行(列)中只出现在某两列(行)中，那么在那两列(行)中,
                    不在那两行(列)的这个候选数都可以删除.
                    把它扩展到三行或四行就可以得到高阶矩形法(也翻译成3链列,4链列)
            '''
            __relatednums()
            if not self.right():
                return
            searched = False 
            for time in range(2, 5):
                row_num_seats = {}
                for rcb_seat in self.row_seats:
                    cannums = self.__getcannums(rcb_seat)
                    for num in self.nums:
                        if cannums.count(num) == time: # 某行的num数是否出现time次
                            if num not in row_num_seats:
                                row_num_seats[num] = []
                            row_num_seats[num].append(self.__getnum_seats(num, rcb_seat))
                for num, rowseats in row_num_seats.items():
                    if len(rowseats) != time: # 某数是否出现在time行
                        continue
                    row_seats = []
                    for seats in rowseats:
                        row_seats.extend(seats)
                    cols = {seat % 9 for seat in row_seats} # 行出现位置所对应的列
                    if len(cols) != time:
                        continue
                    for col in cols:                
                        for seat in set(self.col_seats[col]).difference(row_seats):
                            if num in self.seat_nums[seat][1]:
                                self.seat_nums[seat][1] -= {num}
                                #print('矩形删减法: 有矩形顶角的空格排除此数, 查找处理成功')
                                searched = True
            if searched:
                __rectangle()
        
        def __crack():    
            '''
                暴力破解法
                    从较少候选数的空格开始，测试填入
            '''
            seat_nums = copy.deepcopy(self.seat_nums)
            for seat in seat_nums:
                if seat_nums[seat][0] > 0:
                    continue
                for num in seat_nums[seat][1]: 
                    global count
                    count += 1
                    self.__setnum(seat, num)
                    __rectangle()
                    if self.isdone():                        
                        return
                    else:
                        self.seat_nums = copy.deepcopy(seat_nums)
            
        firstcount = self.numcount()        
        __rectangle()
        if not self.isdone():
            __crack()
        #'''    
        endcount = self.numcount()
        print('{:4d} 初始：{:2d}个，填入：{:2d}个，最终：{:2d}个，crack填入：{:2d}个'.format(
                self.no, firstcount, endcount - firstcount, endcount, count))
        #'''    
                
    def right(self):
        return all([(bool(n) != bool(c)) for n, c in self.seat_nums.values()]) 
        
    def numcount(self):        
        return len([1 for seat in self.seat_nums if self.seat_nums[seat][0] > 0])

    def isdone(self):
        #return self.right() and self.numcount() == 81
        return sum([len({self.seat_nums[seat][0]
                    for seat in rcb_seat if self.seat_nums[seat][0] > 0})
                    for rcb_seat in self.rcb_seats]) == 9 * 27
        
        
class ShuDus(object):

    def __init__(self, filename):
        no_numses = re.findall('(\d+),{9}\n' + (',(\d?)'*9 + '\n') * 9,
                    open(filename).read())
        self.shudus = [ShuDu(no_nums) for no_nums in no_numses]
        with open(filename[:-4] + '.txt', 'w') as fileobj:
            fileobj.write(str(self))
 
    def __str__(self):
        return ''.join([str(shudu) for shudu in self.shudus])        
            
    
if __name__ == '__main__':
    import time
    start = time.time()
    
    ShuDus('c:\\cc\\shudu.csv') 
    
    end = time.time()
    print('用时: {0:6.3f} 秒'.format(end - start))
    
    
#