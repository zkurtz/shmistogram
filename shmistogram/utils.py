from time import time

def say_time_since(timestamp, task=''):
    delta = time() - timestamp
    print(task + ' seconds elapsed: %.2f seconds' % delta)

class ClassUtils(object):
    ''' Basic methods accessible by class inheritance '''
    def vp(self, string):
        ''' Verbose print '''
        if self.verbose:
            print(string)

    def timer(self, timestamp=None, task=''):
        ''' Set a timestamp or return time since a timestamp

        :param timestamp: (datetime or None) If None, return time(); else summarize the time since timestamp
        :param task: (str) A description of what is being timed
        '''
        if not self.verbose:
            return None
        if timestamp is None:
            return time()
        else:
            say_time_since(timestamp, task=task)


