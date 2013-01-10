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
