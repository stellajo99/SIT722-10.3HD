#!/bin/bash

# terraform/setup-remote-state.sh
# Script to create Azure Storage for Terraform remote state

set -e

# Configuration
RESOURCE_GROUP="terraform-state-rg"
STORAGE_ACCOUNT="terraformstate$RANDOM"
CONTAINER_NAME="tfstate"
LOCATION="Australia East"

echo "Setting up Terraform remote state storage..."

# Create resource group for state storage
echo "Creating resource group: $RESOURCE_GROUP"
az group create \
  --name "$RESOURCE_GROUP" \
  --location "$LOCATION"

# Create storage account
echo "Creating storage account: $STORAGE_ACCOUNT"
az storage account create \
  --resource-group "$RESOURCE_GROUP" \
  --name "$STORAGE_ACCOUNT" \
  --sku Standard_LRS \
  --encryption-services blob

# Create storage container
echo "Creating storage container: $CONTAINER_NAME"
az storage container create \
  --name "$CONTAINER_NAME" \
  --account-name "$STORAGE_ACCOUNT"

# Get storage account key
ACCOUNT_KEY=$(az storage account keys list \
  --resource-group "$RESOURCE_GROUP" \
  --account-name "$STORAGE_ACCOUNT" \
  --query '[0].value' -o tsv)

echo "
====================================
Remote State Setup Complete!
====================================

Your Terraform backend configuration:

terraform {
  backend \"azurerm\" {
    resource_group_name  = \"$RESOURCE_GROUP\"
    storage_account_name = \"$STORAGE_ACCOUNT\"
    container_name       = \"$CONTAINER_NAME\"
    key                  = \"ecommerce.terraform.tfstate\"
  }
}

====================================
GitHub Secrets to add:
====================================

TERRAFORM_STATE_RESOURCE_GROUP=$RESOURCE_GROUP
TERRAFORM_STATE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT
TERRAFORM_STATE_CONTAINER=$CONTAINER_NAME
TERRAFORM_STATE_KEY=ecommerce.terraform.tfstate

====================================
Next steps:
====================================

1. Add the GitHub secrets above to your repository
2. Update provider.tf to uncomment the backend configuration
3. Replace the values in provider.tf with the ones above
4. Run 'terraform init' to migrate to remote state

"