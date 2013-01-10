'''
Created on Jan 10, 2013

@author: fabsor
'''
import unittest
from meister.config import YamlConfig


class ListLogger():
    def __init__(self):
        self.logs = []

    def log(self, message, type = 'notice'):
        self.logs.append({"message": message, "type": type})

class AWSProvisionerTest(unittest.TestCase):
    
    def setUp(self):
        self.listLogger = ListLogger()

    def testProvision(self):
        config = YamlConfig("config_aws.yml")
        driver = config.getDriver()
        driver.provision(self.listLogger)
        dnsDriver = config.getDNSDriver()
        dnsDriver.provision(config.getNodes(), self.listLogger)
        driver.terminate(self.listLogger)
        dnsDriver.terminate(config.getNodes(), self.listLogger)
        print self.listLogger.logs
