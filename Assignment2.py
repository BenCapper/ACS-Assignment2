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


# Create VPC - done
# Create master web server - done
# Make into image - done
# Create security groups in vpc - done
# Create instance from template into subnet - done
# Create launch config based on custom template - done
# Create elastic load balancer - done
# Create an auto scaling group
# Create open SSL Cert and LB listener - done
# Configure dynamic scaling policies based on cloudwatch alarms
# Test traffic to load balancer

region = "eu-west-1"
ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")
auto_client = boto3.client('autoscaling')
load_client = boto3.client("elbv2")
cert_client = boto3.client('acm')

string_list = list()
grp_id = list()
web_grp_id = list()
db_grp_id = list()
lb_grp_id = list()
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

tag = {"Key": "Name", "Value": "Master Web Server - Assign Two"}

# If old log exists
if os.path.exists(log_name):
    # Delete
    subproc(f"rm -f {log_name}", "Deleted old log file", "No old log file found", 1)

#Create s3 endpoint with private subnet route tables

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
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1a,
        MapPublicIpOnLaunch={'Value':True}
    )
    pretty_print(f"Created Public Subnet EU-WEST-1A: {pub_west1a}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1A")

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
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1b,
        MapPublicIpOnLaunch={'Value':True}
    )
    pretty_print(f"Created Public Subnet EU-WEST-1B: {pub_west1b}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1B")

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
    attr_response = ec2_client.modify_subnet_attribute(
        SubnetId=pub_west1c,
        MapPublicIpOnLaunch={'Value':True}
    )
    pretty_print(f"Created Public Subnet EU-WEST-1C: {pub_west1c}")
except:
    pretty_print(f"Could not create Public Subnet EU-WEST-1C")

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
    create_response = ec2_resource.create_instances(
        ImageId='ami-0069d66985b09d219',
        KeyName=key_name,
        InstanceType="t2.nano",
        SecurityGroupIds=grp_id,
        MinCount=1,
        MaxCount=1,
        Monitoring={'Enabled': True},
    )
    created_instance = create_response[0]
    inst_id = created_instance.id
    pretty_print(f"Instance {inst_id} created")
    pretty_print(f"Waiting for Instance {inst_id} to become available...")
    created_instance.wait_until_running()
    pretty_print(f"Instance {inst_id} running")
    created_instance.reload()
    created_instance.wait_until_running()
    public_ip = created_instance.public_ip_address
except:
    pretty_print("Could not create the ec2 Instance")


# Set Keypair permissions
subproc(
    f"chmod 400 {key_file_name}",
    "Keypair permissions set",
    "Could not set keypair permissions",
    2,
)

# SSH into instance and install the web app
command_list = '''
sudo yum install httpd -y; sudo systemctl enable httpd; sudo systemctl start httpd;
sudo touch index.html; sudo chmod 777 index.html; sudo echo "<b>Assignment Two Index</b> " >> index.html;
sudo chmod 400 index.html;
sudo cp index.html /var/www/html/index.html
'''
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} '{command_list}'"
result = subproc(
    ssh_command,
    "Http server set up on the ec2 instance",
    "Could not set up the Http server on the ec2 instance",
    2,
    True
)
print(result)
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
print(result)
# SSH into instance and install the web app
command_list = '''
sudo yum update -y ; curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.37.1/install.sh | bash;
. ~/.nvm/nvm.sh; nvm install node; nvm install --lts; curl https://witdevops.s3-eu-west-1.amazonaws.com/app.js --output app.js;
'''
ssh_command = f"ssh -o StrictHostKeyChecking=no -i {key_file_name} ec2-user@{public_ip} '{command_list}'"
result = subproc(
    ssh_command,
    "Hello World web app set up on the ec2 instance",
    "Could not set up the Hello World web app on the ec2 instance",
    2,
    True
)

sleep(20)

