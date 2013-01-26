#!/usr/local/bin/python2.7
# encoding: utf-8

import sys
import config

from argparse import ArgumentParser
from argparse import RawDescriptionHelpFormatter

__all__ = []
__version__ = 0.1
__date__ = '2013-01-10'
__updated__ = '2013-01-10'


class PrintLogger():

    def log(self, message, type = "notice"):
        print "[{0}] {1}".format(type, message)
    
    def logMessage(self, message):
        print message

def main(argv=None): # IGNORE:C0111
    '''Command line options.'''
    try:
        # Setup argument parser
        parser = ArgumentParser(description="Meister", formatter_class=RawDescriptionHelpFormatter)
        parser.add_argument('command', help="A command to execute", default="info", nargs="+")
        parser.add_argument('-f', '--file', action='store', default="meister.yml")

        # Process arguments
        args = parser.parse_args()
        logger = PrintLogger()
        command = args.command[0]
        file = args.file
        configuration = config.YamlConfig(file)

        commands = { 
            "provision": { "cmd": lambda: configuration.provision(logger), "help": "Provision the configuration using the drivers provided." },
            "terminate": { "cmd": lambda: configuration.terminate(logger), "help": "Terminate instances specified by the configuration file." },
            "info": { "cmd": lambda: configuration.info(logger), "help": "Show information about the configuration and the current state." },
            "task": { "cmd": lambda: configuration.task(logger, args.command[1], args.command[2]), "help": "Execute a task on a node."},
            "ssh": { "cmd": lambda: configuration.ssh(logger, args.command[1]), "help": "Open an SSH connection."}

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

if __name__ == "__main__":
    main()
