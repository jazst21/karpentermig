import questionary
from .discover_cluster import export_eks_config
from .generate_karpenter import cli as generate_karpenter_cli

questions = [
    {
        'type': 'list',
        'name': 'karpenter_migration',
        'message': 'Select option:',
        'choices': ['Discover eks cluster nodegroup config', 'Discover deployment config in namespace', 'Generate karpenter config', 'convert deployment to karpenter']
    }
]

answers = questionary.prompt(questions)

if answers['karpenter_migration'] == 'Discover eks cluster nodegroup config':
    export_eks_config()
elif answers['karpenter_migration'] == 'Generate karpenter config':
    generate_karpenter_cli()
else:
    print(f"Selected option: {answers['karpenter_migration']}")

def cli():
    # Function implementation
    pass

# Make sure the cli function is exported
__all__ = ['cli']
