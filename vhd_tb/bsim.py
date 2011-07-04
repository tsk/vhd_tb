import os
import sys
import re
import subprocess

def ghdl_import(unisim_dir = "", work_dir = "", sources_dir = ""):
    cmd = "ghdl -i --ieee=synopsys"
    if unisim_dir != "":
        cmd+=" -P"+unisim_dir
    if work_dir != "":
        cmd+= " --workdir="+work_dir
    path = os.getcwd()
    cmd+=" "+os.path.join(sources_dir,"*.vhd")
    s = subprocess.Popen(cmd,shell=True,stderr=subprocess.PIPE)
    s1,s2=s.communicate()
    if s2 != '':
        print s2
        sys.exit(1)
    return s2

def ghdl_compile(project, unisim_dir = "", work_dir = ""):
    if unisim_dir != "":
        unisim_dir = "-P"+unisim_dir
    if work_dir != "":
        work_dir = "--workdir="+work_dir
    s = subprocess.Popen("ghdl -m --ieee=synopsys "+unisim_dir+" "+work_dir+" "+project,
                        shell=True, stderr = subprocess.PIPE)
    s1,s2=s.communicate()
    return s2

def ghdl_check_syntax(file_,unisim_dir =""):
    if unisim_dir != "":
        unisim_dir = "-P"+unisim_dir
    s = subprocess.Popen("/usr/bin/ghdl -c --ieee=synopsys "+file_,shell=True)
    s.communicate()

def run_ghdl_tb(tb,time,wdir):
    tb2 = os.path.basename(tb)
    dir_ = os.path.dirname(tb)
    if os.path.exists(tb) == False:
        dir_ = wdir
    cmd = os.path.join(dir_,tb2)+" --stop-time="+time+" --vcd="+os.path.join(dir_,tb2)+".vcd"
    s = subprocess.Popen(cmd,shell=True, stderr = subprocess.PIPE)
    s1,s2 = s.communicate()
    return s2

def gtkwave(tb,wdir):
    tb2 = os.path.basename(tb)
    dir_ = os.path.dirname(tb)
    if os.path.exists(tb) == False:
        dir_ = wdir
    cmd = "gtkwave "+os.path.join(dir_,tb2)+".vcd "+os.path.join(dir_,tb2)+".trace"
    s = subprocess.Popen(cmd,shell=True, stderr = subprocess.PIPE)
    s1,s2 = s.communicate()
    return s2

def check_ghdl_error(p):
    error = False
    if p != "":
        exp = "(.*)error(.*)"
        r = re.compile(exp,re.I)
        errors = r.findall(p)
        exp = "(.*)bound(.*)"
        r = re.compile(exp,re.I)
        not_bounds =r.findall(p)
        if errors != [] or not_bounds != []:
            error = True
    return error

if __name__ == "__main__":
    #Test code
    print "Importing vhdl Files"
    p = ghdl_import("","","")
    if p != "":
        print p
        sys.exit()
    print "Compiling"
    p = ghdl_compile("tb_wbDH13","","")
    if p != "":
        exp = "(.*)error(.*)"
        r = re.compile(exp,re.I)
        errors = r.findall(p)
        exp = "(.*)bound(.*)"
        r = re.compile(exp,re.I)
        not_bounds =r.findall(p)
        if errors != [] or not_bounds != []:
            for error in errors:
                print error[0]+" "+error[1]
            for bound in not_bounds:
                print bound[0]+ " " + bound[1]
            sys.exit()
    print "Running TestBench"
    p = run_ghdl_tb("./tb_wbdh13","1200ns")
    print p

