# Terraform Infrastructure

This directory contains Terraform configuration to provision Azure infrastructure for the ecommerce application.

## Architecture

The Terraform configuration provisions:

- **Resource Group**: Container for all Azure resources
- **Azure Container Registry (ACR)**: Stores Docker images
- **Azure Kubernetes Service (AKS)**: Kubernetes cluster for app deployment
- **Azure Storage Account**: Blob storage for product images
- **Azure Key Vault**: Secure storage for secrets and keys

## Setup Instructions

### 1. Prerequisites

- Azure CLI installed and authenticated
- Terraform >= 1.0 installed
- GitHub repository with appropriate secrets

### 2. Set up Remote State Storage

Run the setup script to create storage for Terraform state:

**Windows (PowerShell):**
```powershell
cd terraform
.\setup-remote-state.ps1
```

**Linux/macOS:**
```bash
cd terraform
chmod +x setup-remote-state.sh
./setup-remote-state.sh
```

### 3. Configure GitHub Secrets

Add these secrets to your GitHub repository (Settings > Secrets and variables > Actions):

```
AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","tenantId":"...","subscriptionId":"..."}
TERRAFORM_STATE_RESOURCE_GROUP=terraform-state-rg
TERRAFORM_STATE_STORAGE_ACCOUNT=terraformstate12345
TERRAFORM_STATE_CONTAINER=tfstate
TERRAFORM_STATE_KEY=ecommerce.terraform.tfstate
```

### 4. Enable Remote State Backend

1. Update `provider.tf` - uncomment the backend configuration
2. Replace the placeholder values with your actual state storage details
3. Run `terraform init` to migrate to remote state

### 5. Deploy Infrastructure

**Manual Deployment:**
```bash
terraform init
terraform plan
terraform apply
```

**Automated Deployment:**
- Push to `main` branch - triggers automatic apply
- Create PR - triggers plan and comments on PR
- Manual trigger - use GitHub Actions UI to plan/apply/destroy

## File Structure

```
terraform/
├── provider.tf              # Terraform and provider configuration
├── variables.tf             # Variable definitions
├── terraform.tfvars        # Variable values
├── outputs.tf              # Output definitions
├── resource_group.tf       # Resource group configuration
├── container_registry.tf   # ACR configuration
├── storage_account.tf      # Storage account configuration
├── kubernetes-cluster.tf   # AKS cluster configuration
├── key_vault.tf            # Key Vault configuration
├── setup-remote-state.sh   # Linux/macOS state setup script
├── setup-remote-state.ps1  # Windows state setup script
└── README.md               # This file
```

## Workflow Integration

The infrastructure workflow (`.github/workflows/infrastructure.yml`) runs before your CI/CD pipeline:

1. **Infrastructure** → Provision Azure resources
2. **CI** → Build and test application
3. **CD** → Deploy to provisioned infrastructure

## Customization

### Resource Naming

Update `variables.tf` and `terraform.tfvars` to match your naming conventions:

```hcl
# terraform.tfvars
resource_group_name = "your-resource-group"
acr_name           = "yourregistry"
aks_cluster_name   = "your-aks-cluster"
```

### Environment-Specific Configuration

Create separate `.tfvars` files for different environments:

```bash
terraform apply -var-file="staging.tfvars"
terraform apply -var-file="production.tfvars"
```

## Security Best Practices

1. **Remote State**: Always use remote state in production
2. **Secrets**: Store sensitive values in GitHub Secrets or Key Vault
3. **Access Control**: Use least privilege access for service principals
4. **State Locking**: Enabled automatically with Azure Storage backend

## Troubleshooting

### Common Issues

1. **State Backend Error**: Ensure remote state storage account exists
2. **Authentication Error**: Verify Azure credentials are configured correctly
3. **Resource Conflicts**: Check if resources already exist with same names
4. **Permission Denied**: Ensure service principal has appropriate permissions

### Useful Commands

```bash
# Check Terraform version
terraform version

# Validate configuration
terraform validate

# Format code
terraform fmt -recursive

# Show current state
terraform show

# Import existing resources
terraform import azurerm_resource_group.main /subscriptions/{id}/resourceGroups/{name}
```

## Support

For issues with this Terraform configuration:

1. Check the troubleshooting section above
2. Review GitHub Actions logs for detailed error messages
3. Ensure all prerequisites are met
4. Verify Azure permissions and quotas