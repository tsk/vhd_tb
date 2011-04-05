# Borrowed mostly from Django's management commands
import os
import sys
from optparse import OptionParser, make_option, NO_DEFAULT

from vhd_tb.management.base import BaseCommand

_commands = None

def find_commands(management_dir):
    command_dir = os.path.join(management_dir,'commands')
    try:
        return [f[:-3] for f in os.listdir(command_dir)
                if not f.startswith('_') and f.endswith('.py')]
    except OSError:
        return []

def load_command(app_name,name):
    aname = '%s.management.commands.%s' % (app_name,name)
    module = __import__(aname)
    components = aname.split('.')
    for comp in components[1:]:
        module = getattr(module,comp)

    return module.Command()

def get_commands():
    global _commands
    if _commands is None:
        _commands = dict([(name,'vhd_tb') for name in find_commands(__path__[0])])

    return _commands

class ManagementUtility(object):
    def __init__(self, argv = None):
        self.argv = argv or sys.argv[:]
        self.prog_name = os.path.basename(self.argv[0])
    
    def main_help_text(self):
        usage = ['',"Type '%s help <subcommand>' for help on a specific subcommand."% self.prog_name,'']
        usage.append('Available subcommmands:')
        commands = get_commands().keys()
        commands.sort()
        for cmd in commands:
            usage.append('  %s' % cmd)
        return '\n'.join(usage)

    def fetch_command(self, subcommand):
        try:
            app_name = get_commands()[subcommand]
        except KeyError:
            sys.stderr.write("Unkown command: %r\nType '%s help' for usage.\n" % \
                             (subcommand, self.prog_name))
            sys.exit(1)
        if isinstance(app_name, BaseCommand):
            klass = app_name
        else:
            klass = load_command(app_name, subcommand)
        return klass

    def execute(self):

        parser = OptionParser(usage="%prog subcommand [options] [args]",
                                 option_list = BaseCommand.option_list)
        #TODO: Add input file options
        parser.add_option("-i","--input-file",
                          action="store",
                          dest="config",
                          default="",
                          help="Command secuence from file")
        try:
            options, args = parser.parse_args(self.argv)
        except:
            pass
        try:
            subcommand = self.argv[1]
        except IndexError:
            subcommand = 'help'

        if subcommand == 'help':
            if len(args) > 2:
                self.fetch_command(args[2]).print_help(self.prog_name, args[2])
            else:
                parser.print_help()
                sys.stderr.write(self.main_help_text()+'\n')
                sys.exit(1)
        elif self.argv[1:] in (['--help'],['-h']):
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text()+'\n')
        elif self.argv[1] in (['--input-file'],['-i']):
            print "iiii"
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def execute_from_command_line(argv=None):
    utility = ManagementUtility(argv)
    utility.execute()

if __name__ == "__main__":
    p = find_commands("./")
    print p
