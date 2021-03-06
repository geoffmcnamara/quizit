#! /usr/bin/env python3
# vim: set syntax=none nospell:
# ########### #
# Purpose: write out a quiz (can also have it speak out the questions) and get the user response
#    with each question a score is provided
#    a bonus is added for questions that have the ques_type as joke or riddle
# requires:
#     gtools.py
#     a dat_file - see below should be placed in a subdir called ./quiz-files/
#           python3
#           pip3 install pyttsx3 (which requires the espeak libraries - apt install espeak)
# input:
#     You need to write the DAT_FILE and configure it's location below
#     syntax of DAT_FILE:
#     question or statement | answer|answer|answer... | ques_type
#                           | multiple choices (separated with ';' or ',' but be careful here)
#         ques_type can be blank (simple one answer question),
#            multi_choice, # choices must follow note: multi_choice can be multi-choice or even multichoice
#            riddle, joke  # no score - a bonus is given if it is answered correctly
#     Note: you can escape a ";" with "\;" <-- it will not be considered a
#                           delimiter but will still get printed as ";"
#           Also - trailing comments will get ignored, so will blank lines and comment lines
#           If the trailing comment has '[h]' in it then everything after the '[h]' will be treated as a hint...
# Example: DAT_FILE
# Take the number 5 and add 6 and what is the answer?;11 # only accept 11 [h] The acceptible answer is greater than 10 but less than 15
# Now multiply that number by 5 and what is the answer?;55; depends
# There is a house with four walls. All of the walls are facing south. A bear is circling the house. What color is the bear?;white; riddle
# A fool thinks himself to be wise, but a wise man knows himself to be a fool. Who said this? ; 2 ; multi_choice; Abraham Lincoln; William Shakespeare; Benjamin Franklin; John F Kennedy
# What is the speed of light (in miles per second)?; 186,000|186000
# Joke: Why is 6 afraid of 7 ?; because 7, 8, 9!; joke
# ############################
"""
Usage: my_program.py [-hREcf FILE] [ (-e | -e DAT_FILE) ]  [-u USER] [(-r | -r NUM)]

-h --help    show this
-R           to select a DAT_FILE and view it for review
-f DAT_FILE  specify test data file
-E           edit this program
(-e | -e DAT_FILE)  edit the DAT_FILE (looks in the config var QUIZ_FILE_DIR for the DAT_FILE)
             if no DAT_FILE is given then user will be offered a selection of existing dat files
-c           animated celebrate (happens on random successes)
-u USER      specify username
(-r NUM | -r)      randomize questions , optionally NUM times defaults to hitting a the questions once in random order

Notes:
    The DAT_FILE uses a ";" as a delimiter for the fields
    The syntax of the DAT_FILE should be:
    The question ; answer
        or
    The question ; answer ; question_type
        or
    The question ; answer ; multichoice ; choice1; choice2; ...
    ---
    ques_types can be:
        joke : answer is checked and a bonus credit is added to the score if correct
        riddle : answer is checked and a bonus credit is added to the score if correct
        gimmie : answer is *not* checked but a bonus credit is still added to the score if correct
        depends : used to tell this application not to include this question in a random selection (becuase it depends on the previous question and answer)
        multichoice : used for multiple choice questions, choice options must follow it. Choices should be separated by ";"
            You can also use "multiple choice", "multichoice", multi_choice", "multi-choice"
            Also the choices can be separated by "," but this will fail if any of your choices have a comma in them : eg 12,000
    If a line in the DAT_FILE is blank it will be ignored
    If a line in the DAT_FILE begins with "#" it will be ignore and treated as a comment
    If a line ends with a comment indicated with '#' then it will be dropped except....
        anything after '[h]' in a trailing comment will be considered an available hint
    Example DAT_FILE lines:
    # this is strictly a comment
    4 * 6 = ; 24 # this is a trailing comment that has a hint [h] The answer is more than 20 but less than 30
    What is the speed of light; 2 ; multichoice; 186 ft/sec; 186,000 miles/sec; 186 miles/sec # be very careful of the semicolons and the commas [h] The answer is probably the fastest choice
    # an question can contain a semicolon but it must be escaped with '\'
    "Let all your things have their places\\; let each part of your business have its time." represents _______; order # one of Ben Franklin's 13 virtues
"""

