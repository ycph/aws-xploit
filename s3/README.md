# S3 KMS Ransomware PoC

This repository contains a proof-of-concept that demonstrates how overly
permissive S3 and KMS policies can allow an attacker to re-encrypt every object
in a bucket with a chosen KMS key. The script performs in-place S3 copies to
rewrite encryption metadata, leaving previous versions untouched when versioning
is enabled.

> **Warning:** Only run this code in environments where you have explicit
> authorization.

## Requirements

Install the Python dependencies before running the script:

```bash
pip install -r requirements.txt
```

## Usage

Run the script with the minimal required options:

```bash
python3 s3_kms_ransomware.py --bucket TARGET_BUCKET \
    --kms-key-arn arn:aws:kms:REGION:ACCOUNT:key/ID \
    [--profile PROFILE] [--prefix PREFIX] [--dry-run] [--yes]
```

After printing the configuration, the script prompts for confirmation (unless
you pass `--yes`). It then walks every object, copying it in-place with the
chosen KMS key. When `--dry-run` is set, it only prints which keys would be
copied.

### Options

- `--bucket`, `-b` – target S3 bucket (required)
- `--kms-key-arn`, `-k` – KMS key ARN to use for server-side encryption
- `--profile`, `-p` – AWS CLI profile name (defaults to `default`)
- `--prefix` – limit actions to objects that start with this prefix
- `--dry-run` – list objects without modifying them
- `--yes` – skip the interactive confirmation prompt

### Example

```bash
python3 s3_kms_ransomware.py \
    --bucket production-data \
    --kms-key-arn arn:aws:kms:us-east-1:123456789012:key/abc123 \
    --profile red-team \
    --prefix secrets/ \
    --dry-run
```

This example is a non-destructive dry run that lists every object under
`secrets/` that would be re-encrypted.

## Security notes

- Excessive S3 permissions such as `s3:PutObject` and `s3:ListBucket` are
  sufficient to perform the rewrite.
- Weak KMS key policies that allow encryption with an attacker-controlled key
  are required for this PoC to succeed.
- S3 Versioning preserves older versions if enabled, so an administrator with
  proper permissions can recover from this attack.

Use this script for responsible security testing only.
