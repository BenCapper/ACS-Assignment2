import os
import time
from typing import Protocol
import boto3
import subprocess
import datetime
import webbrowser


def work_with_file(fname, opt, the_str, pass_str, err_str, sleep_dur):
    sleep(sleep_dur)
    try:
        with open(fname, opt) as file:
            file.write(the_str)
            file.close()
        pretty_print(pass_str)
    except:
        pretty_print(err_str)

def pretty_print(the_string):
    print("------------------------------------------------------")
    print(the_string)
    print("------------------------------------------------------")
    with open("log.txt", "a") as logfile:
        logfile.write(str(datetime.datetime.now())[:-7] + ":  " + the_string + "\n")
        logfile.close()

def sleep(duration):
    time.sleep(duration)

def subproc(cmd, pass_str, err_str, sleep_dur, output=None):
    sleep(sleep_dur)
    if output is True:
        try:
            result = subprocess.run(cmd, shell=True, capture_output=True)
            pretty_print(pass_str)
            return result
        except:
            pretty_print(err_str)
    else:
        try:
            subprocess.run(cmd, shell=True)
            pretty_print(pass_str)
        except:
            pretty_print(err_str)


region = "eu-west-1"
ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")
auto_client = boto3.client('autoscaling')
load_client = boto3.client("elbv2")
cert_client = boto3.client('acm')
cloud_client = boto3.client('cloudwatch')

string_list = list()
grp_id = list()
web_grp_id = list()
db_grp_id = list()
lb_grp_id = list()
inst_list = list()
auto_ids = dict()
passwd = "acspassword"
install_cmd = "sudo -S dnf install openssl -y"
key_name_list = ["assign_two"]
key_file_name = "assign_two.pem"
sec_grp = "assign_two"
web_sec_grp = "port3000"
db_sec_grp = "db_sec_grp"
lb_sec_grp = "lb_sec_grp"
log_name = "log.txt"
index_file = "index.html"
key_name = ""
key_response = ""
public_ip = ""
assign_one_key = ""
found_key_name = ""
vpc = ""
vpc_id = ""
igw = ""
nat_id = ""
sg1_response = ""
sg2_response = ""
rt_pub_w1a_id = ""
rt_pub_w1b_id = ""
rt_pub_w1c_id = ""
rt_pri_w1a_id = ""
rt_pri_w1b_id = ""
rt_pri_w1c_id = ""
sub1_rt = ""
sub2_rt = ""
sub3_rt = ""
sub4_rt = ""
sub5_rt = ""
sub6_rt = ""
pub_west1a = ""
pub_west1b = ""
pub_west1c = ""
pri_west1a = ""
pri_west1b = ""
pri_west1c = ""
pub_ip_address = ""
allocation_id = ""
endpoint_id = ""
vpc_sec_grp_resp = ""
web_sec_grp_resp = ""
db_sec_grp_resp = ""
lb_grp_resp = ""
lb_dns = ""
b_cert = ""
priv_key = ""
lb_arn = ""
cert_arn = ""
http_arn = ""
https_arn = ""
http_list_arn = ""
https_list_arn = ""
lb_sec_id = ""
port3000_arn = ""
port_list_arn = ""

tag = {"Key": "Name", "Value": "Master Web Server - Assign Two"}

# If old log exists
if os.path.exists(log_name):
    # Delete
    subproc(f"rm -f {log_name}", "Deleted old log file", "No old log file found", 1)


# Create Vpc
try:
    sleep(1)
    vpc_response = ec2_client.create_vpc(
        CidrBlock="10.0.0.0/16",
        AmazonProvidedIpv6CidrBlock=False,
        TagSpecifications=[
            {
               'ResourceType': 'vpc', 
               'Tags': [
                   {
                       'Key': 'Name',
                       'Value': 'BenVpcA2'
                   }
               ] 
            }
        ]
    )
    vpc_id = vpc_response['Vpc']['VpcId']
    vpc = ec2_resource.Vpc(vpc_id)
    vpc.wait_until_available()
    pretty_print(f"Created VPC: {vpc_id}")
except:
    pretty_print(f"Could not create the VPC")

# Enable DNS Hostnames
try:
    sleep(1)
    ec2_client.modify_vpc_attribute(
        VpcId = vpc_id,
        EnableDnsHostnames = { 'Value': True }
    )
    pretty_print("DNS Hostnames Enabled")
except:
    pretty_print("Could not enable DNS Hostnames")

# Enable DNS Support
try:
    sleep(1)
    ec2_client.modify_vpc_attribute(
        VpcId = vpc_id,
        EnableDnsSupport = { 'Value': True }
    )
    pretty_print("DNS Support Enabled")
except:
    pretty_print("Could not enable DNS Support")

# Create Public Subnet 1
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pub_eu_w1a'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1a',
        CidrBlock='10.0.0.0/20',
        VpcId = vpc_id,
    )
    pub_west1a = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Public Subnet EU-WEST-1A: {pub_west1a}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1A")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1a,
        MapPublicIpOnLaunch={'Value':True},
    )
    pretty_print("Modified Subnet Attribute: Map Public Ip on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Map Public Ip on Launch")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1a,
        EnableResourceNameDnsARecordOnLaunch={'Value': True}
    )
    pretty_print("Modified Subnet Attribute: Enable RBN on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Enable RBN on Launch")

# Create Public Subnet 2
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pub_eu_w1b'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1b',
        CidrBlock='10.0.16.0/20',
        VpcId = vpc_id,
    )
    pub_west1b = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Public Subnet EU-WEST-1B: {pub_west1b}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1B")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1b,
        MapPublicIpOnLaunch={'Value':True},
    )
    pretty_print("Modified Subnet Attribute: Map Public Ip on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Map Public Ip on Launch")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1b,
        EnableResourceNameDnsARecordOnLaunch={'Value': True}
    )
    pretty_print("Modified Subnet Attribute: Enable RBN on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Enable RBN on Launch")

