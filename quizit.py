#! /usr/bin/env python3
# vim: set syntax=none nospell:
# ########### #
# Purpose: write out a quiz (can also have it speak out the questions) and get the user response 
#    with each question a score is provided
#    a bonus is added for questions that have the ques_type as joke or riddle
# requires: 
#     gtools.py
#     a dat_file - see below
#           python3
#           pip3 install pyttsx3 (which requires the espeak libraries - apt install espeak)
# input: 
#     You need to write the DAT_FILE and configure it's location below
#     syntax of DAT_FILE:
#     question or statement | answer|answer|answer... | ques_type | multiple choices
#         ques_type can be blank (simple one answer question), 
#            multi_choice, # choices must follow
#            riddle, joke  # no score, bonus is given if it is answered correctly
# Example: DAT_FILE
# Take the number 5 and add 6 and what is the answer?;11
# Now multiply that number by 5 and what is the answer?;55
# There is a house with four walls. All of the walls are facing south. A bear is circling the house. What color is the bear?;white; riddle
# A fool thinks himself to be wise, but a wise man knows himself to be a fool. Who said this? ; 2 ; multi_choice; Abraham Lincoln; William Shakespeare; Benjamin Franklin; John F Kennedy 
# What is the speed of light (in miles per second)?; 186,000|186000
# Joke: Why is 6 afraid of 7 ?; because 7, 8, 9!; joke  
# ############################
"""
Usage: my_program.py [-hEf FILE] [-e DAT_FILE] [-u USER]

-h --help    show this
-f DAT_FILE  specify test data file [default: ./test.dat]
-E           edit this program
-e DAT_FILE  edit the DAT_FILE
-u USER      specify username

"""

# ### imports ### #
import pyttsx3
from datetime import datetime
import time
import subprocess
from time import sleep
from random import randint
import sys
sys.path.append("/home/geoffm/dev/python/gmodules/")
from gtools import boxit, run_cmd



# ### globals - config ### #
__version__ = "0.9"
DAT_FILE = 'quiz.dat'  # this one can be changed with the -f DAT_FILE argument
USER = "none"   # this one can be changed with the -u USER argument
OUT_FILE = "./quizit-results.dat"  # only writes out results if -u USER is an argument or if FORCE_NAME==Ture
FORCE_NAME = True
engine = pyttsx3.init()
volume = 0.8
prnt = True
say = False
now = datetime.now()
month = now.strftime("%B")
start = time.time()
score = 0

# ### Set pyttsx3 properties _before_ you add things to say #### #
engine.setProperty('rate', 150)    # Speed percent (can go over 100)
engine.setProperty('volume', volume)  # Volume 0-1


# #################################
def sayit(msg, say=say, prnt=prnt):
    # ############################
    """
    will say outloud the msg provided
    optionally you tell it to print or not print or say or not say
    eg:
    >>> msg = "Dave, don't do that"
    >>> sayit(msg)
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
def showpics(dir='/home/geoffm/Pictures',num=1):
    # #########################################
    """
    puprose: just for fun - can be used to call chafa against pictures to show on a terminal using ascii chars
    Note: this function can be removed/ignored
    used it once in the celebrate function to reward a right answer with some pics
    """
    for i in range(0,num):
        cmd = 'find ' + dir + '/wallpapers/ | shuf -n 1'
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True, encoding='utf8')
        pic = process.stdout.readline()
        subprocess.call('chafa -w 9 -s 30x20 ' + str(pic), shell=True)
        sleep(0.3)


# ########################################################
def request_response(rspns="    What is your response? "):
    # ####################################################
    """
    purpose: prints out a question and gets a response
    input: rspns prompt - defaults to the above
    returns: ans - user response
    output:
    # to test python3 -m doctest -v ./quizit.py  # and hit enter
    >>> request_response("testing only")
    ----------------------------------------
        What is your response? 
    ----------------------------------------
    'test only'
    """
    print("-" * 40)
    if rspns == "testing only":
        ans =   "test only"
        print("    What is your response? ")
    else:
        ans = input(rspns)
    print("-" * 40)
    # filter the answer (ans) from the user to lower case and no quotes
    ans = str(ans.lower().strip().replace('"',''))
    return ans


# ################################
def check_answer(ans, right_ans):
    # ############################
    """
    purpose: checks ans against right_ans - forces everything to lower case and strips out double quote marks and surrounding spaces
    input: ans, right_ans - both are required
    """
    success = False
    # filter the answer from the dat file (elems[1]) to lower case and strip off spaces and double quote marks
    right_ans = str(right_ans.strip().lower().replace('"',''))
    # first see if right answer has more than one pssibility
    if '|' in right_ans:
        ans_l = []
        ans_l = right_ans.split('|')
        right_ans = right_ans.replace('|', ' or ')
        if ans in ans_l:
            success = True
    if ans == right_ans:
        success = True
    sayit("Expected answer is [" + right_ans + "] your answer is: [" + str(ans) + "]")
    return success  # either True or False


# ######################
def multi_choice(elems):
    # ##################
    """
    purpose: displays all the multiple choices with item/element numbers, seeks user response and returns it
    input: elems # which is a [list]
    returns: ans # integer
    """
    # print("DEBUG: len(elems): " + str(len(elems)))
    # print("DEBUG: elems: " + str(elems))
    if elems[2].strip() == "multi_choice":
        print("\n")
        num = 1
        # print(" ======\n")
        #print("elems[3:]: " + str(elems[3:]))
        for item in elems[3:]:
            sayit(str(num) + " " + item)
            num += 1
        print("\n")
        # ans = input("What is your choice? ")
        ans = request_response()
        return ans


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
    """
    msg = "You did great!"
    sayit(msg,prnt=False)
    print("\n")
    boxit(msg)
    # print("=" * 40)


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


