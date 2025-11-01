# S3 Storage Configuration Guide

**Version:** v1.0  
**Last Updated:** 2025-10-30  
**Last Updated By:** heiko  
**Status:** Active

---

## Overview

This guide explains how to configure S3-compatible storage for different environments (local, dev, staging, production) and providers (MinIO, Azure, Kvant, AWS).

**Key Insight:** S3 API is a **standard protocol** - the same code works with ALL providers! Just change the endpoint URL.

---

## Current Architecture: Already Provider-Agnostic! ✅

**No adapter pattern needed!** Your code uses `boto3`, which speaks the S3 protocol:

```python
# backend/app/api/services/s3_service.py
s3_client = boto3.client(
    's3',
    endpoint_url=settings.S3_ENDPOINT_URL,      # ← Change this per environment
    aws_access_key_id=settings.S3_ACCESS_KEY_ID,
    aws_secret_access_key=settings.S3_SECRET_ACCESS_KEY,
    region_name=settings.S3_REGION
)
```

This **same code** works with:
- ✅ MinIO (local development)
- ✅ Azure Blob Storage (with S3 API)
- ✅ Kvant S3-compatible storage
- ✅ AWS S3
- ✅ Any S3-compatible provider

---

## Environment Configurations

### 🏠 Local Development (MinIO in Docker)

**When:** Running `docker compose up` on your laptop

**Configuration:**
```bash
# .env or docker-compose.yml
S3_ENDPOINT_URL=http://localhost:9000
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin
S3_BUCKET_NAME=swisper-avatars
S3_REGION=us-east-1
```

**MinIO Console:** http://localhost:9001
- Username: `minioadmin`
- Password: `minioadmin`

**Pros:**
- ✅ No external dependencies
- ✅ Fast
- ✅ Free
- ✅ Data persists in Docker volume

**Cons:**
- ❌ Only accessible locally
- ❌ Lost on `docker compose down -v`

---

### 🔧 Development/Staging (Azure Blob Storage)

**When:** Shared dev/staging environment on Azure

**Status:** ✅ **CONFIGURED** - Using Azure Blob Storage with S3-compatible API

**Prerequisites:**
1. Azure Storage Account with S3-compatible API enabled (configured by DevOps)
2. Access keys from Azure Portal

**Configuration:**
```bash
# helm/helvetiq-backend/dev.yaml
S3_ENDPOINT_URL: "https://<storage-account>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<azure-storage-account-name>"
S3_SECRET_ACCESS_KEY: "<azure-access-key>"
S3_BUCKET_NAME: "swisper-avatars-dev"
S3_REGION: "westeurope"

# helm/helvetiq-backend/staging.yaml
S3_ENDPOINT_URL: "https://<storage-account>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<azure-storage-account-name>"
S3_SECRET_ACCESS_KEY: "<azure-access-key>"
S3_BUCKET_NAME: "swisper-avatars-staging"
S3_REGION: "westeurope"
```

**How to Get Credentials (For DevOps):**
1. Go to **Azure Portal** → **Storage Accounts**
2. Select the storage account (or create new one)
3. Go to **Access Keys** → Copy:
   - Storage Account Name (use as `S3_ACCESS_KEY_ID`)
   - Key1 or Key2 (use as `S3_SECRET_ACCESS_KEY`)
4. Endpoint URL format: `https://<storage-account-name>.blob.core.windows.net`

**Pros:**
- ✅ Shared across team
- ✅ Persistent (managed by Azure)
- ✅ Consistent with PostgreSQL (Azure Managed DB)
- ✅ S3-compatible API (boto3 works transparently)
- ✅ Cost-effective for dev/staging

**Cons:**
- ❌ Costs money (minimal for dev/staging volumes)
- ❌ Requires Azure account

---

### 🚀 Production (Kvant Hosting)

**When:** Deployed to Kvant hosting partner

**Prerequisites:**
1. Get S3 endpoint from Kvant
2. Get access credentials from Kvant

**Configuration:**
```bash
# .env for production at Kvant
S3_ENDPOINT_URL=https://s3.kvant.cloud  # Get actual from Kvant
S3_ACCESS_KEY_ID=<kvant-access-key>
S3_SECRET_ACCESS_KEY=<kvant-secret-key>
S3_BUCKET_NAME=swisper-avatars-prod
S3_REGION=eu-central-1
```

