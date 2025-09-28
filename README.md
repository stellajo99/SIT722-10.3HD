# Complete Automated DevOps Pipeline Tutorial
## From Zero to Production: Implementing Dynamic Infrastructure-Application Integration

> **🎯 Learning Objective**: Learn to build a fully automated DevOps pipeline that dynamically integrates infrastructure provisioning with application deployment, eliminating manual configuration and achieving true Infrastructure as Code.

---

## 📋 **What You'll Learn & Replicate**

By following this tutorial, you'll implement the **complete automation** demonstrated in this project:

### **Core Automation Features**
1. **🔄 Complete Pipeline Automation** - Zero manual intervention from code to production
2. **🏗️ Dynamic Infrastructure Integration** - Real-time Terraform output consumption in deployments
3. **🔐 Advanced Secret Management** - Template-based credential handling with `envsubst`
4. **🔗 Cross-Workflow Orchestration** - Intelligent `workflow_run` triggers and fallbacks
5. **🏠 Ephemeral Environment Management** - SHA-based testing environments with auto-cleanup

### **Architecture You'll Build**
```
GitHub Push → CI (Build/Test/Push) → Infrastructure (Terraform) → Staging (Deploy/Test/Destroy) → Production
     ↓              ↓                        ↓                        ↓                         ↓
   Automated    Container Registry     Live Infrastructure     Ephemeral Testing        Production Ready
```

---

## 🚀 **Quick Start: Replicate This Automation**

### **Prerequisites**
```bash
# Required accounts and tools
✅ GitHub account with Actions enabled
✅ Azure subscription
✅ Basic knowledge of Docker, Kubernetes, Terraform
✅ Git CLI installed
```

### **Step 1: Fork and Setup Repository**
```bash
# Fork this repository on GitHub, then:
git clone https://github.com/YOUR-USERNAME/SIT722-10.3HD
cd SIT722-10.3HD
```

### **Step 2: Azure Service Principal Creation**
```bash
# Create service principal for automated Azure access
az ad sp create-for-rbac --name "github-actions-devops-tutorial" \
  --role "Contributor" \
  --scopes "/subscriptions/{your-subscription-id}" \
  --sdk-auth

# ⚠️ SAVE THE OUTPUT - you'll need it for GitHub Secrets
```

### **Step 3: Configure GitHub Secrets for Automation**
Navigate to: `Your Repository → Settings → Secrets and variables → Actions`

Add these secrets for complete automation:
```yaml
AZURE_CREDENTIALS: # Paste output from Step 2
TERRAFORM_STATE_RESOURCE_GROUP: "terraform-state-rg"
TERRAFORM_STATE_STORAGE_ACCOUNT: "terraformstate84329"
TERRAFORM_STATE_CONTAINER: "tfstate"
TERRAFORM_STATE_KEY: "ecommerce.terraform.tfstate"
```

### **Step 4: Test Complete Automation**
```bash
# Complete automation flow:

# 1. First, trigger infrastructure creation (any terraform changes)
git checkout testing
echo "# Update infrastructure" >> terraform/variables.tf
git add terraform/
git commit -m "infrastructure: trigger Azure infrastructure creation"
git push origin testing
# → This creates/updates Azure infrastructure via Terraform

# 2. Then trigger application deployment to testing
echo "# Testing automation" >> test.txt
git add .
git commit -m "test: trigger complete automation"
git push origin testing
# → This triggers CI → builds containers → pushes to ACR
# → Then auto-triggers staging deployment → creates ephemeral environment → tests → cleanup

# 3. After testing validation, merge to main for production deployment
git checkout main
git merge testing
git push origin main
# → This triggers CI → CD pipeline → deploys to production → accessible IP available

# 🎉 Watch the complete automation chain in GitHub Actions:
# Infrastructure → CI → Staging → Production → Live Accessible Application!
```

---

## 🎓 **Tutorial Deep Dive: Understanding the Automation**

### **🔄 Feature 1: Complete CI Automation with Comprehensive Testing**

**Files to Study**:
- `.github/workflows/ci.yml` (CI pipeline)
- `backend/*/tests/` (Test suites for each service)

