import json

import requests
from tqdm import tqdm

token = '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'

def fetch_commit_details(repo_username, repo_name, commit_hash):
    url = f"https://api.github.com/repos/{repo_username}/{repo_name}/commits/{commit_hash}"
    response = requests.get(url, headers={'X-GitHub-Api-Version': '2022-11-28', 'Authorization': f'Bearer {token}'})
    if response.status_code != 200:
        print(f"Failed to get data: {response.status_code}")
        return None
    return response.json()


def generate_edit_from_patch(patch):
    edit = []
    for patch_part in patch:
        for line in patch_part.split('\n'):  # Splitting each patch part into multiple lines
            stripped_line = line.lstrip()
            if stripped_line.startswith('-') or stripped_line.startswith('+'):
                edit.append(stripped_line)
    return edit


def parse_commit_details(commit_data):
    commit_message = commit_data["commit"]["message"]
    patch_text = []
    files_list = []
    if "files" in commit_data:
        for file in commit_data["files"]:
            files_list.append(file["filename"])
            if "patch" in file:
                patch_text.append(file["patch"])
    repo_username = commit_data["html_url"].split('/')[-4]
    repo_name = commit_data["html_url"].split('/')[-3]
    commit_hash = commit_data["html_url"].split('/')[-1]
    edits = generate_edit_from_patch(patch_text)
    new_feature_data = ",".join(map(str, [len(edits), 1, 0, 3, 21, 0.10]))  # Placeholder values
    commit_info = {
        "new_feature": new_feature_data,
        "commitmessage": commit_message,
        "patch": patch_text,
        "edit": edits,
        "url": [f"https://api.github.com/repos/{repo_username}/{repo_name}/commits/{commit_hash}"],
        "files": files_list,
    }
    return commit_info


def save_to_json(data, filename):
    # check if folder exists
       
    with open(filename, 'w') as f:
        json.dump(data, f)

def generate_train_dataset():
    positive_urls_path = "positive_urls.txt"
    negative_urls_path = "negative_urls.txt"
    with open(positive_urls_path, "r") as f:
        positive_urls = f.read().splitlines()
    with open(negative_urls_path, "r") as f:
        negative_urls = f.read().splitlines()
    for pos_url, neg_url in tqdm(zip(positive_urls, negative_urls)):
        print(pos_url)
        print(neg_url)
        pos_commit_data = fetch_commit_details(repo_username=pos_url.split('/')[-4],
                                               repo_name=pos_url.split('/')[-3],
                                               commit_hash=pos_url.split('/')[-1])
        if pos_commit_data:
            parsed_data = parse_commit_details(pos_commit_data)
            if parsed_data:
                save_to_json(parsed_data, f'pos/{pos_url.split("/")[-1]}.json')
        neg_commit_data = fetch_commit_details(repo_username=neg_url.split('/')[-4],
                                               repo_name=neg_url.split('/')[-3],
                                               commit_hash=neg_url.split('/')[-1])
        if neg_commit_data:
            parsed_data = parse_commit_details(neg_commit_data)
            if parsed_data:
                save_to_json(parsed_data, f'neg/{neg_url.split("/")[-1]}.json')

def generate_experiment_data():
    path = "cryptopp_all_commits.txt"
    with open(path, "r") as f:
        all_urls = f.read().splitlines()
    for url in tqdm(all_urls):
        commit_data = fetch_commit_details(repo_username=url.split('/')[-4],
                                               repo_name=url.split('/')[-3],
                                               commit_hash=url.split('/')[-1])
        if commit_data:
            parsed_data = parse_commit_details(commit_data)
            if parsed_data:
                save_to_json(parsed_data, f'cryptopp/{url.split("/")[-1]}.json')
if __name__ == "__main__":
    generate_experiment_data()