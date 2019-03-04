#!/usr/bin/env python3
# always keep in mind:
# import this # stay well founded in the Way of the Masters

# ### imports ######
import re
# import os
import sys
import inspect
# from inspect import (getframeinfo, currentframe, getouterframes, getsource)
from inspect import (getframeinfo, currentframe)
# import glob
# import logging
# import optparse
from datetime import datetime
import functools
import time
# ###########
# import dis  # this is not *needed* but offers
# dis.dis(myfinc) <-- spits out some useful info re: myfunc()

dtime = datetime.now().strftime("%Y%m%y-%H%M")  # this does not get imported


DBUG = 2  # will print to stdout if set to 1
# -- use 2 to add funcname and funcdocs
# DLOG = os.path.basename(sys.argv[0]) + ".log"  # will append to log to
# file if this is not commented out


# this is kinda cool
# within your function use: dbug.fname()
# and your function name is returned
# using this sys method is faster than inspect methods
fname = lambda n=0: sys._getframe(n + 1).f_code.co_name  # noqa: E731


# #################
def get_source(mod):
    # #############
    """
    returns source code for either a module or module.method
    use: dbug.getsource(iex)
    import random
    dbug.get_source(random.randint)
    Notes:
        You can use help(module) to list functions and their doc
        You can use dir(module) to list attibutes and methods (functions)

    >>> get_source(dbug)  # doctest: +ELLIPSIS, +NORMALIZE_WHITESPACE
        'def dbug(msg=""):...'


    """
    return inspect.getsource(mod)


# ###################
def dbug(msg=""):
    # ###############
    """ # noqa:
    At the top of your script set these global values:
    from inspect import (getframeinfo, currentframe, getouterframes)
    DBUG=2 # will print to stdout if set to 1 -- use 2 to add funcname and funcdocs
    #DLOG=os.path.basename(sys.argv[0])+".log" # will append to log to file if this is not commented out
    Function: dbug() will print (or log) DEBUG: (datetime) [lineno] msg
    print this function doc with CLI help(dbug) or CODE dbug.__doc__
    needs: from inspect import currentframe.
    Simple to use... dbug("my message here")
    use:
    from dbug import dbug
      or
    from dbug import *
    dbug("We are here now")
    required:
    from inspect import (getframeinfo, currentframe, getouterframes)
    import time

    To test run: python3 -m doctest -v dbug.py
    >>> dbug("123")
    DEBUG: [<module>:1] 123
    '1'
    """
    dbug = DBUG if DBUG else 1
    # cf = currentframe()
    fname = str(getframeinfo(currentframe().f_back).function)
    lineno = str(inspect.currentframe().f_back.f_lineno)
    ## msg = "DEBUG: [" + {fname} + ":" + {lineno} + "] " + {msg}
    msg = "DEBUG: [" + fname + ":" + lineno + "] " + msg

    try:
        if dbug >= 0:
            print(msg)
    except BaseException:
        pass

    return lineno


# ############
def dbug_var(x):
    # ########
    """
    To test run: python3 -m doctest -v dbug.py
    >>> a = "xyz"
    >>> dbug_var(a)
    DEBUG: [<module>:1] a:xyz
    '1'

    """
    frame = inspect.currentframe().f_back
    s = inspect.getframeinfo(frame).code_context[0]
    r = re.search(r"\((.*)\)", s).group(1)
    fname = str(getframeinfo(currentframe().f_back).function)
    lineno = str(inspect.currentframe().f_back.f_lineno)
    print("DEBUG: [" + {fname} + ":" + {lineno} + "] " + {r} + ":" + {x})
    return lineno


# ###########
def lineno():
    # #######
    """
    Returns the current line number.
    To test run: python3 -m doctest -v dbug.py
    >>> lineno()
    '1'
    """
    return str(inspect.currentframe().f_back.f_lineno)


# ################
def trace(func):
    # ############
    """
    A decorator wrapper for providing a trace on a func
    use:
        from dbug import trace

        @trace
        def myfunc(arg):
            print(arg)

        myfunc("blah")
         TRACE: Function Running:      myfun(('blah',)) ...
        blah
          TRACE: Function returned:     None
          TRACE: Function doc:          None
          TRACE: Function Elapsed time: 0.0549

    requires:
        import time
        import functools

    To test: I tried to design a doctest w/o success

    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # import pdb; pdb.set_trace()
        st = time.time()
        # print(f'TRACE: calling {func.__name__}() 'f'with {args}, {kwargs}')
        print('  TRACE: Function Running:      ' + {func.__name__} + '(' + {args} + ') ...')

        original_result = func(*args, **kwargs)
        etime = round((time.time() - st), 4)

        # print('  TRACE: Function returned:     ' + {original_result!r})
        print('  TRACE: Function returned:     ' + {original_result})
        print('  TRACE: Function doc:          ' + {func.__doc__})
        print('  TRACE: Function Elapsed time: ' + {etime})

        return original_result  # just in case somebody whats to check this...

    return wrapper



# ####################
def dbug_help():
    # ################
    """
    dbug.py
    """
    s = ''' # noqa:
         Double, double toil and trouble
         Fire burn and caldron bubble
         Fillet of fenny snake
         In the cauldron boil and bake
         ...
         To use dbug.py
         Place in the directory of your choice
         If it is not in the directory of the code file you are working with you
         will need to add code similar to this:
           import sys
         sys.path.append('/home/name/dev/py.d/')
         Then import what you need with the desired func name stated
         eg:
           from dbug import dbug
           from dbug import trace
           from dbug import lineno
         In your code use dbug:
           dbug("We are here and value of var1: "+ str(var1))
           or
           dbug(f"just added var1: {var1} to total: {total}")
         You can also "wrap" a function with trace for quick info on that function
           @trace
           def myfunc(myvar):
                ....
         For line number just print(lineno())
         You could:
           import dbug
         And then make you calls (the long hand way)
           dbug.dbug("We are here now")
           ---
           @dbug.trace
           def myfunc():
               ....
           ---
           print( dbug.lineno() )
         Enjoy!
         '''
    print(s)


if __name__ == '__main__':
    pass