# Create an image from the instance
try:
    sleep(1)
    image_response = ec2_client.create_image(
        Description=sec_grp,
        InstanceId=inst_id,
        Name=sec_grp,
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

# Terminate the template instance
try:
    sleep(1)
    term_response = ec2_client.terminate_instances(
        InstanceIds=[created_instance.id]
    )
    pretty_print(f"Terminated the instance: {inst_id}")
except:
    pretty_print(f"Could not terminate the instance: {inst_id}")

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
su - ec2-user -c 'node app.js'
'''
# Create a Launch configuration based on the image
try:
    sleep(1)
    launch_response = auto_client.create_launch_configuration(
        LaunchConfigurationName='web',
        ImageId=image_id,
        KeyName=key_name,
        SecurityGroups=[web_grp_id[0]],
        UserData=auto_user_data,
        InstanceType='t2.nano',
        InstanceMonitoring={'Enabled': True}
    )
    pretty_print("Created the Launch Configuration")
except:
    pretty_print("Could not create the Launch Configuration")

# Create a security group in Pri subnet with app running on port 3000
try:
    vpc_create_response = ec2_resource.create_instances(
            ImageId=image_id,
            KeyName=key_name,
            InstanceType="t2.nano",
            SecurityGroupIds=web_grp_id,
            UserData=auto_user_data,
            MinCount=1,
            MaxCount=1,
            SubnetId=pub_west1a,
            Monitoring={'Enabled': True},
    )
    vpc_created_instance = vpc_create_response[0]
    vpc_inst_id = vpc_created_instance.id
    pretty_print(f"Instance {vpc_inst_id} created")
    pretty_print(f"Waiting for Instance {vpc_inst_id} to become available...")
    vpc_created_instance.wait_until_running()
    pretty_print(f"Instance {vpc_inst_id} running")
    vpc_created_instance.reload()
    vpc_created_instance.wait_until_running()
    public_ip = vpc_created_instance.public_ip_address
except:
    pretty_print("Could not create ec2 instance")

# Test the Vpc infra is correct with HelloWorld web app
try:
    webbrowser.open_new_tab(f"http://{public_ip}:3000")
    pretty_print("Opening Web Browser to Hello World app")
except:
    pretty_print("Could not open the Web Browser")

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
    sleep(1)
    lb_grp_resp = ec2_resource.create_security_group(
        GroupName=lb_sec_grp,
        VpcId=vpc_id,
        Description=lb_sec_grp
    )
    lb_sec_id = lb_grp_resp.id
    pretty_print(f"Created the security group: {lb_sec_grp}")

        #pretty_print(f"Could not create the security group: {lb_sec_grp}")
    try:
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
                            {"CidrIp": "0.0.0.0/0", "Description": "ssh"},
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
                ],
            )
            pretty_print(f"Inbound security group rules set for: {lb_sec_grp}")
        except:
            pretty_print("Inbound security group rules not set")


# Create an Application Load Balancer for 3 public subnets

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

   #pretty_print("Could not create the Application Load Balancer")

# Wait for the LB to exist
try:
   load_waiter = load_client.get_waiter('load_balancer_exists')
   pretty_print("Waiting for the Load Balancer to exist")
   load_waiter.wait(Names=['assignment-two'])
except:
   pretty_print("Could not find the Load Balancer")

# Wait for the LB to become available
try:
   load_waiter = load_client.get_waiter('load_balancer_available')
   pretty_print("Waiting for the Load Balancer to become available")
   load_waiter.wait(Names=['assignment-two'])
except:
   pretty_print("Could not find the Load Balancer")

# Import the certificate to AWS
try:
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

# Create a HTTP target group
try:
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



# Create Auto-Scaling Group

auto_response = auto_client.create_auto_scaling_group(
    AutoScalingGroupName="ASG1",
    LaunchConfigurationName="web",
    MinSize=1,
    MaxSize=3,
    DefaultCooldown=60,
    HealthCheckType='ELB',
    HealthCheckGracePeriod=300,
    VPCZoneIdentifier=f"{pub_west1a},{pub_west1b},{pub_west1c}",
    TargetGroupARNs=[http_arn]
)

#