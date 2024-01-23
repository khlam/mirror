import os
import requests
import time

GITHUB_API_BASE_URL = 'https://api.github.com'
GITLAB_API_BASE_URL = 'https://gitlab.com/api/v4'

def get_github_repos(github_username):
    repos = []
    page = 1
    while True:
        response = requests.get(f'{GITHUB_API_BASE_URL}/users/{github_username}/repos?type=public&page={page}&per_page=100')
        if response.status_code != 200:
            raise Exception(f'Failed to fetch GitHub repositories: {response.status_code}')
        
        new_repos = response.json()
        if not new_repos:
            break

        repos.extend(new_repos)
        page += 1

    return repos


def create_or_update_gitlab_project(repo, gitlab_token, gitlab_username):
    headers = {'Private-Token': gitlab_token}

    # Modify the project name if the repo is a fork
    project_name_suffix = "-fork" if repo.get('fork') else ""
    project_name = f"{gitlab_username}/{repo['name']}{project_name_suffix}"
    project_url_encoded = requests.utils.quote(project_name, safe="")
    delete_project_url = f'{GITLAB_API_BASE_URL}/projects/{project_url_encoded}'

    # Always try to delete the project
    try:
        print(f"Attempting to delete project (if exists): {delete_project_url}")
        delete_response = requests.delete(delete_project_url, headers=headers)
        if delete_response.status_code in [200, 202, 204]:
            print(f"Deleted existing project {repo['name']} (or the project did not exist).")
    except Exception as e:
        print(f"Error during deletion of project {repo['name']}: {e}")
        pass  # Ignoring the exception and moving on

    print(f"Creating repository {repo['name']} in GitLab...")
    data = {
        'name': repo['name'] + project_name_suffix,
        'description': repo.get('description', ''),
        'visibility': 'public',
        'import_url': repo['clone_url']
    }
    try:
        create_response = requests.post(f'{GITLAB_API_BASE_URL}/projects', headers=headers, data=data)
        if create_response.status_code != 201:
            print(f"Failed to create GitLab project for {repo['name']}. Status Code: {create_response.status_code}, Response: {create_response.text}")
    except Exception as e:
        print(f"Exception occurred while creating GitLab project for {repo['name']}: {e}")


def main():
    github_username = 'khlam' # Replace with your GitHub username
    gitlab_token = os.environ.get('GITLAB_TOKEN')
    gitlab_username = 'khlam'


    if not gitlab_token or not gitlab_username:
        raise Exception("GITLAB_TOKEN and GITLAB_USERNAME must be set")

    repos = get_github_repos(github_username)
    for repo in repos:
        create_or_update_gitlab_project(repo, gitlab_token, gitlab_username)
        print(f'Processed {repo["name"]}.')
        time.sleep(3)

if __name__ == '__main__':
    main()
