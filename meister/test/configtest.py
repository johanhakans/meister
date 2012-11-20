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
