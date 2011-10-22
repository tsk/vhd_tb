import os
import sys
import subprocess
from optparse import make_option,OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb.bsim import *
from vhd_tb.cutils import move_file

class Command(BaseCommand):
    help = "Run TestBench"
    args = "Project"
    option_list = (
        make_option("-w","--work-dir",action='store', dest='work_dir',default=""),
        make_option("-s","--stop-time", action='store', dest='stop_time',default="100ns"),
    )

    def __init__(self):
        pass

    def run_from_argv(self,argv):
        parser = self.create_parser(argv[0],argv[1])
        options, args = parser.parse_args(argv[2:])
        if args != []:
            return self.execute(args,options)
        else:
            self.print_help(argv[0],argv[1])
            sys.exit(1)
    def execute(self,args, options):
        try:
            wdir = options.work_dir
        except:
            wdir = ""
        try:
            arg = options.tb_name
        except:
            arg = args[0]
        try:
            stime = options.stop_time
        except:
            stime = "100ns"
        run_ghdl_tb(arg,stime,wdir)
        #if check_ghdl_error(p):
        #    sys.stderr.write("  "+p)
        #    sys.exit(1)
	#return p
