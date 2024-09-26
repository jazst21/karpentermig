import csv
import yaml
import click
from pathlib import Path
import os
import json

# Update the schema_dir path
schema_dir = os.path.join(os.path.dirname(__file__), 'schema')

def load_and_update_node_pool_schema(eks_config):
    with open(os.path.join(schema_dir, 'nodePool-1-0-0.yaml'), 'r') as f:
        node_pool_schema = yaml.safe_load(f)    
    if not isinstance(eks_config, list) or len(eks_config) == 0:
        raise ValueError("eks_config must be a non-empty list of dictionaries")    
    node_pool_schema['metadata']['name'] = eks_config[0]['NodeGroupName']
    node_pool_schema['spec']['disruption']['consolidationPolicy'] = "WhenEmptyOrUnderutilized"
    return node_pool_schema

def load_and_update_ec2_node_class_schema(eks_config):
    with open(os.path.join(schema_dir, 'ec2NodeClass-1-0-0.yaml'), 'r') as f:
        ec2_node_class_schema=yaml.safe_load(f)
    ec2_node_class_schema['metadata']['name'] = "updated"
    return ec2_node_class_schema
    
def read_eks_config(csv_file):
    # Get the directory of the current script
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Construct the full path to the CSV file
    csv_path = os.path.join(current_dir, csv_file)
    
    with open(csv_path, 'r') as f:
        reader = csv.DictReader(f)
        config = list(reader)
    
    # Always return a list of dictionaries
    return config

def generate_karpenter_config(eks_config):
    # Here you can customize the node_pool and ec2_node_class schemas
    # based on the eks_config values if needed
    return {
        "node_pool": load_and_update_node_pool_schema(eks_config),
        "ec2_node_class": load_and_update_ec2_node_class_schema(eks_config)
    }

def write_karpenter_config(config, output_file):
    with open(output_file, 'w') as f:
        yaml.dump_all([config['node_pool'], config['ec2_node_class']], f, default_flow_style=False)

def log_eks_config(eks_config):
    """
    Recursively iterate through all columns in eks_config and log them in JSON format.
    """
    click.echo("EKS Config:")
    if isinstance(eks_config, dict):
        click.echo(json.dumps(eks_config, indent=2))
    elif isinstance(eks_config, list):
        for idx, config in enumerate(eks_config):
            click.echo(f"Config {idx + 1}:")
            click.echo(json.dumps(config, indent=2))
    else:
        click.echo("Unexpected eks_config format")

@click.command()
@click.option('--input', 'input_file', default=os.path.join(os.getcwd(), 'eks_config.csv'), help='Input CSV file from discover_cluster.py')
@click.option('--output', 'output_file', default='karpenter-config.yaml', help='Output YAML file for Karpenter configuration')
def cli(input_file, output_file):
    eks_config = read_eks_config(input_file)
    karpenter_config = generate_karpenter_config(eks_config)
    write_karpenter_config(karpenter_config, output_file)
    click.echo(f"Karpenter configuration generated: {output_file}")
    log_eks_config(eks_config)
    

if __name__ == '__main__':
    cli()
