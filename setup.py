from distutils.core import setup

setup(name="vhd_tb",
      version="0.1",
      description = "Create Templates for TestBench",
      author ="Alejandro Armagnac",
      author_email = "aarmagnac@yahoo.com.mx",
      license="GPL",
      scripts=["vhd_tb/bin/gentbf.py"],
      packages=["vhd_tb"]
)
