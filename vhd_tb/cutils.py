import os
import sys
import shutil
import hashlib
from vhd_tb import vhdlfile

def isolate_file(file, dst):
    fdic = {}
    if os.path.exists(file):
        files_in_dir = []
        abspath = os.path.abspath(file)
	dname = os.path.dirname(abspath)
	for f in os.listdir(dname):
	    if os.path.isfile(os.path.join(dname,f)):
		if f.split(".")[1] in ("vhdl","VHDL","vhd","VHD"):
		    files_in_dir.append(os.path.join(dname,f))
	ifdic = {}
	fi = open(file)
	fb = fi.read()
	fi.close()
	fvhd = vhdlfile.vhdlfile(fb)
	submodules = fvhd.get_submodules()
        shutil.copy(file,dst)
	get_related_files(file,submodules,files_in_dir,dst)
	

def get_related_files(file, submodules, files_in_dir,dst):
    for f in files_in_dir:
        fi = open(f)
	fb = fi.read()
	fi.close()
	fvhd = vhdlfile.vhdlfile(fb)
	modname = fvhd.get_name()
	if modname in submodules:
	    shutil.copy(f,dst)
	    get_related_files(f,fvhd.get_submodules(),files_in_dir,dst)

def get_related_files_hashes(file, fdic = {} , files_in_dir=[], submodules = []):
    if files_in_dir == []:
        if os.path.exists(file):
            abspath = os.path.abspath(file)
            dname = os.path.dirname(abspath)
            for f in os.listdir(dname):
                if os.path.isfile(os.path.join(dname,f)):
                    if f.split(".")[1] in ("vhdl","VHDL","vhd","VHD"):
                        files_in_dir.append(os.path.join(dname,f))
        fi = open(file)
        fb = fi.read()
        fi.close()
        fvhd = vhdlfile.vhdlfile(fb)
        submodules = fvhd.get_submodules()

    for f in files_in_dir:
        fi = open(f)
        fb = fi.read()
        fi.close()
        hash_ = hashlib.sha1(fb).hexdigest()
        fvhd = vhdlfile.vhdlfile(fb)
        modname = fvhd.get_name()
        if modname in submodules:
            fdic[`os.path.basename(f)`] = hash_
            fdic = get_related_files_hashes(f,fdic,files_in_dir,
                                            fvhd.get_submodules())

    return fdic



def move_file(file_, dest):
    if os.path.exists(file_):
        if os.path.exists(dest):
            shutil.copy(file_, dest)
            os.remove(file_)

def compress(file_):
    import gzip
    import binascii
    f = open(file_,'rb')
    buf = f.read()
    f.close()
    f = gzip.open('tmp.txt.gz','wb')
    f.write(buf)
    f.close()
    f = open('tmp.txt.gz','rb')
    datahex = binascii.b2a_base64(f.read())
    f.close()
    os.remove('tmp.txt.gz')
    return datahex

def decompress(data):
    import gzip
    import binascii
    f = open('tmp.txt.gz','wb')
    f.write(binascii.a2b_base64(datahex))
    f.close()
    f = gzip.open('tmp.txt.gz','rb')
    data = f.read()
    f.close()
    os.remove('tmp.txt.gz')
    return data

def get_vector_conf(ports, pdic):
    vector_size = 0
    for port in ports:
        vector_size += pdic[port][2]
    temp_vector_size = vector_size
    vector_mult = []
    vector_dic = {}
    for port in ports:
        port_size = pdic[port][2]
        lsb = vector_size-1-(port_size-1)
        vector_dic[port] = (vector_size-1,lsb)
        vector_mult.append(pow(2,lsb))
        vector_size = lsb

    return [vector_mult,vector_dic,temp_vector_size]

def get_clock_sources(buf, pdic):
    #TODO: Add 'event and ...
    exp = "[rising|falling]_edge\((.*?)\)"
    r = re.compile(exp, re.I)
    clk_s = r.findall(buf)
    clk_s = list(set(clk_s))
    return clk_s

def extract_data4tb(vhdl_file):
    try:
        f = open(vhdl_file,'r')
        buf = f.read()
        f.close()
    except IOError:
        print "Error: File does not exist\n"
        sys.exit(1)
    vf = vhdlfile.vhdlfile(buf)
    modname = vf.get_name()
    pdic = vf.get_ports_dic()
    clk_source = get_clock_sources(buf, pdic)
    return pdic, clk_source

def int2bin_d(n,digits):
    return "{0:0>{1}}".format(bin(n)[2:], digits)

