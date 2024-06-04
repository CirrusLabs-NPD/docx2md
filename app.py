import tkinter as tk
from tkinter import filedialog, messagebox
import os
import shutil
from PIL import Image, ImageTk
from utils import convert_docx_to_markdown, read_markdown_file


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("DOCX files", "*.docx")])
    if file_path:
        file_name = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(upload_dir, file_name))
        convert_and_display(file_name)


def convert_and_display(file_name):
    output_md_path = os.path.join(output_dir, f"{os.path.splitext(file_name)[0]}.md")
    images_dir = os.path.join(output_dir, "images")
    os.makedirs(images_dir, exist_ok=True)
    convert_docx_to_markdown(
        os.path.join(upload_dir, file_name), output_md_path, images_dir
    )

    with open(output_md_path, "r") as f:
        md_content = f.read()
    md_text.delete("1.0", tk.END)
    md_text.insert(tk.END, md_content)

    for widget in image_frame.winfo_children():
        widget.destroy()

    for image_file in os.listdir(images_dir):
        if image_file.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.abspath(os.path.join(images_dir, image_file))
            img = Image.open(image_path)
            img = img.resize(
                (200, 200), Image.LANCZOS
            )  # Resize image to fit the display
            img = ImageTk.PhotoImage(img)
            img_label = tk.Label(image_frame, image=img)
            img_label.image = img
            img_label.pack()

    shutil.make_archive(output_dir, "zip", output_dir)
    download_button.config(state=tk.NORMAL)


def download_output():
    save_path = filedialog.asksaveasfilename(
        defaultextension=".zip", filetypes=[("Zip files", "*.zip")]
    )
    if save_path:
        shutil.copy(f"{output_dir}.zip", save_path)
        messagebox.showinfo("Download", "Download successful!")


# Setup directories
upload_dir = "upload"
os.makedirs(upload_dir, exist_ok=True)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# GUI setup
root = tk.Tk()
root.title("DOCX to Markdown Converter")

header = tk.Label(root, text="DOCX to Markdown Converter", font=("Arial", 18))
header.pack(pady=10)

info = tk.Label(
    root,
    text="Upload a DOCX file to convert it to Markdown.\nImages embedded in the DOCX file will be extracted and saved in the 'output/images' directory.\nThe converted Markdown file will be saved in the 'output' directory.",
    wraplength=400,
)
info.pack(pady=10)

upload_button = tk.Button(root, text="Upload DOCX File", command=upload_file)
upload_button.pack(pady=10)

download_button = tk.Button(
    root,
    text="Download Output Directory",
    command=download_output,
)
download_button.pack(pady=10)

md_label = tk.Label(root, text="Converted Markdown:")
md_label.pack(pady=10)

md_text = tk.Text(root, height=20, width=60)
md_text.pack(pady=10)

image_frame = tk.Frame(root)
image_frame.pack(pady=10)


footer = tk.Label(root, text="Created by Dev Squad")
footer.pack(pady=10)

root.mainloop()
