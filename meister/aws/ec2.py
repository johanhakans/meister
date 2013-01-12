'''
Created on Nov 22, 2012

@author: fabsor
'''
from libcloud.compute.providers import get_driver
from libcloud.utils.xml import fixxpath, findtext, findattr, findall
from libcloud.compute.drivers.ec2 import NAMESPACE
from libcloud.compute.deployment import ScriptDeployment

class EC2Connection:
    """
    The EC2Connection class is a tiny wrapper around libcloud
    which only exposes the parts of the API that we are interested in.
    """
   
    def __init__(self, driver, ec2_id, ec2_key):
        Driver = get_driver(driver)
        self.conn = Driver(ec2_id, ec2_key)
        self.securityGroups = None
        self.nodes = None

    def getElasticIPs(self, associated=True):
        """
        Get elastic IP addresses.
        @param allocated: Return addresses that are associated with nodes.
        """
        return self.conn.ex_describe_all_addresses(associated)

    def associateIP(self, node, ip_address):
        """
        Associate an IP address to a node.
        """
        return self.conn.ex_associate_addresses(node, ip_address)

    def allocateElasticIP(self):
        """
        Allocate a new elastic IP address and return it.
        """
        params = {
            "Action": "AllocateAddress",
        }
        response = self.conn.connection.request(self.conn.path, params=params).object
        return findtext(element=response, xpath="publicIp", namespace=NAMESPACE)

    def deleteElasticIP(self, ip_address):
        """
        Delete an elastic IP address.
        """
        params = {
            "Action": "ReleaseAddress",
            "PublicIp": ip_address
        }
        self.conn.connection.request(self.conn.path, params=params)


    def getNodes(self, reset = False):
        """
        Get a list of nodes.
        """
        if not self.nodes or reset:
            # Exclude terminated instances.
            def filterTerminated(item):
                return item.extra["status"] != "terminated"
            self.nodes = self.getDict(self.conn.list_nodes(), 'name', filterTerminated)
        return self.nodes

    def createSecurityGroup(self, name, description):
        """
        Create a security groups
        """
        self.conn.ex_create_security_group(name, description)
        group = EC2SecurityGroup(self.conn, name, description)
        return group
    
    def getSecurityGroups(self):
        """
        Get a list of all security groups.
        """
        if not self.securityGroups:
            params = {
                'Action': 'DescribeSecurityGroups',
            }
            self.securityGroups = self._to_securityGroups(self.conn.connection.request(self.conn.path, params=params).object)
        return self.securityGroups

    def deleteSecurityGroup(self, name):
        """
        Delete a security group.
        @param name The name of the parameter.
        """
        if isinstance(name, EC2SecurityGroup):
            name = name.name

        params = {
         'Action': 'DeleteSecurityGroup',
         'GroupName': name,
        }
        if self.securityGroups and name in self.securityGroups:
            del self.securityGroups[name]
        self.conn.connection.request(self.conn.path, params=params)
    
    def _to_securityGroups(self, object):
        """
        Convert a list from aws to security group objects.
        """
        groups = {}
        for el in object.findall(fixxpath(xpath='securityGroupInfo/item', namespace=NAMESPACE)):
            group = self._to_securityGroup(el)
            groups[group.name] = group
        return groups

    def _to_securityGroup(self, element):
        """
        Convert a SecurityGroupInfo aws object to a python object.
        """
        group = EC2SecurityGroup(
            self.conn,    
            findtext(element=element, xpath='groupName',
                          namespace=NAMESPACE),
            findtext(element=element, xpath='groupDescription',
                          namespace=NAMESPACE),
        )
        for ipRule in element.findall(fixxpath(xpath='ipPermissions/item', namespace=NAMESPACE)):
            group.addRule(
                          findtext(element=ipRule, xpath="fromPort", namespace=NAMESPACE),
                          findtext(element=ipRule, xpath="toPort", namespace=NAMESPACE) ,
                          findtext(element=ipRule, xpath="ipRanges/item/cidrIp", namespace=NAMESPACE),
                          findtext(element=ipRule, xpath="ipProtocol", namespace=NAMESPACE) ,
                          False
                          )
        return group

    def createNode(self, image_id, size_id, name, size='8', securityGroup=None, zone=None, keyName=None):
        """
        Create a node on aws.
        """
        params = {
         'Action': 'RunInstances',
         'ImageId': image_id,
         'MinCount': '1',
         'MaxCount': '1',
         'InstanceType': size_id,
         'BlockDeviceMapping.0.DeviceName': '/dev/sda1',
         'BlockDeviceMapping.0.Ebs.VolumeSize': str(size),
         
        }
        if securityGroup:
            params['SecurityGroup.0'] = securityGroup
        if zone:
            params['Placement.AvailabilityZone'] = zone
        if keyName:
            params["KeyName"] = keyName

        object = self.conn.connection.request(self.conn.path, params=params).object
        nodes = self.conn._to_nodes(object, 'instancesSet/item')
        for node in nodes:
            tags = {'Name': name}
            try:
                self.conn.ex_create_tags(resource=node, tags=tags)
            except Exception:
                continue
        if len(nodes) == 1:
            return nodes[0]
        else:
            return nodes

    def destroyNode(self, node_id):
        """
        >>> aws = EC2Connection(EC2_ACCESS_ID, EC2_SECRET_KEY)
        >>> node = aws.createNode(IMAGE, SIZE_ID, SIZE)
        >>> aws.destroyNode(node.id)
        >>> node in node.getNodes()
        """
        nodes = self.getNodes()
        if nodes[node_id]:
            return self.conn.destroy_node(nodes[node_id])
      
    def getDict(self, libcloudlist, property="id", filterFn = None):
        cloudDict = {}
        for item in libcloudlist:
            if not filterFn or filterFn(item):
                cloudDict[getattr(item, property)] = item
        return cloudDict
    
class EC2SecurityGroup:
    """
    A security group
    """
    def __init__(self, con, name, description):
        self.con = con
        self.name = name
        self.description = description
        self.rules = []
    
    def addRule(self, fromPort, toPort, ip, protocol='tcp', commit=True):
        """
        Add a security rule to a group.
        """
        rule = {
            'fromPort': fromPort,
            'toPort': toPort,
            'ip': ip,
            'protocol': protocol
        }
        if not rule in self.rules:
            if commit:
                self.con.ex_authorize_security_group(self.name, fromPort, toPort, ip, protocol)
            self.rules.append(rule)
        return self
    
 
    def listRules(self):
        """
        List all available rules.
        """
        return self.rules
