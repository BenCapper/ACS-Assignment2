import os
import time
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


# Create VPC
# Create master web server
# Make into template
# Create instance from template
# Create security groups in vpc
# Create elastic load balancer
# Create launch config based on custom template
# Create an auto scaling group
# Configure dynamic scaling policies based on cloudwatch alarms
# Test traffic to load balancer

region = "eu-west-1"
ec2_resource = boto3.resource("ec2")
ec2_client = boto3.client("ec2")

string_list = list()
grp_id = list()
key_name_list = ["assign_two"]
key_file_name = "assign_two.pem"
sec_grp = "assignment_two"
log_name = "log.txt"
index_file = "index.html"
ami_resp = ""
key_name = ""
key_response = ""
public_ip = ""
assign_one_key = ""
found_key_name = ""

tag = {"Key": "Name", "Value": "Master Web Server - Assign Two"}

user_data = """
#!/bin/bash
yum update -y
yum install httpd -y
systemctl enable httpd
systemctl start httpd
systemctl start sshd.service
systemctl start ssh.service
echo '<html>' > index.html
echo 'Private IP address: ' >> index.html
curl http://169.254.169.254/latest/meta-data/local-ipv4 >> index.html
echo '<br>' >> index.html
echo 'Availability Zone: ' >> index.html
curl http://169.254.169.254/latest/meta-data/placement/availability-zone >> index.html
echo '<br>' >> index.html
echo 'Subnet: ' >> index.html
MAC=$(curl http://169.254.169.254/latest/meta-data/mac)
curl http://169.254.169.254/latest/meta-data/network/interfaces/macs/${MAC}/subnet-id >> index.html
echo '<br>' >> index.html
cp index.html /var/www/html/index.html"""

vpc_response = ec2_client.create_vpc(
    CidrBlock="10.0.0.0/16",
    AmazonProvidedIpv6CidrBlock=False,
    TagSpecifications=[
        {
           'ResourceType': 'vpc', 
           'Tags': [
               {
                   'Key': 'Name',
                   'Value': 'BenCapperVPCA2'
               }
           ] 
        }
    ]
)
vpc_id = vpc_response['Vpc']['VpcId']
vpc = ec2_resource.Vpc(vpc_id)
vpc.wait_until_available()
print(vpc_id)

# enable public dns hostname so that we can SSH into it later
ec2_client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsSupport = { 'Value': True } )
ec2_client.modify_vpc_attribute( VpcId = vpc.id , EnableDnsHostnames = { 'Value': True } )

# create an internet gateway and attach it to VPC
internetgateway = ec2_resource.create_internet_gateway()
vpc.attach_internet_gateway(InternetGatewayId=internetgateway.id)

route_response = ec2_client.describe_route_tables(
    Filters=[
        {
            'Name': 'vpc-id',
            'Values': [
                vpc.id
            ]
        }
    ]
)
routetable = ec2_resource.RouteTable(route_response['RouteTables'][0]['RouteTableId'])
print(route_response['RouteTables'][0]['RouteTableId'])

subnet_response = ec2_client.create_subnet(
    TagSpecifications= [
        {
            'ResourceType': 'subnet',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'pub_subnet_eu_w1a'
                }
            ]
        }
    ],
    AvailabilityZone='eu-west-1a',
    CidrBlock='10.0.0.0/20',
    VpcId = vpc_id
)

pub1_west1a_sub_id = subnet_response['Subnet']['SubnetId']
print(pub1_west1a_sub_id)


# create a public route (ON SUBNET)
sub1_routetable = vpc.create_route_table(
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pub_subnet_eu_w1a'
                }
            ]
        }
    ]
)
route = sub1_routetable.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=internetgateway.id,
)
sub1_routetable.associate_with_subnet(SubnetId=pub1_west1a_sub_id)

#-----------------------------------------------------------------------------------------------#

subnet2_response = ec2_client.create_subnet(
    TagSpecifications= [
        {
            'ResourceType': 'subnet',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'pub2_subnet_eu_w1b'
                }
            ]
        }
    ],
    AvailabilityZone='eu-west-1b',
    CidrBlock='10.0.16.0/20',
    VpcId = vpc_id
)

pub2_west1b_sub_id = subnet2_response['Subnet']['SubnetId']
print(pub2_west1b_sub_id)


# create a public route (ON SUBNET)
sub2_routetable = vpc.create_route_table(
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pub2_subnet_eu_w1b'
                }
            ]
        }
    ]
)
route2 = sub2_routetable.create_route(
    DestinationCidrBlock='0.0.0.0/0',
    GatewayId=internetgateway.id,
)
sub2_routetable.associate_with_subnet(SubnetId=pub2_west1b_sub_id)

