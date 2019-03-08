#!//usr/bin/env python3
# vim: set syntax=none nospell:
# #####################
# Script name: gtools.py
# Created by: geoff.mcnamara@gmail.com
# Created on: 2018
# Purpose: this is a quick-n-dirty set of tools that might be useful
# ... much room for improvment and lots of danger points - not recommended for anything you care about
# ... use this file in anyway and all your data could be at risk ;)
# ... lots of debugging code still remains and legacy code that should be removed
# ... this file is constantly changing so nothing should depend on it ;)
# ... depends on python3!
# #####################################

# #####
# to use this module:
# import sys
# sys.path.append("/home/geoffm/dev/python/gmodules/")
# from gtools import *
#  or
# place this file in the same directory of your __main__ app
# #####
# dir(gtools)  # <--- will list all the functions in this module
# ##################


# ### imports ######
import re
import os
import sys
import subprocess
# import glob
from datetime import datetime
from docopt import docopt
# import sys
from colorama import init
from colorama import Fore, Style
from math import ceil
#
# for dbug add the following
# sys.path.append("/home/geoffm/dev/py.d/")
# try:
#     from dbug import dbug
# except:
#     pass
# from dbug import trace
# ################
# import unittest
import platform

dtime = datetime.now().strftime("%Y%m%d-%H%M")

init(autoreset=True)  # don't have to RESET after a color print
RED = Style.BRIGHT + Fore.RED
DIM_RED = Style.DIM + Fore.RED
GREEN = Style.BRIGHT + Fore.GREEN
BLUE = Style.BRIGHT + Fore.BLUE
BLACK = Style.BRIGHT + Fore.BLACK
CYAN = Style.BRIGHT + Fore.CYAN
DIM_CYAN = Style.DIM + Fore.CYAN
MAGENTA = Style.BRIGHT + Fore.MAGENTA
RESET = Style.RESET_ALL


# #############
class DoMenu:
    # #########
    """
    NOTE: to test this: echo 1 | python3 -m doctest -v ./gtools.py
    Use:
    Make sure you have the functions called for: in this example:
      do_item1() do_item2 do_item3 do_item4 etc

    # >>> main_menu = DoMenu("Main")
    # >>> main_menu.add_selection({"item1":cls})
    # >>> main_menu.do_select()  # doctest: +ELLIPSIS
    # ============================================================
    #                             Main
    # ============================================================
    #                            1 item1...
    # ...
    """

    def __init__(self, name):
        self.name = name
        # dbug(f"args:{self.args}")
        self.selections = {}
        self.choices = {}
        self.length = 60
        self.cls = False
        self.center = True

    def add_selection(self, selection):
        """
        selection needs to be a dictionary element ie:
          {"get this done":do_it} where do_it is actually a function name
        """
        # dbug(f"selection:{selection}")
        self.selections.update(selection)

    def do_select(self):
        if self.cls:
            cls()

        cnt = 0
        # dbug(f"self.itms:{self.itms}")
        # dbug(f"self.selections:{self.selections}")
        # mmax = max(self.selections)
        # mmax_len = len(mmax)
        # side_len = mmax_len / 2
        # position = int((self.length + 2) / 2 - side_len)
        # dbug(f"mmax:{mmax} mmax_len:{mmax_len} side_len:{side_len} position:{position}")  # noqa:
        do_title_three_line(self.name, self.length)
        # do_line("=",self.length)
        # do_title(self.name,"+",self.length)
        # do_line("=",self.length)

        self.add_selection({"Quit [Qq] or blank": exit})
        for k, v in self.selections.items():
            cnt += 1
            # print(f"{cnt:{position}} {k}")
            print("{:position}} {}".format(cnt, k))
            # dbug(f"k:{k} v:{v}")
            self.choices.update({str(cnt): v})

        do_line("=", self.length)
        # prompt = input(f"Please make your selection [q=quit or 1-{cnt}]: ")
        prompt = input("Please make your selection [q=quit or 1-{}]: ".format(cnt))
        ans = input(center(prompt, self.length))
        do_line("=", self.length)
        # dbug(f"Selected: {ans} Action: {self.choices[ans]}")
        # dbug(f"self.choices:{self.choices}")
        if ans == "q" or ans == "Q" or ans == "":
            exit()
        r = self.choices[ans]()
        return r


