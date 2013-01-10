'''

@author: fabsor
'''
from os.path import isfile
import yaml
from meister import aws

class Config:
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
        self.driver = globals()[data['driver']['name']](self, data)
        self.nodes = {}
        for name, node in data["nodes"].items():
            self.nodes[name] = self.driver.getNode(name, node)

class AWSDriver:
    def __init__(self, config, settings):
        self.aws_id = settings['driver']['id']
        self.aws_key = settings['driver']['key']
        self.aws_region = settings['driver']['region']
        self.defaultZone = settings["driver"]["defaultZone"]
        self.defaultSecurityGroup = settings['driver']['defaultSecurityGroup']
        config.getSecurityGroups = self.getSecurityGroups
        if 'securityGroups' in settings.keys():
            self.securityGroups = settings['securityGroups']


    def getSecurityGroups(self):
        return self.securityGroups
        
    def getConnection(self):
        aws.AWSConnection(self.aws_region, self.aws_id, self.aws_key) 

    def getNode(self, name, definition):
        if not 'securityGroup' in definition:
            definition['securityGroup'] = self.defaultSecurityGroup 
        return AWSNode(name, definition)

class Node:
    def __init__(self, name, definition):
        self.name = name
        self.hostname = definition['hostname']
        for prop in ["externalDNS", "internalDNS"]:
            if prop in definition:
                setattr(self, prop, definition[prop])

class AWSNode(Node):
    def __init__(self, name, definition):
        defaults = {
            "diskSize": "8"
        }
        Node.__init__(self, name, definition)
        for prop in ['image', 'securityGroup', 'size', 'diskSize']:
            if prop in definition:
                setattr(self, prop, definition[prop])
            elif prop in defaults:
                setattr(self, prop, defaults[prop])