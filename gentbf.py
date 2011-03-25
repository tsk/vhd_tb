import sys
import os
import vhdlfile
import ooolib
import getopt
import re

py_file = """
"""
tb_file = """
library ieee;
use ieee.std_logic_1164.all;
library std;
use std.textio.all;
use ieee.numeric_std.all;
use ieee.std_logic_arith.all;
use ieee.std_logic_unsigned.all;

entity <Name> is

end <Name>;

architecture behave of <Name> is

<component>

<signals>

file data_in : text open read_mode is "<file_name>";
begin
<clock_gen>
<instance>
  read_file: process
    variable data_line : line;
    variable data_int : integer;
    variable data_s : std_logic_vector(<max-1> downto 0);
    begin
      while not endfile(data_in) loop
        readline(data_in,data_line);
        read(data_line, data_int);
        data_s := std_logic_vector(to_unsigned(data_int,<max>));
<data>
        wait for <PERIOD>;
      end loop;
      wait;
  end process;

end behave;
"""

clkgt = """gen_clk_<clk>: process(<clk>)
begin
    <clk> <= not <clk> after <PERIOD>/2;
end process;
"""
def _xls_file(vhdl_file, recreate_file = False):
    tb_name = vhdl_file.split(".")[0]
    if os.path.isfile(tb_name+".xls") and recreate_file == False:
        _gen_table_from_xls(tb_name+".xls",vhdl_file)
    else:
        import xlwt
        f = open(vhdl_file,'r')
        buf = f.read()
        f.close()
        vf = vhdlfile.vhdlfile(buf)
        modname = vf.get_name()
        pdic = vf.get_ports_dic()
        cname = []
        ctype = []
        doc = xlwt.Workbook()
        sheet = doc.add_sheet("TB")
        i = 0
        clk_source = _get_clock_sources(buf,pdic)
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                sheet.write(0,i,port+'('+`pdic[port][2]`+')')
                i+=1
        #Get Vector Size
        genclk,period = _get_genclk(clk_source)
        vsize = 0
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                vsize+=pdic[port][2]
        tb_f = tb_file.replace("<Name>","tb_"+modname)
        tb_f = tb_f.replace("<max>",`vsize`)
        tb_f = tb_f.replace("<max-1>",`vsize-1`)
        component = vf.get_component_def()
        signals = vf.gen_signals_code()
        instance = vf.gen_instance("UTT0")
        tb_f = tb_f.replace("<component>",component)
        tb_f = tb_f.replace("<signals>",signals+period)
        tb_f = tb_f.replace("<instance>",instance)
        tb_f = tb_f.replace("<file_name>",tb_name+".tbl")
        tb_f = tb_f.replace("<clock_gen>", genclk)
        tb_f = tb_f.replace("<PERIOD>","100 ns")
        data = ""
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                low = vsize-1-(pdic[port][2]-1)
                if vsize-1 == low:
                    data+="\t"+port+" <= data_s("+`low`+");\n"
                else:
                    data+="\t"+port+" <= data_s("+`vsize-1`+" downto "+`low`+");\n"
                vsize = low
        tb_f = tb_f.replace("<data>",data)
        f = open("tb_"+tb_name+".vhd",'w')
        f.write(tb_f)
        f.close()
        doc.save(tb_name+".xls")
        print "Edit the Test Bench Source File and re run this command"

def _gen_table_from_xls(tb_fname,vhdl_file):
    import xlrd
    doc = xlrd.open_workbook(tb_fname)
    sheet = doc.sheet_by_index(0)
    f = open(vhdl_file,'r')
    buf = f.read()
    f.close()
    vf = vhdlfile.vhdlfile(buf)
    pdic = vf.get_ports_dic()
    vect_dic = {}
    vect_mult = []
    vsize = 0
    clk_source = _get_clock_sources(buf,pdic)
    #Get Vector Size
    for port in pdic:
        if pdic[port][1] in ("in","IN") and port not in clk_source:
            vsize+=pdic[port][2]
    #Get mult
    for port in pdic:
        if pdic[port][1] in ("in","IN") and port not in clk_source:
            low = vsize-1-(pdic[port][2]-1)
            vect_dic[port] = (vsize-1,low)
            vect_mult.append(pow(2,low))
            vsize = low
    #Get Data from spreadsheet an save to text file
    f = open(tb_fname.split(".")[0]+".tbl","w")
    rows = sheet.nrows
    cols = sheet.ncols
    for row in range(1,rows):
        data = 0
        for col in range(cols):
            intr = sheet.cell(row,col).value
            print intr
            data+= int(intr)*vect_mult[col]
        f.write(`data`+"\n")

    f.close()

