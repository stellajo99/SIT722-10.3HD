# Terraform Remote State Setup Instructions

## Step 1: Verify Azure Login

```powershell
# Check if you're logged in
az account show

# If not logged in, run:
az login
```

## Step 2: Run Remote State Setup Script

```powershell
# Navigate to terraform directory
cd terraform

# Run the setup script
.\setup-remote-state.ps1
```

## Step 3: Copy the Output

The script will output something like this:

```
====================================
Remote State Setup Complete!
====================================

Your Terraform backend configuration:

terraform {
  backend "azurerm" {
    resource_group_name  = "terraform-state-rg"
    storage_account_name = "terraformstate12345"
    container_name       = "tfstate"
    key                  = "ecommerce.terraform.tfstate"
  }
}

====================================
GitHub Secrets to add:
====================================

TERRAFORM_STATE_RESOURCE_GROUP=terraform-state-rg
TERRAFORM_STATE_STORAGE_ACCOUNT=terraformstate12345
TERRAFORM_STATE_CONTAINER=tfstate
TERRAFORM_STATE_KEY=ecommerce.terraform.tfstate
```

## Step 4: Add GitHub Secrets

Go to your GitHub repository → Settings → Secrets and variables → Actions

Add these 5 secrets:

1. `AZURE_CREDENTIALS` (you already have this)
2. `TERRAFORM_STATE_RESOURCE_GROUP`
3. `TERRAFORM_STATE_STORAGE_ACCOUNT`
4. `TERRAFORM_STATE_CONTAINER`
5. `TERRAFORM_STATE_KEY`

## Step 5: Update Terraform Backend

In `terraform/provider.tf`, uncomment and update the backend block with the values from Step 3.

## Step 6: Test

```powershell
# Initialize Terraform with remote state
terraform init

# Test that everything works
terraform plan
```

Your infrastructure is now ready for automated CI/CD!