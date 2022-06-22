'''
中国象棋单元测试类型
'''

import unittest
import cProfile
from user import User # 用户


class Test(unittest.TestCase):

    def test_form(self):
        import time
        start = time.time()
        
        user = User(1, 'cjp')
        
        end = time.time()
        print('usetime: %0.3fs' % (end - start))
        
        user.application.mainloop()
        pass


if __name__ == '__main__':

    unittest.main()

    # 测试
    #cProfile.run('unittest.main()')
