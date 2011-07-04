import os
import re
import hashlib

class vhdlfile:
    def __init__(self, Buffer):
        self.__pdic = {}
        self.__clock_sources = []
        self.__hash = hashlib.sha1(Buffer).hexdigest()
        self.headers = Buffer[0:Buffer.lower().find("entity")].strip().split("\n")
        exp="entity(.+?)is\n(.*?)end(.*?);"
        r =re.compile(exp,re.S| re.I)
        l = r.findall(Buffer)
        #Getting Module Name
        self.name_ = l[0][0].strip()
        #Getting Generics
        #TODO: Add support to generics
        exp = "generic(.*?);"
        r = re.compile(exp, re.I)
        generics = r.findall(l[0][1])
        exp = "port(.*)[)];"
        r = re.compile(exp,re.S| re.I)
        ports = r.findall(l[0][1])
        self.__ports_hash = hashlib.sha1(l[0][1]).hexdigest()
        self.__ports_ind_hash = {}
        #Find and remove commentes
        if ports == []:
            self.__file_type = "VHDL Test Bench"
        else:
            self.__file_type = "VHDL Module"
            exp = "--(.*?)\n"
            r = re.compile(exp,re.S)
            comments = r.findall(ports[0])
            for comment in comments:
                ports[0] = ports[0].replace("--"+comment,"")
            ports = ports[0].replace("\n","")
            ports = ports.replace("\t","")
            ports = ports.strip()
            ports = ports.lstrip("(")
            ports = ports.split(";")
            #Delete parasit ports
            while '' in ports:
                ports.remove('')
            for port in ports:
                #Get Port Name
                port = port.split(":")
                Names = port[0].strip()
                Names = Names.split(',')
                #Get Port Size
                exp ="\((.*?) downto (.*?)\)"
                r = re.compile(exp, re.I)
                size_ = r.findall(port[1])
                if size_ != []:
                    size_ = int(size_[0][0])+1-int(size_[0][1])
                else:
                    size_ = 1
                #Get Port direction
                if "out" in port[1]:
                    pdir = "out"
                elif "in" in port[1]:
                    pdir = "in"
                elif "inout" in port[1]:
                    pdir = "inout"
                else:
                    pdir = "out"
                #Get Port Type
                if size_ > 1:
                    exp = pdir+"(.*?)\("
                    r = re.compile(exp, re.I)
                else:
                    exp = pdir+"(.*)"
                    r = re.compile(exp, re.S)
                type_ = r.findall(port[1])[0].strip()
                for Name in Names:
                    self.__pdic[Name.strip()] =(type_,pdir,size_)
                    temp = "[%s,%s,%s]"%(type_,pdir,size_)
                    self.__ports_ind_hash[Name.strip()]=hashlib.sha1(temp).hexdigest()
        #Get Declared modules
	self.__smodules = [] 
	exp = "component(.+?)is"
	r = re.compile(exp,re.I)
	l = r.findall(Buffer)
	for module in l:
	    self.__smodules.append(module.strip())
        #Get clock sources
        exp = "[rising|falling]_edge\((.*?)\)"
        r = re.compile(exp,re.I)
        clk_s = r.findall(Buffer)
        self.__clock_sources = list(set(clk_s))
        

    def get_name(self):
        return self.name_

    def get_component_def(self):
        c = "component "+self.name_+" is\n"
        c+= self.gen_ports_code()
        c+= "\nend component;\n"
        return c

    def get_ports_dic(self):
        return self.__pdic

    def get_clock_sources(self):
        return self.__clock_sources

    def gen_ports_code(self):
        l = len(self.__pdic)
        c=""
        if l>0:
            c="port (\n"
            i=0
            for port in self.__pdic:
                data = self.__pdic[port]
                size = data[2]
                type_ = data[0]
                ft = ''
                direction = data[1]
                if size > 1:
                    ft = "(%s downto 0)" % `size-1`
		#Not work in python 2.4
                #c+="\t{0}: {1} {2} {3}".format(port,direction,type_,ft)+(";")*(i<l-1)+"\n"
		c+= "\t%s: %s %s %s" %(port,direction,type_,ft)
		c+=(";")*(i<l-1)+"\n"
                i += 1
            c+=");"
        return c

    def gen_signals_code(self, initial_state_dic = None):
        l = len(self.__pdic)
        c=""
        print initial_state_dic
        if l>0:
            for port in self.__pdic:
                ival = ''
                data = self.__pdic[port]
                size = data[2]
                type_ = data[0]
                try:
                    tv = initial_state_dic[port]
                    ft = '\''
                    if size > 1:
                        ft = '"'
                    itempval = '{0:0>{1}}'.format(tv,size)
                    ival = ":= %s%s%s"%(ft,itempval,ft)
                except:
                    pass
                ft = ''
                if size > 1:
                    ft = "(%s downto 0)" % `size-1`
                c+="signal %s: %s %s %s;\n" % (port,type_,ft, ival )
        return c

    def gen_instance(self, iname):
        l = len(self.__pdic)
        c=iname+":"+self.name_+"\n"
        if l>0:
            c+="port map(\n"
            i = 0
            for port in self.__pdic:
                c+="\t%s => %s" %(port,port)
		c+= (",")*(i<l-1)+"\n"
                i += 1
            c+=");"
        return c

    def get_submodules(self):
        return self.__smodules

    def get_hashes(self):
        return self.__hash,self.__ports_hash, self.__ports_ind_hash

    def get_input_ports_list(self):
        input_ports = []
        for port in self.__pdic:
            if self.__pdic[port][1] in ("in","IN") and port not in self.__clock_sources:
                input_ports.append(port)

        return input_ports

if __name__ == "__main__":
    f = open('vhd/wbDH13.vhd')
    buf = f.read()
    f.close()
    vhd = vhdlfile(buf)
    print vhd.get_name()
    print vhd.get_submodules()
    print vhd.gen_instance('algo')
    print vhd.get_ports_dic()
    print vhd.return_conf()
