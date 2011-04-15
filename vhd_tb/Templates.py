import os
import sys
import re
class Templates:

	def __init__(self,template_file):
		temp = open(template_file,'r')
		self.temp_buf = temp.read()
		temp.close()
		expresion= "<([a-z|A-Z].*?)>";
		r = re.compile(expresion,re.I)
		l = r.findall(self.temp_buf)
		self.params = list(set(l))

	def get_params(self):
		return self.params

        def __reload_params(self):
		expresion= "<([a-z|A-Z].*?)>";
		r = re.compile(expresion,re.I)
		l = r.findall(self.temp_buf)
		self.params = list(set(l))

	def set_property_value(self, name= '', value = ''):
		self.temp_buf = self.temp_buf.replace("<"+name+">",value)
                self.__reload_params()

	def save_file(self, file_name):
		out_file = open(file_name,'w')
		out_file.write(self.temp_buf)
		out_file.close()

class extractTemplates:
	def __init__(self, file_name):
		temp = open(file_name,'r')
		temp_buf = temp.read()
		temp.close()
		expresion = "\{(.*?)\}"
		r = re.compile(expresion,re.S)
		self.ltemp = r.findall(temp_buf)

	def get_template_list(self):
		return self.ltemp

	def get_template_of(self, temp_name=''):
		index = self.ltemp.index(temp_name)
		return self.ltemp[index+1]

class TemplatesC:

	def __init__(self,TemplateBuf):
		self.TemplateBuf = TemplateBuf
		expresion= "<([a-z|A-Z].*?)>";
		r = re.compile(expresion,re.I)
		l = r.findall(self.TemplateBuf)
		self.params = list(set(l))

	def get_params(self):
		return self.params

	def set_property_value(self, name= '', value = ''):
		self.TemplateBuf = self.TemplateBuf.replace("<"+name+">",value)
                self.__reload_params()

        def __reload_params(self):
		expresion= "<([a-z|A-Z].*?)>";
		r = re.compile(expresion,re.I)
		l = r.findall(self.TemplateBuf)
		self.params = list(set(l))
	def return_code(self):
		return self.TemplateBuf

	def save_file(self, file_name):
		out_file = open(file_name,'w')
		out_file.write(self.TemplateBuf)
		out_file.close()
