#! /usr/bin/env python3
# vim: set nospell:
# ########### #
# Purpose: write out a quiz (can also have it speak out the questions) and get the user response  # noqa:
#    with each question a score is provided
#    a bonus is added for questions that have the ques_type as joke or riddle
# requires:
#     gtools.py
#     dbug.py
#     a dat_file - see below should be placed in a subdir called ./quiz-files/
#           python3
#           pip3 install pyttsx3 (which requires the espeak libraries - apt install espeak)  # noqa:
# input:
#     You need to write the DAT_FILE and configure it's location below
# ############################

"""
-h --help    show this
-R           to select a DAT_FILE and view it for review - like Reviewing notes before a test. Use "q" to quit.
-f DAT_FILE  specify test data file
-E           edit this program
(-e | -e DAT_FILE)  edit the DAT_FILE (looks in the config var QUIZ_FILE_DIR for the DAT_FILE)
             if no DAT_FILE is given then user will be offered a selection of existing dat files
-c           animated celebrate (happens on random successes)
-C <category>] to filter quizes to one category
-u USER      specify username
(-r NUM | -r)      randomize questions , optionally NUM times defaults to hitting a the questions once in random order
-nr NUM      non-random with only NUM questions

Notes:
    Everything is case insensitive. Everything is converted and  compared with lower case.
    The DAT_FILE uses a ";" as a delimiter for the fields, "|" is used for "or", "&" is used for "and"
    The syntax of the DAT_FILE should be:
    The question ; answer
    The question ; answer | answer | answer ...
    The question ; answer & answer & answer ...
    The question ; answer ; question_type
    The question ; answer ; multichoice ; choice1; choice2; ...
    The statement; info
    ---
    If the second field = "info" then the statment is only presented as just that... information.
    ques_types can be:
        joke : answer is checked and a bonus credit is added to the score if correct
        riddle : answer is checked and a bonus credit is added to the score if correct
        gimmie : answer is *not* checked but a bonus credit is still added to the score if correct
        depends : used to tell this application not to include this question in a random selection (because it depends on the previous question and answer)
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
    # a question can contain a semicolon but it must be escaped with '\'
    "Let all your things have their places\\; let each part of your business have its time." represents _______; order # one of Ben Franklin's 13 virtues
    True or Flase: Humans have two legs; true | t
    What are the 3 types of greek columns? ; doric & ionic & corinthian  # [h] separate your three answers by commas
"""

# ### IMPORTS ### #

# try:
#     TTS = True
#     import pyttsx3
# except Excception as e:
#     TTS = False
#     dbug(f"Error: {e}")
from datetime import datetime
import time
import subprocess
from time import sleep
# from random import randint
import sys
import os
from os.path import expanduser
# from math import ceil
import random
import re
import pandas as pd
import readline
sys.path.append("/home/geoffm/dev/python/gmodules/")
from gtools import (dbug, docvars, run_cmd, file_exists, cls, path_to, do_list, printit, select_file,
                    cinput, do_logo, do_close, rootname, do_edit, has_alnum, askYN,
                    gselect, gclr, sub_color, list_files, gcolumnize, boxed, gcolumnize, isnumber,
                    purify_file, get_random_line, splitit, gblock, bool_val, kvarg_val)


# ### GLOBALS - CONFIG ### #
dtime = datetime.now().strftime("%Y%m%d-%H%M")
HOME = expanduser("~")
__version__ = "0.9"
USER = "none"  # this one can be changed with the -u USER argument
FORCE_NAME = True
QUIZ_FILE_DIR = HOME + "/quiz-files"  # this where to normally look
RPT_FILE_EXT = ".rpt"
REPORT_FILE = "quizit" + RPT_FILE_EXT
OUT_FILE = QUIZ_FILE_DIR + "/" + REPORT_FILE
CSV_FILE = QUIZ_FILE_DIR + "/" + "quizit.csv"
DAT_FILE = ""
PIC_DIR = '/home/geoffm/Pictures'  # used for "celebration" if desired
prnt = True
say = False
now = datetime.now()
month = now.strftime("%B")
start = time.time()
multi_choice_types = ["multi_choice", "multi-choice", "multichoice", "mutiple choice", "mutiple-choice", "multiple_choice", "multi"]
ques_types = multi_choice_types + ["joke", "depends", "riddle", "gimmie"]
f_ratio = 70
# ### Set pyttsx3 properties _before_ you add things to say #### #
# engine.setProperty('rate', 150)  # Speed percent (can go over 100)
# engine.setProperty('volume', volume)  # Volume 0-1

# ### GLOBALS ### #
DFMT = "%Y%m%d-%H%M"
DTIME = datetime.now().strftime(DFMT)
SYNTAX_MSG = """
--------------------------------------------------------------------
# ### The syntax can be a challenge... here are some examples: ### #
--------------------------------------------------------------------
True or False Ben Fanklin was a founding father.; T
Who wrote "Hamlet"?; 3; multi; Charles Babage, Homer, Shakespeare, Ben Franklin
True or False.. this question has a hint.; T # [h] This is a hint available to the user if they type "h"
Please type what the Spanish word "gato" means in English: cat
This question has additional info True or False; T # [i] When "[i]" is in the comment, what comes after it will be presented after the user attempts to answer
This question allows multiple answers; 1|2; this answer will be accepted, this one will also be excepted, this one will not be accepted
5 + 4 =; 9|nine   # allows 9 or nine as an answer
How far can a fox run into the woods?; halfway| half way; riddle  # user will get a bonus point if they get it right
Gimmie: Why is 6 afraid of 7 ?; because 7, 8, 9; gimmie # any answer will be accepted....
Joke: Why is 6 afraid of 7 ?; because 7, 8, 9; joke # not included in the score
--------------------------------------------------------------------
"""

# ### FUNCTIONS ### #


def tst(arg1="unknown1", arg2="unknown2"):
    """
    This is just an example testing function. This example shows how you can quickly test whatever you want (any function) while you are still editing a file
    You can completely remove this function
        or rename it
        or call another function within it
        or leave it as an example.
        It demonstrates the use of the -T argument.
    """
    msg = """
    This is a test function and can be called while editing in vim with...  :! ./% -T tst
    or  :! ./% -T tst \"This is farg1\"
    or  :! ./% -T tst \"This is farg1\"  \"This is farg2\"
    Note: the args here are separated by a space.
    """
    dbug(msg, 'boxed', 'centered', box_color="yellow! on grey80")
    dbug(arg1)
    dbug(arg2)