def isPeriod(period):
    res = False
    period = period.strip().split(' ')
    if len(period) == 2:
        try:
            i = float(period[0])
            res = True
        except:
            print "%s is not a number"%period[0]
            return res
        if period[1] in ['ps','ns','us','ms','s']:
            res = True
        else:
            res = False
            print "Wrong unit"
    else:
        print "Wrong Period"
    return res

def tb_config(ports, clk_source = []):
    gconfig = {'tb_period': {},
               'clks_period': {},
               'tables': {},
              }
    if clk_source == []:
        flag = False
        while flag == False:
            print('No clock source detected')
            resp = raw_input('Do you want to select a clock source (y/n):')
            if resp in ['y','Y','n','N']:
                flag = True
    if resp in ['y','Y']:
        print('Available Ports:\n%s'%ports)
        new_clock_sources = raw_input('Select your clock(s) source(s) separated by , (clk1,clk2):\n')
        for clocks in new_clock_sources.split(','):
            clk_source.append(clocks.strip())
    if clk_source == []:
        flag = False
        while flag == False:
            tb_period = raw_input("Set PERIOD for TestBench process ( 25 ns ): ")
            flag = isPeriod(tb_period)
        gconfig['tb_period']['tb'] = tb_period
        gconfig['tables']['tb'] = ports
    elif len(clk_source) == 1:
        flag = False
        while flag == False:
            clk_period = raw_input("Set PERIOD for "+clk_source[0]+" ( 25 ns ): ")
            flag = isPeriod(clk_period)
        flag  = False
        while flag == False:
            initial_state = raw_input("Set initial state for "+clk_source[0]+" (0/1) ")
            if initial_state in ['0','1']:
                flag = True
        flag = False
        while flag == False:
            tb_period = raw_input("Set PERIOD for TestBench process ( 25 ns ): ")
            flag = isPeriod(tb_period)
        gconfig['clks_period'][clk_source[0]] = [clk_period,initial_state]
        gconfig['tb_period']['tb'] = tb_period
        gconfig['tables'][clk_source[0]] = ports
    else:
        flag = False
        while flag == False:
            res = raw_input("There are "+`len(clk_source)`+" clock source.\n Do you want ... tables for each source? (y/n): ")
            if res in ('n','N'):
                for clk in clk_source:
                    flag = False
                    while flag == False:
                        clk_period = raw_input("Set PERIOD for "+clk+" ( 25 ns ): ")
                        flag = isPeriod(clk_period)
                    flag  = False
                    while flag == False:
                        initial_state = raw_input("Set initial state for "+clk+" (0/1) ")
                        if initial_state in ['0','1']:
                            flag = True
                    gconfig['clks_period'][clk] = [clk_period,initial_state]
                flag = False
                while flag == False:
                    tb_period = raw_input("Set PERIOD for TestBench process ( 25 ns ): ")
                    flag = isPeriod(tb_period)
                gconfig['tb_period']['tb'] = tb_period
                gconfig['tables']['tb'] = ports
                flag = True
            elif res in ('y','Y'):
                for clk in clk_source:
                    flag = False
                    while flag == False:
                        clk_period = raw_input("Set PERIOD for "+clk+" ( 25 ns ): ")
                        flag = isPeriod(clk_period)
                    flag  = False
                    while flag == False:
                        initial_state = raw_input("Set initial state for "+clk+" (0/1) ")
                        if initial_state in ['0','1']:
                            flag = True
                    gconfig['clks_period'][clk] = [clk_period,initial_state]
                    flag = False
                    while flag == False:
                        tb_period = raw_input("Set PERIOD for "+clk+" TestBench process ( 25 ns ): ")
                        flag = isPeriod(tb_period)
                    gconfig['tb_period'][clk] = tb_period
                    flag = False
                    while flag == False:
                        print "Select ports for %s process\navailable ports = %s"%(clk,ports)
                        selected_ports = raw_input("Choice ports ( port1,port2,...) : ")
                        selected_ports = selected_ports.strip().split(',')
                        for port in selected_ports:
                            if port in ports:
                                ports.remove(port)
                                flag = True
                            else:
                                print "Wrong ports selections. Try again..."
                                flag = False
                                break;
                    gconfig['tables'][clk] = selected_ports
                flag = True
    return gconfig

def input_formats():
    in_formats = {'xls':'tbl',
                 'xlsx':'tbl',
                 'ods':'tbl',
                }
    return in_formats

if __name__ == "__main__":
   tb_config(['a','b','c'],['clk0','clk1'])
