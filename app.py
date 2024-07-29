import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
from PIL import Image, ImageTk
import requests
import base64
import webbrowser
from utils import convert_docx_to_markdown, read_markdown_file


def upload_file():
    file_paths = filedialog.askopenfilenames(filetypes=[("DOCX files", "*.docx")])
    if file_paths:
        for file_path in file_paths:
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


# def save_on_github():
#     github_token = simpledialog.askstring("GitHub Token", "Enter your GitHub token:")
#     if not github_token:
#         return

#     org_name = simpledialog.askstring(
#         "Organization Name", "Enter the organization name:"
#     )
#     repo_option = messagebox.askyesno(
#         "GitHub Repository", "Do you want to create a new repository?"
#     )
#     if repo_option:
#         repo_name = simpledialog.askstring(
#             "Repository Name", "Enter the name for the new repository:"
#         )
#         create_repo(org_name, repo_name, github_token)
#     else:
#         repo_name = simpledialog.askstring(
#             "Repository Name", "Enter the name of the existing repository:"
#         )

#     branch_name = simpledialog.askstring(
#         "Branch Name", "Enter the branch name:", initialvalue="main"
#     )
#     github_pages = messagebox.askyesno(
#         "GitHub Pages", "Do you want to enable GitHub Pages for this repository?"
#     )

#     output_md_path = os.path.join(
#         output_dir, f"{os.path.splitext(current_file_name)[0]}.md"
#     )
#     with open(output_md_path, "r") as f:
#         md_content = f.read()

#     file_path_in_repo = os.path.basename(output_md_path)
#     add_file_to_repo(org_name, repo_name, file_path_in_repo, md_content, github_token)
#     if github_pages:
#         create_github_pages(org_name, repo_name, github_token)


# def save_on_github():
#     github_token = simpledialog.askstring("GitHub Token", "Enter your GitHub token:")
#     if not github_token:
#         return

#     org_name = simpledialog.askstring(
#         "Organization Name", "Enter the organization name:"
#     )
#     repo_option = messagebox.askyesno(
#         "GitHub Repository", "Do you want to create a new repository?"
#     )
#     if repo_option:
#         repo_name = simpledialog.askstring(
#             "Repository Name", "Enter the name for the new repository:"
#         )
#         create_repo(org_name, repo_name, github_token)
#     else:
#         repo_name = simpledialog.askstring(
#             "Repository Name", "Enter the name of the existing repository:"
#         )

#     branch_name = simpledialog.askstring(
#         "Branch Name", "Enter the branch name:", initialvalue="main"
#     )
#     github_pages = messagebox.askyesno(
#         "GitHub Pages", "Do you want to enable GitHub Pages for this repository?"
#     )

#     # Upload all Markdown files
#     for file_name in os.listdir(output_dir):
#         if file_name.endswith(".md"):
#             file_path = os.path.join(output_dir, file_name)
#             with open(file_path, "r") as f:
#                 md_content = f.read()
#             file_path_in_repo = os.path.basename(file_path)
#             add_file_to_repo(
#                 org_name, repo_name, file_path_in_repo, md_content, github_token
#             )

#     # Upload images if needed
#     images_dir = os.path.join(output_dir, "images")
#     if os.path.isdir(images_dir):
#         for image_file in os.listdir(images_dir):
#             if image_file.endswith((".png", ".jpg", ".jpeg")):
#                 image_path = os.path.join(images_dir, image_file)
#                 with open(image_path, "rb") as img_file:
#                     img_content = img_file.read()
#                 image_base64 = base64.b64encode(img_content).decode()
#                 image_file_path = f"images/{image_file}"
#                 add_file_to_repo(
#                     org_name, repo_name, image_file_path, image_base64, github_token
#                 )

#     if github_pages:
#         create_github_pages(org_name, repo_name, github_token)


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


# def add_file_to_repo(org_name, repo_name, file_path, file_content, token):
#     url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Accept": "application/vnd.github.v3+json",
#     }
#     payload = {
#         "message": "Add file",
#         "content": base64.b64encode(file_content.encode()).decode(),
#     }
#     response = requests.put(url, headers=headers, json=payload)

#     if response.status_code == 201:
#         messagebox.showinfo("GitHub", f"File '{file_path}' added successfully!")
#     else:
#         messagebox.showerror("GitHub", f"Failed to add file. Error: {response.text}")


# def add_file_to_repo(org_name, repo_name, file_path, file_content, token):
#     url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}"
#     headers = {
#         "Authorization": f"Bearer {token}",
#         "Accept": "application/vnd.github.v3+json",
#     }
#     payload = {
#         "message": "Add file",
#         "content": file_content,  # This should be base64-encoded content
#     }
#     response = requests.put(url, headers=headers, json=payload)

#     if response.status_code == 201:
#         messagebox.showinfo("GitHub", f"File '{file_path}' added successfully!")
#     else:
#         print("GitHub", f"Failed to add file. Error: {response.text}")
#         messagebox.showerror("GitHub", f"Failed to add file. Error: {response.text}")


