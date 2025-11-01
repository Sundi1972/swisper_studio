# S3/MinIO Bucket Initialization Guide

**Version:** v1.0  
**Last Updated:** 2025-10-30  
**Last Updated By:** heiko  
**Status:** Active

---

## Changelog

### v1.0 - 2025-10-30
- Initial creation
- Added automated bucket initialization
- Documented safety and idempotency

---

## Overview

This guide explains how S3/MinIO buckets are automatically initialized for avatar icons and other file storage, ensuring they exist across all environments (dev, CI/CD, production).

---

## Current Configuration

### Bucket Name

**`swisper-avatars`** - Configured in `backend/app/core/config.py`

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `S3_ENDPOINT_URL` | `https://s3.amazonaws.com` | S3 endpoint (MinIO or AWS) |
| `S3_ACCESS_KEY_ID` | None | S3 access key |
| `S3_SECRET_ACCESS_KEY` | None | S3 secret key |
| `S3_BUCKET_NAME` | `swisper-avatars` | Bucket for avatar icons |
| `S3_REGION` | `eu-central-1` | AWS region |

### Docker Compose (Development)

```yaml
minio:
  image: minio/minio:latest
  ports:
    - "9000:9000"   # S3 API
    - "9001:9001"   # Console UI
  environment:
    MINIO_ROOT_USER: minioadmin
    MINIO_ROOT_PASSWORD: minioadmin

backend:
  environment:
    - S3_ENDPOINT_URL=http://minio:9000
    - S3_ACCESS_KEY_ID=minioadmin
    - S3_SECRET_ACCESS_KEY=minioadmin
    - S3_BUCKET_NAME=swisper-avatars
```

---

## How It Works

### Automated Initialization

**On every deployment/startup**, `backend_pre_start.py` calls `ensure_s3_buckets()`:

```
1. Application starts
   └─> prestart.sh runs
   └─> backend_pre_start.py executes
   └─> ensure_s3_buckets() called

2. Check if bucket exists
   ├─> Bucket exists? 
   │   └─> ✅ Skip (existing data untouched)
   └─> Bucket missing?
       └─> ✅ Create bucket
       └─> ✅ Set public read policy (MinIO only)

3. Application continues starting
```

---

## 🛡️ Safety: Why This Won't Delete Data

### Question: Will bucket initialization delete my production data?

**Answer: NO! Bucket creation is idempotent.**

```python
# Pseudocode of what happens
if bucket_exists("swisper-avatars"):
    logger.info("Bucket already exists - skipping")
    # ✅ EXISTING DATA IS UNTOUCHED
    return
else:
    create_bucket("swisper-avatars")
    logger.info("Bucket created")
```

**Key Safety Features:**
- ✅ **HEAD check first** - Checks if bucket exists before creating
- ✅ **No delete operations** - Only creates, never deletes
- ✅ **Idempotent** - Safe to run 1000 times
- ✅ **Existing objects preserved** - Files in bucket are never touched

---

## Environments

### Development (Docker Compose)

**Automatic:** Bucket created on `docker compose up`

```bash
docker compose up -d
# prestart creates bucket automatically
# Check MinIO console: http://localhost:9001
#   Username: minioadmin
#   Password: minioadmin
```

### CI/CD (Tests)

**Automatic:** Bucket created before tests run

```bash
# In CI pipeline
docker compose up -d
docker compose exec backend pytest
# Bucket exists, tests can upload/download
```

### Production (AWS S3 or MinIO)

**Automatic:** Bucket created on first deployment

**Two scenarios:**

#### Scenario 1: Bucket doesn't exist yet (first deployment)
```
1. Deploy application
2. prestart.sh runs
3. ensure_s3_buckets() creates bucket
4. Application starts
5. ✅ Bucket ready for use
```

#### Scenario 2: Bucket already exists (subsequent deployments)
```
1. Deploy application
2. prestart.sh runs
3. ensure_s3_buckets() checks bucket
4. Bucket exists → skips creation
5. ✅ Existing data untouched
6. Application starts
```

---

## Manual Operations

