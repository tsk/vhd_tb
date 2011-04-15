from distutils.core import setup
from distutils.command.install import INSTALL_SCHEMES 
import os

packages, data_files = {},[]
root_dir = os.path.dirname(__file__)
if root_dir != "":
    os.chdir(root_dir)
vhd_tb_dir = "vhd_tb"

for dirpath, dirnames, filenames in os.walk(vhd_tb_dir):
    if "__init__.py" in filenames:
        if dirpath == vhd_tb_dir:
            packages[dirpath] = "."
        else:
            packages[dirpath.replace("/",".")] = "./"+dirpath
    elif filenames:
        data_files.append([dirpath,[os.path.join(dirpath,f) for f in filenames]])


for scheme in INSTALL_SCHEMES.values(): 
    scheme['data'] = scheme['purelib']

setup(name="vhd_tb",
      version="0.1",
      description = "Create Templates for TestBench",
      author ="Alejandro Armagnac",
      author_email = "aarmagnac@yahoo.com.mx",
      license="GPL",
      scripts=["vhd_tb/bin/gentbf.py","vhd_tb/bin/isolate_vfile.py","vhd_tb/bin/vhd-tb.py"],
      packages=packages,
      data_files = data_files,
)