def _manual_tb(vhdl_file):
    pass
def _custom(vhdl_file):
    pass
def _ods_file(vhdl_file, recreate_file = False):
    tb_name = vhdl_file.split(".")[0]
    if os.path.isfile(tb_name+".ods") and recreate_file == False:
        _gen_table_from_ods(tb_name+".ods",vhdl_file)
    else:
        f = open(vhdl_file,'r')
        buf = f.read()
        f.close()
        vf = vhdlfile.vhdlfile(buf)
        modname = vf.get_name()
        pdic = vf.get_ports_dic()
        cname = []
        ctype = []
        doc = ooolib.Calc("TB")
        i = 1
        clk_source = _get_clock_sources(buf,pdic)           
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                doc.set_cell_value(i, 1, "string", port+'('+`pdic[port][2]`+')')
                i+=1
        #Get Vector Size
        genclk,period = _get_genclk(clk_source)
        vsize = 0
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                vsize+=pdic[port][2]

        tb_f = tb_file.replace("<Name>","tb_"+modname)
        tb_f = tb_f.replace("<max>",`vsize`)
        tb_f = tb_f.replace("<max-1>",`vsize-1`)
        component = vf.get_component_def()
        signals = vf.gen_signals_code()
        instance = vf.gen_instance("UTT0")
        tb_f = tb_f.replace("<component>",component)
        tb_f = tb_f.replace("<signals>",signals+period)
        tb_f = tb_f.replace("<instance>",instance)
        tb_f = tb_f.replace("<file_name>",tb_name+".tbl")
        tb_f = tb_f.replace("<clock_gen>", genclk)
        tb_f = tb_f.replace("<PERIOD>","100 ns")
        data = ""
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                low = vsize-1-(pdic[port][2]-1)
                if vsize-1 == low:
                    data+="\t"+port+" <= data_s("+`low`+");\n"
                else:
                    data+="\t"+port+" <= data_s("+`vsize-1`+" downto "+`low`+");\n"
                vsize = low
        tb_f = tb_f.replace("<data>",data)
        f = open("tb_"+tb_name+".vhd",'w')
        f.write(tb_f)
        f.close()
        doc.save(tb_name+".ods")
        print "Edit the Test Bench Source File and re run this command"

def _gen_table_from_ods(tb_fname,vhdl_file):
    doc = ooolib.Calc(opendoc = tb_fname)
    doc.set_sheet_index(0)
    (cols, rows) = doc.get_sheet_dimensions()
    f = open(vhdl_file,'r')
    buf = f.read()
    f.close()
    vf = vhdlfile.vhdlfile(buf)
    pdic = vf.get_ports_dic()
    vect_dic = {}
    vect_mult = []
    vsize = 0
    clk_source = _get_clock_sources(buf,pdic)
    #Get Vector Size
    for port in pdic:
        if pdic[port][1] in ("in","IN") and port not in clk_source:
            vsize+=pdic[port][2]
    #Get mult
    for port in pdic:
        if pdic[port][1] in ("in","IN") and port not in clk_source:
            low = vsize-1-(pdic[port][2]-1)
            vect_dic[port] = (vsize-1,low)
            vect_mult.append(pow(2,low))
            vsize = low
    #Get Data from spreadsheet an save to text file
    f = open(tb_fname.split(".")[0]+".tbl","w")
    for row in range(2,rows+1):
        data = 0
        for col in range(1, cols+1):
            intr = doc.get_cell_value(col,row)
            data+= int(intr[1])*vect_mult[col-1]
        f.write(`data`+"\n")

    f.close()


