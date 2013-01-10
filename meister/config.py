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
        self.configFile = configFile
        self.DNSDriver = None
        self.parse()

    def provision(self, logger):
        self.driver.provision(logger)
        if self.DNSDriver:
            self.DNSDriver.provision(self.getNodes(), logger)

    def terminate(self, logger):
        self.driver.terminate(logger)
        if self.DNSDriver:
            self.DNSDriver.terminate(self.getNodes(), logger)
            
    def info(self, logger):
        logger.logMessage("Compute driver: {0}".format(self.data['driver']['name']))
        if self.DNSDriver:
            logger.logMessage("DNS driver: {0}".format(self.data['DNS']['name']))
        logger.logMessage("\nNodes:\n======\n")
        self.driver.info(logger)

    def parse(self):
        data = yaml.load(open(self.configFile).read())
        self.driver = self.drivers[data['driver']['name']](self, data)
        self.DNSDriver = self.DNSDrivers[data['DNS']['name']](self, data)
        self.nodes = {}
        self.data = data
        for name, node in data["nodes"].items():
            self.nodes[name] = self.driver.getNode(name, node)
