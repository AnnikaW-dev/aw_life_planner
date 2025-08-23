# Create test_s3_direct.py and run it

import boto3
import os
from dotenv import load_dotenv

load_dotenv()

def test_s3():
    """Test S3 connection directly with boto3"""

    # Get credentials from .env
    access_key = os.environ.get('AWS_ACCESS_KEY_ID')
    secret_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
    bucket_name = os.environ.get('AWS_STORAGE_BUCKET_NAME')
    region = os.environ.get('AWS_S3_REGION_NAME', 'us-east-1')

    print(f"Testing S3 connection...")
    print(f"Bucket: {bucket_name}")
    print(f"Region: {region}")
    print(f"Access Key: {access_key}")

    try:
        # Create S3 client
        s3 = boto3.client(
            's3',
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name=region
        )

        # Test 1: Check if bucket exists
        print("\n1. Testing bucket access...")
        s3.head_bucket(Bucket=bucket_name)
        print("✅ Bucket exists and is accessible!")

        # Test 2: List bucket contents
        print("\n2. Listing bucket contents...")
        response = s3.list_objects_v2(Bucket=bucket_name, MaxKeys=10)

        if 'Contents' in response:
            print(f"✅ Found {len(response['Contents'])} objects:")
            for obj in response['Contents'][:5]:  # Show first 5
                print(f"   - {obj['Key']} ({obj['Size']} bytes)")
        else:
            print("✅ Bucket is empty (ready for uploads!)")

        # Test 3: Try to upload a test file
        print("\n3. Testing file upload...")
        test_content = "Hello from Django!"
        s3.put_object(
            Bucket=bucket_name,
            Key='test/django-test.txt',
            Body=test_content,
            ACL='public-read'
        )
        print("✅ Test file uploaded successfully!")

        # Test 4: Get the file URL
        url = f"https://{bucket_name}.s3.amazonaws.com/test/django-test.txt"
        print(f"✅ File URL: {url}")

        return True

    except Exception as e:
        print(f"❌ S3 Test failed: {e}")
        return False

if __name__ == "__main__":
    success = test_s3()
    if success:
        print("\n🎉 S3 is working! Let's try collectstatic now.")
    else:
        print("\n💥 S3 connection failed. Check your credentials.")