# Create Public Subnet 3
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pub_eu_w1c'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1c',
        CidrBlock='10.0.32.0/20',
        VpcId = vpc_id,
    )
    pub_west1c = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Public Subnet EU-WEST-1C: {pub_west1c}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1C")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1c,
        MapPublicIpOnLaunch={'Value':True},
    )
    pretty_print("Modified Subnet Attribute: Map Public Ip on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Map Public Ip on Launch")

try:
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1c,
        EnableResourceNameDnsARecordOnLaunch={'Value': True}
    )
    pretty_print("Modified Subnet Attribute: Enable RBN on Launch")
except:
    pretty_print("Could not modify Subnet Attribute: Enable RBN on Launch")

# Create Private Subnet 1
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pri_eu_w1a'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1a',
        CidrBlock='10.0.128.0/20',
        VpcId = vpc_id
    )

    pri_west1a = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Private Subnet EU-WEST-1A: {pri_west1a}")
except:
    pretty_print("Could not create the Private Subnet EU-WEST-1A")

# Create Private Subnet 2
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pri_eu_w1b'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1b',
        CidrBlock='10.0.144.0/20',
        VpcId = vpc_id
    )

    pri_west1b = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Private Subnet EU-WEST-1B: {pri_west1b}")
except:
    pretty_print("Could not create the Private Subnet EU-WEST-1B")

# Create Private Subnet 3
try:
    sleep(1)
    subnet_response = ec2_client.create_subnet(
        TagSpecifications= [
            {
                'ResourceType': 'subnet',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'pri_eu_w1c'
                    }
                ]
            }
        ],
        AvailabilityZone='eu-west-1c',
        CidrBlock='10.0.160.0/20',
        VpcId = vpc_id
    )

    pri_west1c = subnet_response['Subnet']['SubnetId']
    pretty_print(f"Created Private Subnet EU-WEST-1C: {pri_west1c}")
except:
    pretty_print("Could not create the Private Subnet EU-WEST-1C")

# Create Internet Gateway
try:
    sleep(1)
    internetgateway = ec2_resource.create_internet_gateway()
    igw = internetgateway.id
    pretty_print(f"Created Internet Gateway: {igw}")
except:
    pretty_print(f"Could not create the Internet Gateway")

# Attach Internet Gateway to the Vpc
try:
    sleep(1)
    vpc.attach_internet_gateway(InternetGatewayId=igw)
    pretty_print(f"Attached Internet Gateway {igw} to VPC {vpc_id}")
except:
    pretty_print(f"Could not attach Internet Gateway {igw} to VPC {vpc_id}")

# Create Pub-W1A Route Table
try:
    sleep(1)
    sub1_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pub_w1a'
                }
            ]
        }
        ]
    )
    rt_pub_w1a_id = sub1_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pub_w1a_id}")
except:
    pretty_print(f"Could not create the Route Table")

# Create Pub-W1A Route
try:
    sleep(1)
    route = ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw,
        RouteTableId=rt_pub_w1a_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create the Route")

# Associate Route Table with Pub-W1A Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pub_w1a_id,
        SubnetId=pub_west1a
    )
    pretty_print(f"Associated Route Table {rt_pub_w1a_id} with the Public Subnet EU-WEST-1A: {pub_west1a}")
except:
    pretty_print(f"Could not associate the Route Table with the Public Subnet EU-WEST-1A")

# Create Pub-W1B Route Table
try:
    sleep(1)
    sub2_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_w1b'
                }
            ]
        }
        ]
    )
    rt_pub_w1b_id = sub2_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pub_w1b_id}")
except:
    pretty_print(f"Could not create the Route Table")

# Create Pub-W1B Route
try:
    sleep(1)
    route = ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw,
        RouteTableId=rt_pub_w1b_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create the Route")

# Associate Route Table with Pub-W1B Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pub_w1b_id,
        SubnetId=pub_west1b
    )
    pretty_print(f"Associated Route Table {rt_pub_w1b_id} with the Public Subnet EU-WEST-1B: {pub_west1b}")
except:
    pretty_print(f"Could not associate the Route Table with the Public Subnet EU-WEST-1B")

# Create Pub-W1C Route Table
try:
    sleep(1)
    sub3_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_w1c'
                }
            ]
        }
        ]
    )
    rt_pub_w1c_id = sub3_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pub_w1c_id}")
except:
    pretty_print(f"Could not create the Route Table")

# Create Pub-W1C Route
try:
    sleep(1)
    route = ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        GatewayId=igw,
        RouteTableId=rt_pub_w1c_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create the Route")

# Associate Route Table with Pub-W1C Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pub_w1c_id,
        SubnetId=pub_west1c
    )
    pretty_print(f"Associated Route Table {rt_pub_w1c_id} with the Public Subnet EU-WEST-1C: {pub_west1c}")
except:
    pretty_print(f"Could not associate the Route Table with the Public Subnet EU-WEST-1C")

# Allocate Elastic IP
try:
    sleep(1)
    ip_response = ec2_client.allocate_address()
    pub_ip_address = ip_response['PublicIp']
    allocation_id = ip_response['AllocationId']
    pretty_print(f"Allocated Ip Address: {pub_ip_address}")
except:
    pretty_print("Could not allocate an Ip Address (Max 5)")

