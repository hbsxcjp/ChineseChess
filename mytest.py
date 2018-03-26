'''
中国象棋单元测试类型
'''

import unittest
import cProfile

from user import User

#from config_et import *
#from form import *


class Test(unittest.TestCase):

    def test_form(self):
        user = User(1, 'cjp')
        user.application.mainloop()
        pass


if __name__ == '__main__':

    unittest.main()

    # 测试
    #cProfile.run('unittest.main()')
