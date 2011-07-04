import re
import os

templates_dir =('/').join([os.path.dirname(os.path.abspath(__file__)),'templates'])

#Templates for TestBenchs Configs
tb_conf_str = ''''file_name' : <file_name>,
'module_name' : <module_name>,
'tb_name' : <tb_name>,
'gconfig' : <gconfig>,
'work_dir' : <work_dir>,
'source_dir' : <source_dir>,
'unisim_dir' : <unisim_dir>,
'stop_time' : <stop_time>,'''
tb_source_control = ''''hash_src' : <hash_src>,
'hash_src_ports': <hash_src_ports>,
'hash_ind_ports' : <hash_ind_ports>,
'deepfiles_hash' : <deepfiles_hash>'''

clkgt = '''gen_clk_<clk>: process(<clk>)
begin
    <clk> <= not <clk> after <clk_period>/2;
end process;
'''

vhdl_headers ={'normal':'''library ieee;
use ieee.std_logic_1164.all;
library std;
use std.textio.all;
use ieee.numeric_std.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;
''',
               'unisim': "",
              }

def set_config(file_name,tb_name,gconfig,vhdfile,source_dir,
               work_dir,unisim_dir,stop_time):
    data = TemplateBuf(tb_conf_str)
    conf_dic = {}
    conf_dic['file_name'] = `file_name`
    conf_dic['source_dir'] = `source_dir`
    conf_dic['module_name'] = `vhdfile.get_name()`
    conf_dic['tb_name'] = `tb_name`
    conf_dic['gconfig'] = gconfig
    conf_dic['work_dir'] = `work_dir`
    conf_dic['unisim_dir'] = `unisim_dir`
    conf_dic['stop_time'] = `stop_time`
    for conf in conf_dic:
        data.set_property_value(conf,conf_dic[conf])
    return data.return_temp_buf()

def set_source_control(hash_src, hash_src_ports, hash_ind_ports,deepfiles_hash):
    data = TemplateBuf(tb_source_control)
    data.set_property_value('hash_src',`hash_src`)
    data.set_property_value('hash_src_ports', `hash_src_ports`)
    data.set_property_value('hash_ind_ports',hash_ind_ports)
    data.set_property_value('deepfiles_hash',deepfiles_hash)

    return data.return_temp_buf()

class TemplateBuf:
    def __init__(self, temp_buf):
        self.__temp_buf = temp_buf
        exp = "<([a-z|A-Z].*?)>"
        r = re.compile(exp,re.I)
        l = r.findall(self.__temp_buf)
        self.params = list(set(l))

    def get_params(self):
        return self.params

    def __reload_params(self):
        exp = "<([a-z|A-Z].*?)>"
        r = re.compile(exp,re.I)
        l = r.findall(self.__temp_buf)
        self.params = list(set(l))

    def set_property_value(self, name = '', value = ''):
        if not isinstance(value,str):
            value = `value`
        self.__temp_buf = self.__temp_buf.replace("<"+name+">",value)
        self.__reload_params()

    def return_temp_buf(self):
        return self.__temp_buf

    def save_file(self, file_name):
        out_file = open(file_name,'w')
        out_file.write(self.__temp_buf)
        out_file.close()

class Template(TemplateBuf):
    def __init__(self, template_file):
        temp = open(template_file,'r')
        self.__temp_buf = temp.read()
        temp.close()
        TemplateBuf.__init__(self,self.__temp_buf)


