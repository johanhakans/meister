'''

@author: fabsor
'''
import sys; sys.path.append('..')
from os.path import isfile
import yaml
from aws.driver import Driver

class Config:
    drivers = {
        "aws": Driver
    }

    

    def getNodes(self):
        return self.nodes

    def getDriver(self):
        return self.driver

class YamlConfig(Config):
    '''
    Parses and makes configuration accessible.
    '''
    def __init__(self, configFile):
        '''
        
        '''
        self.configFile = configFile
        self.parse()
    
    def parse(self):
        data = yaml.load(open(self.configFile).read())
        self.driver = self.drivers[data['driver']['name']](self, data)
        self.nodes = {}
        for name, node in data["nodes"].items():
            self.nodes[name] = self.driver.getNode(name, node)
