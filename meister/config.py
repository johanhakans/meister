'''

@author: fabsor
'''
import sys; sys.path.append('..')
from os.path import isfile
import yaml
from aws.driver import EC2Driver
from aws.driver import Route53Driver

class Config:
    drivers = {
        "aws": EC2Driver
    }
    
    DNSDrivers = {
        "route53": Route53Driver
    }

    def getNodes(self):
        return self.nodes

    def getDriver(self):
        return self.driver

    def getDNSDriver(self):
        return self.DNSDriver

class YamlConfig(Config):
    '''
    Parses and makes configuration accessible.
    '''
    def __init__(self, configFile):
        '''
        
        '''
        self.configFile = configFile
        self.DNSDriver = None
        self.parse()

    def parse(self):
        data = yaml.load(open(self.configFile).read())
        self.driver = self.drivers[data['driver']['name']](self, data)
        self.DNSDriver = self.DNSDrivers[data['DNS']['name']](self, data)
        self.nodes = {}
        for name, node in data["nodes"].items():
            self.nodes[name] = self.driver.getNode(name, node)