# #####################
def path_to(app):
    # #################
    """Check whether `name` is on PATH and marked as executable."""
    # from whichcraft import which
    from shutil import which
    full_path = which(app)
    # print("full_path: " + full_path)
    # returns None type if it fails?
    if full_path is not None:
        return full_path


# #####################
def center(s, length):
    # #################
    """
    Use: center(str,length)
    returns the margin + s
    # >>> center("what is the center",80)
    # '                               what is the center'
    # """
    # margin = int((length - len(s)) / 2)
    # r = f"{' '*margin}{s}"
    r = "{' '*margin}{s}".format(s)
    return r


# #########
def cls():
    # #####
    """
    Clears the terminal screen.
    """
    # Clear command as function of OS
    command = "-cls" if platform.system().lower() == "windows" else "clear"
    # Action
    os.system(command)
    # print(ansi.clear_screen()) # this works but puts it at the smae cursor
    # location


# ########################
def askYN(msg="Conintue", dfault="y"):
    # ####################
    """
    # >>> askYN()
    # Conintue [y]: True

    # Note: to test: yes | python3 -m doctest -v iex.py
    """
    yes = set(['yes', 'y', 'ye', ''])
    no = set(['no', 'n'])

    while True:
        choice = input(msg + " [" + dfault + "]: ").lower()
        if choice == "":
            choice = dfault
        if choice in yes:
            return True
        elif choice in no:
            return False
        else:
            print("Please respond with 'yes[y]' or 'no[n]' \n")


# ###############################
def helpme(subject="all"):
    # ##########################
    """ try me and see
    to use: import tools
    then: gtools.helpme()
    or
    from gtools import helpme
    then: helpme()
    >>> helpme()
    <BLANKLINE>
        ### general tips ###
        To use tools.helpme()
        import sys
        sys.path.append("/home/geoffm/dev/python/pymodules/")
        #from tools import *
        import tools
        dir(tools)
        tools.helpme()
        helpme("gen")
        WIP
    <BLANKLINE>
        ### os tips ###
        os.move(source, target)
        os.path.isfile(file)
        os.path.exists(file|dir)
        time.ctime(os.path.getmtime("./fo.py"))
        files = os.listdir(directory) # lists all files in that dir including hidden files
        files.sort()
    <BLANKLINE>
        ### python eggs ###
        import __hello__
        import this
            love = this
            this is love --> True
        import antigravity
    <BLANKLINE>


    """

    gen, os, eggs = "", "", ""
    all = gen + os + eggs

    gen = """
    ### general tips ###
    To use tools.helpme()
    import sys
    sys.path.append("/home/geoffm/dev/python/pymodules/")
    #from tools import *
    import tools
    dir(tools)
    tools.helpme()
    helpme("gen")
    WIP
    """

    os = """
    ### os tips ###
    os.move(source, target)
    os.path.isfile(file)
    os.path.exists(file|dir)
    time.ctime(os.path.getmtime("./fo.py"))
    files = os.listdir(directory) # lists all files in that dir including hidden files
    files.sort()
    """

    eggs = """
    ### python eggs ###
    import __hello__
    import this
        love = this
        this is love --> True
    import antigravity
    """

    all = gen + os + eggs
    if subject == "" or subject == 'all':
        print(all)

    if subject == "os":
        print(os)

    if subject == "gen":
        print(gen)


# ###############################
def file_exists(file, type="file"):
    # ###########################
    """
    Note: type can be "file" or "dir" (if it isn't file the assumption is dir)
        should rename this to path_exists... argghh
    >>> file_exists('/etc/hosts')
    True
    """
    if type == "file":
        try:
            os.path.isfile(file)
        except Exception as e:
            print("Exception: " + str(e))
            return False
        return os.path.isfile(file)
    else:
        # check file or dir
        return os.path.exists(file)
    # to move a file use: os.rename(source, target)
    # or shutil.move(source, target)