# ### imports ### #
import pyttsx3
from datetime import datetime
import time
import subprocess
from time import sleep
# from random import randint
import sys
import os
from os.path import expanduser
# sys.path.append("/home/geoffm/dev/python/gmodules/")
from gtools import boxit, run_cmd, select_file, file_exists, cls, path_to
from math import ceil
import random
import re
try:
    from dbug import dbug
except ImportError:
    pass


# ### globals - config ### #
HOME = expanduser("~")
__version__ = "0.9"
USER = "none"   # this one can be changed with the -u USER argument
FORCE_NAME = True
QUIZ_FILE_DIR = HOME + "/quiz-files"  # this where to nomrally look for
# QUIZ_RPTS_DIR = HOME + "/quiz-files"
# QUIZ_FILE_EXT = ".qiz"
RPT_FILE_EXT = ".rpt"
REPORT_FILE = "quizit" + RPT_FILE_EXT
# only writes out results if -u USER is an argument or if FORCE_NAME==Ture
OUT_FILE = QUIZ_FILE_DIR + "/" + REPORT_FILE
# DAT_FILE = QUIZ_FILE_DIR + '/quiz.qiz'  # this one can be changed with
# the -f DAT_FILE argument
engine = pyttsx3.init()
volume = 0.8
prnt = True
say = False
now = datetime.now()
month = now.strftime("%B")
start = time.time()
multi_choice_types = [
    "multi_choice",
    "multi-choice",
    "multichoice",
    "mutiple choice",
    "mutiple-choice",
    "multiple_choice"]
ques_types = multi_choice_types + ["joke", "depends", "riddle", "gimmie"]


# ### Set pyttsx3 properties _before_ you add things to say #### #
engine.setProperty('rate', 150)    # Speed percent (can go over 100)
engine.setProperty('volume', volume)  # Volume 0-1


# #################################
def printit(msg, center=False, x=0, invisable=False, say=False):
    # #############################
    if say:
        sayit(msg)
    if center:
        rows, columns = os.popen('stty size', 'r').read().split()
        pad_left = ceil(int(columns) / 2) - ceil(len(msg) / 2)
    else:
        pad_left = x
    msg = (" " * pad_left) + msg
    if not invisable:
        print(msg)
    return msg


# #################################
def sayit(msg, say=say, prnt=False):
    # ############################
    """
    will say outloud the msg provided
    optionally you tell it to print or not print or say or not say
    eg:
    >>> msg = "Dave, don't do that"
    >>> sayit(msg, prnt=True)
    Dave, don't do that

    #  or
    >>> sayit(msg, prnt=False)

    Enjoy!
    """
    if prnt:
        print(msg)
    if say:
        engine.say(msg)
        engine.runAndWait()


# ###################
def do_all_voices():
    # ###############
    """
    purpose: only used to display all the possible voices
    Note: this function can be removed/ignored
    """
    # be prepared... there are a lot of them
    engine = pyttsx3.init()
    voices = engine.getProperty('voices')
    for voice in voices:
        print("Voice:")
        print(" - ID: %s" % voice.id)
        print(" - Name: %s" % voice.name)
        print(" - Languages: %s" % voice.languages)
        print(" - Gender: %s" % voice.gender)
        print(" - Age: %s" % voice.age)
        engine.setProperty('voice', voice.id)
        engine.say('The quick brown fox jumped over the lazy dog.')
        engine.runAndWait()


# #############################################
def showpics(d='/home/geoffm/Pictures', num=1):
    # #########################################
    """
    puprose: just for fun - can be used to call chafa against pictures
    to show on a terminal using ascii chars
    Note: this function can be removed/ignored
    used it once in the celebrate function to reward a right answer with some pics
    """
    for _ in range(0, num):
        cmd = 'find ' + d + '/wallpapers/ | shuf -n 1'
        process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            shell=True,
        )
        # encoding='utf8')
        pic = process.stdout.readline()
        subprocess.call('chafa -w 9 -s 30x20 ' + str(pic), shell=True)
        sleep(0.3)


