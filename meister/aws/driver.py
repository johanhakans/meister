'''
Created on Jan 10, 2013

@author: fabsor
'''

import ec2
import route53

from provisioner import Provisioner
from libcloud.compute.types import Provider

class EC2Driver:
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
        self.con = None
        if 'securityGroups' in settings.keys():
            self.securityGroups = settings['securityGroups']
    
    def getConnection(self):
        if not self.con:
            self.con = ec2.EC2Connection(self.aws_region, self.aws_id, self.aws_key)
        return self.con

    def getSecurityGroups(self):
        return self.securityGroups

    def getNode(self, name, definition):
        con = self.getConnection()
        nodes = con.getNodes()
        for prop, defaultProp in {"securityGroup": "defaultSecurityGroup", "zone": "defaultZone"}.items():
            if not prop in definition:
                definition[prop] = getattr(self, defaultProp)
        if name in nodes:
            definition["internalIp"] = nodes[name].private_ip[0] if len(nodes[name].private_ip) else None 
            definition["externalIp"] = nodes[name].public_ip[0] if len(nodes[name].public_ip) else None
        return AWSNode(name, definition)

    def provision(self, logger):
        """
        Provision configuration.
        """
        provisioner = Provisioner(self.getConnection(), logger)
        provisioner.provisionSecurityGroups(self.getSecurityGroups())
        provisioner.provisionNodes(self.config.getNodes())
        provisioner.verify(self.config.getNodes())


class Route53Driver:
    def __init__(self, config, settings):
        self.aws_id = settings['id']
        self.aws_key = settings['key']
        self.defaultZone = settings['defaultZone']
        self.config = config 
    
    def getConnection(self):
        return route53.Route53Connection(self.aws_id, self.aws_id)
    
    def provision(self, nodes, logger):
        con = self.getConnection()
        zones = con.getZones()
        if not self.defaultZone in zones:
            zone = con.saveZone(self.defaultZone)
        else:
            zone = con.getZone(zones[self.defaultZone].id)
        for node in nodes:
            for ipProp,nameProp in [("internalIp", "internalDNS"), ("externalIp", "externalDNS")]:
                if hasattr(node, ipProp) and hasattr(node, nameProp):
                    ip =  getattr(node, ipProp)
                    name = getattr(node, nameProp)
                    record = zone.getRecord(name)
                    if not record:
                        zone.addRecord("A", name, ip)
                    elif ip not in record["value"]:
                        record.append(ip)
                        zone.updateRecord(name, record)

class AWSNode():
    def __init__(self, name, definition):
        defaults = {
            "diskSize": "8"
        }
        self.name = name
        self.hostname = definition['hostname']
        for prop in ['image', 'securityGroup', 'size', 'diskSize', 'zone', "externalDNS", "internalDNS", "internalIp", "externalIp"]:
            if prop in definition:
                setattr(self, prop, definition[prop])
            elif prop in defaults:
                setattr(self, prop, defaults[prop])