def _python_script(vhdl_file, recreate_file = False):
    tb_name = vhdl_file.split(".")[0]
    if os.path.isfile(tb_name+".py") and recreate_file == False:
        _gen_table_from_ods(tb_name+".ods",vhdl_file)
    else:
        f = open(vhdl_file,'r')
        buf = f.read()
        f.close()
        vf = vhdlfile.vhdlfile(buf)
        modname = vf.get_name()
        pdic = vf.get_ports_dic()
        cname = []
        ctype = []
        doc = ooolib.Calc("TB")
        i = 1
        clk_source = _get_clock_sources(buf,pdic)           
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                doc.set_cell_value(i, 1, "string", port+'('+`pdic[port][2]`+')')
                i+=1
        #Get Vector Size
        period = "\n"
        genclk = ""
        for clk in clk_source:
            period += "constant PERIOD_"+clk+" : time:= 100 ns;\n"
            clk_c = clkgt.replace("<clk>",clk)
            clk_c = clk_c.replace("<PERIOD>","PERIOD_"+clk)
            genclk += clk_c
        vsize = 0
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                vsize+=pdic[port][2]

        tb_f = tb_file.replace("<Name>","tb_"+modname)
        tb_f = tb_f.replace("<max>",`vsize`)
        tb_f = tb_f.replace("<max-1>",`vsize-1`)
        component = vf.get_component_def()
        signals = vf.gen_signals_code()
        instance = vf.gen_instance("UTT0")
        tb_f = tb_f.replace("<component>",component)
        tb_f = tb_f.replace("<signals>",signals+period)
        tb_f = tb_f.replace("<instance>",instance)
        tb_f = tb_f.replace("<file_name>",tb_name+".tbl")
        tb_f = tb_f.replace("<clock_gen>", genclk)
        tb_f = tb_f.replace("<PERIOD>","100 ns")
        data = ""
        for port in pdic:
            if pdic[port][1] in ("in","IN") and port not in clk_source:
                low = vsize-1-(pdic[port][2]-1)
                if vsize-1 == low:
                    data+="\t"+port+" <= data_s("+`low`+");\n"
                else:
                    data+="\t"+port+" <= data_s("+`vsize-1`+" downto "+`low`+");\n"
                vsize = low
        tb_f = tb_f.replace("<data>",data)
        f = open("tb_"+tb_name+".vhd",'w')
        f.write(tb_f)
        f.close()
        doc.save(tb_name+".ods")
        print "Edit the Test Bench Source File and re run this command"

def _get_clock_sources(buf, pdic):
    exp = "[rising|falling]_edge\((.*?)\)"
    r = re.compile(exp, re.I)
    clk_s = r.findall(buf)
    clk_s = list(set(clk_s))
    return clk_s

def _get_genclk(clk_source):
    genclk = ""
    period = "\n"
    for clk in clk_source:
        t = raw_input("Set PERIOD for "+clk+" :")
        period += "constant PERIOD_"+clk+" : time:= "+t+";\n"
        clk_c = clkgt.replace("<clk>",clk)
        clk_c = clk_c.replace("<PERIOD>","PERIOD_"+clk)
        genclk += clk_c
    return genclk, period

command_dic = {"xls": _xls_file,
               "ods": _ods_file,
               "py": _python_script,
               #"c": _c_program,
               #"cpp": _cpp_program,
               #"cpp_stl": _cpp_stl_program,
               #"pas": _pascal_program,
               #"f": _fortran_program,
               #"oct": _octave_script,
               #"manual":_manual_tb,
               #"custom": _custom,
              }

def project_options(argv):
    Verbose = False
    try:
        opts, args = getopt.getopt(argv, "i:f:r:o:",["file","format","recreate_file","signals_order"])
    except getopt.GetoptError, err:
        print str(err)
    tb_i_format = 'ods'
    replace = False
    for o,a in opts:
        if o in ("-i","--file"):
            vhdl_file = a
        if o in ("-f","--format"):
            if a in command_dic:
                tb_i_format = a
            else:
                print "Format not supported.\nAvailable formats: xdl, ods, manual and custom"
                break;
        if o in ("-r","--recreate_file"):
            replace=True
    command_dic[tb_i_format](vhdl_file,replace)



if __name__ == "__main__":
    project_options(sys.argv[1:])
