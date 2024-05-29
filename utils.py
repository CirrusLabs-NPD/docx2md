import os
import re
import base64
from docx import Document

def convert_docx_to_markdown(docx_path, output_md_path, images_dir):
    document = Document(docx_path)
    os.makedirs(images_dir, exist_ok=True)
    md_content = []

    for paragraph in document.paragraphs:
        md_content.append(paragraph.text)
    
    for rel in document.part.rels.values():
        if "image" in rel.target_ref:
            image = rel.target_part.blob
            image_name = os.path.basename(rel.target_ref)
            image_path = os.path.join(images_dir, image_name)
            with open(image_path, "wb") as img_file:
                img_file.write(image)
            md_content.append(f"![{image_name}](./images/{image_name})")

    with open(output_md_path, "w") as md_file:
        md_file.write("\n\n".join(md_content))

    return output_md_path

def read_markdown_file(md_file_path):
    with open(md_file_path, "r") as md_file:
        return md_file.read()
