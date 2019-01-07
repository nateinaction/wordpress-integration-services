#!/usr/bin/env python

import jwt
import os
import re
import requests
import semver
import subprocess
import time

MAKEFILE_VERSION_REGEX = r'^WORDPRESS_VERSION := (?P<version>[\d\.]+)'


def current_docker_wp_version():
    """Check Makefile on github for current WP version in integration docker"""
    wp_version_check_makefile = 'https://raw.githubusercontent.com/nateinaction/wordpress-integration/master/Makefile'
    response = requests.get(wp_version_check_makefile)
    for line in response.text.splitlines():
        wp_version_match = re.match(MAKEFILE_VERSION_REGEX, line)
        if wp_version_match:
            return wp_version_match.group(1)


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


def git_clone(token):
    repo_url = 'https://x-access-token:{}@github.com/nateinaction/wordpress-integration.git'.format(token)
    output = subprocess.run(['git', 'clone', repo_url], capture_output=True)
    return output.stdout.decode('utf8') + output.stderr.decode('utf8')


def git_add_commit_and_push(version):
    commit_message = 'Updating WordPress to {}'.format(version)

    # git add .
    output = subprocess.run(['git', 'add', '.'], cwd='wordpress-integration', capture_output=True)
    pretty_output = output.stdout.decode('utf8') + output.stderr.decode('utf8')

    # git commit -m "..."
    output = subprocess.run(['git', 'commit', '-m', commit_message], cwd='wordpress-integration', capture_output=True)
    pretty_output += output.stdout.decode('utf8') + output.stderr.decode('utf8')

    # git push origin master
    output = subprocess.run(['git', 'push', 'origin', 'master'], cwd='wordpress-integration', capture_output=True)
    pretty_output += output.stdout.decode('utf8') + output.stderr.decode('utf8')
    return pretty_output


def update_makefile(new_version, makefile_filename):
    """ Set WordPress version in Makefile to the specified version"""
    print('Setting WordPress version in {} to {}'.format(makefile_filename, new_version))

    with open(makefile_filename, 'r') as f:
        contents = f.readlines()

    for line_num, line in enumerate(contents):
        wp_version_match = re.match(MAKEFILE_VERSION_REGEX, line)
        if wp_version_match:
            contents[line_num] = 'WORDPRESS_VERSION := {}\n'.format(new_version)

    with open(makefile_filename, 'w') as f:
        f.writelines(contents)


def update_dockerfiles():
    output = subprocess.run(['make', 'update_wp_version_all'], cwd='wordpress-integration', capture_output=True)
    return output.stdout.decode('utf8') + output.stderr.decode('utf8')


def generate_jwt(app_key):
    github_app_id = '23151'
    payload = {
        'iat': int(time.time()),
        'exp': int(time.time() + (10 * 60)),
        'iss': github_app_id,
    }
    return jwt.encode(payload, app_key, algorithm='RS256')


def fetch_github_token(jwt):
    github_installation_id = '560500'
    url = 'https://api.github.com/app/installations/{}/access_tokens'.format(github_installation_id)
    headers = {
        'Authorization': 'Bearer {}'.format(jwt.decode('utf8')),
        'Accept': 'application/vnd.github.machine-man-preview+json',
    }
    response = requests.post(url, headers=headers)
    return response.json().get('token')


if __name__ == "__main__":
    """
    Check for release availablility. If a new release is available, clone, modify and push the update to Github.
    """
    print('WordPress Integration Docker Updater starting')

    integration_docker_wp_version = current_docker_wp_version()
    print('WordPress Integration Docker WP version at {}'.format(integration_docker_wp_version))

    api_wp_version = latest_wp_version()
    print('Latest API WP version at {}'.format(api_wp_version))

    if (semver.compare(api_wp_version, integration_docker_wp_version) > 0):
        print('An update from {} to {} is available'.format(integration_docker_wp_version, api_wp_version))
        if (is_realease_tar_available(api_wp_version)):
            print('{} release archive is available'.format(api_wp_version))
            # Fetch github secrets
            with open('/secrets/github_app_key.pem', 'r') as pem:
                github_app_key = pem.read()
                print('Github secret has been read')
            
            jwt = generate_jwt(github_app_key)
            print('JWT has been generated')

            token = fetch_github_token(jwt)
            print('Github token received')

            # Clone repo
            output = git_clone(token)
            print(output)

            # Update Makefile WP version
            update_makefile(api_wp_version, 'wordpress-integration/Makefile')
            print('Makefile WP version updated to {}'.format(api_wp_version))

            # Update WP version in Dockerfiles
            output = update_dockerfiles()
            print(output)

            # add, commit, and push changes
            output = git_add_commit_and_push(api_wp_version)
            print(output)
            exit
        print('Release archive for {} is not yet available'.format(api_wp_version))
        exit
    print('Currently at {}, no updates are available'.format(integration_docker_wp_version))
    exit
