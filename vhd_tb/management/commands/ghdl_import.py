import os
import sys
import subprocess
from optparse import make_option,OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb.bsim import *

class Command(BaseCommand):
    help = "Import VHD Files"
    args = ""
    option_list = (
        make_option("-s","--source-dir",action='store',dest='source_dir',default=""),
        make_option("-w","--work-dir",action='store', dest='work_dir',default=""),
        make_option("-u","--unisim-dir", action='store', dest='unisim_dir',default=""),
    )
    def __init__(self):
        pass

    def execute(self,args, options):
        p = ghdl_import(options.unisim_dir,options.work_dir,options.source_dir)
        return p

if __name__ == "__main__":
    p = Command()
    args = sys.argv[:]
    p.run_from_argv(args)
