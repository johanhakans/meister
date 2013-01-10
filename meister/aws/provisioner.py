'''
Created on Jan 10, 2013

@author: fabsor
'''
from aws import ec2
from libcloud.compute.types import Provider

class Provisioner:
    
    
    def __init__(self, connection, logger):
        self.connection = connection
        self.logger = logger
    
    def provisionSecurityGroups(self, groups):
        existingGroups = self.connection.getSecurityGroups()
        for name, group in groups.items():
            if not name in existingGroups:
                self.logger.log("Creating security group {0}".format(name))
                ec2Group = self.connection.createSecurityGroup(name, group["description"])
            else:
                ec2Group = existingGroups[name]
            for rule in group["rules"]:
                self.logger.log("Creating rule {0}:{1}-{2}".format(rule["ip"], rule["fromPort"], rule["toPort"]))
                ec2Group.addRule(rule["fromPort"], rule["toPort"], rule["ip"])

    def provisionNodes(self, nodes):
        # Find existing nodes.
        existingNodes = self.connection.getNodes()
        for name, node in nodes.items():
            # Create non-existing nodes.
            if not name in existingNodes:
                self.logger.log("Creating node {0}".format(name))
                self.connection.createNode(node.image, node.size, name, node.diskSize, node.securityGroup, node.zone)
            else:
                self.logger.log("Node {0} already exists.".format(name))

    def deleteNodes(self, nodes):
        """
        Terminate all nodes from a configuration.
        """
        connection = ec2.EC2Connection(self.region, self.id, self.key)
        existingNodes = connection.getNodes()
        for name in nodes.keys():
            if name in existingNodes:
                existingNodes[name].destroy()
