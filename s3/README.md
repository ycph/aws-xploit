# S3 KMS Ransomware PoC

This PoC shows how misconfigured AWS S3 and KMS permissions may allow an attacker
to rewrite (re-encrypt) existing S3 objects using a chosen KMS key.

The script performs an in-place S3 copy operation to re-encrypt existing objects.
If S3 Versioning is enabled, previous versions remain intact and can be recovered
by an administrator with sufficient permissions.

> For authorized security testing and research **only**.

## Files

- `s3_kms_ransomware.py` – main PoC script
- `requirements.txt` – Python dependencies

## Usage

Edit the configuration inside the script:

```python
AWS_PROFILE = "default"
BUCKET_NAME = "target-bucket"
KMS_KEY_ARN = "arn:aws:kms:REGION:ACCOUNT-ID:key/KEY-ID"
```

Then run:

```bash
python3 s3_kms_ransomware.py
```

## Requirements

Install dependencies with:

```bash
pip install -r requirements.txt
```

## Security Notes

This PoC demonstrates the impact of:

- Excessive S3 permissions (e.g. `s3:PutObject`, `s3:ListBucket`)
- Weak KMS key policies allowing encryption with attacker-chosen keys
- Missing MFA Delete and weak controls on S3 versioned buckets

Use only in controlled environments where you have explicit permission.
