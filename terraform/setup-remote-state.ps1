# terraform/setup-remote-state.ps1
# PowerShell script to create Azure Storage for Terraform remote state

# Configuration
$RESOURCE_GROUP = "terraform-state-rg"
$STORAGE_ACCOUNT = "terraformstate$(Get-Random -Minimum 10000 -Maximum 99999)"
$CONTAINER_NAME = "tfstate"
$LOCATION = "Australia East"

Write-Host "Setting up Terraform remote state storage..." -ForegroundColor Green

try {
    # Create resource group for state storage
    Write-Host "Creating resource group: $RESOURCE_GROUP" -ForegroundColor Yellow
    az group create --name $RESOURCE_GROUP --location $LOCATION

    # Create storage account
    Write-Host "Creating storage account: $STORAGE_ACCOUNT" -ForegroundColor Yellow
    az storage account create `
        --resource-group $RESOURCE_GROUP `
        --name $STORAGE_ACCOUNT `
        --sku Standard_LRS `
        --encryption-services blob

    # Create storage container
    Write-Host "Creating storage container: $CONTAINER_NAME" -ForegroundColor Yellow
    az storage container create `
        --name $CONTAINER_NAME `
        --account-name $STORAGE_ACCOUNT

    # Get storage account key
    $ACCOUNT_KEY = az storage account keys list `
        --resource-group $RESOURCE_GROUP `
        --account-name $STORAGE_ACCOUNT `
        --query '[0].value' -o tsv

    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "Remote State Setup Complete!" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Your Terraform backend configuration:" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "terraform {" -ForegroundColor White
    Write-Host "  backend `"azurerm`" {" -ForegroundColor White
    Write-Host "    resource_group_name  = `"$RESOURCE_GROUP`"" -ForegroundColor White
    Write-Host "    storage_account_name = `"$STORAGE_ACCOUNT`"" -ForegroundColor White
    Write-Host "    container_name       = `"$CONTAINER_NAME`"" -ForegroundColor White
    Write-Host "    key                  = `"ecommerce.terraform.tfstate`"" -ForegroundColor White
    Write-Host "  }" -ForegroundColor White
    Write-Host "}" -ForegroundColor White
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "GitHub Secrets to add:" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "TERRAFORM_STATE_RESOURCE_GROUP=$RESOURCE_GROUP" -ForegroundColor Yellow
    Write-Host "TERRAFORM_STATE_STORAGE_ACCOUNT=$STORAGE_ACCOUNT" -ForegroundColor Yellow
    Write-Host "TERRAFORM_STATE_CONTAINER=$CONTAINER_NAME" -ForegroundColor Yellow
    Write-Host "TERRAFORM_STATE_KEY=ecommerce.terraform.tfstate" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "====================================" -ForegroundColor Green
    Write-Host "Next steps:" -ForegroundColor Green
    Write-Host "====================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "1. Add the GitHub secrets above to your repository" -ForegroundColor White
    Write-Host "2. Update provider.tf to uncomment the backend configuration" -ForegroundColor White
    Write-Host "3. Replace the values in provider.tf with the ones above" -ForegroundColor White
    Write-Host "4. Run 'terraform init' to migrate to remote state" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host "Error occurred: $_" -ForegroundColor Red
    exit 1
}