#!/usr/local/bin/python2.7
# encoding: utf-8
'''
main -- shortdesc

main is a description

It defines classes_and_methods

@author:     user_name
        
@copyright:  2013 organization_name. All rights reserved.
        
@license:    license

@contact:    user_email
@deffield    updated: Updated
'''

import sys
import os
import config

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter
from config import YamlConfig

__all__ = []
__version__ = 0.1
__date__ = '2013-01-10'
__updated__ = '2013-01-10'


class PrintLogger():

    def log(self, message, type = "notice"):
        print "[{0}] {1}".format(type, message)
    
    def logMessage(self, message):
        print message

class CLIError(Exception):
    '''Generic exception to raise and log different fatal errors.'''
    def __init__(self, msg):
        super(CLIError).__init__(type(self))
        self.msg = "E: %s" % msg
    def __str__(self):
        return self.msg
    def __unicode__(self):
        return self.msg



def main(argv=None): # IGNORE:C0111
    '''Command line options.'''

    program_name = "Meister"
    program_version = "v%s" % __version__
    program_build_date = str(__updated__)
    program_version_message = '%%(prog)s %s (%s)' % (program_version, program_build_date)
    program_shortdesc = __import__('__main__').__doc__.split("\n")[1]
    program_license = '''%s

  Created by user_name on %s.
  Copyright 2013 organization_name. All rights reserved.
  
  Licensed under the GPL License
  http://www.gnu.org/licenses/gpl-3.0.txt
  
  Distributed on an "AS IS" basis without warranties
  or conditions of any kind, either express or implied.

USAGE
''' % (program_shortdesc, str(__date__))

    try:
        # Setup argument parser
        parser = ArgumentParser(description=program_license, formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('command', help="A command to execute", default="info")
        parser.add_argument('-f', '--file', action='store', default="meister.py")

        # Process arguments
        args = parser.parse_args()
        logger = PrintLogger()
        command = args.command
        file = args.file
        configuration = config.YamlConfig(file)
        commands = { 
            "provision": { "cmd": lambda: configuration.provision(logger), "help": "Provision the configuration using the drivers provided." },
            "terminate": { "cmd": lambda: configuration.terminate(logger), "help": "Terminate instances specified by the configuration file." },
            "info": { "cmd": lambda: configuration.info(logger), "help": "Show information about the configuration and the current state." }
        }
        if command in commands:
            commands[command]["cmd"]()
        else:
            print "Available commands:\n"
            for command, info in commands.items():
                print "{0}: {1}".format(command, info["help"])

    except KeyboardInterrupt:
        ### handle keyboard interrupt ###
        return 0
    except Exception, e:
        indent = len(program_name) * " "
        sys.stderr.write(program_name + ": " + repr(e) + "\n")
        sys.stderr.write(indent + "  for help use --help")
        return 2

if __name__ == "__main__":
    sys.exit(main())