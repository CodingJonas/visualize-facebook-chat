 # @package constants
# For better error messages
import sys
import traceback
import os
import re

DARK_BLUE="\033[34m"
RED = '\033[91m'
GREEN = '\033[92m'
YELLOW = '\033[93m'
LIGHT_PURPLE = '\033[94m'
PURPLE = '\033[95m'
CYAN = '\033[96m'
END = '\033[0m'

##
# @brief overwrite the system exception output for a more responsive answer
#
# @param type
# @param value
# @param tb
def my_excepthook(type, value, tb):
    lines = traceback.format_list(traceback.extract_tb(tb))
    def shorten(match):
        return 'File "{}"'.format(os.path.basename(match.group(1)))
    lines = [re.sub(r'File "([^"]+)"', shorten, line) for line in lines]
    _print_color(lines)
    # print(''.join(lines))
    print(RED + '{}: {}'.format(type.__name__, value) + END)
    print("--------------------------------------------")

sys.excepthook = my_excepthook

def _print_color(lines):
    for l in lines:
        for i in range(len(l)-1):
            if l[i:i+4]=="line":
                i +=5
                # Find the length of the number
                numLen = 0
                while l[i+numLen].isdigit():
                    numLen +=1

                # Find the length of the function
                funLen = 0
                while not l[i+numLen+4 + funLen]=="\n":
                    funLen+=1

                l = ''.join([DARK_BLUE+"->"+END,
                        l[2:i],
                        YELLOW+"{}".format(l[i:i+numLen])+END,
                        l[i+numLen:i+numLen+5],
                        LIGHT_PURPLE+"{}".format(l[i+numLen+5:i+numLen+5+funLen])+END,
                        CYAN+"{}".format(l[i+numLen+5+funLen:])+END])
                print(l,end="")
                break
    print("")
