from github import Github
from config import config

# Login using the token
g = Github(config.GITHUB_TOKEN)


def approve_pull_request(repo_name, pr_number):
    repo = g.get_repo(repo_name)
    pr = repo.get_pull(pr_number)
    pr.create_review(event="APPROVE")  # Approve the pull request