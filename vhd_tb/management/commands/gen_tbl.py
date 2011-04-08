import os
import sys
import subprocess
from optparse import make_option,OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb import pvhdopt

class Command(BaseCommand):
    help = 'Test Bench Template Generator'
    args = 'VHDL_File'
    option_list = (
        make_option('-f','--format',action='store',dest='tb_format',default='manual', help="xls,ods"),
        make_option('-r','--recreate', action='store_true',dest='replace', default=False, help="Reload File"),
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
            tb_format = options.tb_format
        except:
            tb_format = "manual"
        try:
            replace = options.replace
        except:
            replace = False
        try:
            arg = options.filename
        except:
            arg = args[0]
        pvhdopt.command_dic[tb_format](arg,replace)
	return None
