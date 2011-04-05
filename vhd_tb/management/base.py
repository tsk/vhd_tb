# Borrowed mostly from Django's management commands
import os
import sys
from optparse import make_option, OptionParser

class BaseCommand(object):
    help = ''
    args = ''
    option_list = []
    def __init__(self):
        pass

    def usage(self, subcommand):
        usage = '%%prog %s [options] %s' % (subcommand, self.args)
        if self.help:
            return '%s\n\n%s' % (usage, self.help)
        else:
            return usage

    def create_parser(self, prog_name, subcommand):
        return OptionParser(prog=prog_name,
                            usage=self.usage(subcommand),
                            option_list=self.option_list)

    def print_help(self, prog_name, subcommand):
        parser = self.create_parser(prog_name, subcommand)
        parser.print_help()

    def run_from_argv(self, argv):
        parser = self.create_parser(argv[0],argv[1])
        options, args = parser.parse_args(argv[2:])
        return self.execute(args,options)

    def execute(self,args,options):
        pass