# Create NAT Gateway
try:
    sleep(1)
    nat_response = ec2_client.create_nat_gateway(
        AllocationId=allocation_id,
        SubnetId = pub_west1a,
        ConnectivityType='public',
        TagSpecifications=[
            {
                'ResourceType': 'natgateway',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'nat-west1a'
                    }
                ]
            }
        ]
    )
    nat_id = nat_response['NatGateway']['NatGatewayId']
    pretty_print(f"Created Nat Gateway: {nat_id}")
except:
    pretty_print("Could not create the Nat Gateway")

try:
    sleep(1)
    waiter = ec2_client.get_waiter('nat_gateway_available')
    pretty_print(f"Waiting for the Nat Gateway to become available...")
    waiter.wait(
        NatGatewayIds=[nat_id]
    )
except:
    pretty_print("Could not find the Nat Gateway to wait for")

# Create Pri-W1A Route Table
try:
    sleep(1)
    sub4_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pri_w1a'
                }
            ]
        }
        ]
    )
    rt_pri_w1a_id = sub4_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pri_w1a_id}")
except:
    pretty_print("Could not create the Route Table")

# Create Pri-W1A Route
try:
    sleep(1)
    nat_route=ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=nat_id,
        RouteTableId= rt_pri_w1a_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create Route")

# Associate Route Table with Pri-W1A Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pri_w1a_id,
        SubnetId=pri_west1a
    )
    pretty_print(f"Associated Route Table {rt_pri_w1a_id} with the Private Subnet EU-WEST-1A: {pri_west1a}")
except:
    pretty_print("Could not associate the Route Table with the Private Subnet EU-WEST-1A")

# Create Pri-W1B Route Table
try:
    sleep(1)
    sub5_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pri_w1b'
                }
            ]
        }
        ]
    )
    rt_pri_w1b_id = sub5_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pri_w1b_id}")
except:
    pretty_print("Could not create the Route Table")

# Create Pri-W1B Route
try:
    sleep(1)
    nat_route=ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=nat_id,
        RouteTableId= rt_pri_w1b_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create Route")

# Associate Route Table with Pri-W1B Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pri_w1b_id,
        SubnetId=pri_west1b
    )
    pretty_print(f"Associated Route Table {rt_pri_w1b_id} with the Private Subnet EU-WEST-1B: {pri_west1b}")
except:
    pretty_print("Could not associate the Route Table with the Private Subnet EU-WEST-1B")

# Create Pri-W1C Route Table
try:
    sleep(1)
    sub6_routetable = ec2_client.create_route_table(
        VpcId=vpc_id,
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pri_w1c'
                }
            ]
        }
        ]
    )
    rt_pri_w1c_id = sub6_routetable['RouteTable']['RouteTableId']
    pretty_print(f"Created Route Table: {rt_pri_w1c_id}")
except:
    pretty_print("Could not create the Route Table")

# Create Pri-W1C Route
try:
    sleep(1)
    nat_route=ec2_client.create_route(
        DestinationCidrBlock='0.0.0.0/0',
        NatGatewayId=nat_id,
        RouteTableId= rt_pri_w1c_id
    )
    pretty_print("Created Route")
except:
    pretty_print("Could not create Route")

# Associate Route Table with Pri-W1C Subnet
try:
    sleep(1)
    ec2_client.associate_route_table(
        RouteTableId=rt_pri_w1c_id,
        SubnetId=pri_west1c
    )
    pretty_print(f"Associated Route Table {rt_pri_w1c_id} with the Private Subnet EU-WEST-1C: {pri_west1c}")
except:
    pretty_print("Could not associate the Route Table with the Private Subnet EU-WEST-1C")

# Create S3 Endpoints
try:
    sleep(1)
    endpoint_response = ec2_client.create_vpc_endpoint(
        VpcEndpointType='Gateway',
        VpcId=vpc_id,
        ServiceName='com.amazonaws.eu-west-1.s3',
        RouteTableIds=[
            rt_pri_w1a_id,
            rt_pri_w1b_id,
            rt_pri_w1c_id
        ],
        PrivateDnsEnabled=False,
    )
    endpoint_id = endpoint_response['VpcEndpoint']['VpcEndpointId']
    pretty_print(f"Created VPC Endpoint: {endpoint_id}")
except:
    pretty_print("Could not create the VPC Endpoints")

# Set DHCP Options
try:
    dhcp_response = ec2_client.associate_dhcp_options(
        DhcpOptionsId='dopt-ab9acdcd',
        VpcId=vpc_id,
    )
    pretty_print(f"Associated DHCP options set with Vpc {vpc_id}")
except:
    pretty_print(f"Could not associate DHCP options set with the Vpc")

# Check if the assign_two keypair exists
try:
    sleep(1)
    found_key_name = ec2_client.describe_key_pairs(
        KeyNames=key_name_list
    )["KeyPairs"][0]["KeyName"]
except:
    found_key_name = ""
    pretty_print("Keypair assign_two does not exist")

# Delete any existing keypair named assign_one locally
if os.path.exists(key_file_name):
    subproc(
        f"rm -f {key_file_name}",
        "Deleted old keypair file locally",
        "Could not delete old local keypair",
        1,
    )
else:
    sleep(1)
    pretty_print("No old keypairs found")

# If there is already an AWS key named assign_two, delete it
if found_key_name == key_name_list[0]:
    try:
        delete_key_resp = ec2_client.delete_key_pair(
            KeyName=found_key_name
        )
        sleep(1)
        pretty_print("Deleted old keypair from AWS")
    except:
        pretty_print(f"Could not delete the AWS keypair: {found_key_name}")

# Keypair now deleted on both AWS and locally

# Create a new keypair on AWS
try:
    sleep(1)
    key_response = ec2_client.create_key_pair(
        KeyName=key_name_list[0],
        KeyType="rsa"
    )
    assign_one_key = key_response["KeyMaterial"]
    key_name = key_response["KeyName"]
    pretty_print(f"Keypair {key_file_name} created on AWS")
