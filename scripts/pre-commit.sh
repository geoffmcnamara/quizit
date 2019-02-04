#!/bin/bash
##################################################################
# Script name: t.sh
# Creation by: geoffm
# Creation Date: 20180804
# Last modified: 20180804 geoffm
# Purpose:    used with git to insert creation/modification info in any README.*
# Valid User(s): whoever
# Parameters Expected: none
# How should it be used:   git checkin             
# Notes:      place script in prj/scripts/pre-commit.sh
#             ln -s scripts/pre-commit.sh .git/hooks/pre-commit
# $Id
# vim: noai:verbose:ft=bashr:ts=2:expandtab:
###################################################################


set -e          # exit immediately anytime a command returns non-0
#set -u          # error on undefined variable
#set -x          # shows all commands as they run
#set -n          # no actions
#set -o pipefail # pipe will be considered successful if all the commands involved are executed without errors
##########################

##################
# Global Variables
##################
DTIME=$(date +%Y%m%d-%H%M)
TEMP_FILE=/tmp/$(basename "$0").$$ # this is here 'coz I use it quite a bit 
# see /usr/include/sysexits.h for these standard error codes
# Set the ERRFLAG to no error
#ERRFLAG=0
# Turn off COLOR 
COLOR_FLAG=NO
# Make sure the PATH covers the basics 
PATH=$PATH:/usr/bin:/usr/local/bin:/usr/ucb

#####################
## Functions
#####################
# just to to protect against premature Ctrl-C breaks
trap 'ERRFLAG=91;doEXIT Exiting immediately - Trapped Signal Ctrl-C' INT

##############
initCOLOR ()
##############
{
  COLOR_FLAG=${COLOR_FLAG:-YES} # Can be YES or NO - I use color to easily 
  export COLOR_FLAG
  if [ "x$COLOR_FLAG" = "xYES" ]; then
    # BLACK=$'\033'"[30m"
    RED=$'\033'"[31m"
    GREEN=$'\033'"[32m"
    YELLOW=$'\033'"[33m"
    BLUE=$'\033'"[34m"
    # MAGENTA=$'\033'"[35m"
    # CYAN=$'\033'"[36m"
    # WHITE=$'\033'"[37m"
    # BRIGHT=$'\033'"[01m"
    # BLINK=$'\033'"[05m"
    # REVERSE=$'\033'"[07m"
    NORMAL=$'\033'"[0m"
    # DLINE="${YELLOW}============================================================${NORMAL}"
    SLINE="${YELLOW}------------------------------------------------------------${NORMAL}"
  else
    # BLACK=''
    RED=''
    GREEN=''
    YELLOW=''
    BLUE=''
    # MAGENTA=''
    # CYAN=''
    # WHITE=''
    # BRIGHT=''
    # BLINK=''
    # REVERSE=''
    NORMAL=''
    # DLINE="============================================================"
    SLINE="------------------------------------------------------------"
  fi
  export LINE
}

#################
processCMD ()
################
{
# This just makes it easier to write commands that you
# also want echo'ed to the screen
# Please be sure to escape all quotes (double or single)
# EXAMPLE: 
# processCMD su - $MYUSER -c \"ls -la\"
#    or
# processCMD 'cat ~/.ssh/ida_pub | ssh username@rhost "cat - >>.ssh/authorized_keys2"'
  DEBUG=${DEBUG:-0}

  if [ "$DEBUG" -eq 0 ]; then
    # Because DEBUG is off - actually run the command
    #eval $*
    #printIT ${BLUE}Executing:${NORMAL} $@
    echo ${BLUE}Executing:${NORMAL} "$@"
    eval "$@"
    ERRFLAG=$?
  else
    ERRFLAG=0
    #printIT DEBUG=$DEBUG so ${RED}Not${NORMAL} ${BLUE}Executing:${NORMAL} $@
    echo "DEBUG=$DEBUG so ${RED}Not${NORMAL} ${BLUE}Executing:${NORMAL}" "$@"
  fi
  return $ERRFLAG
}

#############
handleOPTS ()
#############
{
# IMPORTANT: call this function with "handleOPTS $*"
#
# --- Command line Options/Arguments ---
  initCOLOR  # gets color codes and D/S LINE established - default is YES
  PARAMS="CD:Ehi"
  while getopts "$PARAMS" opt; do
  # echo DEBUG: The parameter now being processed is: opt=$opt
  # use VARNAME=$OPTARG for any required arguments to an option
  case $opt in
    C )
      # Toggle COLOR_FLAG - the default is usually YES
      # I use capital C in order to reserve the small c for other
      # purposes - like conf file or whatever.
      if [ "x$COLOR_FLAG" = "xYES" ]; then
        #echo DEBUG: setting COLOR_FLAG to NO
        COLOR_FLAG=NO
      else
        COLOR_FLAG=YES
      fi
      initCOLOR
      ;;
    D )
      DEBUG=$OPTARG
      ;;
    E ) EDITOR=${EDITOR:-vim}
      $EDITOR "$0"
      exit
      ;;
    h )
      doUSAGE 
      #doEXIT
      ;;
		i ) INSTALL="YES" ;;
    * )
      doUSAGE
      ;;
    esac
  done

  shift $(( OPTIND - 1 ))


