import re

import requests
from tqdm import tqdm

token = ''


def get_paginated_data(url, all_pages=False, max_pages=100):
    next_pattern = r'(?<=<)([^>]*)(?=>; rel="next")'
    pages_remaining = True
    data = []
    page_count = 0

    while pages_remaining:
        try:
            response = requests.get(url, params={'per_page': 100},
                                    headers={'X-GitHub-Api-Version': '2022-11-28', 'Authorization': f'Bearer {token}'})
            response.raise_for_status()
            parsed_data = parse_data(response.json())
            data.extend(parsed_data)

            page_count += 1
            print(f"Page {page_count} fetched")
            if not all_pages and page_count >= max_pages:
                break

            link_header = response.headers.get('link')
            pages_remaining = 'rel="next"' in link_header if link_header else False

            if pages_remaining:
                match = re.search(next_pattern, link_header)
                if match:
                    url = match.group(0)
                else:
                    break
        except requests.RequestException as e:
            print(f"An error occurred: {e}")
            break

    return data


def parse_data(data):
    if isinstance(data, list):
        return data
    if not data:
        return []
    keys_to_delete = ['incomplete_results', 'repository_selection', 'total_count']
    for key in keys_to_delete:
        data.pop(key, None)
    namespace_key = next(iter(data), None)
    if namespace_key:
        return data[namespace_key]
    return []


def get_previous_commits(owner, repo, commit_sha, num_commits=5):
    url = f"https://api.github.com/repos/{owner}/{repo}/commits"
    params = {
        'sha': commit_sha,
        'per_page': num_commits
    }
    response = requests.get(url, params=params,
                            headers={'X-GitHub-Api-Version': '2022-11-28', 'Authorization': f'Bearer {token}'})
    if response.status_code == 200:
        commits = response.json()
        return commits[3]
    else:
        return f"Error: {response.status_code}"


if __name__ == "__main__":
    url = 'https://api.github.com/advisories'
    # token params
    advisory_data = get_paginated_data(url,
                                       all_pages=False)  # Set `all_pages` to `False` to get only the first 100 pages
    positive_urls = []
    negative_urls = []
    # extract references from data
    for advisory in tqdm(advisory_data):
        for reference_url in advisory['references']:
            if "commit" in reference_url and "github.com" in reference_url:
                vulnerable_fix_commit_url = reference_url  # html url here
                cwe_id = advisory['cwes'][0]['cwe_id']
                # find the previous commit hash by GitHub api
                commit_hash = vulnerable_fix_commit_url.split('/')[-1]
                owner = vulnerable_fix_commit_url.split('/')[-4]
                repo = vulnerable_fix_commit_url.split('/')[-3]
                try:
                    commit_description = get_previous_commits(owner, repo, commit_hash)
                    non_vulnerable_commit_url = commit_description['html_url']
                    if non_vulnerable_commit_url == vulnerable_fix_commit_url or non_vulnerable_commit_url in positive_urls:
                        continue
                    positive_urls.append(vulnerable_fix_commit_url)
                    negative_urls.append(non_vulnerable_commit_url)
                except Exception as e:
                    print(commit_description)
                    print(f"Error finding previous commit: {e}")
            # save urls to file separately
    with open("positive_urls.txt", "w") as f:
        for url in positive_urls:
            f.write(url + "\n")
    with open("negative_urls.txt", "w") as f:
        for url in negative_urls:
            f.write(url + "\n")