except:
    pretty_print(f"Keypair {key_file_name} could not be created on AWS")

# Save keypair data to file
work_with_file(
    key_file_name,
    "w",
    assign_one_key,
    f"Keypair {key_file_name} created locally",
    f"Keypair {key_file_name} could not be created locally",
    1,
)

# Create security group for template instance
try:
    # Check if security group already exists
    sleep(1)
    desc_response = ec2_client.describe_security_groups(
        GroupNames=[sec_grp]
        )
    grp_id.append(desc_response[
        "SecurityGroups"][0]["GroupId"]
        )
except:
    pretty_print(f"Could not find the {sec_grp} security group")

# grp_id isnt empty, use that security group
if grp_id:
    sleep(1)
    pretty_print(f"Using the security group: {sec_grp}")
# grp_id is empty, create new security group
else:
    try:
        sleep(1)
        sec_grp_resp = ec2_resource.create_security_group(
            GroupName=sec_grp, Description="Port3000"
        )
        pretty_print(f"Created the security group: {sec_grp}")
        waiter = ec2_client.get_waiter('security_group_exists')
        pretty_print("Waiting for the Security Group to become available")
        waiter.wait(GroupNames=[sec_grp])
    except:
        pretty_print(f"Could not create the security group: {sec_grp}")
    # If the create function was successful, set ip permissions
    if sec_grp_resp:
        try:
            sleep(1)
            # Inbound rules
            sec_ingress_response = sec_grp_resp.authorize_ingress(
                IpPermissions=[
                    {
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "ssh"},
                        ],
                    },
                    {
                        "FromPort": 3000,
                        "ToPort": 3000,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                ],
            )
            pretty_print(f"Security group rules set for: {sec_grp}")
        except:
            pretty_print("Security group rules not set")
        try:
            # Get the new security group id
            sleep(1)
            desc_security = ec2_client.describe_security_groups(GroupNames=[sec_grp])
            grp_id.append(desc_security["SecurityGroups"][0]["GroupId"])
            pretty_print(f"Using the security group: {sec_grp}")
        except:
            pretty_print(f"Could not create the security group: {sec_grp}")

# Create a template instance
try:
    sleep(1)
    create_response = ec2_resource.create_instances(
        ImageId='ami-0069d66985b09d219',
        KeyName=key_name,
        InstanceType="t2.nano",
        SecurityGroupIds=grp_id,
        MinCount=1,
        MaxCount=1,
        Monitoring={'Enabled': True},
        PrivateDnsNameOptions={'EnableResourceNameDnsARecord': True}
    )
    created_instance = create_response[0]
    inst_id = created_instance.id
    pretty_print(f"Instance {inst_id} created")
except:
    pretty_print("Could not create the ec2 Instance")

try:
    sleep(1)
    pretty_print(f"Waiting for Instance {inst_id} to become available...")
    created_instance.wait_until_running()
    pretty_print(f"Instance {inst_id} running")
    created_instance.reload()
    created_instance.wait_until_running()
    public_ip = created_instance.public_ip_address
except:
    pretty_print("Instance did not start running")

# Set Keypair permissions
subproc(
    f"chmod 400 {key_file_name}",
    "Keypair permissions set",
    "Could not set keypair permissions",
    2,
)

#Associate iam profile
try:
    response = ec2_client.associate_iam_instance_profile(
        IamInstanceProfile={
            'Arn': 'arn:aws:iam::778769697098:instance-profile/EC2IAM',
            'Name': 'EC2IAM'
        },
        InstanceId=inst_id
    )
    pretty_print("Associated Iam profile with the template instance")
except:
    pretty_print("Could not associate Iam profile with the template instance")

# SSH into instance and install the web app
command_list = '''
sudo yum install httpd -y; sudo systemctl enable httpd; sudo systemctl start httpd; sudo service crond start;
sudo touch index.html; sudo chmod 777 index.html; sudo echo "<b>Assignment Two Index</b> " >> index.html;
sudo cp index.html /var/www/html/index.html; sudo chmod 755 -R /var/www;
'''
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} '{command_list}'"
result = subproc(
    ssh_command,
    "Http server set up on the ec2 instance",
    "Could not set up the Http server on the ec2 instance",
    2,
    True
)

# First ssh attempt failed, keep trying
while result.returncode != 0:
    pretty_print("Failed ssh attempt, trying again...")
    result = subproc(
    ssh_command,
    "Http server set up on the ec2 instance",
    "Could not set up the Http server on the ec2 instance",
    2,
    True
)

# SSH into instance and install the web app
command_list = '''
sudo yum update -y ; curl -sL https://rpm.nodesource.com/setup_16.x | sudo -E bash - ;
sudo yum install -y nodejs ; curl https://witdevops.s3-eu-west-1.amazonaws.com/app.js --output app.js;
'''
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} '{command_list}'"
result = subproc(
    ssh_command,
    "Hello World web app set up on the ec2 instance",
    "Could not set up the Hello World web app on the ec2 instance",
    2,
    True
)

# Secure copy monitor script onto instance
subproc(
    f"scp -o StrictHostKeyChecking=no -i {key_file_name} monitor.sh ec2-user@{public_ip}:.",
    "Monitor script copied onto ec2 instance",
    "Monitor script was not copied onto ec2 instance",
    2,
)

# Secure copy aws credentials onto instance
subproc(
    f"scp -rp -o StrictHostKeyChecking=no -i {key_file_name} ~/.aws ec2-user@{public_ip}:~/",
    "AWS credentials copied onto ec2 instance",
    "AWS credentials was not copied onto ec2 instance",
    2,
)