# #####################
def do_list(l, mode="v"):
    # ##############o#
    """
    # >>> l = ['one','two','three']
    # >>> do_list(l, "nc")
    # ===========
    # || one   ||
    # || two   ||
    # || three ||
    # ===========
    """
    if mode == "nc":
        color = ""
        reset = ""
        mode = "v"
    else:
        color = BLUE
        reset = RESET

    # dbug(f"type(l):{type(l)} mode={mode}")
    if mode == 'v':
        max_len = len(max(l, key=len))
        print(color + "=" * (max_len + 6))
        for x in l:
            # print(f"{color}||{reset} {x:<{max_len}} {color}||{reset}")
            print("{}||{} {:<max_len} {}||{}".format(color, reset, x, color, reset))
        print(color + "=" * (max_len + 6))
    if mode == 'h':
        str = "||"
        for i in l:
            # str += f" {i} ||"
            str += " {} ||".format(i)

        print(BLUE + "=" * len(str))
        print(str)
        print(BLUE + "=" * len(str))


# ######################
def do_kv_cols(d, cols, color=BLUE, title="", col_limit=25):
    # ##################
    """
    #>>> d = {'one':1,"two":2,"three":3}
    #>>> do_kv_cols(d,3,"")
    #=========================================
    #|| one   | 1 || two   | 2 || three | 3 ||
    #=========================================
    """

    # dbug(f"d:{d}")
    # from itertools import imap

    # max_k = max(map(len,d))
    if color == "":
        RESET = ""
        # color_set = ["", "", ""]
    else:
        RESET = Style.RESET_ALL
        # color_set = [f"{RED}", f"{GREEN}", f"{RESET}"]
    max_k = 0
    max_v = 0
    for k, v in d.items():
        #    # dbug(f"v:{v} len(v):{len(str(v))}")
        #    my_k = k
        #    for i in color_set:
        #        if i in my_k:
        #            re.replace(i,"",my_k)
        #    k = my_k
        #    dbug(f"k:{k} my_k:{my_k}")
        if len(str(k)) > max_k:
            max_k = len(str(k))
        if len(str(v)) > max_v:
            max_v = len(str(v))
    if max_k > col_limit:
        max_k = col_limit
    if max_v > col_limit:
        max_v = col_limit

    # dbug(f"max_k:{max_k} max_v:{max_v}")  # ; exit()
    elem_len = max_k + max_v + 7
    # dbug(f"elem_len:{elem_len}")

    if not isinstance(d, dict):
        # dbug(f"type(d):{type(d)} is not a dictionary... ")
        # print(f"type(d):{type(d)} d:{d}")
        print("type(d):{} d:{}".format(type(d), d))
        return

    # elem_len=47
    # word_len = int((elem_len - 7) / 2)
    # word_len = 20
    # dbug(f"word_len:{word_len}")
    border_len = ((cols * elem_len) + 2)
    if title != "":
        do_title(title=title, chr="=", length=border_len)
    else:
        print(color + "=" * border_len + RESET)
    c = 0
    line = ""
    lline = ""
    #
    # display_below = ""
    for k, v in d.items():
        if isinstance(v, dict):
            v = next(iter(v.values()))
        if is_number(v):
            # if type(v) is str:
            #   v = float(v)
            if not isinstance(v, str):
                v = round(v, 2)
                if v > 1000000:
                    v = str(int(v / 1000000)) + "M"
        if v is None:
            v = "none"
        if len(str(v)) > max_v:
            # this trims the val to col_limit length - to keep column size reasonable - this is important
            v = str(v)[:col_limit]
            # dbug("val len: [" + str(len(str(v))) + "]>max_v: [" + str(max_v) + "]")
            # dbug("v: " + str(v))
            # dbug(f"v (limited): {str(v)[:col_limit]}")
        #    display_below += f"{k}: {v}"
        #    continue
        # if len(str(v)) > word_len:
        #     dbug("val_len: [" + str(len(str(v))) + "]>word_len: [" + str(word_len) + "]")
        #     v = v[:word_len]
        if len(str(k)) > max_k:
            # this trims the key to col_limit length - to keep column size reasonable - this is important
            v = str(k)[:col_limit]

        # dbug(f"v:{v} v>max_v: {v:>{max_v}}  and max_v{max_v}")
        if c == 0:
            c += 1
            # line = f"{color}||{RESET} {k:<20} {color}|{RESET} {v:>20} {color}|{RESET}"
            # lline = f"|| {k:<20} | {v:>20} |"
            # line = f"{color}||{RESET} {k:<{max_k}} {color}|{RESET} {v:>{max_v}} {color}|{RESET}"
            line = "{}||{} {:<{max_k}} {}|{} {:>{max_v}} {}|{}".format(color, RESET, k, color, RESET, v, color, RESET)
            
            # lline = f"|| {k:<{max_k}} | {v:>{max_v}} |"
            lline = "|| {:<{max_k}} | {:>{max_v}} |".format(k, v)
            if c == cols:  # or to put another way if cols == 0
                c = 0
                # line += f"{color}|{RESET}"
                # lline = f"|| {k:<{max_k}} | {v:>{max_v}} ||"
                line += "{}|{}".format(color, RESET)
                lline = "|| {:<max_k} | {:>max_v} ||".format(k, v)

                # print(f"{line}")
                print(line)
                line = ""

                # continue
        elif c >= (cols - 1):
            # did we reach number of col
            # dbug(f"end the line ... k:{k} v:{v} c:{c} cols:{cols}")
            # line += f"{color}|{RESET} {k:<20} {color}|{RESET} {v:>20} {color}||{RESET}"
            # line += f"{color}|{RESET} {k:<{max_k}} {color}|{RESET} {v:>{max_v}} {color}||{RESET}"
            line += "{}|{} {:<max_k} {}|{} {:>max_v} {}||{}".format(color, RESET, k, color, RESET, v, color, RESET)
            # lline += f"| {k:<20} | {v:>20} ||"
            # lline += f"| {k:<{max_k}} | {v:>{max_v}} ||"
            lline += "| {:<max_k} | {:>max_v} ||".format(k, v)
            c = 0
            # print(f"{line}")
            print(line)
            line = ""
            continue
        else:
            # add another field
            # dbug(f"c:{c} cols:{cols}")
            # dbug(f"k:{k} v:{v}")
            # line += f"{color}|{RESET} {k:<20} {color}|{RESET} {v:>20} {color}|{RESET}"
            # lline += f"| {k:<20} | {v:>20} |"
            # dbug(f"here now with c:{c} k:{k} v:{v} cols:{cols}")
            # line += f"{color}|{RESET} {k:<{max_k}} {color}|{RESET} {v:>{max_v}} {color}|{RESET}"
            # lline += f"| {k:<{max_k}} | {v:>{max_v}} |"
            line += "{}|{} {:<max_k} {}|{} {:>max_v} {}|{}".format(color, RESET, k, color, RESET, v, color, RESET)
            lline += "| {:<max_k} | {:>max_v} |".format(k, v)
            c += 1
    if c > 0 and c < cols:
        # do a fill if needed...
        # dbug(f"hmmm.. c:{c} cols:{cols}")
        llen = len(lline)
        # fill_len = border_len - (llen + 3)
        # dbug(f"border_len:{border_len} llen:{llen} fill_len:{fill_len}")
        fill = "-" * (border_len - (llen + 3))
        # dbug(f"fill:{fill}")
        line += color + "|" + RESET + fill + color + "||" + RESET
        # dbug(f"line:{line} cols:{cols}")
        # print(f"{line}")
        print(line)
    print(color + "=" * border_len + RESET)
    # if display_below != "":
    #    print(display_below)
    # print("debug: display_below: " + str(display_below))
    # EOB #


