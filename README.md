## quizit 

This application is a python script that reads a text data file with questions, answers, and optionally hints.
The application can [R]eview the data file, [e]dit the data file, or allow the select any data file and run a quiz.
The questions can be randomly presented of sequentially (default).
Various question types can be used.
By default all data files should be located in the directory ~/quiz-files/

### Install
git clone https://github.com/geoffmcnamara/quizit.git

You can link the quizit.py to a convenient location eg:
	ln -s ~/dev/git/quizit/quizit.py ~/bin/   # linked into your home/bin directory, you probably want to add that directory to your PATH
Make sure you have a directoy ~/quiz-files with at least on <quizname>.dat file in it.


-----

for help run quizit.py -h

As mentioned in the help, be careful with the syntax of the quiz data files. The syntax is checked before the quiz test is run and will allow editing if it
finds a problem

I use this to help teach elementary students and myself.

Enjoy
  Geoff McNamara, geoff.mcnamara@gmail.com


------- quizit -------
    
Created on: 20190304-2021
Created by: geoffm
    
----- Last Code Changes -----
    
Modified on: 20190308-0910
Modified by: geoffm
   
------- pre-commit.sh -------
