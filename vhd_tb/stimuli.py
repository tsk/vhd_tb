import sys
import hashlib
import re
from vhd_tb import vhdlfile
from vhd_tb.cutils import *
from vhd_tb.sheets import *
from vhd_tb.templates import templates_dir, TemplateBuf, Template, tb_source_control

class Base(object):
    def __init__(self, vhd_file_name=''):
        self.vhd_file_name = vhd_file_name

    def check_source_changes(self, TestBenchSrcControl):
        flag = False
        flag_src = False
        new_vhd_file = vhdlfile.vhdlfile(open(self.vhd_file_name,'r').read())
        new_hashes = new_vhd_file.get_hashes()
        
        if new_hashes[0] != TestBenchSrcControl['hash_src']:
            flag_src = True
            if new_hashes[1] != TestBenchSrcControl['hash_src_ports']:
                flag_src_ports = True
                hash_ind_ports = TestBenchSrcControl['hash_ind_ports']
                if len(new_hashes[2]) != len(hash_ind_ports):
                    flag = True
                else:
                    for port in new_hashes[2]:
                        try:
                            old_port_hash = hash_ind_ports[ports]
                        except:
                            flag = True
                            break;
                        if new_hashes[2][port] != hash_ind_ports[port]:
                            flag = True
                            break;
        deepfiles_hash = get_related_files_hashes(self.vhd_file_name)
        old_deepfiles_hash = TestBenchSrcControl['deepfiles_hash']
        if len(deepfiles_hash) != len(old_deepfiles_hash):
            flag_src = True
        else:
            for deepfile in deepfiles_hash:
                try:
                    old_deepfile_hash = old_deepfiles_hash[deepfile]
                except:
                    flag_src = True
                    break;
                if deepfiles_hash[deepfile] != old_deepfile_hash:
                    flag_src = True
                    break;

        return flag,flag_src,new_hashes, deepfiles_hash

    def replace_TestBenchSrcControl(self, new_TBSrcControl, file_):
        dirname = os.path.dirname(file_)
        basename = os.path.basename(file_)
        if basename.split('.')[1] == 'pyc':
            basename = '%s.%s'%(basename.split('.')[0],'py')
            file_ = dirname+'/'+basename
        import re
        f = open(file_,'r')
        buf = f.read()
        f.close()
        exp = 'TestBenchSrcControl = {\n(.*)\n}'
        r = re.compile(exp,re.S)
        l = r.findall(buf)
        f = open(file_,'w')
        f.write(re.sub(l[0],new_TBSrcControl,buf))
        f.close()

    def replace_gconfig(self, gconfig, file_):
        dirname = os.path.dirname(file_)
        basename = os.path.basename(file_)
        if basename.split('.')[1] == 'pyc':
            basename = '%s.%s'%(basename.split('.')[0],'py')
            file_ = dirname+'/'+basename
        import re
        f = open(file_,'r')
        buf = f.read()
        f.close()
        exp = '\'gconfig\' : (.*),\n\'work_dir\''
        r = re.compile(exp,re.S)
        l = r.findall(buf)
        print l[0]
        #f = open(file_,'w')
        #f.write(re.sub(l[0],gconfig,buf))
        #f.close()


class xls_source(Base,xls):
    def __init__(self,source_dir,file_name,stm_file_name):
        Base.__init__(self,'/'.join([source_dir,file_name]))
        xls.__init__(self,'/'.join([source_dir,stm_file_name]))


class ods_source(Base,ods):
    def __init__(self,source_dir,file_name,stm_file_name):
        Base.__init__(self,'/'.join([source_dir,file_name]))
        ods.__init__(self,'/'.join([source_dir,stm_file_name]))

class py_source(Base):
    def __init__(self):
        pass