# add this into your code after the handleOPTS to continue reading 
# Handle non-option arguments
#while [ $OPTIND -gt 1 ]; do
#  shift
#  OPTIND=$[ $OPTIND - 1 ]
#done

######
# Add this if you want to ensure that at least one param is given
#if [ "x$1" = "x" ]; then
#  ERRFLAG=9
#  doUSAGE
#  doEXIT
#fi

# other args can now be processed normally within this function
# eg: $0 -C -D 0 arg1
#if [ "x$1" = "xarg1" ]; then
#  ARG1=yes
#  echo ARG1=$ARG1
#fi
}

##########
doUSAGE ()
##########
{
cat << EOF
 Usage: $(basename "$0") [$PARAMS]
        -C            Toggle the color flag. Default COLOR_FLAG=[$COLOR_FLAG]
        -D [#]        Sets DEBUG level
        -h            Will show this usage info...

EOF
  ERRFLAG=${ERRFLAG:-64}
}

#################
doEXIT ()
#################
{
  # Note: trap brings you here: so
	# echo $LINENO ERRFLAG=$ERRFLAG
	EXIT_MSG="$1" 
  if [ -f "$TEMP_FILE" ]; then
    processCMD rm "$TEMP_FILE"
  fi
  # ERRFLAG=${ERRFLAG:-"1000"}
  # if we have params then print them
  [ "$#" -gt 0 ] && echo "$@" 
  # Now exit with appropriate msgs unless EXIT_MSG != YES
  if [ "$ERRFLAG" = "0" ]; then
    if [ ! x"$1" = "x" ]; then
      echo "${GREEN}Success${NORMAL} $(date +%Y%m%d-%H%M): $(basename "$0")  $EXIT_MSG script exiting..."
    fi
    exit $ERRFLAG
  else
    if [ "$ERRFLAG" = "1000" ]; then
      echo "Make sure you change the ERRFLAG [$ERRFLAG] in the script!"
    fi
    if [ ! x"$1" = "x" ]; then
      echo "${RED}WARNING${NORMAL}: Error ${RED}$ERRFLAG${NORMAL}"
      echo "$(date +%Y%m%d-%H%M) exiting..."
    fi
    exit $ERRFLAG
  fi
} # end of doEXIT ()

############
askYN ()
#############
{
# normally expects param 1 to be prompt string
# *** If no params are provided - it acts like a Continue Prompt ***
# param 2 is optional default answer (case does not matter)
# defaults to N without any other direction...
# always returns a capital Y or N in ANS variable
# wip param 3 - timeout
# this function will ALWAYS return 0 if the ANSwer is Y else it returns 1
# EXAMPLE
# quick and dirty:
# askYN "Do you want to install alpine?" y && sudo apt install alpine || echo "Maybe next time..."
#     or longer more traditional method...
# if askYN "Are you happy" n ; then ...
#   echo Then you must be happy
# else
#   echo I wish I could make you happy
# fi
# This example will echo "I wish I could make you happy" with 
#  a "No" or the default answer
#         or
# askYN "Shall we continue" || exit 99
#
  ANS="N"
  TIMEOUT=${3:-0}
  if [ "$TIMEOUT" -ne 0 ]; then
    TIMEOUT_ARG=" -t $TIMEOUT"
  else
    TIMEOUT_ARG=""
  fi

  if [ $# -lt 1 ]; then
    #export ERRFLAG=1
    #doEXIT "This function requires more paramters [askYN]"
    if ! askYN "Continue" Y; then
      # bail out if the user does not answer Yes
      exit
    fi
    return
  fi

  # Set the default
  case "$2" in
    [Yy]|[Yy][Ee][Ss] )
      ANS="Y"
      ;;
    [Nn]|[Nn][Oo] )
      ANS="N"
      ;;
  esac

  while : ; do
    printf "%s (y/n [%s): ", "$1", "$ANS"
    if [ "x$AUTO_FLAG" = "xYES" ] ; then
      echo AUTO_FLAG is set... using default answer [$ANS]...
    else
      read -r $TIMEOUT_ARG -e myANS
    fi
    case "$myANS" in
      [Yy]|[Yy][Ee][Ss] )
        ANS="Y"
        break
        ;;
      [Nn]|[Nn][Oo] )
        ANS="N"
        break
        ;;
      * )
        break
        ;;
    esac  
  done
  export ANS
  if [ "x${ANS}" = "xY" ]; then
    return 0
  else
    return 1
  fi
}

