#!/usr/bin/env python

import jwt
import requests
import semver
import subprocess
import time

OWNER = 'worldpeaceio'
REPO = 'wordpress-integration'
BRANCH = 'develop'


def latest_wp_version():
    """Check WP API for latest version"""
    wp_version_check_api = 'https://api.wordpress.org/core/version-check/1.7/'
    response = requests.get(wp_version_check_api)
    response_json = response.json()
    return response_json.get('offers')[0].get('current')


def is_realease_tar_available(wp_version):
    """Check if the release tar.gz is available"""
    release_url = 'https://codeload.github.com/WordPress/wordpress-develop/tar.gz/{}'.format(wp_version)
    response = requests.get(release_url)
    return (response.status_code == 200)


def git_clone(repo_location, branch, repo_directory=None):
    """Git clone a repo"""
    output = subprocess.run(['git', 'clone', '--depth', '1', '--branch', branch, repo_location, repo_directory],
                            capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')
    return pretty_out + pretty_err


def current_docker_wp_version(repo_directory=None):
    """Check Makefile on github for current WP version in integration docker"""
    output = subprocess.run(['make', 'get_wp_version_makefile'], cwd=repo_directory, capture_output=True)
    return output.stdout.decode('utf8').strip()


def git_add_commit_and_push(commit_message, branch, repo_directory=None):
    # git add .
    output = subprocess.run(['git', 'add', '.'], cwd=repo_directory, capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')

    # git commit -m "..."
    output = subprocess.run(['git', 'commit', '-m', commit_message], cwd=repo_directory, capture_output=True)
    pretty_out += output.stdout.decode('utf8')
    pretty_err += output.stderr.decode('utf8')

    # git push origin master
    output = subprocess.run(['git', 'push', 'origin', branch], cwd=repo_directory, capture_output=True)
    pretty_out += output.stdout.decode('utf8')
    pretty_err += output.stderr.decode('utf8')

    return pretty_out + pretty_err


def update_makefile(new_version, repo_directory=None):
    """ Set WordPress version in Makefile to the specified version"""
    output = subprocess.run(
        ['make', 'update_wp_version_makefile', 'version="{}"'.format(new_version)],
        cwd=repo_directory,
        capture_output=True
    )
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')
    return pretty_out + pretty_err


def update_dockerfile(repo_directory=None):
    output = subprocess.run(['make', 'update_wp_version_dockerfile'], cwd=repo_directory, capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')
    return pretty_out + pretty_err


def update_readme(repo_directory=None):
    output = subprocess.run(['make', 'generate_readme'], cwd=repo_directory, capture_output=True)
    pretty_out = output.stdout.decode('utf8')
    pretty_err = output.stderr.decode('utf8')
    return pretty_out + pretty_err


def generate_jwt(app_key):
    github_app_id = '23151'
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time() + (10 * 60)),
        'iss': github_app_id,
    }
    return jwt.encode(payload, app_key, algorithm='RS256')


def fetch_github_token(github_jwt):
    github_installation_id = '588987'
    url = 'https://api.github.com/app/installations/{}/access_tokens'.format(github_installation_id)
    headers = {
        'Authorization': 'Bearer {}'.format(github_jwt.decode('utf8')),
        'Accept': 'application/vnd.github.machine-man-preview+json',
    }
    response = requests.post(url, headers=headers)
    return response.json().get('token')


def normalize_semver(version):
    """Fix WordPress minor 0 releases that don't adhear to semver"""
    return version if version.count('.') == 2 else '{}.0'.format(version)


if __name__ == "__main__":
    """
    Check for release availablility. If a new release is available, clone, modify and push the update to Github.
    """
    print('WordPress Integration Develop Updater starting')

    # Fetch github secrets
    with open('/secrets/github_app_key.pem', 'r') as pem:
        github_app_key = pem.read()
        print('Github secret has been read')

    generated_jwt = generate_jwt(github_app_key)
    print('JWT has been generated')

    token = fetch_github_token(generated_jwt)
    print('Github token received')

    # Clone repo
    repo_location = 'https://x-access-token:{}@github.com/{}/{}.git'.format(token, OWNER, REPO)
    output = git_clone(repo_location, BRANCH, REPO)
    print(output)
    print('Cloned {} branch of {}/{} '.format(BRANCH, OWNER, REPO))

    # Check WP versions
    integration_docker_wp_version = current_docker_wp_version(REPO)
    print('WordPress Integration Docker WP version at {}'.format(integration_docker_wp_version))

    api_wp_version = latest_wp_version()
    print('Latest API WP version at {}'.format(api_wp_version))

    # Ensure versions follow semver
    api_wp_semver = normalize_semver(api_wp_version)
    integration_docker_wp_semver = normalize_semver(integration_docker_wp_version)
    if semver.compare(api_wp_semver, integration_docker_wp_semver) > 0:
        print('An update from {} to {} is available'.format(integration_docker_wp_version, api_wp_version))
        if is_realease_tar_available(api_wp_version):
            print('{} release archive is available'.format(api_wp_version))

            # Update Makefile WP version
            output = update_makefile(api_wp_version, REPO)
            print(output)

            # Update WP version in the Dockerfile
            output = update_dockerfile(REPO)
            print(output)

            # Update README with new tags
            output = update_readme(REPO)
            print(output)
            print('README.md updated')

            # add, commit, and push changes
            commit_message = 'Updating WordPress to {}'.format(api_wp_version)
            output = git_add_commit_and_push(commit_message, BRANCH, REPO)
            print(output)
            print('Changes have been pushed to the {} branch of {}/{}'.format(BRANCH, OWNER, REPO))
        else:
            print('Release archive for {} is not yet available'.format(api_wp_version))
    else:
        print('Currently at {}, no updates are available'.format(api_wp_version))
