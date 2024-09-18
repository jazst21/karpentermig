import questionary
from .discover_cluster import export_eks_config

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
else:
    print(f"Selected option: {answers['karpenter_migration']}")

def cli():
    # Function implementation
    pass

# Make sure the cli function is exported
__all__ = ['cli']
