# E-Commerce Microservices Platform

A cloud-native e-commerce platform built with microservices architecture, featuring automated CI/CD pipelines, containerized deployment, and Kubernetes orchestration.

## 📋 Table of Contents

- [Architecture Overview](#architecture-overview)
- [Services](#services)
- [CI/CD Pipeline](#cicd-pipeline)
- [Environments](#environments)
- [Deployment](#deployment)


## 🏗️ Architecture Overview

This platform implements a microservices architecture with the following components:

- **Frontend**: Nginx-served static web application
- **Product Service**: FastAPI microservice for product management
- **Order Service**: FastAPI microservice for order processing
- **Customer Service**: FastAPI microservice for customer management
- **Databases**: Separate PostgreSQL instances for each service
- **Container Registry**: Azure Container Registry (ACR)
- **Orchestration**: Azure Kubernetes Service (AKS)

## 🔧 Services

### Backend Services

| Service | Port | Database | Responsibilities |
|---------|------|----------|------------------|
| Product Service | 8000 | products | Product catalog, inventory, pricing |
| Order Service | 8001 | orders | Order processing, cart management |
| Customer Service | 8002 | customers | User accounts, profiles, authentication |

### Frontend
- **Technology**: Static HTML/JS/CSS served by Nginx
- **Port**: 3000 (development), 80 (production)
- **Integration**: Dynamic API endpoint configuration

### Databases
- **Product DB**: PostgreSQL on port 5432
- **Order DB**: PostgreSQL on port 5433
- **Customer DB**: PostgreSQL on port 5434

## 🚀 CI/CD Pipeline

The platform features a comprehensive three-stage CI/CD pipeline:

### 1. Continuous Integration (CI) - `ci.yml`

**Trigger**: Push to `testing` or `main` branches, manual dispatch

**Jobs**:

#### Backend Testing
- **Steps**:
  - Python 3.10 environment setup
  - Dependency installation from `requirements.txt` and `requirements-dev.txt`
  - Automated pytest execution
  - Service isolation and parallel execution

#### Build & Push
- **Dependency**: Requires all backend tests to pass
- **Registry**: Azure Container Registry (ACR)
- **Authentication**: Azure Service Principal
- **Image Tagging**:
  - Main branch: `main-{short-sha}`
  - Testing branch: `testing-{short-sha}`
- **Services Built**:
  - `product-service`
  - `order-service`
  - `customer-service`
  - `frontend`
- **Verification**: Post-push image verification in ACR
- **Artifacts**: Deploy manifest with build metadata

### 2. Production Deployment (CD) - `cd.yml`

**Triggers**:
- **Automatic**: Successful CI completion on `main` branch
- **Manual**: Workflow dispatch with environment selection

**Features**:
- **Concurrency Control**: Prevents overlapping deployments
- **Environment Selection**: Production/staging environment choice
- **Image Tag Resolution**: Automatic from CI or manual specification
- **Resource Groups**: Configurable AKS cluster targeting

**Deployment Process**:

1. **Pre-deployment**:
   - Context validation and safety checks
   - Azure authentication and AKS connection
   - Namespace creation and verification
   - Image existence verification in ACR

2. **Database Deployment**:
   - Conditional database deployment (if not exists)
   - Health check validation
   - Separate databases for each service

3. **Application Deployment**:
   - ConfigMaps and Secrets application
   - Service manifest deployment
   - Image tag updates to deployments
   - Rolling update orchestration

4. **Service Discovery**:
   - LoadBalancer IP allocation waiting
   - External IP collection and validation
   - Frontend runtime configuration update

5. **Verification**:
   - Rollout status monitoring
   - Service availability confirmation

### 3. Staging Environment - `staging-deploy.yml`

**Purpose**: Ephemeral testing environment with automatic cleanup

**Trigger**: Successful CI completion on `testing` branch

**Key Features**:
- **Isolation**: Unique namespace per deployment (`stg-{short-sha}`)
- **Full Stack**: Complete application stack deployment
- **API Testing**: Automated endpoint health checks
- **Auto-Cleanup**: Environment destruction after testing

**Testing Suite**:
- Infrastructure readiness validation
- Pod health confirmation
- LoadBalancer IP assignment
- HTTP endpoint accessibility testing

## 🌍 Environments

### Development Environment
- **Platform**: Docker Compose
- **Command**: `docker-compose up`
- **Features**:
  - Hot reload for development
  - Local PostgreSQL instances
  - Volume mounts for live editing
  - Health check monitoring

### Staging Environment
- **Platform**: Azure Kubernetes Service
- **Lifecycle**: Ephemeral (created and destroyed per deployment)
- **Purpose**: Testing and validation
- **Namespace Pattern**: `stg-{commit-sha}`

### Production Environment
- **Platform**: Azure Kubernetes Service
- **Namespace**: `default` (configurable)
- **High Availability**: Multiple replicas and health checks
- **Monitoring**: Comprehensive logging and metrics
- **Rollback**: Kubernetes native rollback capabilities

## 📦 Deployment

### Prerequisites

1. **Azure Resources**:
   - Azure Container Registry
   - Azure Kubernetes Service cluster
   - Service Principal with appropriate permissions

2. **GitHub Secrets**:
   ```
   AZURE_CONTAINER_REGISTRY=yourregistry.azurecr.io
   AZURE_CREDENTIALS={"clientId":"...","clientSecret":"...","tenantId":"...","subscriptionId":"..."}
   ```

3. **Kubernetes Secrets & ConfigMaps**:
   - Database credentials
   - Azure Storage configuration
   - Application settings


### Automated Deployment

#### Production Deployment
```bash
# Automatic: Merge/Push to main branch triggers production deployment

# Manual: Use GitHub Actions UI
# 1. Go to Actions → CD - Deploy to AKS
# 2. Click "Run workflow"
# 3. Select environment and parameters
# 4. Monitor deployment progress
```

## 📑 Note

The base e-commerce microservices application was provided as part of the SIT722 course material.
My primary contribution and implementation focus was on designing and building the CI/CD pipeline (automation workflows, deployments, and environment orchestration).
