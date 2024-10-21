import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import os
import shutil
from PIL import Image, ImageTk
import requests
import base64
import webbrowser
import subprocess
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

    for image_file in os.listdir(images_dir):
        if image_file.endswith((".png", ".jpg", ".jpeg")):
            image_path = os.path.abspath(os.path.join(images_dir, image_file))
            img = Image.open(image_path)
            img = img.resize((200, 200), Image.LANCZOS)
            img = ImageTk.PhotoImage(img)

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
        "content": file_content,  # This should be base64-encoded content
    }
    requests.put(url, headers=headers, json=payload)


def clone_repo(org_name, repo_name, token, output_dir):
    # Construct the repository URL
    repo_url = f"https://{token}@github.com/{org_name}/{repo_name}.git"

    # Ensure the output directory exists and is writable
    if not os.path.exists(output_dir):
        try:
            os.makedirs(output_dir)
        except OSError as e:
            print(f"Failed to create directory '{output_dir}'. Error: {e}")
            return

    # Construct the command to clone the repository
    clone_command = ["git", "clone", repo_url, output_dir]

    # Execute the command
    try:
        subprocess.run(clone_command, check=True)
        print(f"Repository '{org_name}/{repo_name}' cloned into '{output_dir}'")
    except subprocess.CalledProcessError as e:
        print(f"Failed to clone repository. Error: {e}")


def get_repo_info(org_name, repo_name, token):
    url = f"https://api.github.com/repos/{org_name}/{repo_name}"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        messagebox.showerror(
            "GitHub", f"Failed to get repository info. Error: {response.text}"
        )
        return None


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

    clone_repo(org_name, repo_name, github_token, "clonned")
    if repo_option:
        new_repo_pipeline(org_name, repo_name, github_token)
    else:
        existing_repo_pipeline(org_name, repo_name, github_token)


# def push_files_to_repo(org_name, repo_name, branch_name, github_token, directory):
#     # GitHub API URL for the repository
#     api_url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/"

#     headers = {
#         "Authorization": f"token {github_token}",
#         "Accept": "application/vnd.github.v3+json",
#     }

#     # Walk through the directory and push files
#     for root, dirs, files in os.walk(directory):
#         for file_name in files:
#             file_path = os.path.join(root, file_name)
#             relative_path = os.path.relpath(file_path, directory)

#             with open(file_path, "rb") as file:
#                 file_content = file.read()

#             file_content_base64 = base64.b64encode(file_content).decode()

#             # Prepare the data for GitHub API
#             data = {
#                 "message": f"Update {relative_path}",
#                 "content": file_content_base64,
#                 "branch": branch_name,
#             }

#             # Determine the file path in the repo
#             api_file_url = api_url + relative_path

#             # Check if the file exists in the repo
#             response = requests.get(api_file_url, headers=headers)

#             if response.status_code == 200:
#                 # File exists, update it
#                 file_info = response.json()
#                 data["sha"] = file_info["sha"]
#                 response = requests.put(api_file_url, headers=headers, json=data)
#             elif response.status_code == 404:
#                 # File does not exist, create it
#                 response = requests.put(api_file_url, headers=headers, json=data)
#             else:
#                 response.raise_for_status()

#             if response.status_code not in [200, 201]:
#                 print(
#                     f"Failed to push {relative_path}: {response.status_code} {response.text}"
#                 )