# #############################
def do_line(chr="-", length=40, color=BLACK):
    # #########################
    """
    Use: do_line(chr='-',length=40,color=BLUE)
    Do a line with chr [-] of length [40] with color [BLUE]
    do_line()
    do_line("=")
    do_line("+",60)
    do_line("+",60,RED)
    # >>> do_line("=",50,"")
    # ==================================================
    """
    if color == "":
        # print(f"{chr*length}")
        print(chr*length)
    else:
        # print(f"{color}{chr*length}{RESET}")
        print("{}{}{}".format(color, chr*length, RESET))


# ##################################
def do_title_three_line(str, length=120, color=""):
    # ##############################
    """
    Use: do_title_three_line(str,length=120)
    This should probably be made into a class and combined with do_title
    >>> do_title_three_line("mytitle",30)
    ==============================
               mytitle
    ==============================

    """
    do_line("=", length, color="")
    margin = int((length - len(str)) / 2)
    # print(f"{' '*margin}{str}")
    print(' '*margin + str)
    do_line("=", length, color="")


# ##################
def do_title(title='', chr='=', length=120, color=BLUE, one_three_line=1):
    # ##############
    """
    A quick-n-dirty utility to print out a title line using
    str = as the title string
    c = as the repeated character
    length defaults to 120
    color defaults to blue
    do_title(title, chr, length, color)
    >>> do_title("mytitle","-",40,color="")
    --------------- mytitle ---------------
    '--------------- mytitle ---------------'

    """
    try:
        chr.isalpha()
    except BaseException:
        print("Syntax for do_title(title, chr='=', length=120, color=BLUE)")
        exit()
    if color == "":
        RESET = ""
    else:
        RESET = Style.RESET_ALL

    # dbug(f"str:{str}")
    slen = len(title)
    side_len = int((length - slen - 2) / 2)
    # side_len = int( ( length / 2 ) - ((slen + 2) / 2) )
    side = chr * side_len
    # dbug(f"len(str):{len(str)} slen:{slen} side_len:{side_len}")
    if len(title) > 0:
        # line = f"{color}{side}{RESET} {title} {color}{side}{RESET}"
        line = "{}{}{} {} {}{}{}".format(color, side, RESET, title, color, side, RESET)
    else:
        # line = f"{color}{(chr * length) }{RESET}"
        line = "{}{}{}".format(color, chr*length, RESET)
    # dbug(f"len(line):{len(line)}")
    # print(f"{line}")
    print(line)
    return line