### Check if Bucket Exists

**MinIO (Development):**
```bash
# Via MinIO Console
open http://localhost:9001
# Username: minioadmin, Password: minioadmin

# Via AWS CLI
aws --endpoint-url http://localhost:9000 s3 ls
# Should show: swisper-avatars
```

**AWS S3 (Production):**
```bash
aws s3 ls
# Should show: swisper-avatars
```

### Manually Create Bucket

**Only needed if you want to pre-create before deployment:**

```bash
# MinIO (Development)
aws --endpoint-url http://localhost:9000 \
    s3 mb s3://swisper-avatars

# AWS S3 (Production)
aws s3 mb s3://swisper-avatars --region eu-central-1
```

### Test Upload

```python
# backend/app/core/test_s3.py
from app.core.s3_bucket_init import ensure_s3_buckets
from app.api.services.s3_service import s3_service

# Ensure bucket exists
ensure_s3_buckets()

# Test upload (requires actual file)
with open('test.png', 'rb') as f:
    url = s3_service.upload_avatar_icon(
        user_id="test-user-123",
        avatar_id="test-avatar-456",
        file=f,
        content_type="image/png"
    )
    print(f"Uploaded: {url}")
```

---

## Troubleshooting

### Issue 1: "Bucket does not exist" errors

**Symptoms:** Avatar upload fails with 404/NoSuchBucket

**Cause:** Bucket not initialized

**Solution:**
```bash
# Check prestart logs
docker compose logs backend | grep "S3 bucket"

# Should see:
# "Creating S3 bucket: swisper-avatars"
# OR
# "S3 bucket 'swisper-avatars' already exists"

# If not, manually run:
docker compose exec backend python -m app.core.s3_bucket_init
```

### Issue 2: "Access Denied" errors

**Symptoms:** Bucket operations fail with 403

**Cause:** Invalid credentials

**Solution:**
```bash
# Check environment variables
docker compose exec backend env | grep S3

# Should show:
# S3_ACCESS_KEY_ID=minioadmin
# S3_SECRET_ACCESS_KEY=minioadmin
# S3_ENDPOINT_URL=http://minio:9000

# Fix in docker-compose.yml or .env file
```

### Issue 3: "Bucket creation skipped" but bucket doesn't exist

**Symptoms:** Logs say bucket exists but operations fail

**Cause:** Permission issue or stale state

**Solution:**
```bash
# Manually create bucket
docker compose exec backend python -c "
from app.core.s3_bucket_init import ensure_s3_buckets
ensure_s3_buckets()
"

# Or via MinIO console: http://localhost:9001
```

---

## Configuration Override

### Change Bucket Name (via .env)

**File:** `.env` (create if doesn't exist)

```bash
# .env
S3_BUCKET_NAME=my-custom-bucket-name
```

**Restart:**
```bash
docker compose down
docker compose up -d
# New bucket name will be used
```

### Use AWS S3 Instead of MinIO

**File:** `.env`

```bash
# .env
S3_ENDPOINT_URL=https://s3.amazonaws.com
S3_ACCESS_KEY_ID=AKIAIOSFODNN7EXAMPLE
S3_SECRET_ACCESS_KEY=wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
S3_BUCKET_NAME=swisper-avatars-prod
S3_REGION=eu-central-1
```

---

## Files

```
backend/
├── app/
│   ├── core/
│   │   ├── config.py                # S3 settings
│   │   └── s3_bucket_init.py        # ← Bucket initialization logic
│   ├── api/
│   │   └── services/
│   │       └── s3_service.py        # Upload/delete operations
│   └── backend_pre_start.py         # Calls ensure_s3_buckets()
│
└── docker-compose.yml               # MinIO configuration
```

---

## Related Documentation

- **S3 Service:** `backend/app/api/services/s3_service.py`
- **Avatar Routes:** `backend/app/api/routes/avatars.py`
- **Spec:** `docs/specs/spec_onboarding_preferences_and_avatar_v1.md` Section 6.3

---

**Questions?** See AGENTS.md or ask in dev channel.

