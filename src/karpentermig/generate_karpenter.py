import csv
import yaml
import click
import os
import json
from typing import Dict, List, Any
from jinja2 import Template

# Update the schema_dir path
SCHEMA_DIR = os.path.join(os.path.dirname(__file__), 'schema')

def load_yaml_schema(filename: str) -> Dict[str, Any]:
    """Load a YAML schema file."""
    with open(os.path.join(SCHEMA_DIR, filename), 'r') as f:
        return yaml.safe_load(f)

def update_schema(schema: Dict[str, Any], config: Dict[str, Any], mapping: Dict[str, str]) -> Dict[str, Any]:
    """Update schema based on config and mapping."""
    for schema_key, config_key in mapping.items():
        if config_key in config:
            keys = schema_key.split('.')
            target = schema
            for key in keys[:-1]:
                target = target.setdefault(key, {})
            target[keys[-1]] = config[config_key]
    return schema

def render_template(template_str: str, config: Dict[str, Any]) -> str:
    """Render a Jinja2 template string with the given config."""
    template = Template(template_str)
    return template.render(**config)

def load_and_update_node_pool_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    schema = load_yaml_schema('nodePool-1-0-0.yaml')
    mapping = {
        'metadata.name': 'NodeGroupName',
        'spec.template.spec.requirements[0].values[0]': 'InstanceTypes',
        'spec.limits.cpu': 'MaxSize',
        'spec.limits.memory': 'MaxSize',
    }
    updated_schema = update_schema(schema, config, mapping)
    
    # Apply Jinja2 templating
    yaml_str = yaml.dump(updated_schema)
    rendered_yaml = render_template(yaml_str, config)
    return yaml.safe_load(rendered_yaml)

def load_and_update_ec2_node_class_schema(config: Dict[str, Any]) -> Dict[str, Any]:
    schema = load_yaml_schema('ec2NodeClass-1-0-0.yaml')
    mapping = {
        'metadata.name': 'NodeGroupName',
        'spec.amiFamily': 'AMIType',
        'spec.subnetSelectorTerms[0].tags.Name': 'Subnets',
        'spec.securityGroupSelectorTerms[0].tags.Name': 'SecurityGroups',
    }
    updated_schema = update_schema(schema, config, mapping)
    
    # Apply Jinja2 templating
    yaml_str = yaml.dump(updated_schema)
    rendered_yaml = render_template(yaml_str, config)
    return yaml.safe_load(rendered_yaml)

def read_eks_config(csv_file: str) -> List[Dict[str, Any]]:
    """Read EKS configuration from CSV file."""
    csv_path = os.path.join(os.getcwd(), csv_file)
    with open(csv_path, 'r') as f:
        return list(csv.DictReader(f))

def generate_karpenter_config(eks_config: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate Karpenter configuration based on EKS config."""
    if not eks_config:
        raise ValueError("EKS config is empty")
    return {
        "node_pool": load_and_update_node_pool_schema(eks_config[0]),
        "ec2_node_class": load_and_update_ec2_node_class_schema(eks_config[0])
    }

def write_karpenter_config(config: Dict[str, Any], output_file: str):
    """Write Karpenter configuration to YAML file."""
    with open(output_file, 'w') as f:
        yaml.dump_all([config['node_pool'], config['ec2_node_class']], f, default_flow_style=False)

def log_eks_config(eks_config: List[Dict[str, Any]]):
    """Log EKS configuration in JSON format."""
    click.echo("EKS Config:")
    for idx, config in enumerate(eks_config, 1):
        click.echo(f"Config {idx}:")
        click.echo(json.dumps(config, indent=2))

@click.command()
@click.option('--input', 'input_file', default='eks_config.csv', help='Input CSV file from discover_cluster.py')
@click.option('--output', 'output_file', default='karpenter-config.yaml', help='Output YAML file for Karpenter configuration')
def cli(input_file: str, output_file: str):
    eks_config = read_eks_config(input_file)
    karpenter_config = generate_karpenter_config(eks_config)
    write_karpenter_config(karpenter_config, output_file)
    click.echo(f"Karpenter configuration generated: {output_file}")
    log_eks_config(eks_config)

if __name__ == '__main__':
    cli()