# Set monitor permissions
subproc(
    f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} 'chmod 700 monitor.sh'",
    "Monitor script permissions set",
    "Monitor script permissions were not set",
    2,
)

#sudo cp -R ~/.aws /var/www/html/'
subproc(
    f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} 'sudo cp monitor.sh /var/www/html/monitor.sh' ",
    "Monitor script copied",
    "Monitor script not copied",
    2,
)


# Execute monitor script
permiss_cmd = f"""ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} '(crontab -l ; echo "*/1 * * * * /home/ec2-user/monitor.sh") | crontab -' """
subproc(
    permiss_cmd,
    "Cronjob created for Monitor.sh",
    "Could not create cronjob for Monitor.sh",
    2
)

sleep(5)

# Create an image from the instance
try:
    sleep(1)
    image_response = ec2_client.create_image(
        Description=sec_grp,
        InstanceId=inst_id,
        Name=sec_grp,
            TagSpecifications=[
        {
            'ResourceType': 'image',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'assign_two'
                },
            ]
        },
    ]
    )
    image_id=image_response['ImageId']
    pretty_print(f"Created AMI Image: {image_id}")
except:
    pretty_print("Could not create the AMI Image")

# Wait for the image to exist
try:
    sleep(1)
    pretty_print(f"Waiting for the AMI Image {image_id} to exist")
    image_waiter = ec2_client.get_waiter('image_exists')
    image_waiter.wait(ImageIds=[image_id])
except:
    pretty_print("The AMI Image does not exist")

# Wait for the image to become available
try:
    sleep(1)
    pretty_print(f"Waiting for the AMI Image {image_id} to become available")
    img_waiter = ec2_client.get_waiter('image_available')
    img_waiter.wait(ImageIds=[image_id])
except:
    pretty_print("The AMI Image never became available")

try:
    sleep(1)
    describe_response = ec2_client.describe_images(ImageIds=[image_id])
    pretty_print(f"Found the AMI image: {image_id}")
except:
    pretty_print("Could not find the AMI image")



# Create the Web App security group
try:
    # Check if security group already exists
    sleep(1)
    desc_response = ec2_client.describe_security_groups(
        Filters=[
            {
                'Name': 'group-name',
                'Values': [web_sec_grp]
            }
        ]
        )
    web_grp_id.append(desc_response[
        "SecurityGroups"][0]["GroupId"]
        )
    pretty_print(f"Found Vpc Security Group {web_grp_id}")
except:
    pretty_print(f"Could not find the {web_sec_grp} security group")

# web_grp_id isnt empty, use that security group
if web_grp_id:
    sleep(1)
    pretty_print(f"Using the security group: {web_sec_grp}")
