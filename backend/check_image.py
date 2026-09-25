from database.db import SessionLocal, init_db
from database.models import Content

init_db()
db = SessionLocal()

# Get the image content (Rahul Kulkarni entry)
image_content = db.query(Content).filter(Content.title == 'Rahul Kulkarni').first()

if image_content:
    print(f'Title: {image_content.title}')
    print(f'Content Type: {image_content.content_type}')
    print(f'Has raw_content: {bool(image_content.raw_content)}')
    print(f'Raw content length: {len(image_content.raw_content) if image_content.raw_content else 0}')

    if image_content.raw_content:
        first_part = image_content.raw_content[:200]
        print(f'First 200 chars: {first_part}')
        print(f'Is base64 data URI: {image_content.raw_content.startswith("data:")}')
        print(f'Is JPEG base64: {image_content.raw_content.startswith("/9j")}')

    print(f'Metadata: {image_content.content_metadata}')
else:
    print('No image content found')
    # List all content
    all_content = db.query(Content).all()
    print(f'\nAll content items: {len(all_content)}')
    for c in all_content:
        print(f'  - {c.title} ({c.content_type})')

db.close()
