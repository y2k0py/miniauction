#!/usr/bin/env python3
"""Remove Gamma.app watermark from a PowerPoint file without touching slide images."""

from __future__ import annotations

import re
import shutil
import sys
import zipfile
from io import BytesIO
from pathlib import Path
from xml.etree import ElementTree as ET

NS = {
    "p": "http://schemas.openxmlformats.org/presentationml/2006/main",
    "a": "http://schemas.openxmlformats.org/drawingml/2006/main",
    "r": "http://schemas.openxmlformats.org/officeDocument/2006/relationships",
    "rel": "http://schemas.openxmlformats.org/package/2006/relationships",
}

REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
HYPERLINK_TYPE = (
    "http://schemas.openxmlformats.org/officeDocument/2006/relationships/hyperlink"
)

# Gamma watermark badge size in slide layouts (~1.07M x 0.26M EMU)
MAX_WATERMARK_CX = 1_500_000
MAX_WATERMARK_CY = 400_000


def _register_namespaces() -> None:
    for prefix, uri in NS.items():
        if prefix != "rel":
            ET.register_namespace(prefix, uri)
    ET.register_namespace("", REL_NS)


def _is_gamma_watermark(pic: ET.Element) -> bool:
    """Detect only the small Gamma badge, not regular slide content images."""
    hlink = pic.find(".//a:hlinkClick", NS)
    if hlink is not None:
        return True

    ext = pic.find(".//a:xfrm/a:ext", NS)
    if ext is None:
        return False

    try:
        cx = int(ext.get("cx", 0))
        cy = int(ext.get("cy", 0))
    except ValueError:
        return False

    return cx <= MAX_WATERMARK_CX and cy <= MAX_WATERMARK_CY


def _remove_gamma_watermarks(xml_bytes: bytes) -> tuple[bytes, int]:
    root = ET.fromstring(xml_bytes)
    sp_tree = root.find(".//p:spTree", NS)
    if sp_tree is None:
        return xml_bytes, 0

    removed = 0
    for pic in list(sp_tree.findall("p:pic", NS)):
        if _is_gamma_watermark(pic):
            sp_tree.remove(pic)
            removed += 1

    if removed:
        return ET.tostring(root, encoding="utf-8", xml_declaration=True), removed
    return xml_bytes, 0


def _clean_rels(rels_xml: bytes) -> tuple[bytes, int]:
    root = ET.fromstring(rels_xml)
    removed = 0
    for rel in list(root):
        target = rel.get("Target", "")
        rel_type = rel.get("Type", "")
        if "gamma.app" in target.lower() or (
            rel_type == HYPERLINK_TYPE and "gamma" in target.lower()
        ):
            root.remove(rel)
            removed += 1

    if removed:
        return ET.tostring(root, encoding="utf-8", xml_declaration=True), removed
    return rels_xml, 0


def remove_gamma_branding(pptx_path: Path, *, backup: bool = True) -> int:
    _register_namespaces()

    if backup:
        backup_path = pptx_path.with_suffix(".pptx.bak")
        shutil.copy2(pptx_path, backup_path)

    changes = 0
    output = BytesIO()

    with zipfile.ZipFile(pptx_path, "r") as zin, zipfile.ZipFile(output, "w", zipfile.ZIP_DEFLATED) as zout:
        for item in zin.infolist():
            data = zin.read(item.filename)

            # Gamma watermark lives on slide layouts only, not on slide content images.
            if item.filename.startswith("ppt/slideLayouts/slideLayout") and item.filename.endswith(".xml"):
                new_data, removed = _remove_gamma_watermarks(data)
                if removed:
                    changes += removed
                    data = new_data
            elif item.filename.endswith(".xml.rels"):
                new_data, removed = _clean_rels(data)
                if removed:
                    changes += 1
                    data = new_data

            zout.writestr(item, data)

    pptx_path.write_bytes(output.getvalue())
    return changes


def main() -> None:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "/Users/ivanp/Downloads/MiniAukcje.pptx")
    if not path.exists():
        raise SystemExit(f"File not found: {path}")

    changes = remove_gamma_branding(path)
    print(f"Updated {path}")
    print(f"Backup saved to {path.with_suffix('.pptx.bak')}")
    print(f"Watermark elements removed: {changes}")


if __name__ == "__main__":
    main()
