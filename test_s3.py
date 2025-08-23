# test_s3.py - Test S3 storage directly

import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw_life_planner.settings')
django.setup()

from django.core.files.storage import get_storage_class
from django.core.files.base import ContentFile

print("Testing S3 Storage...")

# Get the storage class
storage_class = get_storage_class(settings.STATICFILES_STORAGE)
storage = storage_class()

print(f"Storage class: {storage_class}")
print(f"Storage bucket: {getattr(storage, 'bucket_name', 'Not found')}")
print(f"Storage location: {getattr(storage, 'location', 'Not found')}")

# Test saving a file
try:
    test_content = ContentFile(b"Hello from Django S3 test!")
    file_name = storage.save("test.txt", test_content)
    print(f"✅ Successfully saved file: {file_name}")

    # Check if file exists
    if storage.exists(file_name):
        print(f"✅ File exists in storage")
    else:
        print(f"❌ File does not exist in storage")

    # Get the URL
    url = storage.url(file_name)
    print(f"📄 File URL: {url}")

except Exception as e:
    print(f"❌ Error testing S3 storage: {e}")
    import traceback
    traceback.print_exc()
