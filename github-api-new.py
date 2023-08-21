#The requests lib will allow HTTP req to GitHub API
import requests
#Create classes of the objects you want to analyze in the future: repos, contributors, PR, etc
class Repository:
    def __init__(self, name, owner, description, stars, forks):
        self.name = name
        self.owner = owner
        self.description = description
        self.stars = stars
        self.forks = forks
        self.contributors = []
        self.issues = []
        self.pull_requests = []
        self.commits = []

class Contributor:
    def __init__(self, login, contributions):
        self.login = login
        self.contributions = contributions

class PullRequest:
    def __init__(self, title, state, created_at, updated_at):
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at

class Issue:
    def __init__(self, title, state, created_at, updated_at):
        self.title = title
        self.state = state
        self.created_at = created_at
        self.updated_at = updated_at
class Commit:
    def __init__(self, sha, author, message, date):
        self.sha = sha  #Sha is the commit hash identifier
        self.author = author
        self.message = message
        self.date = date
#This class is the responsible for authentication with your GitHub info, and also have the methods that make the HTTP calls to GitHub API
class GitHubAnalyzer:
    def __init__(self, token):
        self.token = token
        self.headers = {'Authorization': f'token {self.token}'}

    def get_repositories(self, username):
        url = f'https://api.github.com/users/{username}/repos'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200: #Successfull request
            repositories = response.json() #You'll get the response as a JSON file
            return repositories
        else:
            print(f"Error fetching repositories: {response.status_code}")
            return []

    def get_contributors(self, owner, repo):
        url = f'https://api.github.com/repos/{owner}/{repo}/contributors'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            contributors = response.json()
            return contributors
        else:
            print(f"Error fetching contributors: {response.status_code}")
            return []

    def get_issues(self, owner, repo):
        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            issues = response.json()
            return issues
        else:
            print(f"Error fetching issues: {response.status_code}")
            return []

    def get_pull_requests(self, owner, repo):
        url = f'https://api.github.com/repos/{owner}/{repo}/pulls'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            pull_requests = response.json()
            return pull_requests
        else:
            print(f"Error fetching pull requests: {response.status_code}")
            return []

    def get_commits(self, owner, repo):
        url = f'https://api.github.com/repos/{owner}/{repo}/commits'
        response = requests.get(url, headers=self.headers)
        if response.status_code == 200:
            commits_data = response.json()
            commits = []
            for commit_data in commits_data:
                commit = Commit(
                    sha=commit_data['sha'],
                    author=commit_data['commit']['author']['name'],
                    message=commit_data['commit']['message'],
                    date=commit_data['commit']['author']['date']
                )
                commits.append(commit)
            return commits
        else:
            print(f"Error fetching commits: {response.status_code}")
            return []
#Prompt user for GitHub Token and username
username = input('Enter your GitHub Username: ')
github_token = input('Enter your GitHub Token: ')

#Create an object of GitHubAnalyzer class
github_analyzer = GitHubAnalyzer(github_token)

#Get a list of dicts containing the data of each repo
repositories_data = github_analyzer.get_repositories(username)

#Create repos list containing the Repository objects, which will have the other objects (contributors, pr, etc)
repositories = []
for repo_data in repositories_data:
    if not repo_data['fork'] : #The forked repos are not included
        repo = Repository(
            name=repo_data['name'],
            owner=repo_data['owner']['login'],
            description=repo_data['description'],
            stars=repo_data['stargazers_count'],
            forks=repo_data['forks_count']
        )
        contributors = github_analyzer.get_contributors(repo.owner, repo.name)
        repo.contributors = [Contributor(login=contributor['login'], contributions=contributor['contributions']) for contributor in contributors]

        pull_requests = github_analyzer.get_pull_requests(repo.owner, repo.name)
        repo.pull_requests = [PullRequest(title=pr['title'], state=pr['state'], created_at=pr['created_at'], updated_at=pr['updated_at']) for pr in pull_requests]

        issues = github_analyzer.get_issues(repo.owner, repo.name)
        repo.issues = [Issue(title=issue['title'], state=issue['state'], created_at=issue['created_at'], updated_at=issue['updated_at']) for issue in issues]

        commits = github_analyzer.get_commits(repo.owner, repo.name)
        repo.commits = [Commit(sha=commit.sha, author=commit.author, message=commit.message, date=commit.date) for commit in commits]

        repositories.append(repo)

#Print results
for repo in repositories:
    print(f"Repository: {repo.name}")
    print(f"Owner: {repo.owner}")
    print(f"Description: {repo.description}")
    print(f"Stars: {repo.stars}")

    print("Contributors:")
    for contributor in repo.contributors:
        print(f"- {contributor.login} ({contributor.contributions} contributions)")

    print("Pull Requests:")
    for pr in repo.pull_requests:
        print(f"- {pr.title} ({pr.state}) Created: {pr.created_at}, Updated: {pr.updated_at}")

    print("Open Issues:")
    for issue in repo.issues:
        print(f"- {issue.title} ({issue.state}) Created: {issue.created_at}, Updated: {issue.updated_at}")

    print("Commits:")
    for commit in repo.commits:
        print(f"- SHA: {commit.sha}")
        print(f"  Author: {commit.author}")
        print(f"  Message: {commit.message}")
        print(f"  Date: {commit.date}")