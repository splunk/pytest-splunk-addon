# addonfactory_test_matrix_splunk
This repository is used to control the specific versions of Splunk Docker used in add-on test matrix.

The format of this repository list a single conf file in the root 'splunk_matrix.conf' with a stanza in the pattern of MAJOR.MINOR and a attribute VERSION=semver 

We have added Gihub Action file which run on schedule configured time for checking new version of SC4S and Splunk released or not and based on that it will run workflow and update the version details directly in master branch.

```
SC4S Version
[1]
VERSION=1.51.6
```

```
Splunk Version
[8.1]
VERSION=8.1.1
```
# Additional notes
