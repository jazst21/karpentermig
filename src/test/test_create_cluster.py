import unittest
import os
import boto3
from moto import mock_cloudformation, mock_eks, mock_ec2
from botocore.exceptions import ClientError

class TestCreateCluster(unittest.TestCase):

    @mock_cloudformation
    @mock_eks
    @mock_ec2
    def test_create_cluster(self):
        # Set up mock AWS environment
        os.environ['AWS_DEFAULT_REGION'] = 'us-west-2'
        
        # Create mock resources
        ec2 = boto3.client('ec2')
        vpc = ec2.create_vpc(CidrBlock='10.0.0.0/16')['Vpc']
        subnet1 = ec2.create_subnet(VpcId=vpc['VpcId'], CidrBlock='10.0.1.0/24')['Subnet']
        subnet2 = ec2.create_subnet(VpcId=vpc['VpcId'], CidrBlock='10.0.2.0/24')['Subnet']
        subnet3 = ec2.create_subnet(VpcId=vpc['VpcId'], CidrBlock='10.0.3.0/24')['Subnet']

        # Update configuration files with mock values
        self.update_config_files(subnet1['SubnetId'], subnet2['SubnetId'], subnet3['SubnetId'])

        # Run the create_cluster.sh script
        exit_code = os.system('bash src/test/clusterConfig/create_cluster.sh')
        
        # Check if the script executed successfully
        self.assertEqual(exit_code, 0)

        # Verify that the CloudFormation stack was created
        cf_client = boto3.client('cloudformation')
        try:
            cf_client.describe_stacks(StackName='karpentermig-launch-test-lt')
            stack_created = True
        except ClientError:
            stack_created = False
        
        self.assertTrue(stack_created)

        # Verify that the EKS cluster was created
        eks_client = boto3.client('eks')
        try:
            eks_client.describe_cluster(name='karpentermig-launch-test')
            cluster_created = True
        except ClientError:
            cluster_created = False
        
        self.assertTrue(cluster_created)

    def update_config_files(self, subnet1, subnet2, subnet3):
        # Update karpentermig-launch-test.yaml
        with open('src/test/clusterConfig/karpentermig-launch-test.yaml', 'r') as f:
            content = f.read()
        content = content.replace('subnet-12345678', subnet1)
        content = content.replace('subnet-23456789', subnet2)
        content = content.replace('subnet-34567890', subnet3)
        with open('src/test/clusterConfig/karpentermig-launch-test.yaml', 'w') as f:
            f.write(content)

        # Update create_cluster.sh
        with open('src/test/clusterConfig/create_cluster.sh', 'r') as f:
            content = f.read()
        content = content.replace('SUBNET_1="subnet-12345678"', f'SUBNET_1="{subnet1}"')
        content = content.replace('SUBNET_2="subnet-23456789"', f'SUBNET_2="{subnet2}"')
        content = content.replace('SUBNET_3="subnet-34567890"', f'SUBNET_3="{subnet3}"')
        with open('src/test/clusterConfig/create_cluster.sh', 'w') as f:
            f.write(content)

if __name__ == '__main__':
    unittest.main()