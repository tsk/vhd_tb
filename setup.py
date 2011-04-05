from distutils.core import setup

setup(name="vhd_tb",
      version="0.1",
      description = "Create Templates for TestBench",
      author ="Alejandro Armagnac",
      author_email = "aarmagnac@yahoo.com.mx",
      license="GPL",
      scripts=["vhd_tb/bin/gentbf.py","vhd_tb/bin/isolate_vfile.py","vhd_tb/bin/vhd-tb.py"],
      packages={'vhd_tb':'.','vhd_tb.management':'./vhd_tb/management',
                'vhd_tb.management.commands':'./vhd_tb/management/commands'}
)
