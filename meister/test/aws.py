import unittest
import secrets
from pprint import pprint as pp
from meister import aws
from libcloud.compute.types import Provider

class AWSConnectionTest(unittest.TestCase):
    
    def setUp(self):
        self.aws = aws.AWSConnection(Provider.EC2_EU_WEST, config.EC2_ACCESS_ID, config.EC2_SECRET_KEY)

    def testCreateNode(self):
        """
        Test creating a node.
        """
        image_id = 'ami-c1aaabb5'
        # Create a security group
        if "testgroup" not in self.aws.getSecurityGroups():
            self.aws.createSecurityGroup("testgroup", "testdescription")
        node = self.aws.createNode(image_id, 't1.micro', 'testnode', '10', 'testgroup')
        # We should have a pending state.
        self.assertEqual(node.state, 3)
        self.assertTrue("testnode" in self.aws.getNodes().keys())
        node.destroy()
        # Destroy the newly created node.
    
    def testSecurityGroup(self):
        group = self.aws.createSecurityGroup("mygroup", "mydescription")
        group.addRule("8080", "8081", "10.1.1.1/32")
        self.assertEqual(group.listRules(), [{'fromPort': "8080", 'toPort': "8081", 'ip': "10.1.1.1/32", 'protocol': 'tcp'}])
        self.assertTrue("mygroup" in self.aws.getSecurityGroups())
        self.aws.deleteSecurityGroup("mygroup")
        self.assertTrue("mygroup" not in self.aws.getSecurityGroups())

