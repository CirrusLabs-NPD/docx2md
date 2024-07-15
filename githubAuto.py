import requests
import base64
import pathlib

path = pathlib.Path().resolve()


def create_repo(org_name, repo_name, token):
    url = f"https://api.github.com/orgs/{org_name}/repos"
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json",
    }
    payload = {"name": repo_name, "private": True}
    response = requests.post(url, headers=headers, json=payload)

    if response.status_code == 201:
        print(f"Repository '{repo_name}' created successfully!")
    else:
        print(f"Failed to create repository. Error: {response.text}")


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
        print(f"File '{file_path}' added successfully!")
    else:
        print(f"Failed to add file. Error: {response.text}")


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


# Replace with your organization name, repository name, and personal access token
org_name = "Deloitte-Global-Cloud-Services"
repo_name = "testAJ"
token = "<token>"

create_repo(org_name, repo_name, token)

# Replace with the file path, content, and your personal access token
file_path = "README.md"
filetoread = f"{path}/README.md"
with open(file_path, "r") as file:
    file_content = file.read()

add_file_to_repo(org_name, repo_name, file_path, file_content, token)

create_github_pages(org_name, repo_name, token)