def push_files_to_repo(org_name, repo_name, branch_name, github_token, directory):
    # GitHub API URL for the repository
    api_url = f"https://api.github.com/repos/{org_name}/{repo_name}/contents/"

    headers = {
        "Authorization": f"token {github_token}",
        "Accept": "application/vnd.github.v3+json",
    }

    # Walk through the directory and push files
    for root, dirs, files in os.walk(directory):
        # Skip hidden directories (e.g., .git)
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for file_name in files:
            if file_name.startswith("."):
                continue  # Skip hidden files

            file_path = os.path.join(root, file_name)
            relative_path = os.path.relpath(file_path, directory)

            with open(file_path, "rb") as file:
                file_content = file.read()

            file_content_base64 = base64.b64encode(file_content).decode()

            # Prepare the data for GitHub API
            data = {
                "message": f"Update {relative_path}",
                "content": file_content_base64,
                "branch": branch_name,
            }

            # Determine the file path in the repo
            api_file_url = api_url + relative_path

            # Check if the file exists in the repo
            response = requests.get(api_file_url, headers=headers)

            if response.status_code == 200:
                # File exists, update it
                file_info = response.json()
                data["sha"] = file_info["sha"]
                response = requests.put(api_file_url, headers=headers, json=data)
            elif response.status_code == 404:
                # File does not exist, create it
                response = requests.put(api_file_url, headers=headers, json=data)
            else:
                response.raise_for_status()

            if response.status_code not in [200, 201]:
                print(
                    f"Failed to push {relative_path}: {response.status_code} {response.text}"
                )


def existing_repo_pipeline(org_name, repo_name, github_token):
    branch_name = simpledialog.askstring(
        "Branch Name", "Enter the branch name:", initialvalue="main"
    )
    github_pages = messagebox.askyesno(
        "GitHub Pages", "Do you want to enable GitHub Pages for this repository?"
    )

    output_dir = "output"  # Path to the output directory
    repo_dir = "clonned"  # Path to the clonned directory

    # Copy Markdown files from output_dir to repo_dir
    md_files = [f for f in os.listdir(output_dir) if f.endswith(".md")]
    for md_file in md_files:
        shutil.copy(os.path.join(output_dir, md_file), os.path.join(repo_dir, md_file))

    # Copy styles.css and script.js from root to repo_dir
    src_script = "script.js"
    src_styles = "styles.css"
    shutil.copy(src_script, os.path.join(repo_dir, src_script))
    shutil.copy(src_styles, os.path.join(repo_dir, src_styles))

    # Collect all Markdown files from repo_dir
    md_files = [f for f in os.listdir(repo_dir) if f.endswith(".md")]

    # Create or update index.html in repo_dir
    index_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Doc2MD Converter</title>
    <link rel="stylesheet" href="styles.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" />
    <script src="https://unpkg.com/markdown-it/dist/markdown-it.min.js"></script>
    <script src="https://unpkg.com/marked/marked.min.js"></script>
    <script src="https://unpkg.com/markdown-it-imsize/dist/markdown-it-imsize.min.js"></script>
    <script src="script.js"></script>
</head>
<body>
<header style="background-color:black;color:white;padding:1rem;font-weight:bold;font-family:arial;position:fixed;left:0;top:0;width:100%">CirrusLabs</header>
    <div id="main-div-page">
        <div id="sidebar">
            <ul>
            <li><a href="#content"></a></li>
