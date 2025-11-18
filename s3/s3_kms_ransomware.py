#!/usr/bin/env python3
"""
S3 KMS re-encryption PoC.

This short script uses boto3 to walk through one bucket and reapply server-side
encryption with a provided KMS key. It prints a few status messages, optionally
executes a dry run, and requires confirmation before making any changes.
"""

import argparse
import sys

import boto3
import botocore.exceptions


def parse_args():
    parser = argparse.ArgumentParser(
        description="Re-encrypt objects in an S3 bucket with the supplied KMS key."
    )
    parser.add_argument("--bucket", "-b", required=True, help="Target S3 bucket.")
    parser.add_argument(
        "--kms-key-arn", "-k", required=True, help="KMS key ARN to apply."
    )
    parser.add_argument("--profile", "-p", default="default", help="AWS CLI profile.")
    parser.add_argument(
        "--prefix", default="", help="Limit the work to objects under this prefix."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Report which objects would be updated instead of writing.",
    )
    parser.add_argument(
        "--yes",
        action="store_true",
        help="Skip the confirmation prompt (dangerous).",
    )
    return parser.parse_args()


args = parse_args()

print(f"Connecting with profile: {args.profile}")
print(f"Bucket: {args.bucket}")
print(f"KMS key: {args.kms_key_arn}")
print(f"Prefix: {args.prefix or 'none'}")
print(f"Dry run: {args.dry_run}")

if not args.yes:
    prompt = (
        "This script will copy every matching object inside the bucket using the "
        f"KMS key {args.kms_key_arn}. Proceed? [y/N]: "
    )
    answer = input(prompt).strip().lower()
    if answer not in {"y", "yes"}:
        print("Aborting.")
        sys.exit(0)

try:
    session = boto3.Session(profile_name=args.profile)
except botocore.exceptions.ProfileNotFound as exc:
    print(f"Profile not found: {exc}")
    sys.exit(1)

s3 = session.resource("s3")
client = session.client("s3")
paginator = client.get_paginator("list_objects_v2")

list_kwargs = {"Bucket": args.bucket}
if args.prefix:
    list_kwargs["Prefix"] = args.prefix

total = 0

try:
    pages = paginator.paginate(**list_kwargs)
except botocore.exceptions.ClientError as exc:
    print(f"Unable to list objects: {exc}")
    sys.exit(1)

for page in pages:
    for obj in page.get("Contents", []):
        key = obj["Key"]
        total += 1
        if args.dry_run:
            print("[DRY-RUN]", key)
            continue

        try:
            s3.Object(args.bucket, key).copy_from(
                CopySource={"Bucket": args.bucket, "Key": key},
                ExtraArgs={
                    "ServerSideEncryption": "aws:kms",
                    "SSEKMSKeyId": args.kms_key_arn,
                },
            )
            print("[OK]", key)
        except botocore.exceptions.ClientError as exc:
            print("[ERROR]", key, exc)

print("Done. Total objects handled:", total)
sys.exit(0)
