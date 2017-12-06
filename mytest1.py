'''
中国象棋单元测试类型
'''

import unittest
import time
import cProfile
from user import *
from config_et import *
from form import *


class Test(unittest.TestCase):

    def test_config_et(self):  
        '''
        cc1 = Config_ET(User(1, '陈建平'))
        cc1.save()        
        
        cc2 = Config_ET(User(2, '李晓丹'))
        cc2.save()
        
        cc3 = Config_ET(User(3, '陈思贝'))
        cc3.save()
        '''
        pass       
    
    def test_form(self):        
        
        user = User(1, 'cjp')
        user.loadmanual('聂许战.pgn') #  '兵的着法.pgn'  ''          
        #print(user.chessboard)        
        user.application.mainloop()       
        pass      
    
        
if __name__ == '__main__':

    Test().test_form()
    
    #python -W ignore mytest1.py
    #unittest.main()
    
    # 测试
    #cProfile.run('main()')
    
    