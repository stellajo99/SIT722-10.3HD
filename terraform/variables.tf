# terraform/variables.tf - Updated to match existing infrastructure

variable "resource_group_name" {
  description = "Name of the Azure Resource Group"
  type        = string
  default     = "deakinuni"
}

variable "location" {
  description = "Azure region for resources"
  type        = string
  default     = "Australia East"
}

variable "project_name" {
  description = "Project name for resource naming"
  type        = string
  default     = "ecommerce"
}

variable "environment" {
  description = "Environment (dev, staging, prod)"
  type        = string
  default     = "prod"
}

variable "acr_name" {
  description = "Azure Container Registry name"
  type        = string
  default     = "deakinstellaregistry"
}

variable "storage_account_name" {
  description = "Azure Storage Account name"
  type        = string
  default     = "deakinstellastorage"
}

variable "aks_cluster_name" {
  description = "Azure Kubernetes Service cluster name"
  type        = string
  default     = "deakinstellak8s"
}

variable "aks_node_count" {
  description = "Number of nodes in the AKS cluster"
  type        = number
  default     = 2
}

variable "aks_node_vm_size" {
  description = "VM size for AKS nodes"
  type        = string
  default     = "Standard_B2s"
}

variable "kubernetes_version" {
  description = "Kubernetes version for AKS cluster"
  type        = string
  default     = "1.31.7"
}

variable "postgres_password" {
  description = "PostgreSQL password"
  type        = string
  sensitive   = true
  default     = "postgres"
}

variable "common_tags" {
  description = "Common tags for all resources"
  type        = map(string)
  default = {
    Project     = "Ecommerce"
    Environment = "Production"
    ManagedBy   = "Terraform"
  }
}
