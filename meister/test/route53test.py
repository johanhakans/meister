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
        self.zoneObjs = []
        
    def testCreateZone(self):
        zone = route53.Zone("onedomain.com.", "Example domain")
        zone = self.con.saveZone(zone)
        self.assertEqual(zone.name, "onedomain.com.")
        self.assertEqual(zone.comment, "Example domain")
        self.con.deleteZone(zone)
        
    def testGetZones(self):
        zones = ["example.com.", "example2.com.", "example3.com."]
        self.zoneObjs = [self.con.saveZone(route53.Zone(zone)) for zone in zones]
        fetchedObjs = self.con.getZones()
        def filterZones(val):
            return val.name in zones
        fetchedZones = [zone.name for zone in filter(filterZones, fetchedObjs)]
        fetchedZones.sort()
        self.assertEqual(fetchedZones, zones)
    
    def testCreateRecord(self):
        zone = self.con.saveZone(route53.Zone("onedomain.com.", "Example domain"))
        self.zoneObjs.append(zone)
        zone.addRecord(zone.RECORDTYPE_A, "test.onedomain.com.", "10.1.1.1")
        zone.addRecord(zone.RECORDTYPE_CNAME, "test2.onedomain.com.", "test.onedomain.com")
        self.con.saveZone(zone)
        for record in zone.records.values():
            self.assertTrue(record["saved"])
                
    def tearDown(self):
        unittest.TestCase.tearDown(self)
        if self.zoneObjs:
            for zoneObj in self.zoneObjs:
                self.con.deleteZone(zoneObj)
        