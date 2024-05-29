import streamlit as st
import os
import shutil
from utils import convert_docx_to_markdown, read_markdown_file

# Header
st.title("DOCX to Markdown Converter")

# Information
st.markdown("""
Upload a DOCX file to convert it to Markdown.  
Images embedded in the DOCX file will be extracted and saved in the 'output/images' directory.  
The converted Markdown file will be saved in the 'output' directory.
""")

# Upload file section
st.header("Upload File")
upload_dir = "upload"
os.makedirs(upload_dir, exist_ok=True)  # Create upload directory if it doesn't exist
uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file is not None:
    file_name = os.path.join(upload_dir, uploaded_file.name)  # Path to save uploaded file
    with open(file_name, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    output_dir = "output"
    os.makedirs(output_dir, exist_ok=True)  # Create output directory if it doesn't exist
    output_md_path = os.path.join(output_dir, f"{os.path.splitext(uploaded_file.name)[0]}.md")  # Use uploaded file name for output
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)  # Create images directory if it doesn't exist
    convert_docx_to_markdown(file_name, output_md_path, images_dir)

    st.markdown("### Converted Markdown")
    md_content = read_markdown_file(output_md_path)
    st.markdown(md_content)

    with open(output_md_path, "r") as f:
        st.download_button(
            label="Download Markdown",
            data=f,
            file_name=f"{os.path.splitext(uploaded_file.name)[0]}.md",  # Use uploaded file name for download
            mime="text/markdown"
        )

    # Create a zip file of the output directory
    shutil.make_archive(output_dir, "zip", output_dir)

    # Offer the zip file for download
    st.download_button(
        label="Download Output Directory",
        data=f"{output_dir}.zip",
        file_name=f"{output_dir}.zip",
        mime="application/zip"
    )

    for image_file in os.listdir(images_dir):
        if image_file.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.abspath(os.path.join(images_dir, image_file))  # Get absolute path
            st.image(image_path, caption=image_file)

# Footer
st.markdown("---")
st.markdown("Created by Dev Squad")