# web_grp_id is empty, create new security group
else:
    try:
        sleep(1)
        web_sec_grp_resp = ec2_resource.create_security_group(
            GroupName="Port3000",
            Description="Port3000",
            VpcId=vpc_id
        )
        web_grp_id.append(web_sec_grp_resp.id)
        pretty_print(f"Created the security group: {web_sec_grp}")
        waiter = ec2_client.get_waiter('security_group_exists')
        pretty_print("Waiting for the Security Group to become available")
        waiter.wait(
            GroupIds=web_grp_id
        )
    except:
        pretty_print(f"Could not create the security group: {web_sec_grp}")
    # If the create function was successful, set ip permissions
    if web_sec_grp_resp:
        try:
            sleep(1)
            # Web Inbound rules
            web_sec_ingress_response = web_sec_grp_resp.authorize_ingress(
                IpPermissions=[
                    {
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "ssh"},
                        ],
                    },
                    {
                        "FromPort": 3000,
                        "ToPort": 3000,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                    {
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                    {
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                    {
                        "FromPort": 3389,
                        "ToPort": 3389,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                ],
            )
            pretty_print(f"Security group inbound rules set for: {web_sec_grp}")
        except:
            pretty_print("Inbound Security group rules not set")

# Create the DB security group
try:
    # Check if security group already exists
    sleep(1)
    desc_response = ec2_client.describe_security_groups(
        Filters=[
            {
                'Name': 'group-name',
                'Values': [db_sec_grp]
            }
        ]
        )
    db_grp_id.append(desc_response[
        "SecurityGroups"][0]["GroupId"]
        )
    pretty_print(f"Found Vpc Security Group {db_grp_id}")
except:
    pretty_print(f"Could not find the {db_sec_grp} security group")

# db_grp_id isnt empty, use that security group
if db_grp_id:
    sleep(1)
    pretty_print(f"Using the security group: {db_sec_grp}")
# db_grp_id is empty, create new security group
else:
    try:
        sleep(1)
        db_sec_grp_resp = ec2_resource.create_security_group(
            GroupName=db_sec_grp,
            Description=db_sec_grp,
            VpcId=vpc_id
        )
        db_grp_id.append(db_sec_grp_resp.id)
        pretty_print(f"Created the security group: {db_sec_grp}")
        waiter = ec2_client.get_waiter('security_group_exists')
        pretty_print("Waiting for the Security Group to become available")
        waiter.wait(
            GroupIds=db_grp_id
        )
    except:
        pretty_print(f"Could not create the security group: {db_sec_grp}")
    # If the create function was successful, set ip permissions
    if db_sec_grp_resp:
        try:
            sleep(1)
            # DB inbound rules
            db_sec_ingress_response = ec2_client.authorize_security_group_ingress(
                GroupId=db_grp_id[0],
                IpPermissions=[
                    {
                        "FromPort": 1433,
                        "ToPort": 1433,
                        "IpProtocol": "tcp",
                        "UserIdGroupPairs": [
                            {
                                'GroupId': web_grp_id[0],
                                'VpcId': vpc_id
                            }
                        ]
                    },
                    {
                        "FromPort": 3306,
                        "ToPort": 3306,
                        "IpProtocol": "tcp",
                        "UserIdGroupPairs": [
                            {
                                'GroupId': web_grp_id[0],
                                'VpcId': vpc_id
                            }
                        ]
                    },
                ],
            )
            pretty_print(f"Security group inbound rules set for: {db_sec_grp}")
        except:
            pretty_print("Inbound Security group rules not set")

        try:
            sleep(1)
            #DB outbound rules
            db_sec_egress_response = ec2_client.authorize_security_group_egress(
                GroupId=db_grp_id[0],
                IpPermissions=[
                    {
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "http"},
                        ],
                    },
                    {
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "https"},
                        ],
                    },
                ],
            )
            pretty_print(f"Security group outbound rules set for: {db_sec_grp}")
        except:
            pretty_print("Outbound Security group rules not set")

        try:
            sleep(1)
            # Web outbound rules
            web_sec_egress_response = web_sec_grp_resp.authorize_egress(
                IpPermissions=[
                    {
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "ssh"},
                        ],
                    },
                    {
                        "FromPort": 3000,
                        "ToPort": 3000,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                    {
                        "FromPort": 1433,
                        "ToPort": 1433,
                        "IpProtocol": "tcp",
                        "UserIdGroupPairs": [
                            {
                                'GroupId': db_grp_id[0],
                                'VpcId': vpc_id
                            }
                        ]
                    },
                    {
                        "FromPort": 3306,
                        "ToPort": 3306,
                        "IpProtocol": "tcp",
                        "UserIdGroupPairs": [
                            {
                                'GroupId': db_grp_id[0],
                                'VpcId': vpc_id
                            }
                        ]
                    },
                ],
            )
            pretty_print(f"Security group outbound rules set for: {web_sec_grp}")
        except:
            pretty_print("Outbound Security group rules not set")

        try:
            sleep(1)
            # Remove the default added all traffic outbound rule
            revoke_response = ec2_client.revoke_security_group_egress(
                GroupId=db_grp_id[0],
                IpPermissions=[
                    {
                        'IpProtocol': '-1',
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0'
                            }
                        ]
                    }
                ]
            )
            pretty_print("Revoked an unruly outbound rule from DB Server Security Group")
        except:
            pretty_print("Could not revoke an unruly outbound rule from DB Server Security Group")

        try:
            sleep(1)
            # Remove the default added all traffic outbound rule
            revoke_response = ec2_client.revoke_security_group_egress(
                GroupId=web_grp_id[0],
                IpPermissions=[
                    {
                        'IpProtocol': '-1',
                        'IpRanges': [
                            {
                                'CidrIp': '0.0.0.0/0'
                            }
                        ]
                    }
                ]
            )
            pretty_print("Revoked an unruly outbound rule from Web App Server Security Group")
        except:
            pretty_print("Could not revoke an unruly outbound rule from Web App Server Security Group")
            

# Starts the web app
auto_user_data = '''
#!/bin/bash
sudo service crond start;
sudo cp /var/www/html/monitor.sh /home/ec2-user/monitor.sh;
(crontab -l ; sudo echo "*/1 * * * * /home/ec2-user/monitor.sh") | crontab -;
su - ec2-user -c 'node app.js'
'''
# #INSTANCE_ID=$(curl -s http://169.254.169.254/latest/meta-data/instance-id);
#
#sudo cp -R /var/www/html/.aws ~;
#(crontab -l ; echo "*/1 * * * * /home/root/monitor.sh") | crontab -;
# sudo cp /var/www/html/monitor.sh ~;
# sudo cp -R /var/www/html/.aws ~;
# 


# Create a Launch configuration based on the image
try:
    sleep(1)
    launch_response = auto_client.create_launch_configuration(
        LaunchConfigurationName='web',
        ImageId=image_id,
        IamInstanceProfile='arn:aws:iam::778769697098:instance-profile/EC2IAM',
        KeyName=key_name,
        SecurityGroups=[web_grp_id[0]],
        UserData=auto_user_data,
        InstanceType='t2.nano',
        InstanceMonitoring={'Enabled': True}
    )
    pretty_print("Created the Launch Configuration")
except:
    pretty_print("Could not create the Launch Configuration")


# Create 80/443 Security Group for Load Balancer
try:
    # Check if security group already exists
    sleep(1)
    desc_response = ec2_client.describe_security_groups(
        Filters=[
            {
                'Key': 'group-name',
                'Value': lb_sec_grp
            }
        ]
    )
    if desc_response:
        lb_grp_id.append(desc_response[
            "SecurityGroups"][0]["GroupId"]
        )
except:
    pretty_print(f"Could not find the {lb_sec_grp} security group")

# lb_id isnt empty, use that security group
if lb_grp_id:
    sleep(1)
    pretty_print(f"Using the security group: {lb_sec_grp}")
# lb_id is empty, create new security group
else:
    try:
        sleep(1)
        lb_grp_resp = ec2_resource.create_security_group(
            GroupName=lb_sec_grp,
            VpcId=vpc_id,
            Description=lb_sec_grp
        )
        lb_sec_id = lb_grp_resp.id
        pretty_print(f"Created the security group: {lb_sec_grp}")
    except:
        pretty_print(f"Could not create the security group: {lb_sec_grp}")
    try:
        sleep(1)
        waiter = ec2_client.get_waiter('security_group_exists')
        pretty_print("Waiting for the Security Group to become available")
        waiter.wait(GroupIds=[lb_sec_id])
    except:
        pretty_print("Could not find the LB security group to wait for")
    # If the create function was successful, set ip permissions
    if lb_grp_resp:
        try:
            sleep(1)
            sec_ingress_response = lb_grp_resp.authorize_ingress(
                IpPermissions=[
                    {
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "http"},
                        ],
                    },
                    {
                        "FromPort": 443,
                        "ToPort": 443,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "https"},
                        ],
                    },
                    {
                        "FromPort": 3000,
                        "ToPort": 3000,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "port3000"},
                        ],
                    },
                ],
            )
            pretty_print(f"Inbound security group rules set for: {lb_sec_grp}")
        except:
            pretty_print("Inbound security group rules not set")