"""

    for md_file in md_files:
        file_link = os.path.basename(md_file)
        display_name = file_link.replace(".md", "")
        index_content += f'<li><a href="#" onclick="handleMenuItemClick(\'{file_link}\')">{display_name}</a></li>'

    index_content += """
            </ul>
            </div>
            <div id="content"></div>
            </div>
            </body>
            </html>
            """

    # Save index.html to repo_dir
    index_file_path = os.path.join(repo_dir, "index.html")
    with open(index_file_path, "w") as index_file:
        index_file.write(index_content)

    # Upload all Markdown files to GitHub and update existing files
    for file_name in md_files:
        file_path = os.path.join(repo_dir, file_name)
        with open(file_path, "r") as f:
            md_content = f.read()
        file_content_base64 = base64.b64encode(md_content.encode()).decode()

    # Upload index.html file to GitHub
    with open(index_file_path, "r") as index_file:
        index_content_base64 = base64.b64encode(index_file.read().encode()).decode()

    # Upload styles.css and script.js to GitHub
    for file_name in ["styles.css", "script.js"]:
        file_path = os.path.join(repo_dir, file_name)
        with open(file_path, "r") as file:
            file_content_base64 = base64.b64encode(file.read().encode()).decode()

    # Upload images if needed and delete them after upload
    images_dir = os.path.join(repo_dir, "images")
    if os.path.isdir(images_dir):
        for image_file in os.listdir(images_dir):
            if image_file.endswith((".png", ".jpg", ".jpeg")):
                image_path = os.path.join(images_dir, image_file)
                with open(image_path, "rb") as img_file:
                    img_content = img_file.read()
                image_base64 = base64.b64encode(img_content).decode()
                image_file_path = f"images/{image_file}"

    push_files_to_repo(org_name, repo_name, branch_name, github_token, "clonned")
    if github_pages:
        create_github_pages(org_name, repo_name, github_token)


def new_repo_pipeline(org_name, repo_name, github_token):
    branch_name = simpledialog.askstring(
        "Branch Name", "Enter the branch name:", initialvalue="main"
    )
    github_pages = messagebox.askyesno(
        "GitHub Pages", "Do you want to enable GitHub Pages for this repository?"
    )

    output_dir = "output"  # Replace with the path to your output directory
    src_script = "script.js"
    src_styles = "styles.css"
    # Copy the files to the output directory
    shutil.copy(src_script, os.path.join(output_dir, src_script))
    shutil.copy(src_styles, os.path.join(output_dir, src_styles))
    # Collect all Markdown files
    md_files = [f for f in os.listdir(output_dir) if f.endswith(".md")]

    # Create index.html content
    index_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <title>Doc2MD Converter</title>
    <link rel="stylesheet" href="styles.css" />
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.3/css/all.min.css" />
    <script src="https://unpkg.com/markdown-it/dist/markdown-it.min.js"></script>
    <script src="https://unpkg.com/marked/marked.min.js"></script>
    <script src="https://unpkg.com/markdown-it-imsize/dist/markdown-it-imsize.min.js"></script>
    <script src="script.js"></script>
</head>
<body>
<header style="background-color:black;color:white;padding:1rem;font-weight:bold;font-family:arial;position:fixed;left:0;top:0;width:100%">Cirruslabs</header>'
    <div id="main-div-page">
        <div id="sidebar">
            <ul>
            <li><a href="#content"></a></li>
"""

    for md_file in md_files:
        file_link = os.path.basename(md_file)
        # Ensure file_link is properly quoted in JavaScript
        display_name = file_link.replace(".md", "")
        index_content += f'<li><a href="#" onclick="handleMenuItemClick(\'{file_link}\')">{display_name}</a></li>'

    index_content += """
            </ul>
            </div>
            <div id="content"></div>
            </div>
            </body>
            </html>
            """

    # if repo_option is true use below logic but if repo option is false ,then first check if clonned dir exists,then check if index.html exists => update the index.html with below logic and add updates there . But if index.html doesn't exists then use below logic and create a new index.html

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

    style_file_path = os.path.join(output_dir, "styles.css")
    with open(style_file_path, "r") as style_file:
        style_content_base64 = base64.b64encode(style_file.read().encode()).decode()
    add_file_to_repo(
        org_name,
        repo_name,
        "styles.css",
        style_content_base64,
        github_token,
    )
    script_file_path = os.path.join(output_dir, "script.js")
    with open(script_file_path, "r") as script_file:
        script_content_base64 = base64.b64encode(script_file.read().encode()).decode()
    add_file_to_repo(
        org_name,
        repo_name,
        "script.js",
        script_content_base64,
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
    webbrowser.open_new(
        "https://docs.github.com/en/get-started/onboarding/getting-started-with-your-github-account"
    )


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

# image_label = ttk.Label(root, text="Images", style="TLabel")
# image_label.pack(pady=10)

# image_frame = ttk.Frame(root)
# image_frame.pack(pady=10)

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
