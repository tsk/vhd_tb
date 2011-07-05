import os
import sys
from optparse import make_option, OptionParser
from vhd_tb.management.base import BaseCommand
from vhd_tb import vhdlfile
from vhd_tb.cutils import *
from vhd_tb.templates import templates_dir, TemplateBuf, tb_conf_str, tb_source_control
from vhd_tb.templates import Template, clkgt, vhdl_headers, set_source_control, set_config

def return_process_tbl(gconfig,pdic, temp_buf, stimuli_f, tb_name,source_dir, format_type):
    tables = gconfig['tables']
    process_data = ""
    stimuli_data = ""
    tb_periods = gconfig['tb_period']
    for table in tables:
        template = TemplateBuf(temp_buf)
        stemplate = TemplateBuf(stimuli_f)
        ports = tables[table]
        vector_conf = get_vector_conf(ports,pdic)
        max_size = vector_conf[2]
        file_var_name = 'data_in_%s'%table
        tbl_file = '%s_%s_%s.tbl'%(tb_name,format_type,table)
        data = ""
        for port in ports:
            (msb,lsb) = vector_conf[1][port]
            if msb == lsb:
                data += "\t%s <= data_s(%s);\n"%(port,lsb)
            else:
                data += "\t%s <=data_s(%s downto %s);\n"%(port,msb,lsb)
        template.set_property_value('process_name',table+"_process")
        template.set_property_value('data',data)
        template.set_property_value('max',max_size)
        template.set_property_value('max-1',max_size-1)
        if len(tb_periods) == 1:
            period = tb_periods['tb']
        else:
            period = tb_periods[table]
        template.set_property_value('PERIOD',period)
        template.set_property_value('file_var_name',file_var_name)
        process_data += template.return_temp_buf()
        stemplate.set_property_value('name',file_var_name)
        stemplate.set_property_value('file_name',source_dir+'/'+tbl_file)
        stimuli_data += stemplate.return_temp_buf()

    return process_data,stimuli_data

input_formats = {'xls':'tbl',
                 'xlsx':'tbl',
                 'ods':'tbl',
                }

input_format_module = {'xls':'vhd_tb.sheets',
                         'xlsx':'vhd_tb.sheets',
                         'ods':'vhd_tb.sheets',
                        }

process = {'tbl': [Template(templates_dir+'/process_tbl.tmp').return_temp_buf(),
                   return_process_tbl,
                   'file <name> : text open read_mode is \"<file_name>\";\n'],
           'normal': '<process_name>:process\n<data>',
          }

input_formats_h = '/'.join(input_formats)

def return_signals_and_gen_clk_code(vhdfile,gconfig):
    initial_state_dic = {}
    gen_clk_code = ""
    constant_time_code = ""
    for clk in gconfig['clks_period']:
        template = TemplateBuf(clkgt)
        clk_period,istate = gconfig['clks_period'][clk]
        initial_state_dic[clk] = istate
        template.set_property_value('clk',clk)
        template.set_property_value('clk_period',"%s_PERIOD"%(clk))
        gen_clk_code += template.return_temp_buf()+'\n'
        constant_time_code += "constant %s_PERIOD : TIME := %s\n;"%(clk,clk_period)

    signals_code = vhdfile.gen_signals_code(initial_state_dic)
    return gen_clk_code, signals_code, constant_time_code

def vhd_tb_file(gconfig, vhdfile,tb_name,source_dir,format_type):
    headers = vhdl_headers['normal']
    Name = vhdfile.get_name()
    Component = vhdfile.get_component_def()
    clock_gen, signals, const_time = return_signals_and_gen_clk_code(vhdfile,gconfig)
    instance = vhdfile.gen_instance("UTT0")
    p = process[input_formats[format_type]]
    process_code,stimuli_code = p[1](gconfig,vhdfile.get_ports_dic(),
                                     p[0],p[2],'tb_'+Name,
                                     source_dir,format_type)
    vhd_tb = Template(templates_dir+"/tb_tbl.vhd")
    vhd_tb.set_property_value('headers',headers)
    vhd_tb.set_property_value('Name',tb_name)
    vhd_tb.set_property_value('component',Component)
    vhd_tb.set_property_value('clock_gen',clock_gen)
    vhd_tb.set_property_value('signals',signals+const_time)
    vhd_tb.set_property_value('instance',instance)
    vhd_tb.set_property_value('process',process_code)
    vhd_tb.set_property_value('stimuli_input',stimuli_code)

    return vhd_tb.return_temp_buf()