**What This Automates**:
```yaml
# Automatic triggers
on:
  push:
    branches: [ "testing", "main" ]  # Auto-trigger on branch push
  workflow_dispatch:                 # Manual trigger capability
```

**🧪 Multi-Layer Testing Strategy**:

**1. Unit Tests** (Models & Schemas):
```yaml
# Backend tests with PostgreSQL service
test-backend:
  services:
    postgres:
      image: postgres:13
      env:
        POSTGRES_USER: postgres
        POSTGRES_PASSWORD: postgres
        POSTGRES_DB: test_db
  strategy:
    matrix:
      service: [ "product_service", "order_service", "customer_service" ]
```

**2. Integration Tests** (API Endpoints):
```python
# Example from backend/product_service/tests/test_main.py
def test_create_product_success(client: TestClient, db_session_for_test: Session):
    test_data = {
        "name": "New Test Product",
        "description": "A brand new product for testing",
        "price": 12.34,
        "stock_quantity": 100,
        "image_url": "http://example.com/test_image.jpg",
    }
    response = client.post("/products/", json=test_data)
    assert response.status_code == 201
    # Verify database persistence
    db_product = db_session_for_test.query(Product).filter(...).first()
    assert db_product.name == test_data["name"]
```

**3. Schema Validation Tests**:
```python
# Example from backend/product_service/tests/test_schemas.py
def test_product_create_invalid_price_negative(self):
    data = {"name": "Invalid Product", "price": -10.0, "stock_quantity": 50}
    with pytest.raises(ValidationError) as exc_info:
        ProductCreate(**data)
    assert "greater than 0" in str(exc_info.value)
```

**🚀 Testing Features**:
- **Parallel Test Execution**: Matrix strategy runs all services simultaneously
- **Database Transaction Isolation**: Each test runs in isolated transactions
- **Mock External Services**: Azure Blob Storage mocked for reliable testing
- **Comprehensive Coverage**: Unit tests (models/schemas) + Integration tests (APIs)
- **Validation Testing**: Pydantic schema validation with edge cases

**Key Learning: Dynamic Tag Generation**
```yaml
- name: Compute Build Tag
  id: meta
  run: |
    if [ "${{ github.ref_name }}" = "main" ]; then
      echo "TAG=main-$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
    else
      echo "TAG=testing-$(git rev-parse --short HEAD)" >> $GITHUB_OUTPUT
    fi
```

**🎯 Why This Matters**: Every build gets a unique, traceable tag. This enables:
- Parallel development and testing
- Easy rollbacks to specific commits
- Environment isolation

**How to Replicate**:
1. Copy the tag generation logic
2. Adapt branch names to your workflow
3. Use `${{ steps.meta.outputs.TAG }}` throughout your pipeline

**Verification Command**:
```bash
# Check your built images in ACR
az acr repository show-tags --name yourregistry --repository product-service
```

---

### **🏗️ Feature 2: Dynamic Infrastructure Integration**

**Files to Study**:
- `.github/workflows/infrastructure.yml` (creates outputs)
- `.github/workflows/staging-deploy.yml` (consumes outputs)

**The Innovation**: Real-time Terraform integration in deployment workflows

**In staging-deploy.yml**:
```yaml
- name: Get Terraform outputs
  run: |
    cd terraform
    # 🔥 LIVE infrastructure queries - no hardcoded values!
    REGISTRY=$(terraform output -raw acr_login_server)
    AKS_RG=$(terraform output -raw resource_group_name)
    AKS_NAME=$(terraform output -raw aks_cluster_name)
    STORAGE_ACCOUNT_NAME=$(terraform output -raw storage_account_name)
    STORAGE_KEY=$(terraform output -raw storage_account_primary_key)

    # Set as environment variables for pipeline
    echo "REGISTRY=$REGISTRY" >> $GITHUB_ENV
    echo "AKS_RG=$AKS_RG" >> $GITHUB_ENV
    echo "AKS_NAME=$AKS_NAME" >> $GITHUB_ENV
```

**🎯 Why This Is Revolutionary**:
- **Zero hardcoded values** anywhere in the pipeline
- **Infrastructure changes automatically propagate** to applications
- **True Infrastructure as Code** - change terraform, applications adapt

**How to Replicate This Pattern**:

