class ClassUtils(object):
    ''' Basic methods accessible by class inheritance '''
    def vp(self, string):
        ''' Verbose print '''
        if self.verbose:
            print(string)