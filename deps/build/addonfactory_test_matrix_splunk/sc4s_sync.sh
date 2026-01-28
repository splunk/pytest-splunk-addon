#!/bin/bash
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

current_tag=$(cat SC4S_matrix.conf | grep -oP 'VERSION\s*=\s*([0-9\.]+)')
echo $current_tag
re='VERSION\s*=\s*([0-9.]+)'
if [[ $current_tag =~ $re ]]
then
    current_tag_value=${BASH_REMATCH[1]}
fi
echo $current_tag_value

latest_tag=$(curl -s https://api.github.com/repos/splunk/splunk-connect-for-syslog/releases/latest | grep "tag_name" | cut -d : -f 2)
new_value=$(echo $latest_tag | rev | cut -c3- | rev)
new_value=$(echo $new_value | cut -c3-)
echo $new_value

pip install pip --upgrade
python -m pip install packaging

var=`python -c "from packaging import version; print('True' if(version.parse(str('$new_value')) > version.parse(str('$current_tag'))) else 'False')"`
echo $var

if [ "$var" = "True" ];
then

    git config --global user.email "addonfactory@splunk.com"
    git config --global user.name "Addon Factory template"
    BRANCH=test/sc4s-version-update
    git checkout -b $BRANCH   
    sed -i "s/$current_tag_value/$new_value/g" SC4S_matrix.conf
    git diff
    git add SC4S_matrix.conf
    git status
    git commit -m "test: new sc4s version $new_value update"
    git push -f --set-upstream origin $BRANCH
    git log | head
    git checkout master
    git merge test/sc4s-version-update
    git push origin master
    git branch -d test/sc4s-version-update
else
    echo "SC4S version update not required"
fi