1. **In your infrastructure workflow**, capture outputs:
```yaml
- name: Output Infrastructure Details
  run: |
    terraform output -json > infrastructure-outputs.json
    terraform output -raw resource_group_name  # Test accessibility
```

2. **In your deployment workflow**, consume them:
```yaml
- name: Setup Terraform  # Add this step to access terraform
  uses: hashicorp/setup-terraform@v3

- name: Get Live Infrastructure Values
  run: |
    cd terraform
    terraform init  # Initialize to access state
    REGISTRY=$(terraform output -raw your_acr_output)
    echo "REGISTRY=$REGISTRY" >> $GITHUB_ENV
```

3. **Use the values** throughout your deployment:
```yaml
kubectl set image deployment/your-app container="$REGISTRY/your-app:$TAG"
```

**Test Your Implementation**:
```bash
# Change infrastructure in terraform/variables.tf
# Push changes and verify deployment uses new values automatically
```

---

### **🔐 Feature 3: Advanced Secret Management**

**Files to Study**:
- `k8s/secrets.yaml` (template)
- `.github/workflows/staging-deploy.yml` (substitution logic)

**The Problem**: How do you securely pass infrastructure-generated credentials to applications?

**The Solution**: Template-based secret substitution with `envsubst`

**Step 1: Create Secret Templates**
```yaml
# k8s/secrets.yaml - Note the ${VARIABLE} placeholders
apiVersion: v1
kind: Secret
metadata:
  name: ecomm-secrets-w10e1
type: Opaque
data:
  # These are TEMPLATES, not actual values
  AZURE_STORAGE_ACCOUNT_NAME: ${STORAGE_ACCOUNT_NAME_B64}
  AZURE_STORAGE_ACCOUNT_KEY: ${STORAGE_ACCOUNT_KEY_B64}
  POSTGRES_USER: ${POSTGRES_USER_B64}
  POSTGRES_PASSWORD: ${POSTGRES_PASSWORD_B64}
```

**Step 2: Automated Template Substitution**
```bash
# In your deployment workflow
- name: Apply config & secrets
  run: |
    # Get values from infrastructure (already in env vars)
    POSTGRES_USER="postgres"
    POSTGRES_PASSWORD="postgres"

    # Base64 encode for Kubernetes secrets
    export STORAGE_ACCOUNT_NAME_B64=$(echo -n "$STORAGE_ACCOUNT_NAME" | base64 -w 0)
    export STORAGE_ACCOUNT_KEY_B64=$(echo -n "$STORAGE_KEY" | base64 -w 0)
    export POSTGRES_USER_B64=$(echo -n "$POSTGRES_USER" | base64 -w 0)
    export POSTGRES_PASSWORD_B64=$(echo -n "$POSTGRES_PASSWORD" | base64 -w 0)

    # 🔥 Magic happens here - envsubst replaces ${VARS} with actual values
    envsubst < k8s/secrets.yaml | kubectl apply -n "$NS" -f -
```

**🎯 Security Benefits**:
- **No secrets in git repositories**
- **Dynamic credential generation**
- **Infrastructure-to-application credential flow**
- **Template-based approach scales to any number of secrets**

**How to Replicate This Pattern**:

1. **Create your secret template**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: your-app-secrets
data:
  DATABASE_URL: ${DATABASE_URL_B64}
  API_KEY: ${API_KEY_B64}
```

2. **Add substitution logic**:
```bash
export DATABASE_URL_B64=$(echo -n "$DATABASE_URL" | base64 -w 0)
export API_KEY_B64=$(echo -n "$API_KEY" | base64 -w 0)
envsubst < k8s/your-secrets.yaml | kubectl apply -f -
```

**Verify Your Implementation**:
```bash
# Check secrets were created correctly
kubectl get secret your-app-secrets -o yaml
# Decode and verify values
kubectl get secret your-app-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

### **🔗 Feature 4: Cross-Workflow Orchestration**

**Files to Study**:
- `.github/workflows/staging-deploy.yml` (triggers and conditions)

**The Challenge**: How do you automatically trigger deployment when CI completes, but also allow manual overrides?

**The Solution**: `workflow_run` triggers with intelligent fallbacks