# ############################
def is_number(s):
    # ########################
    """ Returns True is string is a number.
    >>> is_number(-1.5)
    True
    >>> is_number("-1.5")
    True
    >>> is_number("one two three")
    False
    >>> is_number("1.256")
    True
    >>> is_number("--")
    False
    """
    s = str(s)
    s = re.sub(r'^-([0-9.]+)', '\\1', s, 1)
    s = re.sub('\\.', '', s, 1)
    # dbug(f"s:{s}")
    # s = s.replace('.','', 1)
    # dbug(f"s:{s} type(s)={type(s)}")
    # if s.isdigit() == True:
    #     dbug(f"s:{s} is a digit")
    #     return True
    # else:
    #     dbug(f"s:{s} is not a digit")
    # dbug(f"s:{s}")
    r = s.isdigit()
    return r


# ###################################
def print_table(myDict, colList=None):
    # ################################
    """ Pretty_print a list of dictionaries (myDict) as a dynamically sized table.
    If column names (colList) aren't specified, they will show in random order.
    Author: Thierry Husson - Use it as you want but don't blame me.
    >>> print_table({"one":1,"two":2,"three":3})
    =================================================
    || one                  |                 1.00 ||
    || two                  |                 2.00 ||
    || three                |                 3.00 ||
    =================================================

    """
    # if not colList: colList = list(myDict[0].keys() if myDict else [])
    # myList = [colList] # 1st row = header
    # for item in myDict: myList.append([str(item[col] or '') for col in colList])
    # colSize = [max(map(len,col)) for col in zip(*myList)]
    # formatStr = ' | '.join(["{{:<{}}}".format(i) for i in colSize])
    # myList.insert(1, ['-' * i for i in colSize]) # Seperating line
    # for item in myList: print(formatStr.format(*item))
    llen = 49
    print("=" * llen)
    for k, v in myDict.items():
        if is_number(v):
            # dbug(f"k:{k} v:{v}")
            if v > 1000000:
                v = int(v / 1000000)
                v = str(v) + "M"
                # print(f"|| {k:<20} | {v:>20} ||")
                print("|| {:<20} | {:>20} ||".format(k, v))
            else:
                # print(f"|| {k:<20} | {v:>20.2f} ||")
                print("|| {:<20} | {:>20.2f} ||".format(k, v))
        else:
            if v is None:
                v = "na"
            # dbug(f"k:{k} v:{v}")
            # print(f"|| {k:<20} | {v:>20} ||")
            print("|| {:<20} | {:>20} ||".format(k, v))
    print("=" * llen)
    # EOB #


# ### Main Code ###

# ###############
def run_cmd(cmd, prnt=True):
    # ###########
    """
    purpose: runs cmd and returns rc - prints output
      eg: out = run_cmd("uname -o",False)
      # now you can print the output from the cmd:
      print(f"out:{out}")
    >>> r = run_cmd("uname -o")
    GNU/Linux

    """
    import subprocess
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf-8')
    # dbug(f"cmd.split():{cmd.split()} process:{process}")
    out = ""
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            if prnt:
                print(output.strip())
            out += output
    # rc = process.poll()
    # if prnt:
    #     return rc
    # else:
    #     # dbug(f"Returning: {out}")
    #     return out
    return out


