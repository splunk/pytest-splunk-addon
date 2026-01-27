#!/bin/bash
# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# echo all the commands
set -x

REPOORG=splunk
if [[  $GITHUB_USER && ${GITHUB_USER-x} ]]
then
    echo "GITHUB_USER Found"
else
    echo "GITHUB_USER Not Found"
    exit 1
fi
if [[  $GITHUB_TOKEN && ${GITHUB_TOKEN-x} ]]
then
    echo "GITHUB_TOKEN Found"
else
    echo "GITHUB_TOKEN Not Found"
    exit 1
fi

pip install pip --upgrade
python -m pip install -r requirements.txt
splunk_version=$(python splunk_matrix_update.py)
echo $splunk_version

if [ "$splunk_version" = "True" ];
then

    git config --global user.email "addonfactory@splunk.com"
    git config --global user.name "Addon Factory template"
    BRANCH=test/splunk-version-update
    git checkout -b $BRANCH
    git diff
    git add .
    git status
    git commit -m "test: splunk build update"
    git push -f --set-upstream origin $BRANCH
    git checkout master
    git merge test/splunk-version-update
    git push origin master
    git branch -d test/splunk-version-update
else
    echo "Splunk build update not required"
fi
