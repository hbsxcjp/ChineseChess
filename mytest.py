'''
中国象棋单元测试类型
'''

import unittest
import time
import cProfile
from user import *


class Test(unittest.TestCase):

    def test_crossbase(self):            

        crolist = [Cross.allrowcols]
        for cro in [Cross.siderowcols, Cross.kingrowcols,
                    Cross.advisorrowcols, Cross.bishoprowcols, Cross.pawnrowcols]:
            for f in [True, False]:        
                crolist.append(cro[f])                
        for cro in crolist:
            #print(sorted([c for c in cro]), len(cro))        
            pass          
        
    def test_Piece(self):
    
        pieces = Pieces()
        
        blackkingpie = pieces.getkingpiece(BLACK_SIDE)
        redkingpie = pieces.getkingpiece(RED_SIDE)
        #print(blackkingpie, redkingpie)
        
    def test_Board(self):
    
        board = Board() 
        #print(board)

    
    def test_LoadPiecesToBoard(self):
        
        # 新棋局 
        FEN = 'rnbakabnr/9/1c5c1/p1p1p1p1p/9/9/P1P1P1P1P/1C5C1/9/RNBAKABNR r - - 0 1'
        board = Board()
        pieces = board.pieces
        
        board.loadpieces(FEN)
        #print(board)         
        crosses = board.getlivecrosses()
        #print(sorted(crosses), len(crosses))        
        
        pie_moverowcols = [(pie, pie.getmoverowcols(rowcol, board))
                for rowcol, pie in crosses.items()]
        for pie, rowcols in pie_moverowcols:
            #print(pie, sorted(rowcols), len(rowcols))
            pass            
        
        #print(board)        
        
    def test_LoadPGN(self):
        start = time.time()
        
        cc = User(1, '陈建平') #
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
        for pgnfilename in pgnfilenamel:
            #print(pgnfilename)
            cc.loadmanual('pgn/' + pgnfilename)
            cc.saveasmanual('C:/ChineseChess/mytest_' + pgnfilename)
            
        end = time.time()
        #print('usetime: %0.5f' % (end - start))

    
        
if __name__ == '__main__':

    unittest.main()
    
    # 测试
    #cProfile.run('main()')
    
    