def command_tb_file(tb_name, config,source_control, format_type):
    data = Template(templates_dir+"/TestBenchCommandTemplate.py.temp")
    data.set_property_value('config',config)
    data.set_property_value('source_control',source_control)
    data.set_property_value('tb_name', tb_name)
    data.set_property_value('stimuli_source',format_type)
    return data.return_temp_buf()

class Command(BaseCommand):
    help = "Create a TestBench from vhdl file"
    args = "VHDL_File"
    option_list = (
        make_option("-f","--format", action='store', dest='tb_format',
                    default='manual',help=input_formats_h),
        make_option("-w","--work-dir", action='store', dest='work_dir',
                    default='',help="Work dir"),
        make_option("-u","--unisim-dir",action='store',dest='unisim_dir',
                    default='',help="Unisim dir"),
        make_option("-s","--stop-time",action='store',dest = 'stop_time',
                    default='100ns', help="Default simulation stop time"),
    )

    def __init__(self):
        pass

    def run_from_argv(self, argv):
        parser = self.create_parser(os.path.basename(argv[0]),argv[1])
        options, args = parser.parse_args(argv[2:])
        if args !=[]:
            return self.execute(args, options)
        else:
            self.print_help(argv[0],argv[1])
            sys.exit(1)

    def execute(self, args, options):
        try:
            flag_add_sheet = options.add_sheet
            file_name = options.file_name
            source_dir = options.source_dir
            fivhd = '/'.join([source_dir,file_name])
        except:
            flag_add_sheet = False
            file_name = os.path.basename(args[0])
            source_dir = './'+os.path.dirname(args[0])
            fivhd = args[0]
        from vhd_tb.management import call_command        
        from vhd_tb.vhd import tb_options
        opt = tb_options()
        opt.set_attrib('work_dir',options.work_dir)
        opt.set_attrib('unisim_dir',options.unisim_dir)
        opt.set_attrib('source_dir',source_dir)

        call_command('ghdl_import',opt)
        f = open(fivhd,'r')
        buf = f.read()
        f.close()
        command_dir = "commands"
        if os.path.exists(command_dir) == False:
            os.mkdir(command_dir)
        if options.work_dir != "":
            if os.path.exists(options.work_dir) == False:
                os.mkdir(options.work_dir)
        #Create vhd TestBenchCommand
        vf = vhdlfile.vhdlfile(buf)
        gconfig = tb_config(vf.get_input_ports_list(),vf.get_clock_sources())
        tb_name = 'tb_%s'%vf.get_name().lower()
        command_name = "%s_%s.py"%(tb_name,options.tb_format)

        sconfig = set_config(file_name,tb_name,
                            gconfig,vf,
                            source_dir,
                            options.work_dir,
                            options.unisim_dir,
                            options.stop_time
                            )
        hashes = vf.get_hashes()
        deepfiles_hash = get_related_files_hashes(fivhd)
        source_control = set_source_control(hashes[0],hashes[1],hashes[2],deepfiles_hash)
        cmd_file = command_tb_file(tb_name,sconfig,source_control,options.tb_format)
        f = open(command_dir+'/'+command_name,'w')
        f.write(cmd_file)
        f.close()
        #Create vhd TestBench file
        vhd_tb = vhd_tb_file(gconfig,vf,tb_name,source_dir,options.tb_format)
        f = open('/'.join([source_dir,tb_name+".vhd"]),'w')
        f.write(vhd_tb)
        f.close()
        pymodname = input_format_module[options.tb_format]
        #Create stimuli source file
        module = __import__(pymodname)
        components = pymodname.split('.')
        for comp in components[1:]:
            module = getattr(module,comp)
        doc = getattr(module,options.tb_format)(source_dir+'/'+tb_name+'.'+options.tb_format)
        if flag_add_sheet == False:
            doc.create(gconfig['tables'],vf.get_ports_dic())
        else:
            doc.add_sheet(options.prefix, gconfig['tables'], vf.get_ports_dic())

        opt.set_attrib('tb_name',tb_name)
        call_command('ghdl_import',opt)
        call_command('ghdl_compile',opt)
        tmp1 = tb_name+'.'+options.tb_format
        tmp2 = tb_name+'_'+options.tb_format
        print "Edit %s file in sources dir, after that run \'vhd_tb.py %s\' command"%(tmp1,tmp2)