############
chkID ()
############
{
# param $* = list of acceptible users
# example:
# if chkID myname root webuser; then
#    echo Good, the current user is in the acceptible list of users
# else
#    ERRFLAG=99
#    doEXIT "You are not an approved user..."
# fi
#
# this could also be done with [[ $EUID -ne 0 ]] && echo you need to be root
  while [ "$1" ]; do
    # consider "id -un" here - but is it portable?
    if id | cut -d" " -f 1 | grep "$1" >/dev/null; then
      myERRFLAG=0
      break 
    else
      myERRFLAG=1
      #doEXIT "You must be [$1] to use this script"
    fi
    shift
  done
  return $myERRFLAG 
}

##################
update_readmes ()
##################
{
	# echo $FUNCNAME
find ./ -name \*.py -print0 |\
if ! find ./ -name \*.py -print0 ; then
  echo No README.* files found! FAILING...
  exit 1
fi

# for i in $(ls "README.*"); do
find ./ -name "README.*" -print0 |\
  while read -r -d '' i; do
	echo Checking "$i" for Last modification info...

	if ! grep "Modified on:">/dev/null "$i"; then
    BASENAME=$(basename "$i")
		echo Did not find Last modified info
cat <<EOF>>"$i"

------- $BASENAME -------
    
Created on: $DTIME
Created by: $USER
    
----- Last Code Changes -----
    
Modified on: $DTIME
Modified by: $USER
   
------- $BASENAME -------
EOF
	else
		echo Found Last modification info
		sed -i "s/Modified on:.*/Modified on: $DTIME/" "$i"
		sed -i "s/Modified by:.*/Modified by: $USER/" "$i"
	fi

  echo $SLINE
	cat "$i"
  echo $SLINE
done

###
# do CHNAGELOG.prj while we are at it
# if ! [ -f CHANGELOG.prj ]; then
#   touch CHANGELOG.prj
#   echo "Created on:  $DTIME by: $USER" >CHANGELOG.prj
# fi
#   echo "Modified on: $DTIME by: $USER" >>CHANGELOG.prj
###
} 


##############
return_check()
##############
{
	export ERRFLAG=$1
  # echo "$FUNCNAME[0]" "$ERRFLAG"  
	[ "$ERRFLAG" -eq 0 ] || (echo FAILURE... ERRFLAG="$ERRFLAG"; exit "$ERRFLAG")
	echo PASSED...
	# echo ERRFLAG=$ERRFLAG
	return "$ERRFLAG"
}

# ##############
check_pyfiles()
# ##############
{
	# only checks the base prj dir
	echo "Checking any *.py files..."
	find ./ -name \*.py >/dev/null 2>&1 || return
  find ./ -name \*.py -print0 |\
		# while IFS= read -r -d $'\0' file; do
		while read -r -d '' file; do
			echo Running: echo 1 \| python3 -m doctest -v "$file" 
			# the echo here is to mock user input if needed ... does not affect tests that do not seek input
			echo 1 | python3 -m doctest -o FAIL_FAST "$file"
			return_check $?
			# use autopep8 --in-place --aggressive --aggressive <file>.py to fix some errors first
			echo Running autopep8 --inplace --aggressive --aggressive "$file"
			autopep8 --in-place --aggressive --aggressive "$file"  # to fix some errors first
			echo Running flake8 --max-line-length=150 "$file"
			flake8 --max-line-length=150 "$file"
			return_check $?
			echo $SLINE
		done
	echo Note: noqa=no quality assurance... can be used on a line to ignore an error eg: lambda: eample  # noqa: E731,E123
}

###############
function check_shfiles()
###############
{
  echo "Checking any *.sh files..."
	find ./ -name \*.sh >/dev/null 2>&1 || return
  find ./ -name \*.sh -print0 |\
		# while IFS= read -r -d $'\0' file; do
		while read -r -d '' file; do
		  echo Running: shellcheck "$file"
			shellcheck "$file"
			return_check $?
      echo $SLINE
		done
}

# ###########
do_install() 
# ##########
{
	echo "Running: ${FUNCNAME[0]}"
  cd "$(dirname "$0")" || echo "Could not cd..."
  # DIR=$(dirname "$0")
  BASENAME=$(basename "$0")
	echo PWD="$(pwd)"
	ln -s ../../"$0"  ../.git/hooks/pre-commit
	echo ln -s "$DIR/$BASENAME"  ../.git/hooks/pre-commit
  ls -l ../.git/hooks/pre-commit
	echo "Exiting...";exit 1
}


###################
# Main Code
#####################
handleOPTS "$@";shift $(( OPTIND - 1 )) # this is needed if you want to use more args
# 
echo '
++++++++
This is a pre-commit script
- Looks for and updates any README.* files with modified date info
- pre-processes *.py code etc

To skip this check: git commit --no-verify
++++++++
'

[ x$INSTALL = xYES ] && do_install 

update_readmes

check_pyfiles
check_shfiles

ERRFLAG=${ERRFLAG:-$?}
echo "Finished all checks...ERRFLAG=$ERRFLAG"

exit "$ERRFLAG"
### End of Script ###