# ########################################################
def request_response(rspns="What is your response? ", hint=""):
    # ####################################################
    """
    purpose: prints out a question and gets a response
    input: rspns prompt - defaults to the above
    returns: ans - user response
    output:
    """
    printit("-" * 40, center=True)
    if len(hint) > 1:
        rspns += " [q=quit, h=hint]? "
    else:
        rspns += " [q=quit]? "
    if rspns == "test only":
        ans = "test only"
        printit("What is your response? ", center=True)
    else:
        # ans = input(rspns)
        try:
            ans = input(printit(rspns, center=True, invisable=True))
        except KeyboardInterrupt:
            sys.exit()
    # print("ans: " + ans)
    if ans.lower() == "q" or ans.lower() == "quit":
        sys.exit()
    if ans.lower() == 'h':
        printit("Hint:" + hint, center=True)
        ans = request_response()
    # else:
    #     print("ans: [" + ans + "] which apparently is != [q]")
    printit("-" * 40, center=True)
    # filter the answer (ans) from the user to lower case and no quotes
    ans = str(ans.lower().strip().replace('"', ''))
    return ans


# ################################
def check_answer(ans, right_ans):
    # ############################
    """
    purpose: checks ans against right_ans - forces everything to lower case and strips out double quote marks and surrounding spaces
        input: ans, right_ans - both are required
    """
    success = False
    # filter the answer from the dat file (elems[1]) to lower case and strip
    # off spaces and double quote marks
    right_ans = str(right_ans.strip().lower().replace('"', ''))
    # first see if right answer has more than one pssibility
    if '|' in right_ans:
        ans_l = []
        ans_l = right_ans.replace(" ", '').split('|')
        right_ans = right_ans.replace('|', ' or ')
        if ans.strip() in ans_l:
            success = True
    if ans.strip() == "*":
        success = True
    if ans == right_ans:
        success = True
    printit(
        "Expected answer is: [" +
        right_ans +
        "] your answer is: [" +
        str(ans) +
        "]",
        say=True,
        center=True)
    return success  # either True or False


# ######################
def multi_choice(elems):
    # ##################
    """
    purpose: displays all the multiple choices with item/element numbers, seeks user response and returns it
    input: elems # which is a [list]
    returns: ans # integer
    """
    print("\n")
    num = 1
    choices = []
    if len(elems) > 4:
        # here we assume choices have been split using ';'
        for item in elems[3:]:
            choices.append(str(num) + ".) " + item.strip())
            # printit(str(num) + " " + item, say=True, center=True)
            num += 1
    else:
        items = elems[3].split(",")
        for item in items:
            choices.append(str(num) + ".) " + item.strip())
            num += 1
    rows, columns = os.popen('stty size', 'r').read().split()
    max_choice_len = len(max(choices, key=len))
    for choice in choices:
        printit(choice, x=ceil((int(columns) - max_choice_len) / 2))
    print("\n")
    return  # ans


# ##############
def celebrate():
    # ##########
    """
    purpose: informs user of a right anser
    Note: this could be enhanced to reward the user with whatever...
      tells the user using sayit()
      and prints it in boxit()
    input: none
    returns: nothing
    TODO: add a way to use a file for possible cmds to run
        then randomly select one
        there should be a way to set the frequency of running a celebrate animation
        this is sound like a conf file for celebrate
        freq: 1:3
        cmd: sl
        cmd: figlet "You are awesome"
    """
    begin_time = time.time()
    celebrate_file = QUIZ_FILE_DIR + "/" + "quiz-celebrate.cfg"
    if args['-c']:
        if file_exists(celebrate_file):
            cf_lines = open(celebrate_file).read().splitlines()
            cf_lines = [l for l in cf_lines if not l.startswith("#")]
            line = random.choice(cf_lines)
            if bool(re.search('[a-zA-Z]', line)
                    ):  # blank lines will get skipped
                run_cmd(line)
    print("\n")
    msg = "You did great!"
    sayit(msg, prnt=False)
    boxit(msg, center=True)
    end_time = time.time()
    celebrate_time = end_time - begin_time
    return celebrate_time


# ###############
def disappoint():
    # ###########
    """
    purpose: just tells the user that the ans was not correct
       kind of the opposite of celebrate
       Note: this is kind of useless but might be enhanced later to encourage the user to do better in some way...
    """
    sayit("Please try again...")
    # print("=" * 40)