# ###############################
def list_files(path, pattern="*", return_msgs=False):
    # ###########################
    """
    use: list_files("/tmp")
    prints a list of enumerated basename filenames (sorted by name)
    returns a list of those names
    """
    import glob
    import os

    # names = [os.path.basename(x) for x in glob.glob(f"{path}/{pattern}")]
    names = [os.path.basename(x) for x in glob.glob(path + "/" + pattern)]
    names = sorted(names)
    msgs = []
    for n, item in enumerate(names):
        if not return_msgs:
            # print(f"{n:>2})  {item}")
            print("{:>2})  {}".format(n, item))
        # msgs.append(f"{n:>2})  {item}")
        msgs.append("{:>2})  {}".format(n, item))
    if return_msgs:
        return msgs, names
    return names


# ####################################################
def select_file(path, pattern="*", myprint=False, tst=False, box=False, center=False):
    # ################################################
    """
    use: f = select_file("/home/user","*.txt")
    prints a file listed and asked for a choice
    returns basename of the filename selected
    # >>> select_file("/etc/", pattern="passwd", tst=True)
    #  0)  passwd
    # 'passwd'
    """
    # import glob
    # import os

    # names = [os.path.basename(x) for x in glob.glob(f"{path}/{glob_pattern}")]
    # names = sorted(names)
    # for n, item in enumerate(names):
    #     print(f"{n:>2})  {item}")
    if box:
        msgs = []
        msgs, names = list_files(path, pattern, return_msgs=True)
        if len(msgs) == 0:
            return False
    else:
        names = list_files(path, pattern)
        if len(names) == 0:
            return False
    if box:
        # print("Running boxit(msgs)")
        boxit(msgs, center=center, left_justify=True)
    if tst:  # here only for doctest
        choice = 0
    else:
        prompt = "Please enter your choice: [q=quit] "
        if box:
            rows, columns = os.popen('stty size', 'r').read().split()
            pad_left = " " * ceil((int(columns) - len(prompt)) / 2)
        # else:
        #     pad_lect = ""
        choice = input(pad_left + prompt)
    if choice.lower() == 'q' or choice.lower() == 'quit':
        print("Exiting as requested...")
        sys.exit()
    selected = names[int(choice)]
    if myprint:
        print("-"*40)
        # print(f"Selected: [{selected}]")
        print("Selected: [{}]".format(selected))
        print("-"*40)
        if box:
            msgs.append("-"*40)
            msgs.append("Selected: [" + str(selected) + "]")
            msgs.append("-"*40)
    return selected


# ##################################
def reduce_line(line, max_len, pad):
    # ##############################
    """
    reduce a line to no more than max_len with and no broken words
    then return the reduced_line, and remaining_line
    """
    this_line = ""
    remaining_line = ""
    msg_len = len(line)
    msg = line
    if msg_len + pad > max_len:
        # dbug("msg: " + msg)
        # dbug(f"msg_len [{msg_len}] > max_len [{max_len}] and pad: {pad}")
        words = msg.split(" ")
        word_cnt = len(words)
        cnt = 0
        for word in words:
            # dbug("word: " + word)
            # dbug("len(this_line): " + str(len(this_line)))
            if len(this_line) + pad + len(word) + 4 > max_len:
                remaining_line = " ".join(words[cnt:])
                break
            else:
                cnt += 1
                # dbug("adding word: " + word)
                if len(this_line) == 0:
                    this_line += word
                else:
                    this_line += " " + word
                if cnt > word_cnt:
                    break
        # dbug("this_line: " + this_line)
        # dbug("remaining_line: " + remaining_line)
    return this_line, remaining_line