def add_file_to_repo(org_name, repo_name, file_path, file_content, token):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/{file_path}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {
        "message": "Add file",
        "content": file_content,  # This should be base64-encoded content
    }
    response = requests.put(url, headers=headers, json=payload)

    if response.status_code == 201:
        messagebox.showinfo("GitHub", f"File '{file_path}' added successfully!")
    else:
        messagebox.showerror("GitHub", f"Failed to add file. Error: {response.text}")


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

    output_dir = "output"  # Replace with the path to your output directory

    # Collect all Markdown files
    md_files = [f for f in os.listdir(output_dir) if f.endswith(".md")]

    # Create index.html content
    index_content = "<html><body><h1>Table Contents</h1><ul>"
    for md_file in md_files:
        file_link = os.path.basename(md_file)
        index_content += f'<li><a href="{file_link}">{file_link}</a></li>'
    index_content += "</ul></body></html>"

    # Save index.html to output_dir
    index_file_path = os.path.join(output_dir, "index.html")
    with open(index_file_path, "w") as index_file:
        index_file.write(index_content)

    # Upload all Markdown files and delete them after upload
    for file_name in md_files:
        file_path = os.path.join(output_dir, file_name)
        with open(file_path, "r") as f:
            md_content = f.read()
        file_content_base64 = base64.b64encode(md_content.encode()).decode()
        file_path_in_repo = os.path.basename(file_path)
        add_file_to_repo(
            org_name,
            repo_name,
            file_path_in_repo,
            file_content_base64,
            github_token,
        )
        os.remove(file_path)  # Delete the file after uploading

    # Upload index.html file and delete it after upload
    with open(index_file_path, "r") as index_file:
        index_content_base64 = base64.b64encode(index_file.read().encode()).decode()
    add_file_to_repo(
        org_name,
        repo_name,
        "index.html",
        index_content_base64,
        github_token,
    )
    os.remove(index_file_path)  # Delete the file after uploading

    # Upload images if needed and delete them after upload
    images_dir = os.path.join(output_dir, "images")
    if os.path.isdir(images_dir):
        for image_file in os.listdir(images_dir):
            if image_file.endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(images_dir, image_file)
                with open(image_path, "rb") as img_file:
                    img_content = img_file.read()
                image_base64 = base64.b64encode(img_content).decode()
                image_file_path = f"images/{image_file}"
                add_file_to_repo(
                    org_name, repo_name, image_file_path, image_base64, github_token
                )
                os.remove(image_path)  # Delete the image file after uploading

    if github_pages:
        create_github_pages(org_name, repo_name, github_token)


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
        messagebox.showinfo(
            "GitHub Pages", f"URL to access the GitHub Pages: {pages_url}"
        )
    else:
        print(f"Failed to create GitHub Pages. Error: {response.text}")


def guide_to_github():
    webbrowser.open_new("https://developer.deloitte.com/ecr-docs/deloittegithub/")


def github_pat_token():
    webbrowser.open_new(
        "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/creating-a-personal-access-token"
    )


# Setup directories
upload_dir = "upload"
os.makedirs(upload_dir, exist_ok=True)
output_dir = "output"
os.makedirs(output_dir, exist_ok=True)

# GUI setup
root = tk.Tk()
root.title("DOCX to Markdown Converter")
root.geometry("800x600")
root.configure(bg="#2e2e2e")

style = ttk.Style()
style.theme_use("clam")
style.configure(
    "TLabel", font=("Helvetica", 12), background="#2e2e2e", foreground="white"
)
style.configure(
    "TButton", font=("Helvetica", 12), background="#4CAF50", foreground="white"
)
style.configure(
    "TText", font=("Helvetica", 12), background="#2e2e2e", foreground="white"
)
style.configure(
    "Header.TLabel",
    font=("Helvetica", 18, "bold"),
    background="#2e2e2e",
    foreground="white",
)
style.configure("TFrame", background="#2e2e2e")

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
    background=[("active", "#F5E7B2"), ("disabled", "#BBE9FF")],
    foreground=[("active", "white"), ("disabled", "#FFFFFF")],
)

style.configure(
    "TGitHubButton.TButton",
    font=("Helvetica", 12, "bold"),
    background="#333333",
    foreground="white",
    padding=10,
    borderwidth=0,
    relief="flat",
)
style.map(
    "TGitHubButton.TButton",
    background=[("active", "#1a1a1a"), ("disabled", "#BDBDBD")],
    foreground=[("active", "white"), ("disabled", "#F5F5F5")],
)

header_label = ttk.Label(root, text="DOCX to Markdown Converter", style="Header.TLabel")
header_label.pack(pady=20)

upload_button = ttk.Button(
    root, text="Upload DOCX Files", command=upload_file, style="TUploadButton.TButton"
)
upload_button.pack(pady=10)

md_label = ttk.Label(root, text="Markdown Output", style="TLabel")
md_label.pack(pady=10)

md_text = tk.Text(root, wrap=tk.WORD, height=10, width=80, bg="#1e1e1e", fg="white")
md_text.pack(pady=10)

image_label = ttk.Label(root, text="Images", style="TLabel")
image_label.pack(pady=10)

image_frame = ttk.Frame(root)
image_frame.pack(pady=10)

button_frame = ttk.Frame(root)
button_frame.pack(pady=10)

download_button = ttk.Button(
    button_frame,
    text="Download Output",
    command=download_output,
    state=tk.DISABLED,
    style="TDownloadButton.TButton",
)
download_button.pack(side=tk.LEFT, padx=10)

github_button = ttk.Button(
    button_frame,
    text="Save on GitHub",
    command=save_on_github,
    state=tk.DISABLED,
    style="TGitHubButton.TButton",
)
github_button.pack(side=tk.LEFT, padx=10)

guide_button = ttk.Button(
    button_frame,
    text="GitHub Guide",
    command=guide_to_github,
    style="TGitHubButton.TButton",
)
guide_button.pack(side=tk.LEFT, padx=10)

token_button = ttk.Button(
    button_frame,
    text="GitHub PAT Token",
    command=github_pat_token,
    style="TGitHubButton.TButton",
)
token_button.pack(side=tk.LEFT, padx=10)

root.mainloop()
