# scrub_cropped_pdf.py
# doesnt really work 
import pymupdf as fitz
import sys

def scrub(src: str, dst: str) -> None:
    doc = fitz.open(src)
    for page in doc:
        crop = +page.cropbox                  # snapshot before mutating
        page.set_cropbox(page.mediabox)       # expose full media for redaction coords
        mb = page.mediabox
        # annular region = MediaBox \ CropBox (four axis-aligned rects)
        outside = [
            fitz.Rect(mb.x0,   mb.y0,   mb.x1,   crop.y0),
            fitz.Rect(mb.x0,   crop.y1, mb.x1,   mb.y1  ),
            fitz.Rect(mb.x0,   crop.y0, crop.x0, crop.y1),
            fitz.Rect(crop.x1, crop.y0, mb.x1,   crop.y1),
        ]
        for r in outside:
            if r.width > 0 and r.height > 0:
                page.add_redact_annot(r)
        # nuke text, rasterize/remove images, drop vector paths fully covered
        page.apply_redactions(
            images=fitz.PDF_REDACT_IMAGE_REMOVE,
            graphics=fitz.PDF_REDACT_LINE_ART_REMOVE_IF_COVERED,
            text=fitz.PDF_REDACT_TEXT_REMOVE,
        )
        page.set_cropbox(crop)
        page.set_mediabox(crop)               # MediaBox := CropBox; trims page geometry
    # garbage=4 -> full xref compaction (dead-object sweep); clean -> content-stream sanitize
    doc.save(dst, garbage=4, clean=True, deflate=True, deflate_images=True, deflate_fonts=True)
    doc.close()

if __name__ == "__main__":
    scrub(sys.argv[1], sys.argv[2])
