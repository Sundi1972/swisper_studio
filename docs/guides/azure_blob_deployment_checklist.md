# Azure Blob Storage Deployment Checklist

**Version:** v1.0  
**Last Updated:** 2025-10-30  
**Last Updated By:** heiko  
**Status:** Active

---

## Changelog

### v1.0 - 2025-10-30
- Initial creation
- DevOps checklist for Azure Blob Storage setup
- Credential format specification

---

## Overview

This checklist is for DevOps to set up Azure Blob Storage for S3-compatible file storage (avatar icons, attachments) in dev and staging environments.

**Status:** ⚠️ Awaiting Azure Blob Storage credentials from DevOps

---

## Required Information from DevOps

### What We Need

Please provide the following for **both dev and staging**:

```yaml
# For DEV Environment
STORAGE_ACCOUNT_NAME: "<azure-storage-account-name>"
ENDPOINT_URL: "https://<storage-account-name>.blob.core.windows.net"
ACCESS_KEY: "<key1-or-key2-from-azure-portal>"
REGION: "westeurope"  # or your preferred Azure region

# For STAGING Environment
STORAGE_ACCOUNT_NAME: "<azure-storage-account-name>"
ENDPOINT_URL: "https://<storage-account-name>.blob.core.windows.net"
ACCESS_KEY: "<key1-or-key2-from-azure-portal>"
REGION: "westeurope"
```

---

## Azure Portal Setup (For DevOps)

### Step 1: Create Storage Account (or use existing)

1. Go to **Azure Portal** → **Storage Accounts**
2. Create new storage account (or select existing)
   - Name: Choose a name (e.g., `swisperdevfiles`, `swissperstaging`)
   - Region: `West Europe` (or preferred)
   - Performance: **Standard** (sufficient for dev/staging)
   - Redundancy: **LRS** (Locally-redundant storage, cost-effective for non-production)
3. Create the storage account

### Step 2: Enable S3-Compatible API

**Important:** Ensure the storage account supports S3 API:
- Azure Blob Storage natively supports S3 API via `blob.core.windows.net` endpoint
- No additional configuration needed
- Uses standard `boto3` S3 client

### Step 3: Get Access Keys

1. Go to **Storage Account** → **Access Keys**
2. Copy:
   - **Storage account name** (use as `S3_ACCESS_KEY_ID`)
   - **Key1** or **Key2** (use as `S3_SECRET_ACCESS_KEY`)
3. Endpoint URL format: `https://<storage-account-name>.blob.core.windows.net`

### Step 4: Container (Bucket) Creation

**Note:** Containers will be **auto-created** by the backend on first deployment:
- Dev: `swisper-avatars-dev`
- Staging: `swisper-avatars-staging`

No manual creation needed - the prestart script handles this.

---

## Where to Update Credentials

### Dev Environment

**File:** `helm/helvetiq-backend/dev.yaml`

Replace these placeholder values (lines 36-42):

```yaml
# S3/Azure Blob Storage Configuration
# TODO: Replace with actual Azure credentials from DevOps
S3_ENDPOINT_URL: "https://<AZURE_STORAGE_ACCOUNT>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<AZURE_STORAGE_ACCOUNT_NAME>"
S3_SECRET_ACCESS_KEY: "<AZURE_ACCESS_KEY>"
S3_BUCKET_NAME: "swisper-avatars-dev"
S3_REGION: "westeurope"
```

**With:**

```yaml
# S3/Azure Blob Storage Configuration (UPDATED by DevOps)
S3_ENDPOINT_URL: "https://<actual-storage-account>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<actual-storage-account-name>"
S3_SECRET_ACCESS_KEY: "<actual-key-from-azure>"
S3_BUCKET_NAME: "swisper-avatars-dev"
S3_REGION: "westeurope"
```

### Staging Environment

**File:** `helm/helvetiq-backend/staging.yaml`

Replace these placeholder values (lines 36-42):

```yaml
# S3/Azure Blob Storage Configuration
# TODO: Replace with actual Azure credentials from DevOps
S3_ENDPOINT_URL: "https://<AZURE_STORAGE_ACCOUNT>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<AZURE_STORAGE_ACCOUNT_NAME>"
S3_SECRET_ACCESS_KEY: "<AZURE_ACCESS_KEY>"
S3_BUCKET_NAME: "swisper-avatars-staging"
S3_REGION: "westeurope"
```

**With:**

```yaml
# S3/Azure Blob Storage Configuration (UPDATED by DevOps)
S3_ENDPOINT_URL: "https://<actual-storage-account>.blob.core.windows.net"
S3_ACCESS_KEY_ID: "<actual-storage-account-name>"
S3_SECRET_ACCESS_KEY: "<actual-key-from-azure>"
S3_BUCKET_NAME: "swisper-avatars-staging"
S3_REGION: "westeurope"
```

---

## Testing Credentials Locally (Optional)

Before deploying to dev/staging, test credentials from your laptop:

```bash
# Update local .env with Azure credentials
S3_ENDPOINT_URL=https://<storage-account>.blob.core.windows.net
S3_ACCESS_KEY_ID=<storage-account-name>
S3_SECRET_ACCESS_KEY=<access-key>
S3_BUCKET_NAME=swisper-avatars-dev
S3_REGION=westeurope

# Start backend
docker compose up -d backend

# Test bucket creation
docker compose exec backend python -c "
from app.core.s3_bucket_init import ensure_s3_buckets
ensure_s3_buckets()
print('✅ Azure Blob Storage connected successfully!')
"
```

