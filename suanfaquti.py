
import cProfile

def getnum_Q01():
    
    def __ispalindrome(x, scale):
        res = []
        while (x // scale):
            res.append(x % scale)
            x = x // scale
        if x:
            res.append(x)
            
        '''    
        length = len(res)
        for i in range(length // 2):
            if res[i] != res[length - 1 - i]:
                return False
        return True        
        '''
        return res == res[::-1]        
        
    x = 11
    while True:
        x += 2
        if (__ispalindrome(x, 10) and __ispalindrome(x, 8)
            and __ispalindrome(x, 2)):
            print(x, oct(x), bin(x)) # 585 0o1111 1001001001
            return x                
            
            
if __name__ == '__main__':

    cProfile.run('getnum_Q01()')
    
    
    
#    