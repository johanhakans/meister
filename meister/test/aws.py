import unittest
import config
from pprint import pprint as pp
from meister import aws
from libcloud.compute.types import Provider

class AWSConnectionTest(unittest.TestCase):
    
    def setUp(self):
        self.nodes = []
        self.aws = aws.AWSConnection(Provider.EC2_EU_WEST, config.EC2_ACCESS_ID, config.EC2_SECRET_KEY)

    def testCreateNode(self):
        """
        Test creating a node.
        """
        image_id = 'ami-c1aaabb5'
        node = self.aws.createNode(image_id, 't1.micro', 'testnode', '10')
        node.destroy()
        print node
        self.assertEqual(node.image, image_id)
        
    def tearDown(self):
        for node in self.nodes:
            self.aws.destroyNode(node.node_id)
