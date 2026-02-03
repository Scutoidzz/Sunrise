import libzim.reader
import logging

class KiwixEngine:
    def __init__(self, zim_path):
        self.zim_path = zim_path
        self.archive = None
        try:
            self.archive = libzim.reader.Archive(self.zim_path)
            print(f"Loaded ZIM: {self.zim_path}")
        except Exception as e:
            print(f"Failed to load ZIM: {e}")

    def search(self, query):
        """Returns {title, summary, image_bytes} or None"""
        if not self.archive:
            return None

        entry = None
        try:
            entry = self.archive.get_entry_by_path(f"A/{query.title()}")
        except:
            pass

        if not entry:
            return None

        item = entry.get_item()
        content_bytes = bytes(item.content)

        image_data = None
        try:
            html_str = content_bytes.decode('utf-8', errors='ignore')
            if 'src="' in html_str:
                start = html_str.find('src="') + 5
                end = html_str.find('"', start)
                img_rel_path = html_str[start:end]

                if "I/" in img_rel_path:
                    full_img_path = img_rel_path.replace("../", "")
                    img_entry = self.archive.get_entry_by_path(full_img_path)
                    image_data = bytes(img_entry.get_item().content)
        except Exception as e:
            print(f"Image extraction failed: {e}")

        summary = self._extract_summary(html_str) if 'html_str' in locals() else ""

        return {
            "title": entry.title,
            "summary": summary,
            "image": image_data
        }

    def _extract_summary(self, html_str):
        """Extract text summary from HTML content."""
        import re
        text = re.sub('<[^<]+?>', '', html_str)
        text = re.sub(r'\s+', ' ', text).strip()
        return text[:300] + "..." if len(text) > 300 else text