# #########
def main():
    # #####
    """
    everything starts here
    """
    # do_all_voices()  # just to see what the different voices are
    msgs = []
    dtime=datetime.now().strftime("%Y%m%y-%H%M")
    msgs.append("The date is,... " + month + " "   + str(now.day)  + " " + str(now.year) + ", ... ")
    msgs.append("And the time is: " + str(now.hour) + " hours and " + str(now.minute) + " minutes")
    print("\n" * 4 + "=" * 40)
    for msg in msgs:
         sayit(msg, say=False)
    global USER
    if USER == "none" and FORCE_NAME:
        print("\n"*2)
        USER = input("Please enter your name: ")
        print("\n"*2)
    # open the DAT_FILE and read all the lines
    msg = "Quizit [version: " + __version__ + "]: " + DAT_FILE
    if USER != "none":
        msg += " USER: " + USER
    boxit(msg, x=5)
    try:
        with open(DAT_FILE) as file:
            lines = file.readlines()
    except Exception as e:
        print("Exception: " + str(e))
        ans = input("Do you want to create and edit it? [y/n] ")
        if ans.lower() == "yes" or ans.lower() == "y":
            do_edit(DAT_FILE)
        sys.exit()

    ques_cnt = 0
    score = 0
    for line in lines:
        ques_cnt += 1
        # syntax of DAT_FILE
        # question or statement | answer|answer|answer... | ques_type | multiple choices
    
        print("\n" * 2 )
        msgs = []
        msgs.append("Question: " + str(ques_cnt))
        # boxit("Question: " + str(ques_cnt))
        # line = line.replace('\n','')
        elems = line.split(";")
        # print("Debug: elems: " + str(elems))
        ques = elems[0]
        msgs.append("-" * 20)
        msgs.append(ques)
        right_answer = elems[1]
        sayit(ques, prnt=False)
        # boxit(ques)
        # print(f"before call to boxit msgs: {msgs}")
        boxit(msgs,x=5,y=5)
        if len(elems) > 2:
            ques_type = str(elems[2].strip().lower())
            # print("DEBUG: ques_type: " + ques_type)
            if ques_type == "multi_choice":
                ans = multi_choice(elems)
                # continue
            elif ques_type == "joke" or ques_type == "riddle":
                # no score change
                print("-" * 40)
                sayit("Your answer will be scored as a bonus ... !")
                ans = request_response()
                ques_cnt -= 1
            else:
                print("Unknown question type: " + ques_type)
        else:  # no ques_type declared - simple answer question
            ans = request_response()
        if check_answer(ans, right_answer):  # WIP
            print(f"running celebrate")
            celebrate()
            score += 1
        else:
            disappoint()
        pcnt = str(round(score*100/ques_cnt,2))
        sayit("Score: " + str(score) + " out of " + str(ques_cnt) + " Your percent correct = " + str(round(score*100/ques_cnt,2)) +"%" )
    # print out the final score and elapsed time
    # TODO eventually this should have a user sign in and have these results saved
    print("=" * 40)    
    end = time.time()
    msg = f"\n\nThe elapsed time: {(end-start):0.2f} seconds"
    sayit(msg)
    sayit("Score: " + str(score))
    if USER != "none":
        msg = f"User: {USER:15}, Dtime: {dtime}, DatFile: {DAT_FILE:15}, Score: {pcnt:>6}%, Elapsed_time: {end-start:0.2f}, Num ques: {ques_cnt:6}"
        print(msg)
        global OUT_FILE
        with open(OUT_FILE,'a') as f:
            f.write(msg + "\n")

    # EOB #


# ########################
def do_edit(file, lnum=0):
    # ####################
    """  # noqa:
    a quick-n-dirty utility to edit a file
    Initiate edit on a file - with lineno if provided
    """
    if lnum:
        cmd = f"vim {file} +{str(lnum)}"
    else:
        cmd = f"vim {file}"
    r = subprocess.call(cmd, shell=True)
    # print(f"{cmd}")
    return r


# ###################
def handleOPTS(args):
    # ###############
    """
    purpose: handles options
    """
    print(f"args: {args}")
    if args['-E']:
        do_edit(__file__)
        sys.exit()
    if args['-e']:
        do_edit(args['-e'])
        sys.exit()
    if args['-f']:
        global DAT_FILE
        DAT_FILE=args['-f']
        print("Setting DAT_FILE to " + DAT_FILE)
    if args['-u']:
        global USER
        USER = args['-u']
        print("USER: " + USER)


if __name__ == "__main__":
    # TODO need to add docopts to optionally take a DAT_FILE name to run
    # TODO add a way to track a user and final scores with elapsed times - KISS eg: sqlite3 quizit.db 
    # quizit.db schema id, username, dat_file(test name), dat_file last mod date?,  date, score (#questions, #bonus quest, #right), elapsed_time, notes, created, modified?
    # import doctest
    # doctest.testmod()
    from docopt import docopt
    args = docopt(__doc__) # , version=__file__ + "0.9")
    handleOPTS(args)
    main()