**Expected output:**
```
INFO: Creating bucket: swisper-avatars-dev
✅ Azure Blob Storage connected successfully!
```

Or if bucket already exists:
```
INFO: Bucket swisper-avatars-dev already exists
✅ Azure Blob Storage connected successfully!
```

---

## Deployment Steps

### Step 1: Update Helm Values

Update the files with actual Azure credentials (see above).

### Step 2: Deploy to Dev

```bash
helm upgrade --install helvetiq-backend ./helm/helvetiq-backend -f ./helm/helvetiq-backend/dev.yaml
```

**The backend will automatically:**
1. Connect to Azure Blob Storage
2. Create container `swisper-avatars-dev` (if it doesn't exist)
3. Set public read policy
4. Start serving requests

### Step 3: Verify Dev Deployment

Check backend logs for successful bucket initialization:

```bash
kubectl logs -n dev deployment/helvetiq-backend --tail=100 | grep "S3\|bucket"
```

**Expected log entries:**
```
INFO: S3Service initialized with endpoint: https://<storage-account>.blob.core.windows.net, bucket: swisper-avatars-dev
INFO: Bucket swisper-avatars-dev verified/created successfully
```

### Step 4: Deploy to Staging

```bash
helm upgrade --install helvetiq-backend ./helm/helvetiq-backend -f ./helm/helvetiq-backend/staging.yaml
```

### Step 5: Verify Staging Deployment

```bash
kubectl logs -n staging deployment/helvetiq-backend --tail=100 | grep "S3\|bucket"
```

---

## Verification Checklist

After deployment, verify:

- [ ] **Backend starts successfully** (no S3 errors in logs)
- [ ] **Bucket created in Azure Portal**
  - Go to Storage Account → Containers
  - Verify `swisper-avatars-dev` and `swisper-avatars-staging` exist
- [ ] **Upload avatar test**
  - Go to dev/staging frontend: `https://dev.swisper.ai` or `https://staging.swisper.ai`
  - Create avatar, upload icon
  - Verify icon appears in UI
  - Check Azure Portal → Storage Account → Container → Blob exists
- [ ] **URL format correct**
  - Icon URL should be: `https://<storage-account>.blob.core.windows.net/swisper-avatars-dev/users/{user_id}/{avatar_id}/icon.png`

---

## Troubleshooting

### Issue: "S3 credentials not configured"

**Symptom:**
```
WARNING: S3 credentials not configured - S3 uploads will fail
```

**Solution:**
- Verify `S3_ACCESS_KEY_ID` and `S3_SECRET_ACCESS_KEY` are set in Helm values
- Check they're not empty or still placeholder values (`<AZURE_...>`)

---

### Issue: "Access Denied" or "403 Forbidden"

**Symptom:**
```
ERROR: S3 upload failed: An error occurred (AccessDenied) when calling the PutObject operation
```

**Solution:**
1. Verify access key is correct (copy from Azure Portal again)
2. Check storage account allows public access (needed for avatar icons)
3. Verify storage account is in same Azure subscription

---

### Issue: "Bucket creation failed"

**Symptom:**
```
ERROR: Failed to create bucket: swisper-avatars-dev
```

**Solution:**
1. Check if container name is already taken (must be globally unique in Azure)
2. Try different container name: `swisper-avatars-dev-<unique-suffix>`
3. Update `S3_BUCKET_NAME` in Helm values

---

### Issue: "Endpoint URL incorrect"

**Symptom:**
```
ERROR: Could not connect to the endpoint URL
```

**Solution:**
- Verify endpoint URL format: `https://<storage-account-name>.blob.core.windows.net`
- No trailing slash
- Must include `https://`
- Storage account name must match Azure Portal

---

## Security Notes

### Access Keys
- **Keep access keys secret** - never commit to Git
- Rotate keys periodically (Azure Portal → Access Keys → Regenerate)
- Use Key1 or Key2 (you can rotate one while the other is active)

### Container Access
- Containers (buckets) are configured with **public read** access for avatar icons
- Write access requires valid access key (secured)
- Consider using Azure SAS tokens for more granular control (future enhancement)

---

## Cost Estimation (Dev/Staging)

**Storage:**
- First 50 TB: ~$0.0184 per GB/month
- Expected usage: <1 GB for dev/staging
- **Est. cost: ~$0.02 - $0.05 per month**

**Transactions:**
- 10,000 write operations: ~$0.10
- 10,000 read operations: ~$0.01
- **Est. cost: <$1 per month for dev/staging combined**

**Total: <$2/month for both dev and staging** (negligible)

---

## Related Documentation

- **S3 Storage Configuration Guide:** `docs/guides/s3_storage_configuration_guide.md`
- **S3 Bucket Initialization:** `docs/guides/s3_bucket_initialization_guide.md`
- **Backend Config:** `backend/app/core/config.py` (S3 settings)
- **S3 Service:** `backend/app/api/services/s3_service.py`

---

## Contact

**Questions?** Contact development team or see related documentation above.

---

**Next Steps:** Awaiting Azure Blob Storage credentials from DevOps to complete deployment.

