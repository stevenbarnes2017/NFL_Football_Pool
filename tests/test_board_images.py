import unittest

from Football_Project.services.board_images import (
    MAX_IMAGE_BYTES,
    ImageUploadError,
    sniff_content_type,
    strip_jpeg_metadata,
)


def _segment(marker, payload):
    return b"\xff" + bytes([marker]) + (len(payload) + 2).to_bytes(2, "big") + payload


JPEG_WITH_EXIF = (
    b"\xff\xd8"
    + _segment(0xE0, b"JFIF\x00\x01\x01")
    + _segment(0xE1, b"Exif\x00\x00GPS-LAT-LON")
    + _segment(0xFE, b"comment")
    + _segment(0xDB, b"\x00" * 65)
    + b"\xff\xda\x00\x08scan-data\xff\xd9"
)


class SniffTests(unittest.TestCase):
    def test_known_types(self):
        self.assertEqual(sniff_content_type(b"\x89PNG\r\n\x1a\n...."), "image/png")
        self.assertEqual(sniff_content_type(JPEG_WITH_EXIF), "image/jpeg")
        self.assertEqual(sniff_content_type(b"GIF89a...."), "image/gif")
        self.assertEqual(sniff_content_type(b"RIFF\x00\x00\x00\x00WEBPVP8 "), "image/webp")

    def test_rejects_svg_html_and_junk(self):
        for data in (b"<svg onload=alert(1)>", b"<html><script>", b"%PDF-1.7", b""):
            self.assertIsNone(sniff_content_type(data))


class StripJpegTests(unittest.TestCase):
    def test_removes_exif_and_comments_keeps_image_data(self):
        out = strip_jpeg_metadata(JPEG_WITH_EXIF)
        self.assertNotIn(b"GPS-LAT-LON", out)
        self.assertNotIn(b"comment", out)
        self.assertIn(b"JFIF", out)
        self.assertTrue(out.endswith(b"\xff\xda\x00\x08scan-data\xff\xd9"))

    def test_malformed_input_is_returned_unchanged(self):
        bad = b"\xff\xd8\xff\xe1\xff\xff short"
        self.assertEqual(strip_jpeg_metadata(bad), bad)
        self.assertEqual(strip_jpeg_metadata(b"GIF89a"), b"GIF89a")


class SaveImageValidationTests(unittest.TestCase):
    def test_rejects_before_touching_the_db(self):
        from Football_Project.services.board_images import save_image

        for data, msg in ((b"", "No image"), (b"<svg/>", "Only PNG"), (b"GIF89a" + b"0" * MAX_IMAGE_BYTES, "too large")):
            with self.assertRaises(ImageUploadError) as ctx:
                save_image(data, uploader_user_id=1, group_id=1)
            self.assertIn(msg, str(ctx.exception))


if __name__ == "__main__":
    unittest.main()
