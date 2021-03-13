#!/usr/bin/env python3
#
# Mysqldump-to-blob
#
# Run a mysqldump and store as an Azure Blob Storage blob
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
proc = subprocess.Popen(['/usr/bin/mysqldump', '-A', '--skip-extended-insert', '-r', config['mysqldump_file_output']], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
output, err = proc.communicate()


if proc.returncode != 0:
	print("Failed to run mysqldump")
	payload = { 'token': config['pushover_api_token'], 'user': config['pushover_user_key'], 'message': 'mysqldump-to-blob.py backup returned exit code ' + str(proc.returncode) }
	requests.post(config['pushover_endpoint'], data=payload)
	sys.exit(proc.returncode)

block_blob_service.create_blob_from_path(config['container_name'], config['blob_name'], config['mysqldump_file_output'])

os.remove(config['mysqldump_file_output'])