# #####################
def chk_syntax(lines):
    # ################
    """
    quick check of syntax on lines
    """
    for line in lines:
        line = line.strip()
        # purify the line - if blank, ignore, and strip off any comments
        # this ignores trailing comments - turns the line blank if it is all a
        # comment line
        line = line.partition('#')[0]
        if not line.strip():  # if the line is empty.. empty string is a False value
            # dbug("found a blank line")
            continue
        semicolons = re.findall(r"(?<!\\);", line)
        # dbug("len(semicolons): " + str(len(semicolons))
        # semicolon_cnt = sum(map(lambda x : 1 if ';' in x else 0, line))
        semicolon_cnt = len(semicolons)
        if semicolon_cnt < 1:
            print(
                "Syntax of line appears incorrect with no separator [;] found: \n" +
                line +
                "\n")
            return False
        # elems = line.split(";")
        elems = re.split(r'(?<!\\);', line)
        # dbug("elems: " + str(elems))
        # ques = elems[0].strip()
        ans = elems[1].strip()
        if ans == "":
            print("Problem with provided answer [" + str(ans) + "]")
            print("This line has a problem:\n" + line)
            print(
                "Perhaps it is a problem with provided answer [" + str(ans) + "]")
            return False
        if semicolon_cnt > 1:
            ques_type = elems[2].strip()
            if ques_type not in ques_types:
                print("Question does not appear to be correct: \n" + line + "\n")
                return False
            if "multi" in ques_type:
                if semicolon_cnt < 3:
                    print(
                        "Not enough choices for ques_type [" + ques_type + "]")
                    return False
    return True


