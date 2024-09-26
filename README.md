# Simple Karpenter Migration Tool
Migrate your EKS cluster from NodeGroup Cluster Autoscaler to Karpenter

# Overview
The automation CLI tool is expected to do:

1. [Feature-1] Discovery of the EKS Cluster Cluster Auto Scaler and its entirely Workloads configurations to explore the variation of scaling method it currently employs. [CAS configs, Node Groups, ASGs, Launch Templates, PDBs, Deployments nodeSelectors,NodeAffinity,PodAffinity, TopologySpeads, Taints). Discovery prerequisite kubectl access to EKS clusters.
2. [Feature-2] Describe the Variations the Cluster Currently Employs, Emphasize the changes impact on different configuration artifacts. This would be helpful for customer with smaller engineering team which does not have proper CICD/GitOps documenting all the stack architecture in place.
3. [Feature-3] Generate recommended ready to test configuration artifacts required. Including : Karpenter, Deployment, PDB configs. The customer can start using this for staging to production after testing and tuning.

The scenario automation CLI support would be:

1. AWS EKS Cluster. All Region.
2. 3 scenario autoscaling: 
    1. Managed NodeGroups (ASGs)
    2. Managed NodeGroups (ASGs) + Launch Templates
    3. ~~Zone-aware ASGs (Multi-AZ)~~

# Download
karpentermig is available on PyPI https://pypi.org/project/karpentermig/

```bash
pip install karpentermig
```

# Running the tool
## pre-requisites
- python 3.10+
- aws cli installed, configured and with access to your EKS cluster
- kubectl installed and configured to talk to your EKS cluster
- eksctl installed and configured to talk to your EKS cluster

```bash
karpentermig
```
