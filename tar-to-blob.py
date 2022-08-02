#!/usr/bin/env python3
#
# Tar-to-blob
#
# Run a file backup with tar and store as an Azure Blob Storage blob
#
# Copyright 2019 Peter Upfold
#
# Licensed under the Apache 2.0 Licence.

import os, uuid, sys
from azure.storage.blob import BlockBlobService
import yaml
import subprocess
import requests
import os

config_file = open('config.yml', 'r')
config = yaml.safe_load(config_file)

block_blob_service = BlockBlobService(account_name=config['account_name'], account_key=config['account_key'])

# run mysqldump
proc = subprocess.Popen(['/bin/tar', '--same-owner', '-czpvf', config['tar_file_output'], config['tar_file_directory']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

output, err = proc.communicate()


if proc.returncode != 0:
	print("Failed to run mysqldump")

	payload = { 'token': config['pushover_api_token'], 'user': config['pushover_user_key'], 'message': 'tar-to-blob.py backup returned exit code ' + str(proc.returncode) }
	requests.post(config['pushover_endpoint'], data=payload)

	sys.exit(proc.returncode)

block_blob_service.create_blob_from_path(config['container_name'], config['tar_blob_name'], config['tar_file_output'])

os.remove(config['tar_file_output'])