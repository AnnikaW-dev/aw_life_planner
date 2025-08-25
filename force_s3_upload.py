# force_s3_upload.py - Manually upload static files to S3

import os
import django

from django.core.files.base import ContentFile
from django.contrib.staticfiles import finders
from storages.backends.s3boto3 import S3Boto3Storage

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'aw_life_planner.settings')
django.setup()


# Create S3 storage directly
class TempStaticStorage(S3Boto3Storage)
    location = 'static'
    default_acl = 'public-read'
    file_overwrite = True


storage = TempStaticStorage()

print(f"🔍 Using S3 storage")
print(f"🔍 Bucket: {getattr(storage, 'bucket_name', 'Not found')}")
print(f"🔍 Location: {getattr(storage, 'location', 'Not found')}")

# Find all static files
static_files = []
for finder in finders.get_finders():
    for path, storage_obj in finder.list(['CVS', '.*', '*~']):
        static_files.append((path, finder.find(path)))

print(f"📁 Found {len(static_files)} static files")

# Upload each file to S3
uploaded_count = 0
for relative_path, absolute_path in static_files:
    if absolute_path and os.path.exists(absolute_path):
        try:
            with open(absolute_path, 'rb') as f:
                file_content = ContentFile(f.read())

            # Save to S3
            saved_name = storage.save(relative_path, file_content)
            print(f"✅ Uploaded: {relative_path}")
            uploaded_count += 1

        except Exception as e:
            print(f"❌ Error uploading {relative_path}: {e}")
    else:
        print(f"⚠️  File not found: {absolute_path}")

print(f"\n🎉 Upload complete! {uploaded_count} files uploaded to S3")
print(f"🌐 Your static files should be available at:"
      f" https://{storage.bucket_name}.s3.amazonaws.com/static/")
