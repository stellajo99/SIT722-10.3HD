# terraform.tfvars - Production values for your existing infrastructure

# Resource Group and Location
resource_group_name = "deakinuni"
location           = "Australia East"

# Project Settings
project_name = "ecommerce"
environment  = "prod"

# Azure Container Registry
acr_name = "deakinstellaregistry"

# Azure Storage Account
storage_account_name = "deakinstellastorage"

# Azure Kubernetes Service
aks_cluster_name = "deakinstellak8s"
aks_node_count   = 2
aks_node_vm_size = "Standard_B2s"

# Kubernetes Version
kubernetes_version = "1.31.7"

# PostgreSQL Configuration
# Note: In production, this should be set via environment variable or GitHub secret
postgres_password = "postgres"

# Common Tags
common_tags = {
  Project     = "Ecommerce"
  Environment = "Production"
  ManagedBy   = "Terraform"
  Repository  = "SIT722-10.3HD"
}