#--------------------------------------------------------------------------#

subnet3_response = ec2_client.create_subnet(
    TagSpecifications= [
        {
            'ResourceType': 'subnet',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'pri_subnet_eu_w1a'
                }
            ]
        }
    ],
    AvailabilityZone='eu-west-1a',
    CidrBlock='10.0.128.0/20',
    VpcId = vpc_id
)

pri_west1a_sub_id = subnet3_response['Subnet']['SubnetId']
print(pri_west1a_sub_id)


# create a public route (ON SUBNET)
sub3_routetable = vpc.create_route_table(
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pri_subnet_eu_w1a'
                }
            ]
        }
    ]
)

sub3_routetable.associate_with_subnet(SubnetId=pri_west1a_sub_id)

#--------------------------------------------------------------------------#

subnet4_response = ec2_client.create_subnet(
    TagSpecifications= [
        {
            'ResourceType': 'subnet',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'pri2_subnet_eu_w1b'
                }
            ]
        }
    ],
    AvailabilityZone='eu-west-1b',
    CidrBlock='10.0.144.0/20',
    VpcId = vpc_id
)

pri2_west1b_sub_id = subnet4_response['Subnet']['SubnetId']
print(pri2_west1b_sub_id)


# create a public route (ON SUBNET)
sub4_routetable = vpc.create_route_table(
        TagSpecifications= [
        {
            'ResourceType': 'route-table',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'rt_pri2_subnet_eu_w1b'
                }
            ]
        }
    ]
)

sub4_routetable.associate_with_subnet(SubnetId=pri2_west1b_sub_id)

#---------------------------------------------------------------------------#

# If old log exists
if os.path.exists(log_name):
    # Delete
    subproc(f"rm -f {log_name}", "Deleted old log file", "No old log file found", 1)



# Check if the assign_one keypair exists
try:
    sleep(1)
    found_key_name = ec2_client.describe_key_pairs(
        KeyNames=key_name_list
    )["KeyPairs"][0]["KeyName"]
except:
    found_key_name = ""
    pretty_print("Keypair assign_one does not exist")

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

# If there is already an AWS key named assign_one, delete it
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
            GroupName=sec_grp, Description="Assignment1"
        )
        pretty_print(f"Created the security group: {sec_grp}")
    except:
        pretty_print(f"Could not create the security group: {sec_grp}")
    # If the create function was successful, set ip permissions
    if sec_grp_resp:
        try:
            sleep(1)
            # Ref: https://stackoverflow.com/questions/66441122/how-to-access-my-instance-through-ssh-writing-boto3-code
            sec_ingress_response = sec_grp_resp.authorize_ingress(
                IpPermissions=[
                    {
                        "FromPort": 22,
                        "ToPort": 22,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "internet"},
                        ],
                    },
                    {
                        "FromPort": 80,
                        "ToPort": 80,
                        "IpProtocol": "tcp",
                        "IpRanges": [
                            {"CidrIp": "0.0.0.0/0", "Description": "internet"},
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



# Get image AMI by desc as ->
# aws ssm get-parameters --names /aws/service/ami-amazon-linux-latest/amzn2-ami-hvm-x86_64-gp2 --region eu-west-1 >> log.txt"""
# returns 2nd most recent ami?
try:
    ami_resp = ec2_client.describe_images(
        Filters=[
            {
                "Name": "description",
                "Values": [
                    "Amazon Linux 2 Kernel 5.10 AMI 2.0.20220218.1 x86_64 HVM gp2"
                ],
            }
        ]
    )["Images"][0]["ImageId"]
    pretty_print(f"Successfully retrieved image AMI: {ami_resp}")
except:
    pretty_print(f"Could not retrieve the image AMI")

# Create the instance
try:
    create_response = ec2_resource.create_instances(
        ImageId=ami_resp,
        KeyName=key_name,
        UserData=user_data,
        InstanceType="t2.nano",
        SecurityGroupIds=grp_id,
        MinCount=1,
        MaxCount=1,
    )
    pretty_print(f"Instance created")
    created_instance = create_response[0]
    created_instance.wait_until_running()
    pretty_print(f"Instance running")
    created_instance.reload()
    created_instance.wait_until_running()
    public_ip = created_instance.public_ip_address
except:
    pretty_print("Could not create ec2 instance")



# Add a tag to the instance
try:
    created_instance.create_tags(Tags=[tag])
    pretty_print(f"Tag added to instance: {tag}")
except:
    pretty_print(f"Could not add tag to the instance: {tag}")


image_response = ec2_client.create_image(
    Description=sec_grp,
    InstanceId=created_instance.id,
    Name=sec_grp
)