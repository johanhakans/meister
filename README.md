# Meister

Meister is a CLI tool that aims to ease setting up a complex system of
servers on a cloud hosting provider.  It works by creating a yaml
configuration file that contains all configuration that you want to
provision to a cloud hosting provider. That file can then be version
controlled so that changes in the server stack are easily overviewed.

# Installation
    
	(sudo) python setup.py install

# The meister.yml file

    ---
    # The management server is the main server.
	# A history of the meister.yml is stored here so that changes can be executed.
    managementServer: mgmt

    # The key file is the private key to use when connecting to new hosts.
    keyFile: /path/to/keyfile

    # Tasks can be executed on nodes. This could be for instance be installing puppet.
    # All methods in the task file are exposed. Fabric is available for executing tasks on the machine.
    taskModule: tasks

    # The default user is used when connecting to nodes through ssh.
	# This can be overriden on node level by specifying the user property.
    defaultUser: ubuntu

    # The default key to use.
    defaultKeyFile = /path/to/key

    # The driver is used to create servers on the cloud hosting provider.
    driver:
        name: aws # Only aws is supported currently.
        id: your-id # AWS id
        key: your-key # AWS
       region: your-region # The region, for instance eu-west-1
       defaultSecurityGroup: group # The default security grups that nodes should belong to. This can be overriden by specifiying the securityGroup property.
       defaultZone: eu-west-1a # The default AWS Zone.
       defaultKeyName: example # Default key pair name. Create this keypair in the aws console first!

    DNS:
      name: Provider # Name of your provider, for instance route53
      id: your-id # Route 53 id
      key: your-key # Route 53 key
      defaultZone: example.com. # The zone to use by default. All nodes will register their domains here if you don't specify another zone in the node definition.

    # Security groups with firewall rules.
    securityGroups:
      group:
        description: Group1 description
        rules:
            - ip: 10.10.1.1/32
              fromPort: 8081
              toPort: 8082
            - ip: 0.0.0.0/0
              fromPort: 22
              toPort: 22

        group2:
            description: Group2 description
            rules:
                - ip: 0.0.0.0/0
                  fromPort: 22
                  toPort: 22

    # The nodes to create.
    nodes:
        mgmt:
            hostname: mgmt
            size: t1.micro
            diskSize: 20 # Size in GB. Defaults to 8gb
            externalDNS: mgmt.example.com.
            internalDNS: mgmt.internal.example.com.
            image: ami-c1aaabb5
            tasks: # Tasks are run when the node is first set up.
              - install_puppet
              - install_puppet_master
        application1:
            hostname: application1
            size: t1.micro
            image: ami-c1aaabb5
            externalDNS: application1.example.com.
            internalDNS: application1.internal.example.com.
            tasks:
                - install_puppet
                - register_node
         application2:
             hostname: application2
             size: t1.micro
             externalDNS: application2.example.com. # Binds to external IP address
             internalDNS: application2.internal.example.com. # Binds to internal IP address
             image: ami-c1aaabb5
             securityGroup: group2
             tasks:
                 - install_puppet
                 - register_node



# Usage

1. Create a meister.yml file.
3. Optionally create a python module with tasks that should be
executed on the machine. Refer to the
[Fabric documentation](http://docs.fabfile.org/en/1.5/) for more
info.
2. run meister provision:  


	meister provision


3. Verify that all machines are running on the aws console.

