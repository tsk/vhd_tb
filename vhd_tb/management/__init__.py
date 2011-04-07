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

class LaxOptionParser(OptionParser):                                                 
    """                                                                              
    An option parser that doesn't raise any errors on unknown options.               
                                                                                     
    This is needed because the --settings and --pythonpath options affect            
    the commands (and thus the options) that are available to the user.              
    """                                                                              
    def error(self, msg):                                                            
        pass                                                                         
                                                                                     
    def print_help(self):                                                            
        """Output nothing.                                                           
                                                                                     
        The lax options are included in the normal option parser, so under           
        normal usage, we don't need to print the lax options.                        
        """                                                                          
        pass                                                                         
                                                                                     
    def print_lax_help(self):                                                        
        """Output the basic options available to every command.                      
                                                                                     
        This just redirects to the default print_help() behaviour.                   
        """                                                                          
        OptionParser.print_help(self)                                                
                                                                                     
    def _process_args(self, largs, rargs, values):                                   
        """                                                                          
        Overrides OptionParser._process_args to exclusively handle default           
        options and ignore args and other options.                                   
                                                                                     
        This overrides the behavior of the super class, which stop parsing           
        at the first unrecognized option.                                            
        """
        while rargs:                                                                 
            arg = rargs[0]                                                           
            try:                                                                     
                if arg[0:2] == "--" and len(arg) > 2:                                
                    # process a single long option (possibly with value(s))          
                    # the superclass code pops the arg off rargs                     
                    self._process_long_opt(rargs, values)                            
                elif arg[:1] == "-" and len(arg) > 1:                                
                    # process a cluster of short options (possibly with              
                    # value(s) for the last one only)                                
                    # the superclass code pops the arg off rargs                     
                    self._process_short_opts(rargs, values)                          
                else:                                                                
                    # it's either a non-default option or an arg                     
                    # either way, add it to the args list so we can keep             
                    # dealing with options                                           
                    del rargs[0]                                                     
                    raise Exception                                                  
            except:                                                                  
                largs.append(arg)

def call_command(subcommand, options):
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
    print "running "+subcommand+" ..."
    klass.execute(None,options)

def parser_file(file_):
    import inspect
    modname = inspect.getmodulename(file_)
    path = os.path.abspath(file_)
    sys.path.append(os.path.dirname(path))
    __import__(modname)
    module = sys.modules[modname]
    for action in module.actions:
        call_command(action,module)
    

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

        parser = LaxOptionParser(usage="%prog subcommand [options] [args]",
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
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text()+'\n')
                sys.exit(1)
        elif self.argv[1:] in (['--help'],['-h']):
            parser.print_lax_help()
            sys.stderr.write(self.main_help_text()+'\n')
        elif self.argv[1] in (['--input-file','-i']):
            try:
                opt = self.argv[2]
            except IndexError:
                parser.print_lax_help()
                sys.stderr.write(self.main_help_text()+'\n')
                sys.exit()
            parser_file(self.argv[2])
        else:
            self.fetch_command(subcommand).run_from_argv(self.argv)

def execute_from_command_line(argv=None):
    utility = ManagementUtility(argv)
    utility.execute()

if __name__ == "__main__":
    p = find_commands("./")
    print p
