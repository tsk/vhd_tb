from vhd_tb.vhdlfile import vhdlfile
from vhd_tb.Templates import *

class port(object):
    def __init__(self,name,type_,size_,direction):
        self.type= type_
        self.size= size_
        self.direction =direction
        self.name=name
        self.ival = None

    def get_type(self):
        return self.type

    def get_size(self):
        return self.size

    def get_direction(self):
        return self.direction

    def get_ival(self):
        return self.ival

    def set_ival(self, val):
        self.ival = val

    def get_vhd_code_port(self):
        rang = ""
        if self.size > 1:
            rang = "(%s downto 0)"%(self.size-1)
        return "%s : %s %s %s"%(self.name,self.direction,self.type,rang)

    def get_vhd_code_signal(self):
        rang = ""
        ft="'"
        if self.size > 1:
            rang =  "(%s downto 0)"%(self.size-1)
            ft = '"'
        if self.ival != None:
            rang += ":= %s%s%s"%(ft,"{0:0>{1}}".format(bin(self.ival)[2:],self.size),ft)
        return "%s : %s %s %s"%(self.name,self.direction,self.type,rang)

class module_wrap(vhdlfile):
    def __init__(self, vhd_file):
        vhdlfile.__init__(self,vhd_file)
        self.__process_file()

    def __process_file(self):
        for port in self.__ports_dic:
            conf_port = pdic[p]
            setattr(self,p,port(p,conf_port[0],conf_port[1],conf_port[2]))

    def save_file_state(self):
        pass

class module_tb(module_wrap):
    def __init__(self, vhd_file, type_, temp_file = None):
        self.module_wrap.__init__(self,vhd_file)

    def write_tb_file(self):
        pass

    def run(self):
        pass

import os
import sys
from optparse import make_option, OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb.bsim import *
from vhd_tb.cutils import *
from vhd_tb.templates import set_config, set_source_control
from vhd_tb.management import call_command
import vhd_tb.vhdlfile

class tb_options(object):
    def __init__(self):
        self.__option_list = []

    def set_attrib(self, name, value):
        setattr(self,name,value)
        self.__option_list.append(name)

    def get_option_list(self):
        return self.__option_list


class TestBenchCommand(BaseCommand):
    help = "Run TestBench for ..."
    args =""
    file_ = ''
    TBConfig = {}
    TBSrcControl = {}
    stimuli_source = ''
    stm_in_file = ''
    commands = {'no_change':['ghdl_run_tb','gtkwave'],
               'source_change':['ghdl_compile',
                                'ghdl_run_tb','gtkwave'],
               'ports_change': ['create_tb'],
              }
    pre_actions = {'no_change' : ['gen_tbl'],
                   'source_change' : ['replace_TBSrcControl','gen_tbl'],
                   'ports_change': [],
                  }
    tb_options_list = ['tb_name','source_dir','work_dir',
                      'unisim_dir','stop_time']
    option_list = (
        make_option('-w','--work-dir',action='store', dest='work_dir',default='', help="Work dir"),
        make_option('-u','--unisim-dir',action='store', dest='unisim_dir',default='', help='Unisim dir'),
        make_option('-s','--stop-time',action='store', dest='stop_time',default='',help="stop time e.g. 100ns"),
    )

    def __init__(self):
        self.source_dir = self.TBConfig['source_dir']
        self.file_name = self.TBConfig['file_name']
        self.tb_name = self.TBConfig['tb_name']

    def gen_tbl(self):
        tables = self.TBConfig['gconfig']['tables']
        f = open(self.source_dir+'/'+self.file_name,'r')
        buf = f.read()
        f.close()
        vhd_file = vhdlfile.vhdlfile(buf)
        self.stimuli_source.get_table(tables,vhd_file.get_ports_dic(),self.tb_name)

    def replace_TBSrcControl(self):
        self.stimuli_source.replace_TestBenchSrcControl(self.__source_control,
                                                        self.file_)

    def run_from_argv(self, argv):
        parser = self.create_parser(argv[0],argv[1])
        options, args = parser.parse_args(argv[2:])
        return self.execute(args,options)

    def execute(self,args,options):
        tb_options_ = tb_options()
        for opt in self.tb_options_list:
            tb_options_.set_attrib(opt,self.TBConfig[opt])

        if options.work_dir != '':
            tb_options_.work_dir = options.work_dir
        if options.unisim_dir != '':
            tb_options_.unisim_dir = options.unisim_dir
        if options.stop_time != '':
            tb_options_.stop_time = options.stop_time

        flag,flag_src,new_hash, deepfiles_hash = self.stimuli_source.check_source_changes(self.TBSrcControl)
        self.__source_control = set_source_control(new_hash[0],new_hash[1],new_hash[2],deepfiles_hash)

        if flag == True:
            schd = 'ports_change'
            tb_options_.set_attrib('add_sheet',True)
            tb_options_.set_attrib('file_name',self.file_name)
            tb_options_.set_attrib('prefix','bak')
            tb_options_.set_attrib('tb_format',self.stimuli_source.get_format())
        elif flag_src == True:
            schd = 'source_change'
            call_command('ghdl_import',tb_options_)
        else:
            schd = 'no_change'

        for action in self.pre_actions[schd]:
            getattr(self,action)()

        for action in self.commands[schd]:
            call_command(action,tb_options_)
