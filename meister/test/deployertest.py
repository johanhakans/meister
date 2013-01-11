'''
Created on Jan 11, 2013

@author: fabsor
'''

import unittest
import secrets
import time
from meister.aws import ec2
from meister.deploy import Deployer
from libcloud.compute.types import Provider


class DeployerTest(unittest.TestCase):
    
    def setUp(self):
        self.con = ec2.EC2Connection(Provider.EC2_EU_WEST, secrets.EC2_ACCESS_ID, secrets.EC2_SECRET_KEY)
        self.node = self.con.createNode('ami-c1aaabb5', 't1.micro', 'testnode', keyName="example")
        # Wait for running state.
        while self.node.extra["status"] != "running":
            nodes = self.con.getNodes(True)
            self.node = nodes['testnode']
            time.sleep(10)
        
    def testDeploy(self):
        deployer = Deployer(self.node.public_ip[0], username="ubuntu", keyFile=secrets.KEY_FILE)
        deployer.run("ls /")
        deployer.sudo("ls /")
        deployer.put("testfile", "/home/ubuntu/testfile")
        import tasks
        deployer.runTasks(tasks.test_task)

    def tearDown(self):
        unittest.TestCase.tearDown(self)
        self.node.destroy()