"""Image uploads for message board posts and announcements.

Images live in the board_image table (pods have no persistent disk) and are
referenced from post bodies as ![alt](/board/images/<token>); see
services/text_format.py for rendering.
"""

import secrets

from Football_Project.extensions import db
from Football_Project.models import BoardImage, GroupMember

MAX_IMAGE_BYTES = 5 * 1024 * 1024

# Only raster formats browsers display inline. No SVG: it can carry script.
_SIGNATURES = (
    (b"\x89PNG\r\n\x1a\n", "image/png"),
    (b"\xff\xd8\xff", "image/jpeg"),
    (b"GIF87a", "image/gif"),
    (b"GIF89a", "image/gif"),
)


class ImageUploadError(ValueError):
    pass


def sniff_content_type(data: bytes) -> str | None:
    """Identify the image type from its leading bytes (never trust the client)."""
    for magic, content_type in _SIGNATURES:
        if data.startswith(magic):
            return content_type
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return "image/webp"
    return None


def strip_jpeg_metadata(data: bytes) -> bytes:
    """Drop APP1 (EXIF/XMP: GPS location, camera serials) and comment segments.

    Pixel data is untouched. If the file doesn't parse as expected it is
    returned unchanged rather than corrupted.
    """
    if not data.startswith(b"\xff\xd8"):
        return data
    out = bytearray(b"\xff\xd8")
    i = 2
    while i + 4 <= len(data):
        if data[i] != 0xFF:
            return data
        marker = data[i + 1]
        if marker == 0xDA:  # start of scan: copy the rest verbatim
            out += data[i:]
            return bytes(out)
        length = int.from_bytes(data[i + 2:i + 4], "big")
        if length < 2 or i + 2 + length > len(data):
            return data
        if marker not in (0xE1, 0xFE):  # keep everything except APP1 and COM
            out += data[i:i + 2 + length]
        i += 2 + length
    return data


def save_image(data: bytes, *, uploader_user_id: int, group_id: int | None) -> BoardImage:
    """Validate and store an uploaded image. Does not commit."""
    if not data:
        raise ImageUploadError("No image received.")
    if len(data) > MAX_IMAGE_BYTES:
        raise ImageUploadError("Image is too large (max 5 MB).")

    content_type = sniff_content_type(data)
    if not content_type:
        raise ImageUploadError("Only PNG, JPEG, GIF or WebP images can be uploaded.")
    if content_type == "image/jpeg":
        data = strip_jpeg_metadata(data)

    image = BoardImage(
        token=secrets.token_urlsafe(16),
        uploader_user_id=uploader_user_id,
        group_id=group_id,
        content_type=content_type,
        byte_size=len(data),
        data=data,
    )
    db.session.add(image)
    return image


def can_view_image(user, image: BoardImage) -> bool:
    """Announcement images (no group) are visible to any logged-in user;
    board images only to active members of that group, or global admins."""
    if image.group_id is None or getattr(user, "is_admin", False):
        return True
    return GroupMember.query.filter_by(
        user_id=user.id, group_id=image.group_id, is_active=True
    ).first() is not None