# Create an Application Load Balancer for 3 public subnets
try:
    lb_response = load_client.create_load_balancer(
        Name='assignment-two',
        Subnets=[
            pub_west1a,
            pub_west1b,
            pub_west1c
        ],
        SecurityGroups=[lb_sec_id],
        Type='application'
    )
    lb_arn = lb_response['LoadBalancers'][0]['LoadBalancerArn']
    lb_dns = lb_response['LoadBalancers'][0]['DNSName']
    pretty_print(f"Created Application Load Balancer in Public Subnets {pub_west1a}, {pub_west1b}, {pub_west1c}")
except:
    pretty_print("Could not create the Application Load Balancer")

# Wait for the LB to exist
try:
   sleep(1)
   load_waiter = load_client.get_waiter('load_balancer_exists')
   pretty_print("Waiting for the Load Balancer to exist")
   load_waiter.wait(Names=['assignment-two'])
except:
   pretty_print("Could not find the Load Balancer")

# Wait for the LB to become available
try:
    sleep(1)
    load_waiter = load_client.get_waiter('load_balancer_available')
    pretty_print("Waiting for the Load Balancer to become available")
    load_waiter.wait(Names=['assignment-two'])
except:
    pretty_print("Could not find the Load Balancer")

# Create a HTTP target group
try:
    sleep(1)
    tg_response = load_client.create_target_group(
        Name='assign-http-tg',
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id,
        TargetType='instance'
    )
    http_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
    pretty_print(f"Created HTTP Target Group {http_arn}")
except:
    pretty_print("Could not create HTTP Target Group")

# Create a HTTP listener
try:
    sleep(1)
    http_list_response = load_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=80,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': http_arn
            }
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'HTTP Listener'
            }
        ]
    )
    http_list_arn = http_list_response['Listeners'][0]['ListenerArn']
    pretty_print("Created HTTP Listener")
except:
    pretty_print("Could not create HTTP Listener")

# Create port3000 target group
try:
    sleep(1)
    tg_response = load_client.create_target_group(
        Name='assign-3000-tg',
        Protocol='HTTP',
        Port=3000,
        VpcId=vpc_id,
        TargetType='instance'
    )
    port3000_arn = tg_response['TargetGroups'][0]['TargetGroupArn']
    pretty_print(f"Created Port3000 Target Group {port3000_arn}")
except:
    pretty_print("Could not create Port3000 Target Group")

# Create a Port3000 listener
try:
    sleep(1)
    http_list_response = load_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTP',
        Port=3000,
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': port3000_arn
            }
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'Port3000 Listener'
            }
        ]
    )
    port_list_arn = http_list_response['Listeners'][0]['ListenerArn']
    pretty_print("Created 3000 Listener")
except:
    pretty_print("Could not create 3000 Listener")

openssl_cmd = f'echo "{passwd}" | {install_cmd}'
cert_cmd=f'''
openssl \
  req \
  -newkey rsa:2048 -nodes \
  -keyout privkey.pem \
  -x509 -days 36500 -out certificate.csr \
  -subj "/C=IE/ST=WX/L=Earth/O=WIT/OU=SSD/CN={lb_dns}"
'''
# Installs OpenSSL
subproc(
    openssl_cmd,
    "Installed OpenSSL locally",
    "Could not install OpenSSL, already installed or incorrect password",
    1
)

# Create cert for the LB
subproc(
    cert_cmd,
    "Created OpenSSL Certificate",
    "Could not create OpenSSL Certificate",
    1
)

# Convert the cert to bytes
try:
    sleep(1)
    with open("certificate.csr", "r") as cert:
        content = cert.read()
        b_cert = bytes(content, 'utf-8')
        pretty_print("Certificate converted to bytes")
except:
    print("Could not convert certificate to bytes")

# Convert the key to bytes
try:
    sleep(1)
    with open("privkey.pem", "r") as key:
        content = key.read()
        priv_key = bytes(content, 'utf-8')
        pretty_print("Private key converted to bytes")
except:
    print("Could not convert Private key to bytes")

# Import the certificate to AWS
try:
    sleep(1)
    cert_response = cert_client.import_certificate(
        Certificate=b_cert,
        PrivateKey=priv_key,
        Tags=[
            {
                'Key': 'Name',
                'Value': 'LB_Cert'
            }
        ]
    )
    cert_arn = cert_response['CertificateArn']
    pretty_print(f"Imported LB Certificate: {cert_arn}")
except:
    pretty_print("Could not import LB Certificate")

# Create a HTTPS target group
try:
    sleep(1)
    tg2_response = load_client.create_target_group(
        Name='assign-https-tg',
        Protocol='HTTPS',
        Port=443,
        VpcId=vpc_id,
        TargetType='instance'
    )
    https_arn = tg2_response['TargetGroups'][0]['TargetGroupArn']
    pretty_print(f"Created HTTPS Target Group {https_arn}")
except:
    pretty_print("Could not create HTTPS Target Group")

