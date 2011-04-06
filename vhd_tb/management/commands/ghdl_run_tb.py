import os
import sys
import subprocess
from optparse import make_option,OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb.bsim import *

class Command(BaseCommand):
    help = "Run TestBench"
    args = "Project"
    option_list = (
        make_option("-w","--work-dir",action='store', dest='work_dir',default=""),
        make_option("-u","--unisim-dir", action='store', dest='unisim_dir',default=""),
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
        p = ghdl_compile(args[0],options.unisim_dir,options.work_dir)
	return p
