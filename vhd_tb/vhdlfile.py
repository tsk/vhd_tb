import os
import re

class vhdlfile:
    def __init__(self, Buffer):
        self.__pdic = {}
        exp="[E|e][N|n][T|t][I|i][T|t][Y|y](.+?)[I|i][S|s]\n(.*?)[E|e][N|n][D|d](.*?);"
        r =re.compile(exp,re.S)
        l = r.findall(Buffer)
        #Getting Module Name
        self.name_ = l[0][0].strip()
        #Getting Generics
        exp = "generic(.*?);"
        r = re.compile(exp, re.I)
        generics = r.findall(l[0][1])
        exp = "[P|p][O|o][R|r][T|t](.*)[)];"
        r = re.compile(exp,re.S)
        ports = r.findall(l[0][1])
        #Find and remove commentes
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
            #Get P rt Name
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
        #Get Declared modules
	self.__smodules = [] 
	exp = "component(.+?)is"
	r = re.compile(exp,re.I)
	l = r.findall(Buffer)
	for module in l:
	    self.__smodules.append(module.strip())

    def get_name(self):
        return self.name_

    def get_component_def(self):
        c = "component "+self.name_+" is\n"
        c+= self.gen_ports_code()
        c+= "\nend component;\n"
        return c

    def get_ports_dic(self):
        return self.__pdic

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

    def gen_signals_code(self):
        l = len(self.__pdic)
        c=""
        if l>0:
            for port in self.__pdic:
                data = self.__pdic[port]
                size = data[2]
                type_ = data[0]
                ft = ''
                if size > 1:
                    ft = "(%s downto 0)" % `size-1`
                c+="signal %s: %s %s;\n" % (port,type_,ft)
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
