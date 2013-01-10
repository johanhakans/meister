'''
Created on Jan 10, 2013

@author: fabsor
'''

import ec2

from provisioner import Provisioner
from libcloud.compute.types import Provider

class Driver:
    REGIONS = {
        "eu-west-1": Provider.EC2_EU_WEST,
        "us-west-1": Provider.EC2_US_WEST,
        "us-west-2": Provider.EC2_US_WEST_OREGON,
        "us-east-1": Provider.EC2_US_EAST,
        "ap-southeast-1": Provider.EC2_AP_SOUTHEAST,
        "ap-northeast-1": Provider.EC2_AP_NORTHEAST,
        "sa-east-1": Provider.EC2_SA_EAST
    }

    def __init__(self, config, settings):
        self.aws_id = settings['driver']['id']
        self.aws_key = settings['driver']['key']
        self.aws_region = self.REGIONS[settings['driver']['region']]
        self.defaultZone = settings["driver"]["defaultZone"]
        self.defaultSecurityGroup = settings['driver']['defaultSecurityGroup']
        config.getSecurityGroups = self.getSecurityGroups
        self.config = config
        if 'securityGroups' in settings.keys():
            self.securityGroups = settings['securityGroups']
    
    def getConnection(self):
        return ec2.EC2Connection(self.aws_region, self.aws_id, self.aws_key)


    def getSecurityGroups(self):
        return self.securityGroups


    def getNode(self, name, definition):
        for prop, defaultProp in {"securityGroup": "defaultSecurityGroup", "zone": "defaultZone"}.items():
            if not prop in definition:
                definition[prop] = getattr(self, defaultProp)
        return AWSNode(name, definition)

    def provision(self, logger):
        """
        Provision configuration.
        """
        provisioner = Provisioner(self.getConnection(), logger)
        provisioner.provisionSecurityGroups(self.getSecurityGroups())
        provisioner.provisionNodes(self.config.getNodes())

class AWSNode():
    def __init__(self, name, definition):
        defaults = {
            "diskSize": "8"
        }
        self.name = name
        self.hostname = definition['hostname']
        for prop in ['image', 'securityGroup', 'size', 'diskSize', 'zone', "externalDNS", "internalDNS"]:
            if prop in definition:
                setattr(self, prop, definition[prop])
            elif prop in defaults:
                setattr(self, prop, defaults[prop])