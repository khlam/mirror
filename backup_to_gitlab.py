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
    project_name = f"{gitlab_username}/{repo['name']}"
    project_url_encoded = requests.utils.quote(project_name, safe="")
    check_project_url = f'https://gitlab.com/api/v4/projects/{project_url_encoded}'

    # Check if project already exists in GitLab
    project_response = requests.get(check_project_url, headers=headers)

    if project_response.status_code == 200:
        print(f"Repository {repo['name']} already exists in GitLab. Consider updating or using a different name.")
        return  # Skip creation and possibly handle updating here

    # Create the project if it doesn't exist
    print(f"Creating repository {repo['name']} in GitLab...")
    data = {
        'name': repo['name'],
        'description': repo['description'],
        'visibility': 'public',
        'import_url': repo['clone_url']
    }
    create_response = requests.post('https://gitlab.com/api/v4/projects', headers=headers, data=data)
    if create_response.status_code != 201:
        print(f'Failed to create GitLab project for {repo["name"]}. Status Code: {create_response.status_code}, Response: {create_response.text}')
        raise Exception(f'Failed to create GitLab project for {repo["name"]}')


def main():
    github_username = 'khlam' # Replace with your GitHub username
    gitlab_token = os.environ.get('GITLAB_TOKEN')
    gitlab_username = os.environ.get('GITLAB_USERNAME')

    if not gitlab_token or not gitlab_username:
        raise Exception("GITLAB_TOKEN and GITLAB_USERNAME must be set")

    repos = get_github_repos(github_username)
    for repo in repos:
        create_or_update_gitlab_project(repo, gitlab_token, gitlab_username)
        print(f'Processed {repo["name"]}.')
        time.sleep(3)

if __name__ == '__main__':
    main()
