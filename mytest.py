﻿'''
中国象棋单元测试类型
'''

import unittest
import time
import cProfile
from user import *
from config_et import *
from form import *


class Test(unittest.TestCase):
       
    def test_setandgetPGN(self):
        start = time.time()        
        chessboard = ChessBoard()
        pgnfilenamel = ['“石林杯”全国象棋团体锦标赛 - 广东许银川 (先胜) 上海胡荣华.PGN',
                '东北联队、上海队象棋友谊赛 - 东北王嘉良 (先负) 上海胡荣华.PGN',
                '“象棋南北国手团体对抗赛” - 北方队赵国荣 (先胜) 南方队胡荣华.PGN',
                #'第一届“嘉宝杯”粤沪象棋对抗赛 - 上海胡荣华 (先和) 广东吕钦.PGN',
                #'五羊杯 - 广东吕钦 (先胜) 上海胡荣华.PGN',
                #'第一届“嘉宝杯”粤沪象棋对抗赛 - 上海胡荣华 (先胜) 广东吕钦.PGN',
                #'(着法：红先胜).PGN',
                '第十九届“五羊杯”象棋冠军赛 - 湖北柳大华 (先和) 上海胡荣华.PGN',
                'a.pgn',
                '聂许战.pgn',
                '兵的着法.pgn']
        for filename in pgnfilenamel:
            #print(pgnfilename)'pgn/' + pgnfilename
            with open('pgn/'+filename) as f:
                pgn = f.read()
            chessboard.setpgn(pgn)
            with open('c:/chinesechess/mytest_'+filename, 'w') as f:
                f.write(chessboard.getpgn())
            pass            
        end = time.time()
        print('usetime: %0.5f' % (end - start))

    def test_form(self):
        user = User(1, 'cjp')
        user.application.mainloop()
        pass      
    
        
if __name__ == '__main__':

    unittest.main()
    
    # 测试
    #cProfile.run('unittest.main()')
    
    