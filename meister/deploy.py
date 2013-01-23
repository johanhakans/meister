'''
Created on Jan 11, 2013

@author: fabsor
'''
from time import sleep
from fabric.api import settings, abort, run, cd, sudo, put, env, prompt, get
from fabric.contrib.files import exists

class Deployer:
    
    def __init__(self, hostname, port = None, username = None, keyFile = None, retries = 2, hostList = {}):
        self.hostname = hostname
        self.port = port
        self.username = username
        self.keyFile = keyFile
        self.hoststring = hostname
        self.hostList = hostList
        self.retries = 2
        if port:
            self.hoststring = "{0}:{1}".format(self.hoststring, port)
        if username:
            self.hoststring = "{0}@{1}".format(username, self.hoststring)

    def put(self, localPath, remotePath = None, useSudo = False):
        return self.runTask(put, [localPath, remotePath, useSudo])

    def get(self, remotePath, localPath = None, useSudo = False):
        return self.runTask(get, [remotePath, localPath])

    def fileExists(self, path):
        return self.runTask(exists, [path])

    def run(self, command):
        return self.runTask(run, { "command": command })
        
    def sudo(self, command):
        return self.runTask(sudo, [command])

    def runTask(self, task, args = [], tries = 0):
        with settings(host_string = self.hostname, user=self.username, key_filename=self.keyFile, host=self.hostname, meister = self.hostList):
            try:
                return task(**args) if isinstance(args, dict) else task(*args)
            except Exception as e:
                print e
                if tries < self.retries:
                    sleep(5)
                    return self.runTask(task, args, tries + 1)
                else:
                    raise e