# ############################################
def boxit(msg, length=80, x=0, y=0, center=False, left_justify=False):
    # ########################################
    """
    this is so ugly but it seems to work
    input: msg
    output:
        +======+
        | msg  |
        | msg  |
        +======+
    >>> boxit("my message", x=2, y=1)
    <BLANKLINE>
    <BLANKLINE>
      +==============================================================================+
      |                                   my message                                 |
      +==============================================================================+

    """
    if center:
        rows, columns = os.popen('stty size', 'r').read().split()
        # x = ceil(int(columns)/2) - ceil(length / 2)
        x = ceil((int(columns) - length)/2)
        # print(f"cols: {columns} length: {length} x: {x}")
    # dbug(f"doing boxit")
    # Now force it to be a list
    if type(msg) == str:
        # dbug(f"This is a string")
        msgs = []
        msgs.append(msg)
    if type(msg) == list:
        msgs = msg
        # dbug(f"msg is a list")
    pad = 2  # min spaces on each side
    max_len = length
    new_msgs = []
    # dbug("msgs: " + str(msgs))
    # max_msg_len = len(max(msgs, key=len))  # this works, for the msgs list, how long is the longest line
    # dbug("max_msg_len: " + str(max_msg_len))
    for msg in msgs:
        # dbug(f"working on msg: {msg}")
        # msg_len = len(msg)
        # dbug("msg_len: " + str(msg_len))
        # max_msg_len = msg_len
        # num_lines = ceil(msg_len/max_len)
        # dbug("num_lines: " + str(num_lines))
        # print("max_len: " + str(max_len) + " msg_len: " + str(msg_len) + " num_lines: " + str(num_lines))
        # print("+" * (max_len + (2 * pad)))
        if len(msg) + pad > max_len:
            keep_reducing = True
            while keep_reducing:
                reduced_line, remaining_line = reduce_line(msg, max_len, pad)
                # dbug("after reduce_line... reduced_line: " + reduced_line +"\nremaining_line: " + remaining_line)
                # dbug("len(remaining_line): " + str(len(remaining_line)))
                new_msgs.append(reduced_line)
                if len(remaining_line) + pad < max_len:
                    # dbug("keep reducing ... len(remaining_line): " + str(len(remaining_line)))
                    keep_reducing = False
                    if len(remaining_line) > 1:
                        new_msgs.append(remaining_line)
                else:
                    msg = remaining_line
        else:
            new_msgs.append(" " + msg)
    print("\n" * y)
    shift_right = " " * x
    # ### top of box ### #
    print(shift_right + "+" + ("=" * (max_len - 2)) + "+")  # top of box
    max_new_msg_len = len(max(msgs, key=len))  # this works
    # dbug("max_new_msg_len: " + str(max_new_msg_len) + " while max_len: " + str(max_len))
    if left_justify:
        # this is what is needed to center the largest line
        l_margin = ceil((max_len - max_new_msg_len - 2) / 2)
    for msg in new_msgs:
        if len(msg) > max_len:
            # this *should* never happen
            sys.exit()
        if not left_justify:
            c_margin = ceil(((max_len - 2) - len(msg)) / 2)  # center_margin
            l_margin = c_margin
        line = "|" + (" " * l_margin) + msg
        line_len = len(line)
        line = line + (" " * (max_len - (line_len + 1))) + "|"
        line = shift_right + line
        print(line)
    # ### bottom of box ### #
    print(shift_right + "+" + ("=" * (max_len - 2)) + "+")  # bottom of box


# ########################
def do_edit(file, lnum=0):
    # ####################
    """  # noqa:
    a quick-n-dirty utility to edit a file
    Initiate edit on a file - with lineno if provided
    """
    if lnum:
        # cmd = f"vim {file} +{str(lnum)}"
        cmd = "vim i" + file + " " + str(lnum)
    else:
        # cmd = f"vim {file}"
        cmd = "vim " + file
    r = subprocess.call(cmd, shell=True)
    # print(f"{cmd}")
    return r


def main(args):
    """
    Description: WIP

    Usage: myprog.py [-hEt] [--dir]

    Options
        -h                Help
        --dir             prints all the functions here and exits
        -v, --version     Prints version

    """
    # print(f"Your code goes here - {dtime} {__file__} {__name__} {args}")
    print("Your code goes here - {} {} {} {}".format(dtime, __file__, __name__, args))
    if args['--dir']:
        import sys
        sys.path.append('/home/geoffm/dev/python/gmodules')
        import gtools
        print("dir(gtools): " + '\n'.join(dir(gtools)))
        print("file: " + __file__)
    if args['-E']:
        do_edit(__file__)
        sys.exit()


if __name__ == '__main__':  # allow this code to run independently or as a module
    args = docopt(main.__doc__, version=" 0.9")
    if args['-t']:
        import doctest
        doctest.testmod(verbose=True)
    main(args)