```yaml
# staging-deploy.yml - Dual trigger system
on:
  workflow_run:
    workflows: ["CI (testing push → test → ACR push)"]  # Auto trigger
    types: [completed]
    branches: [testing]
  workflow_dispatch:  # Manual override
    inputs:
      image_tag:
        description: "ACR image tag to deploy (e.g., testing-abcdef1)"
        required: false
      namespace_suffix:
        description: "Override namespace suffix"
        required: false
```

**Smart Conditional Logic**:
```yaml
jobs:
  deploy-staging:
    # Only run if:
    # 1. Manual trigger OR
    # 2. Auto trigger from successful CI on testing branch
    if: github.event_name == 'workflow_dispatch' ||
        (github.event_name == 'workflow_run' &&
         github.event.workflow_run.conclusion == 'success' &&
         github.event.workflow_run.head_branch == 'testing')
```

**Dynamic Context Handling**:
```yaml
- name: Compute image TAG / Namespace
  run: |
    # Handle different trigger sources
    if [ "${{ github.event_name }}" = "workflow_run" ]; then
      SHA="${{ github.event.workflow_run.head_sha }}"  # From CI trigger
    else
      SHA="${{ github.sha }}"  # From manual trigger
    fi

    # Allow manual tag override
    INPUT_TAG="${{ inputs.image_tag || '' }}"
    if [ -n "$INPUT_TAG" ]; then
      TAG="$INPUT_TAG"  # Use provided tag
    else
      TAG="testing-${SHA:0:7}"  # Generate from SHA
    fi
```

**🎯 Why This Enables True Automation**:
- **Hands-off development workflow**: Push → Auto CI → Auto Deploy → Auto Test
- **Emergency manual control**: Deploy specific versions when needed
- **Context awareness**: Different behavior for different trigger sources

**How to Replicate This Pattern**:

1. **Set up workflow_run trigger**:
```yaml
on:
  workflow_run:
    workflows: ["Your CI Workflow Name"]  # Exact name from ci.yml
    types: [completed]
    branches: [your-branch]
```

2. **Add manual fallback**:
```yaml
  workflow_dispatch:
    inputs:
      version:
        description: "Version to deploy"
        required: false
```

3. **Handle both contexts**:
```yaml
- name: Determine Deploy Version
  run: |
    if [ "${{ github.event_name }}" = "workflow_run" ]; then
      VERSION="auto-${{ github.event.workflow_run.head_sha }}"
    else
      VERSION="${{ inputs.version || 'latest' }}"
    fi
    echo "VERSION=$VERSION" >> $GITHUB_ENV
```

**Test Your Implementation**:
```bash
# Test automatic trigger
git push origin testing  # Should auto-trigger CI then your workflow

# Test manual trigger
# Go to GitHub Actions → Your Workflow → Run workflow
```

---

### **🏠 Feature 5: Ephemeral Environment Management**

**Files to Study**:
- `.github/workflows/staging-deploy.yml` (namespace creation and cleanup)

**The Innovation**: SHA-based isolated testing environments with automatic cleanup

**Dynamic Environment Creation**:
```yaml
- name: Compute image TAG / Namespace
  run: |
    # Create unique namespace per commit
    SHORT="${SHA:0:7}"  # First 7 chars of git SHA
    NS_SUFFIX="${{ inputs.namespace_suffix || '' }}"
    if [ -z "$NS_SUFFIX" ]; then
      NS_SUFFIX="$SHORT"  # Use git SHA as default
    fi
    NS="stg-$NS_SUFFIX"  # Results in: stg-abc1234

    echo "NS=$NS" >> $GITHUB_OUTPUT

- name: Create / ensure staging namespace
  run: |
    NS="${{ steps.meta.outputs.NS }}"
    kubectl get ns "$NS" >/dev/null 2>&1 || kubectl create namespace "$NS"
    echo "Staging namespace: $NS"
```

**Complete Environment Deployment**:
```yaml
- name: Apply databases
  run: |
    kubectl apply -n "$NS" -f k8s/product-db.yaml
    kubectl apply -n "$NS" -f k8s/order-db.yaml
    kubectl apply -n "$NS" -f k8s/customer-db.yaml

- name: Apply services
  run: |
    kubectl apply -n "$NS" -f k8s/product-service.yaml
    kubectl apply -n "$NS" -f k8s/order-service.yaml
    kubectl apply -n "$NS" -f k8s/customer-service.yaml
```