# #########
def main():
    # #####
    """
    everything starts here
    """
    # handleOPTS should already have been completed
    cls()
    # ### Date and Time ### #
    msgs = []
    remove_time = 0
    dtime = datetime.now().strftime("%Y%m%y-%H%M")
    msgs.append("The date is,... " + month + " " +
                str(now.day) + " " + str(now.year) + ", ... ")
    msgs.append("And the time is: " + str(now.hour) +
                " hours and " + str(now.minute) + " minutes")
    for msg in msgs:
        sayit(msg, say=False)
    # ### DAT_FILE ### #
    global QUIZ_FILE_DIR
    global DAT_FILE
    # if no quiz_file_dir then create it
    if not file_exists(QUIZ_FILE_DIR, type="dir"):
        print(
            "No quiz file dir [" +
            QUIZ_FILE_DIR +
            "] found... creating the directory.")
        os.mkdir(QUIZ_FILE_DIR)
    # if no DAT_FILE given in args or the one given does't exists then select
    # one...
    try:
        DAT_FILE
    except BaseException:
        printit("Listing of files in [" + QUIZ_FILE_DIR + "]", center=True)
        dat_file = select_file(
            QUIZ_FILE_DIR,
            pattern="*.dat",
            box=True,
            center=True)
        if not dat_file:
            print("No matching files found... ")
            print(
                "Please create a quiz file first - preferably in the [" +
                QUIZ_FILE_DIR +
                "] directory")
            sys.exit()
        else:
            DAT_FILE = QUIZ_FILE_DIR + "/" + dat_file
    print("\n" * 2)
    if not file_exists(DAT_FILE) or DAT_FILE == "none":  # or not args['-f']:
        print("Did not find [" + DAT_FILE + "]")
        dat_file = select_file(QUIZ_FILE_DIR, pattern="*.dat")
        if not dat_file:
            print("No matching files found... ")
            # DAT_FILE = "none"
        else:
            DAT_FILE = QUIZ_FILE_DIR + "/" + dat_file
    # now lets try opening it and reading in the lines - otherwise ask about
    # editing one
    try:
        with open(DAT_FILE) as file:
            lines = file.readlines()
            lines = [l for l in lines if not l.startswith("#")]
            # quickly check syntax of lines
            # if args['-r']:
            #     lines = random.shuffle(lines)
    except Exception as e:
        print("Exception: " + str(e))
        try:
            ans = input("Do you want to create and edit it? [y/n] ")
        except KeyboardInterrupt:
            sys.exit()
        if ans.lower() == "yes" or ans.lower() == "y":
            do_edit(DAT_FILE)
        else:
            # print("ans: " + ans)
            print("... no usable quiz file declared ... exiting...")
            sys.exit()
    if not chk_syntax(lines):
        # print("Syntax of file: [" + DAT_FILE + "] failed... please investigate.")
        ans = input("Do you want to edit this file [" + DAT_FILE + "] (y|n)? ")
        if "y" in ans.lower():
            do_edit(DAT_FILE)
        sys.exit()
    # ### USER ### #
    global USER
    if USER == "none" and FORCE_NAME:
        # print("\n"*1)
        try:
            # USER = input("Please enter your name: ")
            msg = "Please enter your name: "
            USER = input(printit(msg, center=True, invisable=True))
        except KeyboardInterrupt:
            sys.exit()
        print("\n" * 1)
    # ### processall the lines in the DAT_FILE ### #
    BASENAME_DAT_FILE = os.path.basename(DAT_FILE)
    title = "Quizit [version: " + __version__ + "]: " + BASENAME_DAT_FILE
    if USER != "none":
        title += " USER: " + USER
    # ### read in the DAT_FILE ### #
    ques_cnt = 0
    scored_ques_cnt = 0
    score = 0
    # first clear the screen
    cls()
    boxit(title, center=True)
    # dbug("just did boxit(title, center=True)")
    # ### begin loop of lines in DAT_FILE ### #
    for line in lines:
        hint = ""
        if "[h]" in line.partition('#')[2]:
            hint = line.partition('[h]')[2]
        # this ignores trailing comments - turns the line blank if it is all a
        # comment line
        line = line.partition('#')[0]
        if not line.strip():  # if the line is empty.. empty string is a False value
            # dbug("found a blank line")
            continue
        ques_type = ""
        ques_cnt += 1
        scored_ques_cnt += 1  # this will get decremented with non-scored questions
        # elems = line.split(";")
        elems = re.split(r'(?<!\\);', line)
        if len(elems) > 2:
            ques_type = str(elems[2].strip().lower())
        if args['-r']:
            line = random.choice(lines)
            if ques_type == "depends":  # or line.startswith("#"):
                # print("debug: ques_type: " + ques_type)
                continue
            if args['NUM'] is not None:
                if ques_cnt >= int(args['NUM']):
                    break
            # elems = line.split(";")
            elems = re.split(r'(?<!\\);', line)
        # ques_cnt += 1
        # dbug("here now")
        # print("\n" * 2 )
        msgs = []
        msgs.append("Question: " + str(ques_cnt))
        ques = elems[0].replace("\\;", ";")
        msgs.append("-" * 20)
        msgs.append(ques)
        try:
            right_answer = elems[1]
        except Exception as e:
            dbug("All elems: " + str(elems) + "e: " + str(e))
            sys.exit()
        boxit(msgs, center=True, y=1)
        if len(elems) > 2:
            ques_type = str(elems[2].strip().lower())
            if ques_type in multi_choice_types:
                multi_choice(elems)  # lists all the choices
            elif ques_type == "gimmie":
                # the user will be out right given a point in the score as a bonus
                #     score += 1
                printit("-" * 40, center=True)
                printit(
                    "Your answer will be scored as a bonus ... !",
                    say=True,
                    center=True)
                scored_ques_cnt -= 1
            elif ques_type == "joke" or ques_type == "riddle":
                # make this a bonus question
                printit("-" * 40, center=True)
                printit(
                    "Your answer will be scored as a bonus ... !",
                    say=True,
                    center=True)
                scored_ques_cnt -= 1
            else:
                if ques_type not in ques_types:
                    printit(
                        "Possible error in DAT_FILE: Unknown question type: " +
                        ques_type)
                # ques_cnt += 1
        ans = request_response(hint=hint)
        if check_answer(ans, right_answer) or ques_type == "gimmie":
            remove_time += celebrate()
            score += 1
        else:
            disappoint()
        pcnt = str(round(score * 100 / ques_cnt, 2))
        print("\n" * 1)
        printit(
            "Score: " +
            str(score) +
            " out of " +
            str(scored_ques_cnt) +
            " scored questions.",
            center=True)
        printit("Your percent correct = " +
                str(round(score * 100 / scored_ques_cnt, 2)) + "%", center=True)
    printit("=" * 40, center=True)
    end = time.time()
    elapsed_time = (end - start) - remove_time
    msg = "The elapsed time: {:0.2f} seconds (minus celebration time)".format(
        elapsed_time)
    printit(msg, center=True, say=True)
    if USER != "none":  # This should always be the case if FORCE_USER is true
        # assuming QUIZ_FILE_DIR has been created at the beginning of main()
        # msg = f"User: {USER:15}, Dtime: {dtime}, DatFile: {BASENAME_DAT_FILE:25}, Score: {pcnt:>6}%, Elapsed_time: {end-start:0.2f}, Num ques: {ques_cnt:6}"
        msg = "User: {:15}, Dtime: {}, DatFile: {:25}, Score: {:>6}%, Elapsed_time: {:0.2f}, Num ques: {:6}".format(
            USER, dtime, BASENAME_DAT_FILE, pcnt, end - start, ques_cnt)
        global OUT_FILE
        with open(OUT_FILE, 'a') as f:
            f.write(msg + "\n")
        print("\n")
        printit("Wrote results into: " + OUT_FILE, say=False, center=True)
        print("\n" * 2)
    # EOB #