**Setup Steps:**
1. Contact Kvant support: "We need S3-compatible storage"
2. They provide:
   - S3 endpoint URL
   - Access Key ID
   - Secret Access Key
3. Update production `.env` with values

**Pros:**
- ✅ Same hosting as your app
- ✅ Low latency
- ✅ Integrated billing

**Cons:**
- ❌ Vendor-specific endpoint (but standard S3 API)

---

## Configuration Per Environment

### Summary Table

| Environment | Provider | Endpoint | When to Set Up |
|-------------|----------|----------|----------------|
| **Local Dev** | MinIO | `http://localhost:9000` | ✅ Already works (docker-compose) |
| **CI/CD Tests** | MinIO | `http://minio:9000` | ✅ Already works (docker-compose) |
| **Dev/Staging** | Azure Blob | `https://<account>.blob.core.windows.net` | ✅ **CONFIGURED** (awaiting credentials from DevOps) |
| **Production** | Kvant S3 | `https://s3.kvant.cloud` (TBD) | ⚠️ **When migrating to Kvant** |

---

## Environment Variable Reference

### All S3 Settings (`.env` file)

```bash
# S3 Endpoint - CHANGE THIS per environment
S3_ENDPOINT_URL=http://localhost:9000

# Access Credentials - CHANGE THIS per environment
S3_ACCESS_KEY_ID=minioadmin
S3_SECRET_ACCESS_KEY=minioadmin

# Bucket Name - Can be same or different per environment
S3_BUCKET_NAME=swisper-avatars

# Region - Ignored by MinIO, required for AWS/Azure
S3_REGION=us-east-1
```

### How Pydantic Reads These

```python
# backend/app/core/config.py
class Settings(BaseSettings):
    S3_ENDPOINT_URL: str = "http://localhost:9000"  # Default
    S3_ACCESS_KEY_ID: str | None = None
    # ...
    
    # Pydantic AUTOMATICALLY reads from:
    # 1. Environment variables
    # 2. .env file
    # 3. Falls back to defaults
```

---

## Migration Path to Kvant

### Step 1: Get Kvant S3 Details

Contact Kvant support:
> "We need S3-compatible storage for avatar icons and file uploads. Please provide:
> - S3 endpoint URL
> - Access Key ID  
> - Secret Access Key
> - Recommended region"

### Step 2: Test Connection Locally

```bash
# Test Kvant S3 from your laptop
export S3_ENDPOINT_URL=https://s3.kvant.cloud  # From Kvant
export S3_ACCESS_KEY_ID=<kvant-key>
export S3_SECRET_ACCESS_KEY=<kvant-secret>
export S3_BUCKET_NAME=swisper-avatars-prod

# Test bucket creation
docker compose exec backend python -m app.core.s3_bucket_init
```

### Step 3: Update Production .env

```bash
# Production .env at Kvant
S3_ENDPOINT_URL=https://s3.kvant.cloud
S3_ACCESS_KEY_ID=<kvant-key>
S3_SECRET_ACCESS_KEY=<kvant-secret>
S3_BUCKET_NAME=swisper-avatars-prod
S3_REGION=eu-central-1
```

### Step 4: Deploy

```bash
# Deploy to Kvant
# Bucket will be auto-created on first startup!
# Your code doesn't change - just the env vars
```

---

## Why No Adapter Pattern Needed

### S3 API is a Standard

```
┌─────────────────────────────────────┐
│  Your Application (boto3 client)   │
│                                     │
│  s3_client.upload_fileobj(...)     │  ← Same code!
└───────────────┬─────────────────────┘
                │
                │ S3 API Protocol (HTTP REST)
                │
        ┌───────┴────────┐
        │                │
    ┌───▼────┐      ┌───▼────┐      ┌───▼────┐
    │ MinIO  │      │ Azure  │      │ Kvant  │
    │        │      │  Blob  │      │   S3   │
    └────────┘      └────────┘      └────────┘
      Local           Dev/Stg          Prod
```

**All speak the same protocol!** Just point to different endpoint.

