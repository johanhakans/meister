'''
Created on Jan 10, 2013

@author: fabsor
'''
from aws import ec2
from libcloud.compute.types import Provider
from config import AWSNode

class PrintLogger():
    """
    Logger that prints everything it gets.
    """
    def log(self, message, type="notice"):
        print "[{0}] {1}".format(type, message)

class Provision(object):
    '''
    classdocs
    '''
    
    def getProvisioner(self):
        # Hard-coded for now.
        return AWSProvisioner(self.config)

    def __init__(self, config):
        '''
        @param config: A config object with the configuration that should be provisioned.
        '''
        self.config = config



    def provision(self):
        pass
        

class AWSProvisioner:
    REGIONS = {
        "eu-west-1": Provider.EC2_EU_WEST,
        "us-west-1": Provider.EC2_US_WEST,
        "us-west-2": Provider.EC2_US_WEST_OREGON,
        "us-east-1": Provider.EC2_US_EAST,
        "ap-southeast-1": Provider.EC2_AP_SOUTHEAST,
        "ap-northeast-1": Provider.EC2_AP_NORTHEAST,
        "sa-east-1": Provider.EC2_SA_EAST
    }
    
    
    def __init__(self, config, logger):
        driver = config.getDriver()
        self.config = config
        self.id = driver.aws_id
        self.key = driver.aws_key
        self.region = self.REGIONS[driver.aws_region]
        self.defaultZone = driver.defaultZone
        self.logger = logger
    
    def provisionSecurityGroups(self, groups):
        connection = ec2.EC2Connection(self.region, self.id, self.key)
        existingGroups = connection.getSecurityGroups()
        for name, group in groups.items():
            if not name in existingGroups:
                ec2Group = connection.createSecurityGroup(name, group["description"])
            else:
                ec2Group = existingGroups[name]
            for rule in group["rules"]:
                ec2Group.addRule(rule["fromPort"], rule["toPort"], rule["ip"])

    def provisionNodes(self, nodes):
        connection = ec2.EC2Connection(self.region, self.id, self.key)
        # Find existing nodes.
        existingNodes = connection.getNodes()
        for name, node in nodes.items():
            # Create non-existing nodes.
            if not name in existingNodes:
                self.logger.log("Creating node {0}".format(name))
                connection.createNode(node.image, node.size, name, node.diskSize, zone=self.defaultZone)
            else:
                self.logger.log("Node {0} already exists.".format(name))
                
    def getNodes(self):
        connection = ec2.EC2Connection(self.region, self.id, self.key)
        existingNodes = connection.getNodes()
        nodes = {}
        for name, node in existingNodes:
            nodes[name] = AWSNode()
        return nodes

    def deleteNodes(self, nodes):
        """
        Terminate all nodes from a configuration. 
        """
        connection = ec2.EC2Connection(self.region, self.id, self.key)
        existingNodes = connection.getNodes()
        for name in nodes.keys():
            if name in existingNodes:
                existingNodes[name].destroy()
