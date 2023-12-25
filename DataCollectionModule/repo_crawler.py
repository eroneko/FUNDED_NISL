import requests
from ghsa_crawler import token
def get_all_commits(repo_owner, repo_name):
    commits_url = f"https://api.github.com/repos/{repo_owner}/{repo_name}/commits"
    commits = []
    page = 1
    while True:
        print(f"Page {page}")
        response = requests.get(commits_url, params={'per_page': 100, 'page': page}, headers={'X-GitHub-Api-Version': '2022-11-28', 'Authorization': f'Bearer {token}'})
        if response.status_code != 200:
            print(f"Failed to fetch commits: {response.status_code}")
            break

        data = response.json()
        if not data:  # No more data to process
            break

        for commit in data:
            commits.append(commit)
        page += 1

    return commits

def filter_vulnerability_commits(commits):
    vulnerability_keywords = ['fix', 'bug', 'security', 'vulnerability', 'cve', 'patch']
    vulnerability_commits = []
    for commit in commits:
        try:
            commit_message = commit['commit']['message'].lower()
            if any(keyword in commit_message for keyword in vulnerability_keywords):
                vulnerability_commits.append(commit['html_url'])
        except:
            pass

    return vulnerability_commits

# 示例使用
repo_owner = 'weidai11'  # 仓库所有者
repo_name = 'cryptopp'  # 仓库名称
all_commits = get_all_commits(repo_owner, repo_name)
all_commits = filter_vulnerability_commits(all_commits)
# save to txt
with open(f'{repo_name}_all_commits.txt', 'w') as f:
    for commit in all_commits:
        f.write(commit + '\n')
