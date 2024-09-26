from unittest.mock import patch
import unittest
import sys
from unittest.mock import MagicMock

# Mock questionary if it's not installed
try:
    import questionary
except ImportError:
    questionary = MagicMock()
    questionary.text.return_value.ask.return_value = "mocked_response"
    questionary.confirm.return_value.ask.return_value = True
    sys.modules['questionary'] = questionary

from karpentermig.discover_cluster import export_eks_config
from karpentermig.cli import cli

class TestKarpenterMig(unittest.TestCase):

    @patch('karpentermig.discover_cluster.boto3')
    def test_export_eks_config(self, mock_boto3):
        # Mock the necessary AWS calls
        mock_eks_client = MagicMock()
        mock_ec2_client = MagicMock()
        mock_boto3.client.side_effect = [mock_eks_client, mock_ec2_client]

        # Set up mock return values
        mock_eks_client.list_clusters.return_value = {'clusters': ['test-cluster']}
        mock_eks_client.list_nodegroups.return_value = {'nodegroups': ['test-nodegroup']}
        mock_eks_client.describe_nodegroup.return_value = {
            'nodegroup': {
                'nodegroupName': 'test-nodegroup',
                'scalingConfig': {'desiredSize': 2, 'minSize': 1, 'maxSize': 3},
                'instanceTypes': ['t3.medium'],
                'subnets': ['subnet-12345'],
                'remoteAccess': {'sourceSecurityGroups': ['sg-12345']}
            }
        }
        mock_ec2_client.describe_subnets.return_value = {'Subnets': [{'SubnetId': 'subnet-12345', 'Tags': [{'Key': 'Name', 'Value': 'TestSubnet'}]}]}
        mock_ec2_client.describe_security_groups.return_value = {'SecurityGroups': [{'GroupId': 'sg-12345', 'GroupName': 'TestSG'}]}

        # Call the function
        export_eks_config(region='us-west-2', cluster_name='test-cluster', output='test_output.csv')

        # Assert that the necessary AWS calls were made
        mock_eks_client.list_nodegroups.assert_called_once_with(clusterName='test-cluster')
        mock_eks_client.describe_nodegroup.assert_called_once_with(clusterName='test-cluster', nodegroupName='test-nodegroup')

    def test_cli(self):
        # Instead of patching cli.export_eks_config, patch the actual function
        with patch('karpentermig.export_eks_config') as mock_export:
            # Your test code here
            pass

if __name__ == '__main__':
    unittest.main()
