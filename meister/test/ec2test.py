import unittest
import time
import secrets
from meister.aws import ec2
from libcloud.compute.types import Provider


class AWSConnectionTest(unittest.TestCase):
    
    def setUp(self):
        self.con = ec2.EC2Connection(Provider.EC2_EU_WEST, secrets.EC2_ACCESS_ID, secrets.EC2_SECRET_KEY)

    def testCreateNode(self):
        """
        Test creating a node.
        """
        image_id = 'ami-c1aaabb5'
        # Create a security group
        if "testgroup" not in self.con.getSecurityGroups():
            self.con.createSecurityGroup("testgroup", "testdescription")
        node = self.con.createNode(image_id, 't1.micro', 'testnode', '10', 'testgroup')
        # We should have a pending state.
        self.assertEqual(node.state, 3)
        self.assertTrue("testnode" in self.con.getNodes().keys())
        # Wait for a bit, to get the node into running state.
        while node.extra["status"] != "running":
           time.sleep(4)
           node = self.con.getNodes(True)["testnode"]
        # Test associating an IP address to the node.
        ip_address = self.con.allocateElasticIP()
        self.con.associateIP(node, ip_address)
        node = self.con.getNodes(True)["testnode"]
        self.assertTrue(node.public_ip[0], ip_address)
        self.con.deleteElasticIP(ip_address)
        ips = self.con.getElasticIPs()
        self.assertTrue(ip_address not in ips)
        node.destroy()

    
    def testSecurityGroup(self):
        group = self.con.createSecurityGroup("mygroup", "mydescription")
        group.addRule("8080", "8081", "10.1.1.1/32")
        self.assertEqual(group.listRules(), [{'fromPort': "8080", 'toPort': "8081", 'ip': "10.1.1.1/32", 'protocol': 'tcp'}])
        self.assertTrue("mygroup" in self.con.getSecurityGroups())
        self.con.deleteSecurityGroup("mygroup")
        self.assertTrue("mygroup" not in self.con.getSecurityGroups())

        