**Automated Testing**:
```yaml
- name: Test API endpoints
  run: |
    # Get LoadBalancer IPs
    PRODUCT_IP=$(kubectl get svc product-service-w10e1 -n "$NS" -o jsonpath='{.status.loadBalancer.ingress[0].ip}')

    # Test endpoints
    if curl -sf --max-time 30 "http://$PRODUCT_IP:8000/products"; then
      echo "✅ Product Service: PASS"
    else
      echo "❌ Product Service: FAIL"
    fi
```

**Guaranteed Cleanup**:
```yaml
- name: Destroy staging environment (always)
  if: always()  # Runs even if previous steps fail
  run: |
    kubectl delete namespace "${{ steps.meta.outputs.NS }}" --wait=false
```

**🎯 Why This Is Game-Changing**:
- **Parallel Development**: Multiple PRs can test simultaneously
- **Perfect Isolation**: Each deployment in separate namespace
- **Zero Resource Waste**: Automatic cleanup after testing
- **Traceability**: Namespace name maps to exact git commit

**How to Replicate This Pattern**:

1. **Generate unique identifiers**:
```yaml
- name: Generate Environment ID
  run: |
    ENV_ID="test-$(git rev-parse --short HEAD)"  # Or use $GITHUB_RUN_ID
    echo "ENV_ID=$ENV_ID" >> $GITHUB_ENV
```

2. **Create isolated environment**:
```yaml
- name: Create Test Environment
  run: |
    kubectl create namespace "$ENV_ID"
    kubectl label namespace "$ENV_ID" purpose=testing
```

3. **Deploy your application**:
```yaml
- name: Deploy to Test Environment
  run: |
    kubectl apply -n "$ENV_ID" -f k8s/
```

4. **Always cleanup**:
```yaml
- name: Cleanup Test Environment
  if: always()
  run: |
    kubectl delete namespace "$ENV_ID" --ignore-not-found
```

**Advanced Pattern - Multiple Environments**:
```bash
# Create environments for different purposes
kubectl create namespace "pr-${PR_NUMBER}"      # Per pull request
kubectl create namespace "feature-${BRANCH}"    # Per feature branch
kubectl create namespace "load-test-${DATE}"    # For load testing
```

---

## 🧪 **Complete Testing Guide: Verify Your Implementation**

### **Test 1: Complete Testing Pipeline Verification**
```bash
# This tests the complete testing and automation chain
git checkout testing
echo "Test automation $(date)" > test-automation.txt
git add .
git commit -m "test: complete automation flow"
git push origin testing

# Expected flow:
# 1. CI workflow starts automatically
# 2. Unit Tests: Model & Schema validation (pytest backend/*/tests/test_models.py test_schemas.py)
# 3. Integration Tests: API endpoints with PostgreSQL (pytest backend/*/tests/test_main.py)
# 4. Builds and pushes containers to ACR (only after ALL tests pass)
# 5. Staging workflow triggers automatically
# 6. Creates ephemeral environment
# 7. Deploys and tests applications
# 8. Cleans up environment
```

**Watch Points - Testing Phase**:
- **Unit Test Results**: All model and schema validations pass
- **Integration Test Results**: All API endpoints return expected responses
- **Database Tests**: Transaction isolation and rollback working correctly
- **Mock Services**: Azure Blob Storage mocking successful
- **Test Parallel Execution**: All 3 services tested simultaneously

**Watch Points - Deployment Phase**:
- GitHub Actions shows both workflows running
- ACR receives new container images (only after tests pass)
- Kubernetes namespace created then deleted
- All tests pass before cleanup

### **Test 1.1: Local Testing Verification**
```bash
# Run tests locally to verify test suite before CI
cd backend/product_service
pip install -r requirements-dev.txt
pip install -r requirements.txt

# Run unit tests
pytest tests/test_models.py -v
pytest tests/test_schemas.py -v

# Run integration tests (requires PostgreSQL)
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=postgres
export POSTGRES_DB=test_db
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
pytest tests/test_main.py -v

# Run all tests
pytest tests/ -v
```

