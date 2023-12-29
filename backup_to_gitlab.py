import os
import requests

def get_github_repos(github_username):
    repos = []
    page = 1
    while True:
        response = requests.get(f'https://api.github.com/users/{github_username}/repos?type=public&page={page}&per_page=100')
        if response.status_code == 200:
            new_repos = response.json()
            if not new_repos:
                break
            repos.extend(new_repos)
            page += 1
        else:
            raise Exception('Failed to fetch GitHub repositories')
    return repos


def create_or_update_gitlab_project(repo, gitlab_token, gitlab_username):
    headers = {'Private-Token': gitlab_token}
    project_name = f"{gitlab_username}/{repo['name']}"
    project_url_encoded = requests.utils.quote(project_name, safe="")
    check_project_url = f'https://gitlab.com/api/v4/projects/{project_url_encoded}'

    # Check if project already exists in GitLab
    project_response = requests.get(check_project_url, headers=headers)

    if project_response.status_code == 200:
        print(f"Repository {repo['name']} exists in GitLab. Deleting and re-creating...")
        # Delete the existing project
        delete_response = requests.delete(check_project_url, headers=headers)
        if delete_response.status_code not in [202, 204]: # Success or No Content
            raise Exception(f'Failed to delete existing GitLab project for {repo["name"]}')

    # Whether deleted or not, create the project
    print(f"Creating repository {repo['name']} in GitLab...")
    data = {
        'name': repo['name'],
        'description': repo['description'],
        'visibility': 'public',
        'import_url': repo['clone_url']
    }
    create_response = requests.post('https://gitlab.com/api/v4/projects', headers=headers, data=data)
    if create_response.status_code not in [201]:  # Created
        raise Exception(f'Failed to create GitLab project for {repo["name"]}')


def main():
    github_username = 'khlam' # Replace with your GitHub username
    gitlab_token = os.environ.get('GITLAB_TOKEN')
    gitlab_username = os.environ.get('GITLAB_USERNAME')

    repos = get_github_repos(github_username)
    for repo in repos:
        create_or_update_gitlab_project(repo, gitlab_token, gitlab_username)
        print(f'Processed {repo["name"]}.')

if __name__ == '__main__':
    main()
