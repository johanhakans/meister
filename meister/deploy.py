'''
Created on Jan 11, 2013

@author: fabsor
'''
from fabric.api import settings, abort, run, cd, sudo, put, env, prompt, get

class Deployer:
    
    def __init__(self, hostname, port = None, username = None, keyFile = None):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.keyFile = keyFile
        self.hoststring = hostname
        if port:
            self.hoststring = "{0}:{1}".format(self.hoststring, port)
        if username:
            self.hoststring = "{0}@{1}".format(username, self.hoststring)

    def put(self, localPath, remotePath = None, useSudo = False):
        with settings(host_string=self.hoststring, key_filename=self.keyFile):
            put(localPath, remotePath, useSudo)
    
    def run(self, command):
        with settings(host_string=self.hoststring, key_filename=self.keyFile):
            run(command)
        
    def sudo(self, command):
        with settings(host_string=self.hoststring, key_filename=self.keyFile):
            sudo(command)

    def runTask(self, task):
        with settings(host_string=self.hoststring, key_filename=self.keyFile):
            task()