**Expected Local Test Results**:
- ✅ test_models.py: 15+ model validation tests pass
- ✅ test_schemas.py: 25+ schema validation tests pass
- ✅ test_main.py: 10+ API integration tests pass
- ✅ Database transactions properly isolated
- ✅ Mock Azure services working correctly

### **Test 2: Infrastructure Change Propagation**
```bash
# Test dynamic infrastructure integration
# 1. Modify terraform/variables.tf
sed -i 's/deakinstellak8s2025/your-new-cluster-name/g' terraform/variables.tf

# 2. Commit infrastructure change
git add terraform/
git commit -m "infrastructure: update cluster name"
git push origin testing

# 3. Verify deployment uses new values
# Check workflow logs show new cluster name
```

### **Test 3: Manual Override Capabilities**
```bash
# Test manual deployment with specific image tag
# 1. Go to GitHub Actions → staging-deploy
# 2. Click "Run workflow"
# 3. Enter image_tag: "testing-abc1234" (use existing tag)
# 4. Enter namespace_suffix: "manual-test"
# 5. Verify it uses your specified values
```

### **Test 4: Secret Template Substitution**
```bash
# Verify secrets are created correctly
kubectl get secrets -n stg-abc1234  # Use actual namespace from test
kubectl get secret ecomm-secrets-w10e1 -n stg-abc1234 -o yaml

# Decode and verify a secret value
kubectl get secret ecomm-secrets-w10e1 -n stg-abc1234 \
  -o jsonpath='{.data.POSTGRES_USER}' | base64 -d
```

### **Test 5: Parallel Environment Isolation**
```bash
# Create multiple test environments simultaneously
# 1. Create branch test1: git checkout -b test1; git push origin test1
# 2. Create branch test2: git checkout -b test2; git push origin test2
# 3. Manually trigger staging deploy for both
# 4. Verify both environments run simultaneously
kubectl get namespaces | grep stg-
```

---

## 🎯 **Production Deployment Tutorial**

### **Extending to Production**

**Step 1: Create Production Workflow**
```yaml
# .github/workflows/production-deploy.yml
name: Production Deployment
on:
  workflow_run:
    workflows: ["CI (testing push → test → ACR push)"]
    types: [completed]
    branches: [main]  # Only deploy main branch to production

jobs:
  deploy-production:
    if: github.event.workflow_run.conclusion == 'success'
    runs-on: ubuntu-latest
    environment: production  # Requires approval

    steps:
      # Same steps as staging but with production namespace
      - name: Deploy to Production
        run: |
          NS="production"
          # Same deployment logic but no cleanup
```

**Step 2: Add Approval Gates**
```yaml
# In GitHub repo settings → Environments
# Create "production" environment
# Add required reviewers
# Add deployment protection rules
```

**Step 3: Production-Specific Configurations**
```yaml
# k8s/production/
├── configmaps.yaml          # Production config values
├── secrets.yaml            # Production secret templates
├── product-service.yaml    # With resource limits
└── ingress.yaml           # Production ingress rules
```

---

## 🔧 **Troubleshooting Guide: Common Issues & Solutions**

### **Issue 1: ImagePullBackOff Errors**
```bash
# Symptom: Pods stuck in ImagePullBackOff
# Cause: Image doesn't exist in ACR or wrong tag

# Debug steps:
kubectl describe pod <pod-name> -n <namespace>
kubectl logs <pod-name> -n <namespace>

# Verify image exists:
az acr repository show-tags --name yourregistry --repository product-service

# Check exact image name being pulled:
kubectl get deployment product-service-w10e1 -n <namespace> -o yaml | grep image:
```

**Common Fixes**:
- Ensure CI workflow completed successfully
- Verify image tag matches what CI pushed
- Check ACR permissions for AKS cluster

### **Issue 2: Secret Template Not Substituting**
```bash
# Symptom: Secrets contain literal ${VARIABLE_B64} instead of values
# Cause: Environment variables not set or envsubst not available

# Debug steps:
echo "STORAGE_ACCOUNT_NAME: $STORAGE_ACCOUNT_NAME"  # Verify env vars
which envsubst  # Verify envsubst available

# Manual test:
export TEST_VAR_B64=$(echo -n "test-value" | base64 -w 0)
echo 'test: ${TEST_VAR_B64}' | envsubst
```

