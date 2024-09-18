import csv
import yaml
import click
from pathlib import Path

def read_eks_config(csv_file):
    with open(csv_file, 'r') as f:
        reader = csv.DictReader(f)
        return list(reader)

def generate_karpenter_config(eks_config):
    provisioner = {
        'apiVersion': 'karpenter.sh/v1alpha5',
        'kind': 'NodePool',
        'metadata': {'name': 'default'},
        'spec': {
            'requirements': [
                {'key': 'karpenter.sh/capacity-type', 'operator': 'In', 'values': ['on-demand']},
                {'key': 'node.kubernetes.io/instance-type', 'operator': 'In', 'values': []}
            ],
            'limits': {'resources': {'cpu': 1000, 'memory': '1000Gi'}},
            'providerRef': {'name': 'default'},
            'ttlSecondsAfterEmpty': 30
        }
    }

    node_template = {
        'apiVersion': 'karpenter.k8s.aws/v1alpha1',
        'kind': 'EC2NodeClass',
        'metadata': {'name': 'default'},
        'spec': {
            'subnetSelector': {},
            'securityGroupSelector': {},
            'tags': {'KarpenterManaged': 'true'},
            'blockDeviceMappings': [
                {
                    'deviceName': '/dev/xvda',
                    'ebs': {
                        'volumeSize': '100Gi',
                        'volumeType': 'gp3',
                        'deleteOnTermination': True
                    }
                }
            ]
        }
    }

    for config in eks_config:
        # Add instance types
        instance_types = [t.strip() for t in config['InstanceTypes'].split(',')]
        provisioner['spec']['requirements'][1]['values'].extend(instance_types)

        # Set AMI family or custom AMI
        if config['AMIType'] != 'N/A':
            node_template['spec']['amiFamily'] = config['AMIType']
        elif config['AMIID'] != 'N/A':
            node_template['spec']['amiSelector'] = {'aws::ids': [config['AMIID']]}

        # Set subnet selector
        subnet_names = [s.strip() for s in config['Subnets'].split(',')]
        if subnet_names:
            node_template['spec']['subnetSelector'] = {'Name': f"{subnet_names[0]}*"}

        # Set security group selector
        sg_names = [sg.strip() for sg in config['SecurityGroups'].split(',')]
        if sg_names:
            node_template['spec']['securityGroupSelector'] = {'Name': f"{sg_names[0]}*"}

    # Remove duplicates from instance types
    provisioner['spec']['requirements'][1]['values'] = list(set(provisioner['spec']['requirements'][1]['values']))

    return [provisioner, node_template]

@click.command()
@click.option('--input', 'input_file', default='eks_config.csv', help='Input CSV file from discover_cluster.py')
@click.option('--output', 'output_file', default='karpenter-config.yaml', help='Output YAML file for Karpenter configuration')
def cli(input_file, output_file):
    eks_config = read_eks_config(input_file)
    karpenter_config = generate_karpenter_config(eks_config)

    with open(output_file, 'w') as f:
        yaml.dump_all(karpenter_config, f, default_flow_style=False)

    print(f"Karpenter configuration has been generated and saved to {output_file}")

if __name__ == '__main__':
    cli()
