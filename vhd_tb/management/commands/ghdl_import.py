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
        try:
            udir = options.unisim_dir
        except:
            udir = ""
        try:
            wdir = options.work_dir
        except:
            wdir = ""
        try:
            src = options.source_dir
        except:
            src = ""

        p = ghdl_import(udir,wdir,src)
        print p
        return p

