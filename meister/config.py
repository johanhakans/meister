'''

@author: fabsor
'''
import sys;
from os.path import isfile, dirname, isdir
import os
import yaml
from aws.driver import EC2Driver
from aws.driver import Route53Driver
from deploy import Deployer
import time

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
        self.basedir = dirname(configFile)
        sys.path.append(self.basedir)
        self.statusFile = "{0}/{1}".format(self.basedir, "meister")
        self.DNSDriver = None
        self.parse()

    def provision(self, logger):
        status = {}
        if isfile(self.statusFile):
            status = yaml.load(open(self.statusFile).read())
        self.driver.provision(logger)
        if self.DNSDriver:
            self.DNSDriver.provision(self.getNodes(), logger)
        # Run tasks
        if self.tasksModule:
            logger.log("Running tasks.")
            nodes = self.getNodes().items()
            # Create a host list that can be used by fabric scripts.
            hostList = {}
            for name, node in nodes:
                hostList[name] = node.externalIp

            # Always take the management server first, if it is available.
            # This is necessary since the other nodes could depend on the management server being in place.
            if "managementServer" in self.data:
                mgmt = self.data["managementServer"]
                def sortNodes(item1, item2):
                    if item1[0] == mgmt:
                        return -1
                    return 0
                nodes = sorted(nodes, sortNodes)

            for name, node in nodes:
                if node.user:
                    logger.log("Running tasks for {0}".format(name))
                    deployer = Deployer(node.externalIp, username=node.user, keyFile=node.keyFile, hostList = hostList)
                    meisterFile = "/home/{0}/.meister".format(node.user)
                    status = self.getTaskStatus(deployer, logger, meisterFile)
                    # Filter out tasks that has already been run.
                    tasks = filter(lambda task: task not in status["tasks"], node.tasks)
                    for task in tasks:
                        if isinstance(task, dict):
                            taskFnName = task["name"]
                            args = task["arguments"]
                        else:
                            taskFnName = task
                            args = []
                        taskFn = getattr(self.tasksModule, taskFnName, None)
                        if taskFn:
                            deployer.runTask(taskFn, args)
                            status["tasks"].append(task)
                            self.putTaskStatus(status, deployer, logger, meisterFile)

    def task(self, logger, nodeName, task):
        nodes = self.getNodes()
        if not nodeName in nodes:
            logger.log("Node {0} does not exist.".format(nodeName), "error")
            return
        taskFn = getattr(self.tasksModule, task, None)
        if not taskFn:
            logger.log("Task {0} does not exist.".format(task), "error")
            return;

        node = nodes[nodeName]
        deployer = Deployer(node.externalIp, username=node.user, keyFile=node.keyFile)
        deployer.runTask(taskFn)

    def ssh(self, logger, nodeName):
        node = self.getNodes()[nodeName]
        deployer = Deployer(node.externalIp, username=node.user, keyFile=node.keyFile)
        deployer.ssh()

    def getTaskStatus(self, deployer, logger, meisterFile = "~/.meister"):
        if isfile("/tmp/meister-status"):
            os.remove("/tmp/meister-status")
        if deployer.fileExists(meisterFile):
            file = deployer.get(meisterFile, "/tmp/meister-status")[0]
        else:
            return { "tasks": [] }
        content = yaml.load(open(file).read())
        return content

    def putTaskStatus(self, status, deployer, logger, meisterFile = "~/.meister"):
        file = open("/tmp/meister-status", 'w')
        yaml.dump(status, file)
        file.close()
        deployer.put("/tmp/meister-status", meisterFile)
        os.remove("/tmp/meister-status")

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
        # self.DNSDriver = self.DNSDrivers[data['DNS']['name']](self, data)
        self.nodes = {}
        self.data = data
        self.tasksModule = __import__(data["tasksModule"]) if "tasksModule" in data else None
        self.defaultKeyFile = data["defaultKeyFile"] if "defaultKeyFile" in data else None
        self.defaultUser = data["defaultUser"] if "defaultUser" in data else None

        for name, node in data["nodes"].items():
            self.nodes[name] = self.driver.getNode(name, node)
            self.nodes[name].tasks = node["tasks"] if "tasks" in node else []
            for prop, defaultProp in [("keyFile", "defaultKeyFile"), ("user", "defaultUser")]:
                if (prop in node):
                    setattr(self.nodes[name], prop, node[prop])
                else:
                    val = getattr(self, defaultProp, None)
                    setattr(self.nodes[name], prop, val)
