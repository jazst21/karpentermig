#!/bin/bash

set -e

# Configuration
CLUSTER_NAME="karpentermig-launch-test"
NODE_GROUP_NAME="ng-t3-small-lt"
REGION="us-west-2"
STACK_NAME="${CLUSTER_NAME}-lt"
CF_TEMPLATE="launch-template-cf.yaml"
EKSCTL_CONFIG="karpentermig-launch-test.yaml"

# Replace these with your actual values
AMI_ID="ami-12345678"
SUBNET_1="subnet-12345678"
SUBNET_2="subnet-23456789"
SUBNET_3="subnet-34567890"

echo "Step 1: Creating Launch Template using CloudFormation"
aws cloudformation create-stack --stack-name $STACK_NAME \
  --template-body file://$CF_TEMPLATE \
  --parameters ParameterKey=ClusterName,ParameterValue=$CLUSTER_NAME \
               ParameterKey=NodeGroupName,ParameterValue=$NODE_GROUP_NAME \
               ParameterKey=AMIId,ParameterValue=$AMI_ID \
  --region $REGION

echo "Waiting for CloudFormation stack to complete..."
aws cloudformation wait stack-create-complete --stack-name $STACK_NAME --region $REGION

echo "Step 2: Retrieving LaunchTemplateId"
LAUNCH_TEMPLATE_ID=$(aws cloudformation describe-stacks --stack-name $STACK_NAME --region $REGION \
  --query "Stacks[0].Outputs[?OutputKey=='LaunchTemplateId'].OutputValue" --output text)

echo "LaunchTemplateId: $LAUNCH_TEMPLATE_ID"

echo "Step 3: Updating eksctl configuration file"
sed -i.bak \
  -e "s/id: !Ref NodeGroupLaunchTemplate/id: $LAUNCH_TEMPLATE_ID/" \
  -e "s/subnet-12345678/$SUBNET_1/" \
  -e "s/subnet-23456789/$SUBNET_2/" \
  -e "s/subnet-34567890/$SUBNET_3/" \
  $EKSCTL_CONFIG

echo "Step 4: Creating EKS cluster using eksctl"
eksctl create cluster -f $EKSCTL_CONFIG

echo "Cluster creation complete!"