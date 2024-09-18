import questionary
from script import export_eks_config  # Changed this line

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
