from libcloud.compute.types import Provider
from libcloud.compute.providers import get_driver

class AWSConnection:
    """
    The AWSConnection class is a tiny wrapper around libcloud
    which only exposes the parts of the API that we are interested in.
    """
   
    def __init__(self, driver, ec2_id, ec2_key):
        Driver = get_driver(driver)
        self.conn = Driver(ec2_id, ec2_key)

    def getNodes(self):
        """
        Get a list of nodes.
        """
        if not self.nodes:
            self.nodes = self.conn.list_nodes()
            return self.nodes

    def createSecurityGroup(self, name, description):
        """
        Create a security groups
        """
        self.conn.ex_create_security_group(name, description)
        return self

    def addSecurityRule(self, name, fromPort, toPort, ip, protocol='tcp'):
        self.conn.ex_authorize_security_group(name, fromPort, ip, protocol)
        return self

    def createNode(self, image_id, size_id, name, size='8'):
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
         'BlockDeviceMapping.0.Ebs.VolumeSize': size
        }
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
        >>> aws = AWSConnection(EC2_ACCESS_ID, EC2_SECRET_KEY)
        >>> node = aws.createNode(IMAGE, SIZE_ID, SIZE)
        >>> aws.destroyNode(node.id)
        >>> node in node.getNodes()
        """
        nodes = self.getDict(self.getNodes())
        if nodes[node_id]:
            return self.conn.destroy_node(nodes[node_id])
      
    def getDict(self, libcloudlist):
        cloudDict = {}
        for item in libcloudlist:
            cloudDict[item.id] = item
        return cloudDict