### Comparison: If You Needed Adapters

```python
# ❌ BAD: Different code per provider
if provider == "azure":
    azure_client.upload_blob(...)
elif provider == "kvant":
    kvant_client.put_object(...)
elif provider == "aws":
    aws_client.upload_file(...)

# ✅ GOOD: Same code, different endpoint
s3_client = boto3.client('s3', endpoint_url=settings.S3_ENDPOINT_URL)
s3_client.upload_fileobj(...)  # Works everywhere!
```

---

## Azure Blob Storage Setup (If Needed)

### Prerequisites

1. Azure subscription
2. Storage Account created

### Enable S3-Compatible API

**Option 1: Azure Portal**
1. Go to Azure Portal → Storage Accounts
2. Select your storage account
3. Settings → Configuration
4. Enable "Hierarchical namespace" (Data Lake Gen2)
5. This enables S3-compatible API

**Option 2: Azure CLI**
```bash
az storage account create \
  --name swisperavatarsdev \
  --resource-group helvetiq-dev \
  --location westeurope \
  --sku Standard_LRS \
  --enable-hierarchical-namespace true
```

### Get Credentials

```bash
# Get access keys
az storage account keys list \
  --account-name swisperavatarsdev \
  --resource-group helvetiq-dev \
  --output table

# Output:
# KeyName    Value
# ---------  -------------------------------------
# key1       <your-access-key>
# key2       <your-secret-key>
```

### Configuration

```bash
# .env for Azure
S3_ENDPOINT_URL=https://swisperavatarsdev.blob.core.windows.net
S3_ACCESS_KEY_ID=<key1>
S3_SECRET_ACCESS_KEY=<key2>
S3_BUCKET_NAME=swisper-avatars-dev
S3_REGION=westeurope
```

---

## Recommendations

### For Local Development
✅ **Use MinIO** (already configured in docker-compose)
- Zero setup
- Free
- Fast

### For Shared Dev/Staging
⚠️ **Only if needed:**
- Multiple developers need shared avatars?
  - **Yes** → Use Azure Blob Storage
  - **No** → Everyone uses local MinIO

### For Production
✅ **Use Kvant S3** (when available)
- Same datacenter as your app
- Low latency
- Integrated with hosting

---

## Testing Configuration

### Test Current Setup

```bash
# Check current config
docker compose exec backend python -c "
from app.core.config import settings
print(f'Endpoint: {settings.S3_ENDPOINT_URL}')
print(f'Bucket: {settings.S3_BUCKET_NAME}')
print(f'Credentials: {\"Yes\" if settings.S3_ACCESS_KEY_ID else \"No\"}')
"
```

### Test Upload

```python
# backend/test_s3_upload.py
from app.api.services.s3_service import s3_service
import io

# Create test image
test_file = io.BytesIO(b'fake image data')

# Upload
url = s3_service.upload_avatar_icon(
    user_id="test-user",
    avatar_id="test-avatar",
    file=test_file,
    content_type="image/png"
)

print(f"✅ Upload successful: {url}")
```

---

## Troubleshooting

### Issue: "S3 credentials not configured"

**Solution:** Set environment variables:
```bash
export S3_ACCESS_KEY_ID=minioadmin
export S3_SECRET_ACCESS_KEY=minioadmin
```

### Issue: "Bucket does not exist" on AWS/Azure

**Cause:** Bucket auto-creation might fail with permissions

**Solution:** Manually create bucket first:
```bash
# AWS
aws s3 mb s3://swisper-avatars-prod

# Azure
az storage container create \
  --name swisper-avatars-prod \
  --account-name swisperavatarsdev
```

---

## Summary

✅ **No adapter pattern needed** - S3 API is standard
✅ **Configuration via .env** - Already implemented
✅ **Works with any provider** - MinIO, Azure, Kvant, AWS
✅ **Auto-creates buckets** - Safe and idempotent

**Next steps:**
1. ✅ Local dev: Already working (MinIO)
2. ⚠️ Shared dev/staging: Set up Azure **only if needed**
3. ⚠️ Production: Get Kvant S3 details **when migrating**

---

**Questions?** See `docs/guides/s3_bucket_initialization_guide.md` for more details.

