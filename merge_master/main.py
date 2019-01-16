#!/usr/bin/env python

import jwt
import os
import re
import requests
import semver
import subprocess
import time

OWNER = 'worldpeaceio'
REPO = 'wordpress-integration'
DEVELOP_BRANCH = 'develop'
PROD_BRANCH = 'master'


def check_develop_branch_status():
    """Check develop branch for CI status and most recent commit ID"""
    develop_branch_status_api = 'https://api.github.com/repos/{}/{}/commits/{}/statuses'.format(OWNER, REPO, DEVELOP_BRANCH)
    response = requests.get(develop_branch_status_api)
    response_json = response.json()
    most_recent_status = response_json[0]
    status_url = most_recent_status.get('url')
    status_state = most_recent_status.get('state')
    return status_state, status_url


def get_commit_id_from_status_url(url):
    """
    Gets commit ID from a URL like
    https://api.github.com/repos/worldpeaceio/wordpress-integration/statuses/45ac8810372444b0b0cb8111d2d43a7479541fbd
    """
    return url.split('/')[-1]


def get_prod_most_recent_commit_id():
    prod_branch_commit_api = 'https://api.github.com/repos/{}/{}/commits?sha={}'.format(OWNER, REPO, PROD_BRANCH)
    response = requests.get(prod_branch_commit_api)
    response_json = response.json()
    return response_json[0].get('sha')


def git_clone(repo_location, branch, repo_directory=None):
    """Git clone a repo"""
    output = subprocess.run(['git', 'clone', '--depth', '1', '--branch', branch, repo_location, repo_directory], capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')
    return pretty_out + pretty_err


def git_fetch_and_push(branch, repo_directory=None):
    # git fetch origin master
    output = subprocess.run(['git', 'fetch', 'origin', branch], cwd=repo_directory, capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')

    # git push origin master
    output = subprocess.run(['git', 'push', 'origin', branch], cwd=repo_directory, capture_output=True)
    pretty_out += output.stdout.decode('utf8')
    pretty_err += output.stderr.decode('utf8')

    return pretty_out + pretty_err


def generate_jwt(app_key):
    github_app_id = '23151'
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time() + (10 * 60)),
        'iss': github_app_id,
    }
    return jwt.encode(payload, app_key, algorithm='RS256')


def fetch_github_token(jwt):
    github_installation_id = '588987'
    url = 'https://api.github.com/app/installations/{}/access_tokens'.format(github_installation_id)
    headers = {
        'Authorization': 'Bearer {}'.format(jwt.decode('utf8')),
        'Accept': 'application/vnd.github.machine-man-preview+json',
    }
    response = requests.post(url, headers=headers)
    return response.json().get('token')


if __name__ == "__main__":
    """
    If develop branch is ahead of master and CI is passing then merge develop to master.
    """
    print('WordPress Integration Merge Master starting')

    dev_branch_state, dev_branch_url = check_develop_branch_status()
    dev_branch_commit_id = get_commit_id_from_status_url(dev_branch_url)
    print('{} branch of {}/{} at commit ID {}'.format(DEVELOP_BRANCH, OWNER, REPO, dev_branch_commit_id))

    prod_branch_commit_id = get_prod_most_recent_commit_id()
    print('{} branch of {}/{} at commit ID {}'.format(PROD_BRANCH, OWNER, REPO, prod_branch_commit_id))

    if dev_branch_commit_id != prod_branch_commit_id:
        # Check if dev branch is passing CI
        if dev_branch_state == 'success':
            print('Commit IDs differ and CI status is passing, starting clone and push')

            # Fetch github secrets
            with open('/secrets/github_app_key.pem', 'r') as pem:
                github_app_key = pem.read()
                print('Github secret has been read')
            
            jwt = generate_jwt(github_app_key)
            print('JWT has been generated')

            token = fetch_github_token(jwt)
            print('Github token received')

            # Clone repo
            repo_location = 'https://x-access-token:{}@github.com/{}/{}.git'.format(token, OWNER, REPO)
            output = git_clone(repo_location, DEVELOP_BRANCH, REPO)
            print(output)
            print('Cloned {} branch of {}/{}'.format(DEVELOP_BRANCH, OWNER, REPO))

            # Push changes in develop to master
            output = git_push(PROD_BRANCH, REPO)
            print(output)
            print('Pushed {} branch of {}/{} to {}'.format(DEVELOP_BRANCH, OWNER, REPO, PROD_BRANCH))
        else:
            print('CI status is currently {}'.format(dev_branch_state))
    else:
        print('{} and {} branches share the same commit ID'.format(DEVELOP_BRANCH, PROD_BRANCH))
