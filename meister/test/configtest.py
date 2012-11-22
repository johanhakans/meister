'''
Tests for the config class.
@author: fabsor
'''
import unittest
from meister.config import YamlConfig

class ConfigTest(unittest.TestCase):
    
    def testConfigParse(self):
        config = YamlConfig("config.yml")
        driver = config.getDriver()
        self.assertEqual(driver.aws_id, 'your-id')
        self.assertEqual(driver.aws_key, 'your-key')
        self.assertEqual(driver.aws_region, 'your-region')
        # Get a list of nodes, assert that the nodes
        # in the configuration is there.
        nodes = config.getNodes()
        self.assertTrue("mgmt" in nodes)
        self.assertTrue("application1" in nodes)
        self.assertTrue("application2" in nodes)
        
        mgmt = nodes["mgmt"]
        self.assertEqual(mgmt.image, 'ami-c1aaabb5')
        self.assertEqual(mgmt.size, 't1.micro')
        self.assertEqual(mgmt.hostname, 'mgmt')
        self.assertEqual(mgmt.securityGroup, 'group')
        
        # Application 2 should have it's own group
        application2 = nodes["application2"]
        self.assertEqual(application2.securityGroup, 'group2')
        
        # Browse security groups.
        groups = config.getSecurityGroups()
        self.assertTrue("group" in groups)
        self.assertTrue("group2" in groups)
        
        group1 = groups["group"]
        self.assertEqual(group1['description'], "Group1 description")
        self.assertEqual(group1['rules'][0]["ip"], "10.10.1.1/32")
        self.assertEqual(group1['rules'][1]["ip"], "192.168.1.0/32")
        