**Common Fixes**:
- Verify Terraform outputs are being captured
- Check environment variable names match template variables
- Ensure envsubst is installed in runner

### **Issue 3: Terraform State Conflicts**
```bash
# Symptom: "state locked" errors
# Cause: Previous terraform run didn't complete properly

# Debug steps:
terraform show  # Check current state
terraform force-unlock <lock-id>  # Use lock ID from error

# Prevention:
terraform plan -lock-timeout=300s  # Increase timeout
```

### **Issue 4: Workflow Not Triggering**
```bash
# Symptom: staging-deploy doesn't start after CI
# Cause: workflow_run trigger misconfiguration

# Debug checklist:
✅ Workflow name in trigger matches exactly
✅ Branch name matches
✅ CI workflow completed successfully
✅ Repository settings allow workflow triggers
```

**Common Fixes**:
- Check exact workflow name in ci.yml
- Verify branches match in both workflows
- Check repository workflow permissions

---

## 🚀 **Advanced Extensions: Next Level Automation**

Once you've mastered the core automation, try these advanced patterns:

### **1. Multi-Environment Matrix Deployment**
```yaml
strategy:
  matrix:
    environment: [staging, production]
    region: [eastus, westus]
```

### **2. Automated Rollback on Failure**
```yaml
- name: Health Check & Rollback
  run: |
    if ! curl -f http://$SERVICE_IP/health; then
      kubectl rollout undo deployment/product-service -n $NS
      exit 1
    fi
```

### **3. Blue-Green Deployment**
```yaml
- name: Blue-Green Switch
  run: |
    kubectl patch service product-service -p '{"spec":{"selector":{"version":"green"}}}'
```

### **4. Integration with External Systems**
```yaml
- name: Notify Slack
  uses: 8398a7/action-slack@v3
  with:
    status: ${{ job.status }}
    webhook_url: ${{ secrets.SLACK_WEBHOOK }}
```

---

## 📚 **Learning Resources & Further Reading**

### **Concepts Demonstrated**
- **GitOps**: Declarative configuration management
- **Infrastructure as Code**: Terraform integration patterns
- **Microservices**: Service mesh communication
- **DevSecOps**: Secure secret management
- **SRE**: Automated testing and cleanup

### **Related Technologies to Explore**
- **ArgoCD**: GitOps continuous deployment
- **Helm**: Kubernetes package management
- **Prometheus**: Monitoring and alerting
- **Istio**: Service mesh networking
- **Trivy**: Container security scanning

### **Production Considerations**
- Multi-region deployments
- Disaster recovery procedures
- Compliance and audit logging
- Performance monitoring
- Cost optimization

---

## 🤝 **Contributing to This Tutorial**

Help others learn by improving this tutorial:

1. **Fork** the repository
2. **Enhance** documentation or add new automation features
3. **Test** your changes thoroughly
4. **Submit** pull request with clear explanation
5. **Update** this README with your improvements

**Areas for Contribution**:
- Additional testing patterns
- Security enhancements
- Performance optimizations
- More cloud provider integrations
- Advanced monitoring setups

---

## 📄 **License & Acknowledgments**

This educational project is MIT licensed.

**Course Context**: This project was developed for SIT722 Software Deployment and Operation at Deakin University. The base e-commerce application was provided as course material. The innovative automation pipeline, infrastructure integration, and DevOps practices demonstrated here represent significant extensions beyond the base requirements.

**Educational Use**: This tutorial is designed to teach enterprise-grade DevOps automation patterns. Feel free to use, modify, and extend for your learning and teaching needs.

---

**🎓 Completion Achievement: You've learned enterprise-grade DevOps automation patterns used by Fortune 500 companies. These skills directly apply to real-world production environments and represent advanced knowledge in modern software delivery practices.**

## 🔗 **Quick Navigation**
- [Automation Features](#what-youll-learn--replicate)
- [Quick Start](#quick-start-replicate-this-automation)
- [Deep Dive Tutorials](#tutorial-deep-dive-understanding-the-automation)
- [Testing Guide](#complete-testing-guide-verify-your-implementation)
- [Troubleshooting](#troubleshooting-guide-common-issues--solutions)
- [Advanced Extensions](#advanced-extensions-next-level-automation)