'''

@author: fabsor
'''
import sys;
from os.path import isfile, dirname, isdir
import os
import yaml
from fabric.operations import prompt
from fabric.contrib.console import confirm
from aws.driver import EC2Driver
from aws.driver import Route53Driver
from deploy import Deployer
import time

DRIVERS = {
    "aws": EC2Driver
}
    
DNSDrivers = {
    "route53": Route53Driver
}

class Config:
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
                    deployer = Deployer(node.externalIp, username=node.user, keyFile=node.keyFile)
                    status = self.getTaskStatus(deployer, logger)
                    # Filter out tasks that has already been run.
                    tasks = filter(lambda task: task not in status["tasks"], node.tasks)
                    for task in tasks:
                        taskFn = getattr(self.tasksModule, task, None)
                        if taskFn:
                            deployer.runTask(taskFn)
                            status["tasks"].append(task)
                            self.putTaskStatus(status, deployer, logger)

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

    def getTaskStatus(self, deployer, logger):
        if isfile("/tmp/meister-status"):
            os.remove("/tmp/meister-status")
        exists = deployer.run("test -f ~/.meister", True)
        if not exists.return_code:
            file = deployer.get("~/.meister", "/tmp/meister-status")[0]
        else:
            return { "tasks": [] }
        content = yaml.load(open(file).read())
        return content

    def putTaskStatus(self, status, deployer, logger):
        file = open("/tmp/meister-status", 'w')
        yaml.dump(status, file)
        file.close()
        deployer.put("/tmp/meister-status", "~/.meister")
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
        self.driver = DRIVERS[data['driver']['name']](self, data)
        self.DNSDriver = DNSDrivers[data['DNS']['name']](self, data)
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


class YamlConfigWriter:
    def listDrivers(self, drivers):
        i = 1;
        for name, driver in drivers.items():
            print "{0}. {1}".format(i, name)
            i += 1
        return i

    def interactive(self):
        settings = { "driver": {}}
        print "Available compute drivers:"
        i = self.listDrivers(DRIVERS)
        def validateDriver(response):
            if int(response) - 1 > i:
                raise Exception("Invalid driver number")
            return int(response) - 1

        driverId = prompt("Select driver:", validate=validateDriver)
        print driverId
        driver = DRIVERS.keys()[driverId]
        settings["driver"]["name"] = driver
        DriverClass = DRIVERS[driver]
        if hasattr(DriverClass, "interactive"):
            DriverClass.interactive(settings)
        nodes = {}
        useDNS = confirm("Do you want to use DNS?")
        if useDNS:
            settings["DNS"] = {}
            i = self.listDrivers(DNSDrivers)
            driverId = prompt("Select driver:", validate=validateDriver)
            settings["DNS"]["name"] = DNSDrivers.keys()[driverId]
            DNSDrivers[settings["DNS"]["name"]].interactive(settings)
        
        def promptNode():
            name, node = self.createNode(DriverClass, useDNS)
            nodes[name] = node
            if prompt("Do you want to create another node?"):
                promptNode()

        if confirm("Do you want to define nodes?"):
            promptNode()
        

    def createNode(self, Driver, useDNS = False):
        node = {}
        props = [
            ("hostname", "Host name"),
            ] + Driver.NodeProperties
        name = prompt("Name:")
        if useDNS:
            props.append(("externalDNS", "External DNS"))
            props.append(("internalDNS", "internal DNS"))

        for prop, title in props:
            node[prop] = prompt(title + ":")

        return (name, node)
            
        