# Create a HTTPS listener
try:
    sleep(1)
    https_list_response = load_client.create_listener(
        LoadBalancerArn=lb_arn,
        Protocol='HTTPS',
        Port=443,
        Certificates=[
            {
                'CertificateArn': cert_arn,
            }
        ],
        DefaultActions=[
            {
                'Type': 'forward',
                'TargetGroupArn': https_arn
            }
        ],
        Tags=[
            {
                'Key': 'Name',
                'Value': 'HTTPS Listener'
            }
        ]
    )
    https_list_arn = https_list_response['Listeners'][0]['ListenerArn']
    pretty_print("Created HTTPS Listener")
except:
    pretty_print("Could not create HTTPS Listener")

# Create Auto-Scaling Group
try:
    sleep(1)
    auto_response = auto_client.create_auto_scaling_group(
        AutoScalingGroupName="ASG1",
        LaunchConfigurationName="web",
        MinSize=2,
        DesiredCapacity=2,
        MaxSize=3,
        HealthCheckGracePeriod=120,
        VPCZoneIdentifier=f"{pub_west1a},{pub_west1b},{pub_west1c}",
        TargetGroupARNs=[http_arn, port3000_arn, https_arn],
        Tags=[
            {
                'ResourceType': 'auto-scaling-group',
                'Key': 'Name',
                'Value': 'AutoScaled',
                'PropagateAtLaunch': True
            }
        ]
    )
    pretty_print(f"Created Auto Scaling Group")
except:
    pretty_print(f"Could not create Auto Scaling Group")

# Put Upper Scaling Policy
try:
    sleep(1)
    up_policy_resp = auto_client.put_scaling_policy(
        AutoScalingGroupName="ASG1",
        PolicyName="scale-out",
        PolicyType="SimpleScaling",
        AdjustmentType="ChangeInCapacity",
        ScalingAdjustment=1
    )
    up_policy_arn = up_policy_resp['PolicyARN']
    pretty_print(f"Created Scale-Out Policy: {up_policy_arn}")
except:
    pretty_print(f"Could not create Scale-Out Policy: {up_policy_arn}")

# Put Upper Cloudwatch Alarm
try:
    sleep(1)
    ucw_response = cloud_client.put_metric_alarm(
        AlarmName='CPUsageH',
        AlarmDescription='High CPU alarm',
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistic='Average',
        Period=60,
        EvaluationPeriods=1,
        Threshold=50,
        ComparisonOperator='GreaterThanThreshold',
        AlarmActions=[up_policy_arn]
    )
    pretty_print(f"Created High CPU Usage Alarm")
except:
    pretty_print(f"Could not create High CPU Usage Alarm")

# Put Lower Scaling Policy
try:
    sleep(1)
    lo_policy_resp = auto_client.put_scaling_policy(
        AutoScalingGroupName="ASG1",
        PolicyName="scale-in",
        PolicyType="SimpleScaling",
        AdjustmentType="ChangeInCapacity",
        ScalingAdjustment=-1,
    )
    lo_policy_arn = lo_policy_resp['PolicyARN']
    pretty_print(f"Created Scale-In Policy: {lo_policy_arn}")
except:
    pretty_print(f"Could not create Scale-In Policy: {lo_policy_arn}")

# Put Lower Cloudwatch Alarm
try:
    sleep(1)
    lcw_response = cloud_client.put_metric_alarm(
        AlarmName='CPUsageL',
        AlarmDescription='Low CPU alarm',
        MetricName='CPUUtilization',
        Namespace='AWS/EC2',
        Statistic='Average',
        Period=60,
        EvaluationPeriods=2,
        Threshold=40,
        ComparisonOperator='LessThanThreshold',
        AlarmActions=[lo_policy_arn]
    )
    pretty_print(f"Created Low CPU Usage Alarm")
except:
    pretty_print(f"Could not create Low CPU Usage Alarm")

sleep(120)

# Get instance ids
find_auto_resp = ec2_client.describe_instances(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': [vpc_id]
        },
    ]
)

inst_1= find_auto_resp['Reservations'][0]['Instances'][0]['PublicIpAddress']
inst_1_id= find_auto_resp['Reservations'][0]['Instances'][0]['InstanceId']
inst_2= find_auto_resp['Reservations'][1]['Instances'][0]['PublicIpAddress']
pretty_print(inst_1)
pretty_print(inst_2)


curl_cmd = f'''
curl -s "http://{lb_dns}/?[1-100]";
'''
# Send 100 requests to the Load Balancer
result = subproc(
    curl_cmd,
    "Sent curl requests to the Load Balancer",
    "Could not send curl requests to the Load Balancer",
    2,
    True
)

sleep(10)
access_log_cmd=f'''
sudo cat /etc/httpd/logs/access_log
'''
# Get access log for instance 1
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{inst_1} '{access_log_cmd}'"
result = subproc(
    ssh_command,
    "Revrieved Access Logs",
    "Could not check Access Logs",
    2,
    True
)
pretty_print(str(result.stdout))

# Get access log for instance 2
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{inst_2} '{access_log_cmd}'"
result = subproc(
    ssh_command,
    "Retrieved Access Logs",
    "Could not check Access Logs",
    2,
    True
)
pretty_print(str(result.stdout))

# Open Web Browser
try:
    time.sleep(2)
    webbrowser.open_new_tab(f"http://{lb_dns}")
    webbrowser.open_new_tab(f"http://{lb_dns}:3000")
    pretty_print("Browser opened")
except:
    pretty_print("Could not open the browser")


ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{inst_1} 'while true; do x=0; done'"
# Overload CPU
result = subproc(
    ssh_command,
    f"Overloading {inst_1} CPU to force autoscale",
    "Could not overload the CPU",
    2,
    True
)



