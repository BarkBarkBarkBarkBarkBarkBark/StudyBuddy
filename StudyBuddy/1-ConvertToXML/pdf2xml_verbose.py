import fitz  # PyMuPDF
import xml.etree.ElementTree as ET

doc = fitz.open(input("Full Path: "))
root = ET.Element("document")

for page_num, page in enumerate(doc, start=1):
    page_el = ET.SubElement(root, "page", number=str(page_num))
    for block in page.get_text("dict")["blocks"]:
        block_el = ET.SubElement(page_el, "block", bbox=str(block["bbox"]))
        for line in block.get("lines", []):
            for span in line.get("spans", []):
                ET.SubElement(block_el, "text", bbox=str(span["bbox"])).text = span["text"]

tree = ET.ElementTree(root)
tree.write(input("Output File Name (ex. chapter.xml): "), encoding="utf-8", xml_declaration=True)
