'''
Created on Jan 10, 2013

@author: fabsor
'''
import ec2
from libcloud.compute.types import Provider
import time

class Provisioner:
    
    
    def __init__(self, connection, logger):
        self.connection = connection
        self.logger = logger
    
    def provisionSecurityGroups(self, groups, nodes = {}):
        existingGroups = self.connection.getSecurityGroups(True)
        for name, group in groups.items():
            if not name in existingGroups:
                self.logger.log("Creating security group {0}".format(name))
                ec2Group = self.connection.createSecurityGroup(name, group["description"])
            else:
                ec2Group = existingGroups[name]
            for rule in group["rules"]:
                if rule["ip"][0] == "^":
                    if len(nodes) == 0:
                        continue
                    name = rule["ip"][1:].partition(":")
                    if nodes[name[0]]:
                        rule["ip"] = nodes[name[0]].externalIp if len(name) < 2 or name[2] != "internal" else nodes[name[0]].internalIp
                        rule["ip"] += "/32"
                    else:
                        continue
                self.logger.log("Creating rule {0}:{1}-{2}".format(rule["ip"], rule["fromPort"], rule["toPort"]))
                ec2Group.addRule(rule["fromPort"], rule["toPort"], rule["ip"])

    def provisionNodes(self, nodes):
        # Find existing nodes.
        existingNodes = self.connection.getNodes()
        elasticIps = self.connection.getElasticIPs(False)
        for name, node in nodes.items():
            # Create non-existing nodes.
            if not name in existingNodes:
                self.logger.log("Creating node {0}".format(name))
                createdNode = self.connection.createNode(node.image, node.size, name, node.diskSize, node.securityGroup, node.zone, node.keyName)
            else:
                self.logger.log("Node {0} already exists.".format(name))

    def deleteNodes(self, nodes):
        """
        Terminate all nodes from a configuration.
        """
        existingNodes = self.connection.getNodes()
        for name in nodes.keys():
            if name in existingNodes:
                self.logger.log("Deleting node {0}".format(name))
                existingNodes[name].destroy()
        self.logger.log("Waiting for nodes to die...")
        def waitForNodes():
            existingNodes = self.connection.getNodes(True)
            for name in nodes.keys():
                if name in existingNodes:
                    return waitForNodes()
        waitForNodes()

    
    def createElasticIps(self, nodes):
        # Associate elastic IP addresses.
        existingNodes = self.connection.getNodes(True)
        elasticIps = self.connection.getElasticIPs(False)
        for name, node in nodes.items():
            if nodes[name].elasticIP and (not existingNodes[name].public_ip or existingNodes[name].public_ip[0] not in elasticIps):
                self.logger.log("Setting up elastic IP for {0}".format(name))
                if len(elasticIps):
                    print "using existing ip"
                    elasticIp = elasticIps.pop()
                else:
                    self.logger.log("Allocating new IP address")
                    elasticIp = self.connection.allocateElasticIP()
                
                self.logger.log("Using IP {0}".format(elasticIp))
                self.connection.associateIP(existingNodes[name], elasticIp)
                while existingNodes[name].public_ip[0] != elasticIp:
                    existingNodes = self.connection.getNodes(True)
                    time.sleep(2)
                node.externalIp = elasticIp

    def deleteSecurityGroups(self, groups):
        existingGroups = self.connection.getSecurityGroups()
        for name in groups.keys():
            if name in existingGroups:
                self.logger.log("Deleting security group {0}".format(name))
                self.connection.deleteSecurityGroup(name)

    def verify(self, nodes, wait=10):
        """
        Verify changes by waiting until the servers are done 
        """
        existingNodes = self.connection.getNodes(True)
        for name, node in nodes.items():
            self.verifyNode(name, node, wait)

    def verifyNode(self, name, node, wait, step = None):
        existingNodes = self.connection.getNodes(True)
        if name in existingNodes:
            existingNode = existingNodes[name]
            if existingNode.extra["status"] == "running":
                status = self.connection.checkNodeStatus(existingNode)
                # We are good to go. Next please.
                if status['systemStatus'] == "ok" and status['instanceStatus'] == "ok":
                    if existingNode.public_ip:
                        node.externalIp = existingNode.public_ip[0]
                        node.internalIp = existingNode.private_ip[0]
                # The machine is booting up.
                elif status['systemStatus'] == 'initializing' or status['instanceStatus'] == 'initializing':
                    if step != "initializing":
                        self.logger.log("Waiting for node {0} to be set up".format(name))
                        step = "initializing"
                    time.sleep(wait)
                    return self.verifyNode(name, node, wait, step)
                # Something went horribly wrong, we can't recover from this.
                else:
                    raise Exception("AWS could not set up instance {0}".format(name))
            # The machine is being created in EC2.
            else:
                if step != "creating":
                    self.logger.log("Waiting for node {0} to be started in EC2".format(name, wait))
                    step = "creating"
                time.sleep(wait)
                return self.verifyNode(name, node, wait, step)
