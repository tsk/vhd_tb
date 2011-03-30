#!/usr/bin/env python

import sys
import os
import getopt
from vhd_tb import cutils

def options(argv):
    try:
        opts, args = getopt.getopt(argv, "i:p:",["file","path_dest"])
    except getopt.GetoptError,err:
        print str(err)

    for o,a in opts:
        if o in ("-i","--file"):
	    fname = a
	    dst = os.path.basename(fname).split(".")[0]
	if o in ("-p","--path_dest"):
	    dst = a
    if not os.path.isdir(dst):
   	os.mkdir(dst)

    if fname != "" or fname !=None:
   	cutils.isolate_file(fname,dst)

if __name__ == "__main__":
   options(sys.argv[1:])
