import boto3
import csv
from botocore.exceptions import ClientError
import click
import questionary
from boto3 import client

def select_region():
    try:
        regions = boto3.session.Session().get_available_regions('eks')
    except ClientError as e:
        if e.response['Error']['Code'] == 'UnauthorizedOperation':
            print("Error: AWS CLI token or access to the account is not valid.")
            print("Please check your AWS credentials and try again.")
            return []
        else:
            print(f"An unexpected error occurred: {e}")
            return []
    selected_region = questionary.select(
        "Select AWS region:",
        choices=regions
    ).ask()
    return selected_region

def select_eks_cluster(region):
    eks_client = client('eks', region_name=region)
    try:
        clusters = eks_client.list_clusters()['clusters']
    except ClientError as e:
        if e.response['Error']['Code'] == 'AccessDeniedException':
            print("Error: You don't have permission to list EKS clusters.")
            print("Please check your IAM permissions and try again.")
            return None
        else:
            print(f"An unexpected error occurred: {e}")
            return None
    
    if not clusters:
        print(f"No EKS clusters found in the region {region}.")
        return None

    selected_cluster = questionary.select(
        "Select an EKS cluster:",
        choices=clusters
    ).ask()
    
    return selected_cluster

def export_eks_config(region=None, cluster_name=None, output='eks_config.csv'):
    """Discover AWS EKS cluster node group and launch template configuration and export to CSV."""
    try:
        # Select region if not provided
        if not region:
            region = select_region()
        
        # Initialize AWS clients
        eks_client = boto3.client('eks', region_name=region)
        ec2_client = boto3.client('ec2', region_name=region)
        asg_client = boto3.client('autoscaling', region_name=region)

        # Select cluster if not provided
        if not cluster_name:
            cluster_name = select_eks_cluster(region)
            if not cluster_name:
                return

        # Get node groups for the cluster
        node_groups = eks_client.list_nodegroups(clusterName=cluster_name)['nodegroups']

        # Prepare data for CSV
        data = []
        for ng_name in node_groups:
            ng_info = eks_client.describe_nodegroup(clusterName=cluster_name, nodegroupName=ng_name)['nodegroup']
            
            # Get launch template info if available
            lt_info = {}
            ami_id = 'N/A'
            if 'launchTemplate' in ng_info:
                lt_id = ng_info['launchTemplate']['id']
                lt_info = ec2_client.describe_launch_templates(LaunchTemplateIds=[lt_id])['LaunchTemplates'][0]
                
                # Extract AMI ID from launch template
                lt_version = ng_info['launchTemplate'].get('version', '$Default')
                lt_data = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id,
                    Versions=[lt_version]
                )['LaunchTemplateVersions'][0]['LaunchTemplateData']
                ami_id = lt_data.get('ImageId', 'N/A')

            # Get subnet names
            subnet_ids = ng_info.get('subnets', [])
            subnet_names = []
            if subnet_ids:
                subnets = ec2_client.describe_subnets(SubnetIds=subnet_ids)['Subnets']
                subnet_names = [next((tag['Value'] for tag in subnet['Tags'] if tag['Key'] == 'Name'), subnet['SubnetId']) for subnet in subnets]

            # Get security group IDs
            sg_ids = set()
            if 'launchTemplate' in ng_info:
                lt_id = ng_info['launchTemplate']['id']
                lt_version = ng_info['launchTemplate'].get('version', '$Default')
                lt_data = ec2_client.describe_launch_template_versions(
                    LaunchTemplateId=lt_id,
                    Versions=[lt_version]
                )['LaunchTemplateVersions'][0]['LaunchTemplateData']
                sg_ids.update(lt_data.get('NetworkInterfaces', [{}])[0].get('Groups', []))
            else:
                # If no launch template, get security groups from EC2 instances
                asg_name = ng_info['resources']['autoScalingGroups'][0]['name']
                asg_info = asg_client.describe_auto_scaling_groups(AutoScalingGroupNames=[asg_name])['AutoScalingGroups'][0]
                instance_ids = [i['InstanceId'] for i in asg_info['Instances']]
                if instance_ids:
                    instances = ec2_client.describe_instances(InstanceIds=instance_ids)['Reservations'][0]['Instances']
                    for instance in instances:
                        for nic in instance['NetworkInterfaces']:
                            sg_ids.update([sg['GroupId'] for sg in nic['Groups']])

            # Get security group names
            sg_names = []
            if sg_ids:
                try:
                    sgs = ec2_client.describe_security_groups(GroupIds=list(sg_ids))['SecurityGroups']
                    sg_names = [sg['GroupName'] for sg in sgs]
                except ClientError as e:
                    print(f"Error fetching security group names: {e}")
                    sg_names = list(sg_ids)  # Use IDs if names can't be fetched

            data.append({
                'ClusterName': cluster_name,
                'NodeGroupName': ng_name,
                'InstanceTypes': ', '.join(ng_info.get('instanceTypes', [])),
                'DesiredSize': ng_info['scalingConfig']['desiredSize'],
                'MinSize': ng_info['scalingConfig']['minSize'],
                'MaxSize': ng_info['scalingConfig']['maxSize'],
                'AMIType': ng_info.get('amiType', 'N/A'),
                'DiskSize': ng_info.get('diskSize', 'N/A'),
                'LaunchTemplateName': lt_info.get('LaunchTemplateName', 'N/A'),
                'LaunchTemplateVersion': ng_info.get('launchTemplate', {}).get('version', 'N/A'),
                'AMIID': ami_id,  # Add AMI ID to the data
                'Subnets': ', '.join(subnet_names),
                'SecurityGroups': ', '.join(sg_names),
            })
        # Write data to CSV file
        with open(output, 'w', newline='') as csvfile:
            fieldnames = ['ClusterName', 'NodeGroupName', 'InstanceTypes', 'DesiredSize', 'MinSize', 'MaxSize', 'AMIType', 'DiskSize', 'LaunchTemplateName', 'LaunchTemplateVersion', 'AMIID', 'Subnets', 'SecurityGroups']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            for row in data:
                writer.writerow(row)

        print(f"EKS configuration exported to {output}")

    except ClientError as e:
        print(f"An error occurred: {e}")
@click.command()
@click.option('--region', help='AWS region')
@click.option('--cluster-name', help='EKS cluster name')
@click.option('--output', default='eks_config.csv', help='Output CSV file name')
def cli(region, cluster_name, output):
    export_eks_config(region, cluster_name, output)

if __name__ == '__main__':
    cli()