def get_qa(contents, delimiter=" "):
    """
    purpose:
    input:
    returns:
    """
    # dbug(delimiter)
    rand_line = get_random_line(contents)
    # dbug(rand_line)
    # phrases = rand_line.split(delimiter)
    # phrases = rand_line.rpartition(delimiter)
    # phrases = re.split('["|\'] +- +', rand_line)
    # phrases = re.split(delimiter, rand_line)
    phrases = splitit(rand_line, delimiter)
    # dbug(phrases)
    try:
        question = phrases[0]
        question = question.lstrip('"')
        question = question.lstrip("'")
        answer = phrases[1]
    except Exception as Error:
        dbug(Error)
        dbug(f"\nrand_line: [{rand_line}]\nphrases: {phrases}")
    # dbug(f"returning question: {question} answer: {answer}", 'ask')
    return question, answer


def playloop(mode):
    """--== Init ==--"""
    shuffle_b = False
    if mode == 'vocab':
        # voc_file
        # voc_file = "Vocabulary_list.csv"
        voc_file = QUIZ_FILE_DIR + "/Vocabulary_list.csv"
        filename = voc_file
        delimiter = ","
    if mode == 'quotes':
        # shuffle_b = False
        if args['--shuffle']:
            shuffle_b = True
        # dbug(shuffle_b, 'ask')
        # quote_file
        # quote_file = "~/data/lines.dat"
        quote_file = QUIZ_FILE_DIR + "/lines.dat"
        filename = quote_file
        delimiter = r"[\"|\'] +[-–—―] +"  # amazingly all those dashes are different symbols...
    """--== SEP_LINE ==--"""
    max_deflectors = 4
    deflectors = []
    """--== SEP_LINE ==--"""
    filename = os.path.expanduser(filename)
    contents = purify_file(filename)
    """--== SEP_LINE ==--"""
    repeat_flag = False
    while True:
        cls()
        print("\n"*4)
        if not repeat_flag:
            # get a new question
            deflectors = []
            question, answer = get_qa(contents, delimiter)
            # dbug(question)
            # dbug(answer)
            deflectors.append(answer)
            # dbug(deflectors, 'ask')
        while len(deflectors) < max_deflectors:
            # dbug(deflectors)
            # word, definition = get_def_and_pop(wd_list, word_dict)
            # choice_list.append(definition)
            deflector_question, deflector_answer = get_qa(contents, delimiter)
            """--== avoid repeat question of repeat deflector ==--"""
            if deflector_question == question or deflector_answer in deflectors:
                # dbug(f"found {deflector_answer} in deflectors: {deflectors} question: {question}")
                continue
            else:
                # dbug(f"not found {deflector_answer} deflectors: {deflectors} question: {question}")
                deflectors.append(deflector_answer)
        # random.shuffle(choice_list)
        random.shuffle(deflectors)
        # print(word)
        """--== print question ==--"""
        if shuffle_b:
            move_on = False
            X = 4
            orig_words = question.split()
            while not move_on:
                words = question.split()
                # dbug(orig_words)
                X += 1
                quote_start = " ".join(orig_words[:X])
                remaining_words = words[X:]
                printit(quote_start + "......", 'boxed', 'centered', title=f"First {X} words of quote:")
                # askYN()
                random.shuffle(remaining_words)
                dbug(remaining_words)
                # dbug(words)
                msg = []
                msg.append(", ".join(remaining_words))
                if len(msg) == 0:
                    continue
                printit(msg, 'boxed', 'centered', title="From this list rearrage the words to recreate the proper quote.")
                printit("Proper quote:", 'centered')
                question_len = len(question)
                # dbug(question_len)
                shift = -(question_len // 2) + 10
                # dbug(shift)
                proper_quote = cinput("Your answer: ", shift=shift, dflt=quote_start)
                if proper_quote == " ".join(orig_words):
                    print("\n" * 3)
                    printit("[green!]Correct![/]\n", 'boxed', 'centered', box_color="white! on black")
                    print("\n" * 3)
                    move_on = True
                else:
                    # dbug("not so much")
                    printit(" ".join(orig_words), 'boxed', 'centered', title="Proper quote")
                    if askYN("Do you want to move on?", "y", 'centered'):
                        move_on = True
        else:
            printit(question, 'boxed', 'centered', txt_center=99)
        # print("---------------")
        """--== print deflectors and ask user ==--"""
        choice = gselect(deflectors, 'centered', rtrn="k", footer="[e,q]")
        if choice in ('e'):
            printit(msg)
            askYN("Continue?")
            do_edit(filename)
            do_close()
        if choice in ("q", "Q", ""):
            do_close()
        if isnumber(choice):
            choice = int(choice)
        # dbug(choice)
        """--== provide feedback ==--"""
        if len(additional_info) > 1:
            printit(additional_info, 'boxed', 'centered', footer=dbug('here'))
        if deflectors[choice-1] == answer:
            # correct
            # print("Correct!\n")
            print("\n" * 3)
            printit("[green!]Correct![/]\n", 'boxed', 'centered', box_color="white! on black")
            print("\n" * 3)
            askYN("", 'centered')
            repeat_flag = False
        elif choice == 0:
            # exit
            exit(0)
        else:
            # incorrect
            # print("Incorrect")
            print("\n" * 3)
            printit("[red!]Incorrect![/]", 'boxed', 'centered', box_color="white! on black")
            print("\n" * 3)
            if askYN("Try again?", "y", 'centered'):
                repeat_flag = True
            else:
                printit(f"Correct answer: {answer}", 'boxed', 'centered', box_color="white! on black")
                askYN("Continue?", 'centered')


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
def showpics(pic_dir, num=1):
    # #########################################
    """   # noqa:
    puprose: just for fun - can be used to call chafa against pictures
    to show on a terminal using ascii chars
    Note: this function can be removed/ignored
    used it once in the celebrate function to reward a right answer with some pics
    """
    global PIC_DIR
    pic_dir = PIC_DIR
    for _ in range(0, num):
        # TODO This needs to be pythonized
        cmd = 'find ' + pic_dir + '/wallpapers/ | shuf -n 1'
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
    # print("rspns: " + rspns)
    # printit("-" * 40, center=True)
    printit("\n"*2)
    if len(hint) > 1:
        rspns += " [q=quit, h=hint]? "
    else:
        rspns += " [q=quit]? "
    # ### this is just for testing ### #
    if rspns == "test only":
        ans = "test only"
        # printit("What is your response? ", center=True)
        printit("What is your response? ", center=True)
    else:
        # ans = input(rspns)
        try:
            ans = input(printit(rspns, center=True, prnt=False, rtrn_type="str"))
        except KeyboardInterrupt:
            sys.exit()
    # print("ans: " + ans)
    # dbug(ans)
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
    # ### END def request_response(rspns="What is your response? ", hint=""): ### #


# ################################
def check_answer(ans, right_ans):
    # ############################
    """   # noqa:
    purpose: checks ans against right_ans - forces everything to lower case and strips out double quote marks and surrounding spaces
        input: ans, right_ans - both are required
    """
    global f_ratio
    #from rich.console import Console
    #console = Console
    global f_ratio
    # f_ratio = 60  # TODO make this a GLOBAL
    if args['-F']:
        from thefuzz import fuzz
        if args['ratio']:
            f_ratio = args['ratio']
        dbug(f"User has Fuzzy Logic invoked and f_ratio: {f_ratio}.")
    fuzz_msg = ""
    success = False
    # dbug(f"ans: {ans} right_ans: {right_ans}")
    # filter the answer from the dat file (elems[1]) to lower case and strip
    # off spaces and double quote marks
    # dbug(f"ans: {ans} right_ans: {right_ans}")
    # remove whitespace from beginning and the end
    right_ans = str(right_ans.strip().lower().replace('"', ''))
    # dbug(f"right_ans: {right_ans}")
    # first see if right answer has more than one pssibility
    if '|' in right_ans:
        # dbug(f"found | in right_ans: {right_ans}")
        ans_l = []  # ans (list)
        ans_l = right_ans.strip().split('|')
        # dbug(f"ans_l: {ans_l}")
        # ans_l = right_ans.replace(" ", '').split('|')
        # dbug(f"ans_l: {ans_l}")
        right_ans = right_ans.replace('|', ' or ')
        # dbug(f"ans: {ans} ans_l: {ans_l} ")
        # dbug(f"ans_l: {ans_l}")
        my_ans_l = []
        for i in ans_l:
            # dbug(f"i: {i}")
            # item = i.lstrip(" ")
            #item = item.rstrip(" ")
            item = i.strip(" ")
            my_ans_l.append(item)
        ans_l = my_ans_l
        # dbug(f"ans_l: {ans_l} my_ans_l: {my_ans_l}")
        if ans.strip() in ans_l:
            # dbug(f"Success... ans: {ans}")
            success = True
        if args['-F']:
            for i in ans_l:
                #ans = ans.strip()
                #elem = i.strip()
                fuzz_ratio = fuzz.ratio(ans, i)
                dbug(f"fuzz_ratio: {fuzz_ratio} Your answer: ={ans}= Possible i: ={i}=")
                # ans = "namea"
                i = "namea"
                fuzz_ratio = fuzz.ratio(ans, i)
                print(f"fuzz_ratio: {fuzz_ratio} Your answer: ={ans}= Possible i: ={i}=")
                # dbug(f"fuzz_ratio: {fuzz_ratio} f_ratio: {f_ratio}")
                if fuzz_ratio >= f_ratio:
                    fuzz_msg = "However, you got close enough to call this a success ..."
                    success = True
                    break
    if '&' in right_ans:
        ans_l = []
        ans_l = right_ans.replace(" ", '').split('&')
        # if "," in ans:
        #     answers = [x.strip() for x in ans.split(',')]
        #     # dbug(f"answers: {answers} ans_l: {ans_l}")
        answers = [x.strip() for x in ans.split(',')]
        # dbug(f"ans_l: {ans_l} ")
        # dbug(f"answers: {answers} ans_l: {ans_l} ")
        need_cnt = len(answers)
        cnt = 0
        for a in answers:
            if a in ans_l:
                printit(f"Your answer [{a}] is correct!", center=True)
                cnt += 1
        # printit(f"Need {need_cnt} answers. Found {cnt} correct answers", center=True) noqa:  # noqa:
        if cnt >= need_cnt:
            success = True
    if ans.strip() == "*":
        success = True
    if ans == right_ans:
        fuzz_ratio = 100
        success = True
        # dbug(f"fuzz_ratio: {fuzz_ratio} f_ratio: {f_ratio} ans: {ans} ")
    printit(f"Expected answer is: " + sub_color('bold yellow') + f"{right_ans}" + sub_color('reset') + " your answer is: " + sub_color('bold yellow') + ans + sub_color('reset'), center=True)
    # if args['-F']:
    #     fuzz_ratio = fuzz.ratio(ans, right_ans)
    #     if fuzz_ratio >= f_ratio:
    #         fuzz_msg = "[bold yellow]However[/],you got close enough to call this a success ...!!!"
    #         success = True
    if fuzz_msg != "" and fuzz_ratio < 100:
        # dbug(fuzz_ratio)
        printit(fuzz_msg, 'center')
    return success  # either True or False


# ############
def blank_choice(elems):
    # ##########
    """
    WIP
    not used????
    """
    dbug("Does anyone use this?")
    # dbug(f"func: blank_choice({elems})")
    ans = input("What is your response: ")
    if "," in ans:
        answers = [x.strip() for x in ans.split(',')]
        dbug(f"answers: {answers}")
    dbug(f"elems: {elems}")
    dbug(f"elems[1]: {elems[1]}")
    if "|" in elems[1]:
        poss_ans = elems[1].split("|")
        dbug(f"poss_ans: {poss_ans}")
        for answer in answers:
            if answer in poss_ans:
                print(f"Correct word: {answer} in poss_ans: {poss_ans}")
            else:
                print(f"Sorry answer: {answer} is incorrect")
    dbug(f"ans: {ans}")


# ######################
def multi_choice(elems, myprint=False):
    # ##################
    """  # noqa:
    purpose: displays all the multiple choices with item/element numbers, seeks user response and returns it
    input: elems # which is a [list]
    returns: ans # integer
    """
    # dbug(f"elems: {elems}")
    print("\n")
    num = 1
    choices = []
    if len(elems) > 4:
        # here we assume choices have been split using ';'
        for item in elems[3:]:
            choices.append(str(num) + ".) " + item.strip())
            # printit(str(num) + " " + item, say=say, center=True)
            num += 1
    else:
        items = elems[3].split(",")
        for item in items:
            choices.append(str(num) + ".) " + item.strip())
            num += 1
    rows, columns = os.popen('stty size', 'r').read().split()
    # max_choice_len = len(max(choices, key=len))
    for choice in choices:
        # dbug(f"choice: {choice}")
        choice = choice.partition('#')[0]  # if a line has a comment just get what is before it  # noqa:
        # printit(choice, x=ceil((int(columns) - max_choice_len) / 2))
    print("\n")
    return choices  # ans


# ###############
#def askYN(msg):  # noqa:
#    # ###########
#    """
#    WIP
#    """
#    r = input(msg + " ")
#    if r.lower() == "y or r.lower()" == "yes":
#        return True
#    else:
#        return False


def rlinput(prompt, prefill=''):
    readline.set_startup_hook(lambda: readline.insert_text(prefill))
    try:
        return input(prompt)
    finally:
        readline.set_startup_hook()


# ##############
def celebrate(celebrate_file, tst=False):
    # ##########
    """  # noqa:
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
    # dbug(f"celebrate_file: {celebrate_file} tst: {tst}")
    begin_time = time.time()
    # celebrate_file = QUIZ_FILE_DIR + "/" + "quiz-celebrate.cfg"
    if tst:
        if file_exists(celebrate_file):
            cf_lines = open(celebrate_file).read().splitlines()
        else:
            dbug(f"Failed to find file: {celebrate_file}")
            sys.exit()
        # for line in fileinput.input(celebrate_file, inplace=True):
        #    if not line.startswith("#"):
        #       cf_lines.append =  line
        #
        cf_lines = [line for line in cf_lines if not line.startswith("#")]
        for line in cf_lines:
            dbug("Testing line this command line: \n\n" + line + "\n\n")
            r = run_cmd(line)
            if askYN(f"Did this line: {line} execute properly?", "y", quit=True):
                dbug("OK")
            else:
                dbug("Failed!")
                do_edit(celebrate_file)
                # import fileinput
                # for line in fileinput.input("test.txt", inplace=True):
                #    print "%d: %s" % (fileinput.filelineno(), line),
            # if not r:
            #     dbug("*** Please investigate this failed command line:\n" + line)  # noqa:
        return
    if args['-c'] or tst:
        if file_exists(celebrate_file):
            cf_lines = open(celebrate_file).read().splitlines()
            cf_lines = [line for line in cf_lines if not line.startswith("#")]
            line = random.choice(cf_lines)
            if bool(re.search('[a-zA-Z]', line)):  # blank lines will get skipped  # noqa:
                run_cmd(line)
    print("\n")
    msg = sub_color('blink bold yellow') + "Congratulations!" + sub_color('reset') +  " You did great!"
    # sayit(msg, say=say, prnt=False)
    # boxit(msg, center=True, left_justify=2)
    # printit(msg, 'boxed', 'centered', color='yellow', box_color='red')
    printit(msg, 'boxed', 'centered', color='bold yellow', box_color='bold green on rgb(40,40,40)')
    # congrats_l = ["Keep up the good work", "Stick with it, you are awesome", "I admire your success!"]
    end_time = time.time()
    celebrate_time = end_time - begin_time
    return celebrate_time


# ###############
def disappoint():
    # ###########
    """   # noqa:
    purpose: just tells the user that the answer was not correct
       kind of the opposite of celebrate
       Note: this is kind of useless but might be enhanced later to encourage the user to do better in some way...
    """
    # sayit("Please try again...", say=say)
    # printit("Sorry, you will do better on this question next time...", 'centered')
    # printit(sub_color('blink red') + "Sorry" + sub_color('reset') + ", you will do better on this question next time...", 'centered', 'boxed')
    printit("[red]Sorry[/], you will do better on this question next time...", 'centered', 'boxed', box_color="red")


# #####################
def chk_syntax(lines):
    # ################
    """
    quick check of syntax on lines in the DAT_FILE
    """
    for line in lines:
        line = line.strip()
        # purify the line - if blank, ignore, and strip off any comments
        # this ignores trailing comments - turns the line blank if it is all a
        # comment line
        line = line.partition('#')[0]
        if not line.strip():  # if the line is empty.. empty string is a False value  # noqa:
            # dbug("found a blank line")
            continue
        semicolons = re.findall(r"(?<!\\);", line)
        # dbug("len(semicolons): " + str(len(semicolons))
        # semicolon_cnt = sum(map(lambda x : 1 if ';' in x else 0, line))
        semicolon_cnt = len(semicolons)
        if semicolon_cnt < 1:
            print("Syntax of line appears incorrect with no separator [;] found: \n" + line + "\n")  # noqa:
            return False
        # elems = line.split(";")
        elems = re.split(r'(?<!\\);', line)
        # dbug("elems: " + str(elems))
        # ques = elems[0].strip()
        ans = elems[1].strip()
        if ans == "":
            print("Problem with provided answer [" + str(ans) + "]")
            print("This line has a problem:\n" + line)
            print("Perhaps it is a problem with provided answer [" + str(ans) + "]")
            return False
        if semicolon_cnt > 1:
            ques_type = elems[2].strip()
            if ques_type not in ques_types:
                print("Question does not appear to be correct: \n" + line + "\n")
                print("Syntax: question or statement ; answer | or answer |or an other answer... ; ques_type ; multiple_choice_1, multiple_choice_2, ...")  # noqa:
                return False
            if "multi" in ques_type:
                if semicolon_cnt < 3:
                    print("Not enough choices for ques_type [" + ques_type + "]")  # noqa:
                    return False
    return True
    # ### END def chk_syntax(lines):


# #########################
def process_lines(lines, ques_cnt=0, scored_ques_cnt=0, num_ques=0, score=0, remove_time=0):
    # #####################
    """
    WIP
    This where we cycle through each question
    We return prcnt
    """
    # dbug(f"starting process_lines")
    LOOP = True  # noqa:
    # dbug(f"LOOP: {LOOP}")
    # num_lines = len(lines)
    # dbug(f"loop: {LOOP} ques_cnt: {ques_cnt}")
    # dbug(f" ques_cnt: {ques_cnt}")
    # if args['NUM']:
    #     num_ques_to_ask = int(args['NUM'])
    while LOOP:
        # dbug(lines)
        for line in lines:
            additional_info = ""
            hint = ""
            ques_type = ""
            msgs = []
            # dbug(f"processing line: {lines_processed}")
            hint = ""
            # dbug(f"ques_cnt: {ques_cnt} num_ques: {num_ques}")
            if ques_cnt >= num_ques:
                LOOP = False
                # dbug(f"the loop should end here")
                break
            # dbug(f"ques_cnt {ques_cnt} num_ques: {num_ques}")
            # dbug(f"line: {line}")
            # printit(line, 'boxed', title="printit(line, boxed...)", footer=dbug('here'))
            # dbug(f"hint: {hint}")
            phrases = line.partition("#")
            # dbug(phrases[2])  # keep in mind that "#" becomes a phrase as well
            # if "[h]" in line.partition('#')[2]:
            if "[h]" in phrases[2]:
                hint = phrases[2].replace("[h]", "")
                # dbug(f"line: {line}")
                # dbug(f"hint: {hint}")
            # if "[i]" in line.partition('#')[2]:
            if "[i] " in phrases[2]:
                # dbug(phrases[2])
                additional_info = phrases[2]
                additional_info = additional_info.replace("[i] ", "").strip()
                # dbug(additional_info)
                additional_info = additional_info.replace("\\n", "\n")
            # this ignores trailing comments
            # if not line.strip():  # if the line is empty.. empty string is a False value
                # dbug("Found a blank line")  # skip blank lines
            # dbug(line)
            # if not line.isalnum() or line == "":  # blank lines will get skipped  # noqa:
            # if line == "":  # blank lines will get skipped
            if not has_alnum(line):  # blank lines will get skipped
                # dbug(f"line: {line} continuing on...")
                LOOP = True
                continue
            # dbug(line)
            # printit(line, 'boxed', footer=dbug('here'))
            line = line.partition('#')[0]  # if a line has a comment just get what is before it
            # dbug(line)
            # printit(line, 'boxed', footer=dbug('here'))
            # elems = line.split(";")
            elems = re.split(r'(?<!\\);', line)  # spliting line into elements using ";" as a delimiter
            # dbug(f"elems: {elems}")
            # dbug(f"elems[1]: {elems[1]}")
            """--== INFO LINE ==--"""
            if elems[1].lower().strip() == "info" or elems[1].lower().strip() == "information":
                # dbug(f"args[-r]: {args['-r']}")
                # need to build remove time here
                info_start_time = time.time()
                # printit("Information:", center=True)
                if not args['-r']:
                    # dbug(f"elems: {elems}")
                    elems[0] = elems[0].replace("\\;", ";")
                    msgs = elems[0].split("\\n")
                    # dbug(f"boxit(msgs: {msgs})")
                    # boxit(msgs, center=True, y=1, title="Information Only")
                    # printit(msgs, 'boxed', 'centered', title="Information Only")
                    printit(msgs, 'boxed', 'centered', title="Information Only")
                    # boxit(elems[0], center=True, y=1)
                    # request_response(rspns="This is for your information only. Hit Enter to continue.")  # noqa:
                    msg = "Information only. Hit " + sub_color("white") + "Enter" + sub_color('reset') + " to continue..."
                    # askYN(msg, 'center')
                    ans = cinput(msg)
                    dbug(ans)  # needs documentation
                    cls()
                    # dbug("???")
                    do_quizit_title()
                    remove_time += info_start_time - time.time()
                continue  # continue to the next line
            """--== SEP LINE ==--"""
            ques_cnt += 1
            scored_ques_cnt += 1  # this will get decremented with non-scored questions  # noqa:
            if len(elems) > 2:
                ques_type = str(elems[2].strip().lower())
                # dbug(f"ques_type: {ques_type}")
            # dbug(f"elems: {elems}")
            # dbug(f"args: {args}")
            if args['-r']:
                # select a random line
                # dbug(f"ques_type: {ques_type} line: {line}")
                hint = ""
                """
                WIP
                if args('-R'):
                    lines = get_them_all()
                """
                line = random.choice(lines)
                if "[h]" in line.partition('#')[2]:
                    hint = line.partition('[h]')[2]
                    # dbug(f"hint: {hint}")
                if ques_type == "info":
                    continue
                if ques_type == "depends":  # or line.startswith("#"):
                    continue
                if line.lower().startswith('refer'):  # just like depends
                    continue
                elems = re.split(r'(?<!\\);', line)
            # dbug(f"args: {args}")
            # if args['--nr'] and num_ques > 0:
                # TODO maybe start at random line and then cycle through lines for num times
                # dbug(f"args['NUM']: {args['NUM']}")
                # if args['NUM'] is not None:
            if ques_cnt > num_ques:
                LOOP = False
                dbug("the loop should have ended here")
                break
                # elems = re.split(r'(?<!\\);', line)
            # ques_cnt += 1
            # dbug("here now")
            # print("\n" * 2 )
            # msgs.append("Question: " + str(ques_cnt) + f" of {num_ques}")
            """--== SEP LINE ==--"""
            if ques_cnt > num_ques:
                LOOP = False
                # dbug(f"the loop should end here")
                break
            """--== SEP LINE ==--"""
            title = " Question: " + str(ques_cnt) + f" of {num_ques} "
            ques = elems[0].replace("\\;", ";")
            # msgs.append("-" * 20)
            msgs.append("   ")
            msgs.append(ques)
            msgs.append("   ")
            try:
                right_answer = elems[1]
            except Exception as e:
                dbug("All elems: " + str(elems) + "e: " + str(e))
                sys.exit()
            # dbug(right_answer)
            # dbug(f"calling boxit(msgs: {msgs})")
            # boxit(msgs, center=True, y=1)
            if len(elems) > 2:
                ques_type = str(elems[2].strip().lower())
                if ques_type in multi_choice_types:
                    choices = multi_choice(elems)  # lists all the choices
                    new_choices = []
                    for choice in choices:
                        choice = choice.partition('#')[0]  # if a line has a comment just get what is before it
                        # dbug(f"adding choice: {choice}")
                        new_choices.append(choice)
                    # dbug(new_choices)
                    new_choices = gblock(new_choices)
                    # dbug(new_choices)
                    msgs = msgs + new_choices
                    # dbug(f"calling boxit(msgs: {msgs})")
                    msgs.append(" ")
                    # printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='yellow')
                    printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='bold yellow on rgb(40,40,40)')
                # elif ques_type == 'blank':
                #     blank_choice(elems)
                elif ques_type == "gimmie":
                    # the user will be out right given a point in the score as a bonus  # noqa:
                    #     score += 1
                    printit("-" * 40, center=True)
                    # printit("Your answer will be scored as a bonus ... !", 'centered', say=say)
                    printit("Your answer will be scored as a bonus ... !", 'centered')
                    scored_ques_cnt -= 1
                    # boxit(msgs, center=True, y=1)
                    # printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='yellow')
                    printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='bold yellow on rgb(40,40,40)')
                elif ques_type == "joke" or ques_type == "riddle":
                    # make this a bonus question
                    if ques_type == "joke":
                        printit("-" * 40, center=True)
                        printit("Your answer will be scored as a bonus ... !", say=say, center=True)
                        scored_ques_cnt -= 1
                    # boxit(msgs, center=True, y=1)
                    # printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='yellow')
                    printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='bold yellow on rgb(40,40,40)')
                else:
                    if ques_type not in ques_types:
                        printit("Possible error in DAT_FILE: Unknown question type: " + ques_type)
                    # ques_cnt += 1
            else:
                # boxit(msgs, center=True, y=1)
                # printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='yellow')
                printit(msgs, 'boxed', 'centered', center=99, title=title, footer=" Capitalization is not important, spelling is... ", box_color='bold yellow on rgb(40,40,40)')
            ans = request_response(hint=hint)
            if len(additional_info) > 1:
                print()
                printit(additional_info, 'boxed', 'centered', title=" Additional Information", footer=dbug('here'), box_color="white on black")
                print()
                additional_info = ""
            if ques_type == "riddle":
                lines = f'The corrent answer:  {right_answer.replace("|", " or ")}\n'
                lines += "This program is unable to score a riddle because the wording can be phrased many different ways. "
                lines += "Therefore, please determine for yourself if you had the correct answer or not and answer yes or no below."
                # printit(lines, 'boxed', 'centered', box_color="green", color='yellow')
                printit(lines, 'boxed', 'centered', box_color="green", color='bold yellow on rgb(40,40,40)')
                ans = cinput("Did you have the right answer? [y|N] ")
                if ans.lower() in ['y', "yes"]:
                    score += 1
                    remove_time += celebrate(QUIZ_FILE_DIR + "/" + "quiz-celebrate.cfg")
                else:
                    disappoint()
            else:
                # not a riddle
                if check_answer(ans, right_answer) or ques_type == "gimmie":
                    if ques_type in multi_choice_types:
                        # dbug(f"choices: {choices} right_ans: {right_answer}")
                        if "|" in right_answer:
                            # dbug(f"found | in right_answer: {right_answer}")
                            ans_l = []
                            ans_l = right_answer.replace(" ", '').split('|')
                            right_ans = right_answer.replace('|', ' or ')
                            # dbug(f"ans: {ans} ans_l: {ans_l}")
                            if ans.strip() in ans_l:
                                # dbug(f"Success...")
                                printit(f"The expected answer: {right_ans}", center=True)
                        else:
                            choice = int(right_answer) - 1
                            printit(f"The right answer is: {choices[choice]}", center=True)
                    remove_time += celebrate(QUIZ_FILE_DIR + "/" + "quiz-celebrate.cfg")
                    score += 1
                else:
                    disappoint()
            # dbug(f"str(round(score * 100 / ques_cnt: {ques_cnt}, 2)) ")
            pcnt = str(round(score * 100 / ques_cnt, 2))
            print("\n" * 1)
            if scored_ques_cnt < 1:
                scored_ques_cnt = 1
            printit("=" * 40, center=True)
            if int(score) < 1:
                prcnt_score = "0"
            else:
                prcnt_score = str(round((score * 100) / scored_ques_cnt, 2))
            printit("Score: " + str(score) + " out of " + str(scored_ques_cnt) + " scored questions.",  # noqa:
                center=True)
            printit("Your percent correct = " + prcnt_score + "%", center=True)
            print("\n")
            cinput("")
            # cls()
            do_quizit_title()
            # END for line in lines:
        # END while LOOP:
    return pcnt
    # EOB def process_lines(lines, ques_cnt=0, scored_ques_cnt=0, num_ques=0, score=0, remove_time=0):  # noqa:


def do_quizit_title():
    global DAT_FILE
    basename_dat_file = os.path.basename(DAT_FILE)
    title = " Quizit [version: " + __version__ + "]: " + basename_dat_file
    if USER != "none":
        title += " USER: " + USER
    # ### read in the DAT_FILE ### #
    # first clear the screen
    cls()
    # show the Title
    # dbug("???")
    # boxit(title, center=True, left_justify=2, color='red')
    printit(title, 'boxed', center=True, color='bold yellow', box_color="bold white on rgb(40,40,60)")
    print("\n"*4)


def get_categories_lvls(*args, **kwargs):
    #category = args['CATEGORY']
    rtrn_type = kvarg_val("rtrn", kwargs, dflt="")
    categories = []
    cat_files_d = {}
    levels_d = {"0": 0}
    lvl_files_d = {}
    uncategorized = 0
    no_lvl = 0
    cnt = 0
    f_l = list_files(QUIZ_FILE_DIR, "*.dat")
    # dbug(f_l, 'ask')
    for f in f_l:
        cnt += 1
        cat = ""
        lvl = ""
        # dbug(f"Now checking: {pf} for category: {category}")
        lines = [line.rstrip() for line in open(f) if line.startswith("#")]
        for line in lines:
            if "categories:" in line.lower():
                cat = re.search('(?<=categories:)(\w+)', line).group(1)
                if cat not in categories:
                    categories.append(cat)
                cat_files_d.setdefault(cat, []).append(f)
            if "category:" in line.lower():
                cat = re.search('(?<=category: )(\w+)', line).group(1)
                if cat not in categories:
                    categories.append(cat)
                cat_files_d.setdefault(cat, []).append(f)
            if "level:" in line.lower():
                # dbug(line)
                lvl = re.search('(?<=level: )(\w+)', line).group(1)
                if lvl:
                    if lvl not in levels_d:
                        levels_d[lvl] = 1
                    else:
                        levels_d[lvl] += 1
                    lvl_files_d.setdefault(lvl, []).append(f)
            # else:
            #     levels_d["0"] += 1
            #     dbug(f"We have a cat: {cat} in pf: {pf}")
        if cat == "":
            uncategorized += 1
           #  uncat_files_d['uncategorized'].append(f)
            cat_files_d.setdefault('uncategorized', []).append(f)
            # dbug(f"f: {f} no cat uncategorized: {uncategorized}")
        if lvl == "":
            no_lvl += 1
            # dbug(f"f: {f} no lvl no_lvl: {no_lvl}")
    # dbug(cnt)
    categories.append(f"Uncategorized ({uncategorized})")
    # levels.append(f"No level ({no_lvl})")
    # dbug(categories)
    # dbug(levels_d)
    # dbug(categories)
    # dbug(cat_files_d)
    # dbug(lvl_files_d)
    if rtrn_type in ("cat", "category", "cats", "categories", "c"):
        return cat_files_d
    levels_d['0'] = cnt - len(lvl_files_d)
    return categories, levels_d, cat_files_d, lvl_files_d



# #########
def main(args):
    # #####
    """
    everything starts here
    TODO: need to whittle this down to function call, it is way too "runon"
    """
    """--== Init ==--"""
    # ### DAT_FILE ### #
    global QUIZ_FILE_DIR
    if args['--celebrate_test']:
        celebrate(QUIZ_FILE_DIR + "/" + "quiz-celebrate.cfg", tst=True)
        sys.exit()
    if not file_exists(QUIZ_FILE_DIR, type="dir"):
        printit("No quiz file dir [" + QUIZ_FILE_DIR + "] found...", 'centered')
        if askYN("Do you want me to create it? ", "centered"):
            os.mkdir(QUIZ_FILE_DIR)
        else:
            do_close()
    global DAT_FILE
    # dbug(f"DAT_FILE: {DAT_FILE}", 'ask')
    try:
        # dbug(f"trying to see if DAT_FILE != empty ")
        os.path.exists(DAT_FILE)
    except Exception as Error:
        dbug(Error)
    remove_time = 0
    global USER
    """--== Process ==--"""
    #cls()
    row1_box_color = "red"
    categories, levels_d, cat_files_d, lvl_files_d = get_categories_lvls()
    levels_box = boxed(f"Levels {len(levels_d) - 1} No_Lvl_Declared: {levels_d['0']}", title=" Levels Info ", footer="L)evel Selection", box_color=row1_box_color)
    # cats_box = boxed(gcolumnize(categories), title=" Categories Information ", footer=" C)ategory Selection ", box_color=row1_box_color)
    cats_box = boxed(f"Categories: {len(categories)}", title=" Categories Information ", footer=" C)ategory Selection ", box_color=row1_box_color, txt_center=99)
    # boxes = []
    # boxes.append(box_cats)
    # boxes.append(levels_box)
    if not file_exists(DAT_FILE) or DAT_FILE == "none":  # or not args['-f']:
        do_logo(rootname(__file__), 'centered', figlet=True, color='yellow on rgb(20,20,20)', box_color="red on rgb(20,20,20)")
        quiz_files = list_files(QUIZ_FILE_DIR, pattern="*.dat")
        # dbug(type(quiz_files))
        quiz_names = [rootname(f) for n, f in enumerate(quiz_files, start=1)]
        quiz_selections = []
        for n, quiz in enumerate(quiz_names, start=1):
            quiz_selections.append(f"{n:>3}) {quiz}")
        # dbug(type(quiz_selections))
        box_quizes = boxed(gcolumnize(quiz_selections, cols=5), title="Quiz Names", box_color="cyan")
        row1 = gcolumnize([levels_box, cats_box])
        row2 = box_quizes
        quiz_selections_content = row1 + row2
        printit(quiz_selections_content, 'boxed', 'centered', center=99, title="Quiz Selections", box_color="white on black", txt_center=99)
        quiz = cat_ans = lvl_ans = "unknown"
        ans = cinput("Please select: L)evel C)ategory or Q)uit: ")
        # dbug(ans)
        # dbug(type(ans))
        if ans in ("q", "Q"):
            do_close()
        if isnumber(ans):
            quiz = quiz_files[int(ans)-1]
        if ans in ("c", "C"):
            cat_ans = gselect(categories, 'centered', rtrn="v", cols=4)
            # dbug(cat_ans)
            quiz = gselect(cat_files_d[cat_ans], 'centered', rtrn="v", cols=2)
            cls()
            # dbug(quiz)
        if ans in ("l", "L"):
            lvl_ans = gselect(levels_d, 'centered', rtrn="k")
            select_files_d = lvl_files_d[lvl_ans]
            quiz = gselect(select_files_d, 'centered')
        # dbug(quiz)
        """--== SEP_LINE ==--"""
        DAT_FILE = quiz
        if ans in ("E"):
            do_edit(__file__)
            do_close()
    try:
        # all non-commented out lines:
        lines = [line.rstrip() for line in open(DAT_FILE) if not line.startswith("#")]
    except Exception as e:
        dbug(f"DAT_FILE: [{DAT_FILE}] Exception: {e} Selected: {ans}", 'centered')
        #try:
        #    ans = cinput("Do you want to create and edit it? [y/n] ", "n")
        #except KeyboardInterrupt:
        #    sys.exit()
        #if ans.lower() == "yes" or ans.lower() == "y":
        #    do_edit(DAT_FILE)
        #else:
        #    printit("... no usable quiz file declared ... exiting...", 'centered')
        #    sys.exit()
        do_close()
    ques_lines = []
    # num_ques = len(ques_lines)
    if not chk_syntax(lines):
        ans = input("Do you want to edit this file [" + DAT_FILE + "] (y|n)? ")
        if "y" in ans.lower():
            printit(SYNTAX_MSG)
            askYN()
            do_edit(DAT_FILE)
        sys.exit()
    for line in lines:
        # if line == "":
        if not has_alnum(line):
            continue
        elems = re.split(r'(?<!\\);', line)  # spliting line into elements using ";" as a delimiter
        # dbug(f"elems: {elems}")
        if elems[1].lower().strip() in ['info']:
            continue
        ques_lines.append(line)
    # ### USER ### #
    if USER == "none" and FORCE_NAME:
        # print("\n"*1)
        # dbug(USER)
        try:
            # USER = input("Please enter your name: ")
            msg = "Please enter your name: "
            # USER = input(printit(msg, center=True, invisable=True))
            USER = cinput(msg)
            if USER in ("q", "Q"):
                do_close()
            # dbug(USER)
        except KeyboardInterrupt:
            sys.exit()
        print("\n" * 1)
    # ### process all the lines in the DAT_FILE ### #
    basename_dat_file = os.path.basename(DAT_FILE)
    do_quizit_title()
    ques_cnt = 0
    num_ques = len(ques_lines)
    if args['NUM'] is not None:
        num_ques = int(args['NUM'])
    pcnt = process_lines(lines, ques_cnt=ques_cnt, num_ques=num_ques)
    # dbug(f"end of lines loop")
    printit("=" * 40, center=True)
    end = time.time()
    elapsed_time = (end - start) - remove_time
    msg = f"The elapsed time: {elapsed_time:0.2f} seconds (minus celebration time). Percent right: {pcnt}"
    # printit(msg, 'boxed', 'centered', 'shadowed', say=say)
    printit(msg, 'boxed', 'centered')
    if USER != "none":  # This should always be the case if FORCE_USER is true
        # assuming QUIZ_FILE_DIR has been created at the beginning of main()
        # msg = f"User: {USER:15}, Dtime: {dtime}, DatFile: {basename_dat_file:25}, Score: {pcnt:>6}%, Elapsed_time: {end-start:0.2f}, Num ques: {ques_cnt:6}"  # noqa:
        # msg = "User: {:15}, Dtime: {}, DatFile: {:25}, Score: {:>6}%, Elapsed_time: {:0.2f}, Num ques: {:6}".format(  # noqa:
        header = 'User,Dtime,DatFile,Score,Elapsed_time,Num ques'
        msg = "{},{},{},{},{},{}".format(USER, dtime, basename_dat_file, pcnt, end - start, ques_cnt)
        global OUT_FILE
        global CVS_FILE
        with open(OUT_FILE, 'a') as f:
            f.write(msg + "\n")
        if not os.path.isfile(CSV_FILE):
            with open(CSV_FILE, 'a') as f:
                f.write(header)
            f.close()
        with open(CSV_FILE, 'a') as f:
            f.write(msg + "\n")
        print("\n")
        printit("Wrote results into: " + OUT_FILE, say=say, center=True)
        print("\n" * 2)
        """--== SEP LINE ==--"""
        # printit("Show [P]ast performance on this quiz or  show [A]ll past performance\n [q]uit or Enter will quit", 'centered', 'boxed', title=f" You have completed this quiz with a score of: {pcnt}%. ", center=99)
        printit("Show [P]ast performance on this quiz or  show [A]ll past performance\n [q]uit or Enter will quit", 'centered', 'boxed', title=f" You have completed this quiz with a score of: {pcnt}%. ", center=99)
        ans = request_response()
        if ans.lower() == "p":
            df = pd.read_csv(CSV_FILE)
            df_filtered = df[(df.User == USER) & (df.DatFile == basename_dat_file)]
            print("=" * 40)
            print(df_filtered)
            avg_score = df_filtered['Score'].mean(axis=0).round(2)
            score_cnt = df_filtered['Score'].count()
            avg_etime = df_filtered['Elapsed_time'].mean().round(2)
            print("-" * 40)
            print("score_count: " + str(score_cnt) + "     avg_score: " + str(avg_score) + " avg_etime: " + str(avg_etime))
            print("=" * 40)
        if ans.lower() == "a":
            df = pd.read_csv(CSV_FILE)
            df_filtered = df[(df.User == USER)]
            print("=" * 40)
            print(df_filtered)
            avg_score = df_filtered['Score'].mean(axis=0).round(2)
            score_cnt = df_filtered['Score'].count()
            avg_etime = df_filtered['Elapsed_time'].mean().round(2)
            min_etime = df_filtered['Elapsed_time'].min().round(2)
            print("-" * 40)
            print("score_count: " + str(score_cnt) + "     avg_score: " + str(avg_score) + " avg_etime: " + str(avg_etime) + " min_etime: " + str(min_etime))
            print("=" * 40)
    # ### END: def main(args):


@docvars(os.path.basename(__file__))
# ###################
def handleOPTS(args):  # noqa:
    # ###############
    """
    Usage:
        {0}
        {0} -h
        {0} -R
        {0} -c
        {0} -S
        {0} --celebrate_test
        {0} -e | -e DAT_FILE
        {0} -f DAT_FILE
        {0} -C | -C CATEGORY
        {0} -E | -E NUM
        {0} -u USER
        {0} -r [NUM]
        {0} --nr NUM
        {0} -F [ratio]
        {0} --vocab
        {0} --quotes [--shuffle]
        {0} --create
    """
    global say
    global DAT_FILE
    # dbug("args: " + str(args))
    if args['-E']:
        NUM = ""  # noqa:
        if args['NUM']:
            NUM = args['NUM']  # noqa:
        do_edit(__file__, lnum=NUM)
        sys.exit()
    if args['-e']:
        if args['DAT_FILE'] is not None:
            printit(SYNTAX_MSG)
            askYN()
            do_edit(args['DAT_FILE'])
            # do_edit(QUIZ_FILE_DIR + "/" + args['DAT_FILE'])
        else:
            # do_logo(rootname(__file__), 'shadowed', 'centered', figlet=True, box_color="yellow")
            do_logo(rootname(__file__), 'centered', figlet=True, box_color="yellow")
            printit("Select a file for editing please", 'centered')
            dat_file = select_file(QUIZ_FILE_DIR, 'centered', 'boxed', 'shadowed', pattern="*.dat")
            printit(SYNTAX_MSG)
            askYN()
            do_edit(dat_file)
        sys.exit()
    if args['-f']:
        global f_ratio
        # f_ratio = 70
        if args['ratio']:
            f_ratio = args['ratio']
    if args['-C']:
        # global DAT_FILE
        cat_files_d = get_categories_lvls(rtrn="cats")
        cat_ans = gselect(cat_files_d, 'centered', rtrn="v", cols=4)
        # dbug(cat_ans)
        quiz = gselect(cat_ans, 'centered', rtrn="v", cols=2)
        # quiz = gselect(cat_files_d[cat_ans], 'centered', rtrn="v", cols=2)
        # dbug(f"DAT_FILE: {DAT_FILE}")
        cls()
        DAT_FILE = quiz
        # dbug(DAT_FILE)
        # main(args)
    if args['-S']:
        say = True
    if args['-R']:  # open quiz for review only
        dat_file = select_file(QUIZ_FILE_DIR, pattern="*.dat", box=True, center=True)
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
    if args['-f']:  # select a specific quiz by file name
        # global DAT_FILE
        DAT_FILE = args['-f']
        # print("Setting DAT_FILE to " + DAT_FILE)
    if args['-u']:  # inserts username, avoids being asked for the name
        global USER
        USER = args['-u']
        # print("USER: " + USER)
    if args['--vocab']:
        playloop("vocab")
    if args['--quotes']:
        playloop('quotes')
    if args['--create']:
        # global QUIZ_FILE_DIR
        filename = cinput("Please provide a filename (you should end it with '.dat':")
        filename = QUIZ_FILE_DIR + "/" + filename
        if not file_exists(filename):
            hdr = ["# category: none level: 0\n"]
            hdr.append("# Syntax: question or statement ; answer | or answer |or an other answer... ; ques_type ; multiple_choice_1, multiple_choice_2, ...\n")
            hdr.append("# For quotes the syntax is: \"Your quote\" - author\n")
            hdr.append("# For vocab the syntax is: word, definitio\n")
            with open(filename, "w")as f:
                f.writelines(hdr)
        printit(SYNTAX_MSG)
        askYN()
        do_edit(filename)
        return


if __name__ == "__main__":
    from docopt import docopt
    args = docopt(handleOPTS.__doc__, version=__file__ + "1.0")
    handleOPTS(args)
    main(args)
