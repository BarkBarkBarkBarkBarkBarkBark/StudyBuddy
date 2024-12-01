from pdfminer.high_level import extract_text

# Extract text from a PDF
text = extract_text(input("Full Path: "))

# Save text into a simple XML structure
with open(input("Output File Name (ex. chapter.xml): "), "w") as xml_file:
    xml_file.write(f"<document>\n{text}\n</document>")
