import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
from PIL import Image, ImageTk
import requests
import base64
from utils import convert_docx_to_markdown, read_markdown_file


def upload_file():
    file_path = filedialog.askopenfilename(filetypes=[("DOCX files", "*.docx")])
    if file_path:
        file_name = os.path.basename(file_path)
        shutil.copy(file_path, os.path.join(upload_dir, file_name))
        convert_and_display(file_name)


def convert_and_display(file_name):
    global current_file_name
    current_file_name = file_name
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
            img = img.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)
            img_label = ttk.Label(image_frame, image=img)
            img_label.image = img
            img_label.pack()

    shutil.make_archive(output_dir, "zip", output_dir)
    download_button.config(state=tk.NORMAL)
    github_button.config(state=tk.NORMAL)


def download_output():
    save_path = filedialog.asksaveasfilename(
        defaultextension=".zip", filetypes=[("Zip files", "*.zip")]
    )
    if save_path:
        shutil.copy(f"{output_dir}.zip", save_path)
        messagebox.showinfo("Download", "Download successful!")


def save_on_github():
    github_token = simpledialog.askstring("GitHub Token", "Enter your GitHub token:")
    if not github_token:
        return

    org_name = simpledialog.askstring(
        "Organization Name", "Enter the organization name:"
    )
    repo_option = messagebox.askyesno(
        "GitHub Repository", "Do you want to create a new repository?"
    )
    if repo_option:
        repo_name = simpledialog.askstring(
            "Repository Name", "Enter the name for the new repository:"
        )
        create_repo(org_name, repo_name, github_token)
    else:
        repo_name = simpledialog.askstring(
            "Repository Name", "Enter the name of the existing repository:"
        )

    branch_name = simpledialog.askstring(
        "Branch Name", "Enter the branch name:", initialvalue="main"
    )
    github_pages = messagebox.askyesno(
        "GitHub Pages", "Do you want to enable GitHub Pages for this repository?"
    )

    output_md_path = os.path.join(
        output_dir, f"{os.path.splitext(current_file_name)[0]}.md"
    )
    with open(output_md_path, "r") as f:
        md_content = f.read()

    file_path_in_repo = os.path.basename(output_md_path)
    add_file_to_repo(org_name, repo_name, file_path_in_repo, md_content, github_token)
    if github_pages:
        create_github_pages(org_name, repo_name, github_token)


def create_repo(org_name, repo_name, token):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"name": repo_name, "private": True}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        messagebox.showinfo("GitHub", f"Repository '{repo_name}' created successfully!")
    else:
        messagebox.showerror(
            "GitHub", f"Failed to create repository. Error: {response.text}"
        )


def add_file_to_repo(org_name, repo_name, file_path, file_content, token):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "message": "Add file",
        "content": base64.b64encode(file_content.encode()).decode(),
    }
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 201:
        messagebox.showinfo("GitHub", f"File '{file_path}' added successfully!")
    else:
        messagebox.showerror("GitHub", f"Failed to add file. Error: {response.text}")


def enable_github_pages(token, repo):
    url = f"https://api.github.com/repos/{repo}/pages"
    data = {"source": {"branch": "main", "path": "/"}}
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    response = requests.post(url, json=data, headers=headers)
    if response.status_code == 201:
        messagebox.showinfo("GitHub Pages", "GitHub Pages enabled successfully!")
    else:
        messagebox.showerror(
            "GitHub Pages",
            f"Failed to enable GitHub Pages: {response.json().get('message')}",
        )


def create_github_pages(org_name, repo_name, token):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/pages"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.switcheroo-preview+json",
    }
    payload = {"source": {"branch": "main", "path": "/"}}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        pages_url = response.json().get("html_url")
        print(f"GitHub Pages created successfully for repository '{repo_name}'!")
        print(f"URL to access the GitHub Pages: {pages_url}")
    else:
        print(f"Failed to create GitHub Pages. Error: {response.text}")


# Setup directories
upload_dir = "upload"
os.makedirs(upload_dir, exist_ok=True)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# GUI setup
root = tk.Tk()
root.title("DOCX to Markdown Converter")
root.geometry("800x600")

style = ttk.Style()
style.configure("TLabel", font=("Helvetica", 12))
style.configure("TButton", font=("Helvetica", 12))
style.configure("TText", font=("Helvetica", 12))
style.configure("Header.TLabel", font=("Helvetica", 18, "bold"))
style.configure("TFrame", background="#f0f0f0")

# Adding custom styles for buttons with improved UI
style.configure(
    "TUploadButton.TButton",
    font=("Helvetica", 12, "bold"),
    background="#4CAF50",
    foreground="white",
    padding=10,
    borderwidth=0,
    relief="flat",
)
style.map(
    "TUploadButton.TButton",
    background=[("active", "#45a049"), ("disabled", "#A5D6A7")],
    foreground=[("active", "white"), ("disabled", "#E8F5E9")],
)

style.configure(
    "TDownloadButton.TButton",
    font=("Helvetica", 12, "bold"),
    background="#008CBA",
    foreground="white",
    padding=10,
    borderwidth=0,
    relief="flat",
)
style.map(
    "TDownloadButton.TButton",
    background=[("active", "#007bb5"), ("disabled", "#90CAF9")],
    foreground=[("active", "white"), ("disabled", "#E3F2FD")],
)

style.configure(
    "TGitHubButton.TButton",
    font=("Helvetica", 12, "bold"),
    background="#333333",
    foreground="white",
    padding=20,
    borderwidth=0,
    relief="flat",
)
style.map(
    "TGitHubButton.TButton",
    background=[("active", "#555555"), ("disabled", "#B0BEC5")],
    foreground=[("active", "white"), ("disabled", "#CFD8DC")],
)

header = ttk.Label(root, text="DOCX to Markdown Converter", style="Header.TLabel")
header.pack(pady=10)

info = ttk.Label(
    root,
    text="Upload a DOCX file to convert it to Markdown.\nImages embedded in the DOCX file will be extracted and saved in the 'output/images' directory.\nThe converted Markdown file will be saved in the 'output' directory.",
    wraplength=600,
    justify=tk.CENTER,
    style="TLabel",
)
info.pack(pady=10)

button_frame = ttk.Frame(root, padding="10 10 10 10")
button_frame.pack(pady=10)

upload_button = ttk.Button(
    button_frame,
    text="Upload DOCX File",
    command=upload_file,
    style="TUploadButton.TButton",
)
upload_button.grid(row=0, column=0, padx=10)

download_button = ttk.Button(
    button_frame,
    text="Download Output",
    command=download_output,
    state=tk.DISABLED,
    style="TDownloadButton.TButton",
)
download_button.grid(row=0, column=1, padx=10)

github_button = ttk.Button(
    button_frame,
    text="Save on GitHub",
    command=save_on_github,
    state=tk.DISABLED,
    style="TGitHubButton.TButton",
)
github_button.grid(row=0, column=2, padx=10)

text_frame = ttk.Frame(root, padding="10 10 10 10")
text_frame.pack(pady=10, fill=tk.BOTH, expand=True)

md_text = tk.Text(text_frame, wrap=tk.WORD, font=("Helvetica", 12))
md_text.pack(fill=tk.BOTH, expand=True)

image_frame = ttk.Frame(root, padding="10 10 10 10")
image_frame.pack(pady=10)

root.mainloop()