# ########################
def do_edit(file, lnum=0):
    # ####################
    """  # noqa:
    a quick-n-dirty utility to edit a file
    Initiate edit on a file - with lineno if provided
    """
    if lnum:
        # cmd = f"vim {file} +{str(lnum)}"
        cmd = "vim " + file + " " + str(lnum)
    else:
        # cmd = f"vim {file}"
        cmd = "vim " + file
    r = subprocess.call(cmd, shell=True)
    return r


# ###################
def handleOPTS(args):
    # ###############
    """
    purpose: handles options
    """
    # print("args: " + str(args))
    if args['-E']:
        do_edit(__file__)
        sys.exit()
    if args['-e']:
        if args['DAT_FILE'] is not None:
            do_edit(QUIZ_FILE_DIR + "/" + args['DAT_FILE'])
        else:
            dat_file = select_file(
                QUIZ_FILE_DIR,
                pattern="*.dat",
                box=True,
                center=True)
            do_edit(QUIZ_FILE_DIR + "/" + dat_file)
        sys.exit()
    if args['-R']:
        dat_file = select_file(
            QUIZ_FILE_DIR,
            pattern="*.dat",
            box=True,
            center=True)
        rows, columns = os.popen('stty size', 'r').read().split()
        rows = int(rows)
        cols = int(columns)
        #  geom = COL, ROWS, x, y)
        geom = str(cols) + "x" + str(rows) + "+30+30"
        cmd = "'less " + QUIZ_FILE_DIR + "/" + dat_file + "'"
        # this will open an xterm as big as the current one with top left
        # screen location 30+30
        term_cmds = {
            "tilix": " --geometry=" + geom + " -e " + cmd,
            "xterm": " -fa 'monospace' -fs 14 -g " + geom + ' -e ' + cmd,
            "terminator": " -e " + cmd + " --geometry=1200x800+30+30",
            "gnome-terminal": " --geometry=" + geom + " -e " + cmd,
            "rxvt-unicode": " --geometry=" + geom + " -e " + cmd,
            "eterm": " --geometry=" + geom + " -e " + cmd,
            "Xfce4-terminal": " --geometry=" + geom + " -e " + cmd,
            "termite": " --geometry=" + geom + " -e " + cmd,
        }
        print("=" * 40)
        for k, v in term_cmds.items():
            if path_to(k):
                full_path = path_to(k)
                full_cmd = full_path + v
                print("Running: " + full_cmd)
                run_cmd(full_cmd)
                break  # found a working term --- done!
        print("=" * 40)
        sys.exit()
    if args['-f']:
        global DAT_FILE
        DAT_FILE = args['-f']
        # print("Setting DAT_FILE to " + DAT_FILE)
    if args['-u']:
        global USER
        USER = args['-u']
        # print("USER: " + USER)


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(__doc__)  # , version=__file__ + "0.9")
    handleOPTS(args)
    main()
