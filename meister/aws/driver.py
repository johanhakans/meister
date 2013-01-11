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
        self.defaultKeyName = settings['driver']['defaultKeyName']
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
        for prop, defaultProp in {"securityGroup": "defaultSecurityGroup", "zone": "defaultZone", "keyName": "defaultKeyName"}.items():
            if not prop in definition and getattr(self, defaultProp, None):
                definition[prop] = getattr(self, defaultProp)
        if name in nodes:
            definition["internalIp"] = nodes[name].private_ip[0] if len(nodes[name].private_ip) else None 
            definition["externalIp"] = nodes[name].public_ip[0] if len(nodes[name].public_ip) else None
        return AWSNode(name, definition)
    
    def info(self, logger):
        con = self.getConnection()
        savedNodes = con.getNodes()
        con = self.getConnection()
        for name, node in self.config.getNodes().items():
            if name in savedNodes:
                status = "running"
            else:
                status = "not started"
            logger.log("\n" + str(node), status)
        
    def provision(self, logger):
        """
        Provision configuration.
        """
        provisioner = Provisioner(self.getConnection(), logger)
        provisioner.provisionSecurityGroups(self.getSecurityGroups())
        provisioner.provisionNodes(self.config.getNodes())
        provisioner.verify(self.config.getNodes())
        
    def terminate(self, logger):
        """
        Terminate all nodes in this configuration.
        """
        provisioner = Provisioner(self.getConnection(), logger)
        provisioner.deleteNodes(self.config.getNodes())
        provisioner.verify(self.config.getNodes())
        provisioner.deleteSecurityGroups(self.getSecurityGroups())


class Route53Driver:
    def __init__(self, config, settings):
        self.aws_id = settings['DNS']['id']
        self.aws_key = settings['DNS']['key']
        self.defaultZone = settings['DNS']['defaultZone']
        self.config = config
    
    def getConnection(self):
        return route53.Route53Connection(self.aws_id, self.aws_key)
    
    def provision(self, nodes, logger):
        con = self.getConnection()
        zones = con.getZones()
        if not self.defaultZone in zones:
            logger.log("Creating Zone {0}".format(self.defaultZone))
            zone = con.saveZone(route53.Zone(self.defaultZone))
        else:
            logger.log("Using zone {0}".format(self.defaultZone))
            zone = con.getZone(zones[self.defaultZone].id)
        for node in nodes.values():
            for ipProp,nameProp in [("internalIp", "internalDNS"), ("externalIp", "externalDNS")]:
                if hasattr(node, ipProp) and hasattr(node, nameProp):
                    ip =  getattr(node, ipProp)
                    name = getattr(node, nameProp)
                    record = zone.getRecord(name)
                    if not record:
                        logger.log("Creating record {0}".format(name))
                        zone.addRecord("A", name, ip)
                    elif ip not in record["value"]:
                        zone.deleteRecord(name)
                        zone.addRecord("A", name, ip)
        con.saveZone(zone)

    def terminate(self, nodes, logger):
        con = self.getConnection()
        zones = con.getZones()
        if self.defaultZone in zones:
            logger.log("Deleting zone {0}".format(self.defaultZone))
            con.deleteZone(zones[self.defaultZone])

class AWSNode():
    def __init__(self, name, definition):
        defaults = {
            "diskSize": "8"
        }
        self.name = name
        self.hostname = definition['hostname']
        for prop in ['image', 'securityGroup', 'size', 'diskSize', 'zone', "externalDNS", "internalDNS", "internalIp", "externalIp", "keyName"]:
            if prop in definition:
                setattr(self, prop, definition[prop])
            elif prop in defaults:
                setattr(self, prop, defaults[prop])
    def __str__(self):
        info = ""
        for prop in ['name', 'hostname', 'image', 'securityGroup', 'size', 'diskSize', 'zone', "externalDNS", "internalDNS", "internalIp", "externalIp", "keyName"]:
            if hasattr(self, prop):
                info += prop + ": " + str(getattr(self, prop)) + "\n"
        return info
