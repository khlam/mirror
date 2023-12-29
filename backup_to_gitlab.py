import os
import requests

def get_github_repos(github_username):
    response = requests.get(f'https://api.github.com/users/{github_username}/repos?type=public')
    if response.status_code == 200:
        return response.json()
    else:
        raise Exception('Failed to fetch GitHub repositories')

def create_or_update_gitlab_project(repo, gitlab_token, gitlab_username):
    headers = {'Private-Token': gitlab_token}
    project_name = f"{gitlab_username}/{repo['name']}"
    check_project_url = f'https://gitlab.com/api/v4/projects/{requests.utils.quote(project_name, safe="")}'

    # Check if project already exists in GitLab
    project_response = requests.get(check_project_url, headers=headers)

    if project_response.status_code == 200:
        print(f"Repository {repo['name']} exists in GitLab. Updating...")
        # Update project settings if needed, or perform other update actions
        # For instance, trigger a pull mirror update, etc.
    else:
        print(f"Creating repository {repo['name']} in GitLab...")
        data = {
            'name': repo['name'],
            'description': repo['description'],
            'visibility': 'public',
            'import_url': repo['clone_url']
        }
        create_response = requests.post('https://gitlab.com/api/v4/projects', headers=headers, data=data)
        if create_response.status_code not in [201]:
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
