'''
Created on Jan 10, 2013

@author: fabsor
'''
import unittest
from meister.config import YamlConfig
from meister.provision import AWSProvisioner
from meister.provision import PrintLogger


class AWSProvisionerTest(unittest.TestCase):


    def testProvisionNodes(self):
        config = YamlConfig("config_aws.yml")
        provisioner = AWSProvisioner(config, PrintLogger())
        provisioner.provisionNodes(config.getNodes())

    def testProvisionSecurityGroups(self):
        config = YamlConfig("config_aws.yml")
        provisioner = AWSProvisioner(config, PrintLogger())
        provisioner.provisionSecurityGroups(config.getDriver().getSecurityGroups())


