'''
Test route 53 integration.

@author: fabsor
'''
import unittest 
from meister.aws import route53
from secrets import EC2_ACCESS_ID, EC2_SECRET_KEY, ROUTE_53_ZONE_ID
class Route53Test(unittest.TestCase):
    def setUp(self):
        self.con = route53.Route53Connection(EC2_ACCESS_ID, EC2_SECRET_KEY)
        
    def testCreateZone(self):
        zone = route53.Zone("example.com.", "Example domain")
        zone = self.con.saveZone(zone)
        self.assertEqual(zone.name, "example.com.")
        self.assertEqual(zone.comment, "Example domain")
        self.con.deleteZone(zone)
        
