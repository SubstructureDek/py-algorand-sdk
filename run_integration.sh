#!/usr/bin/env bash

set -e

rootdir=`dirname $0`
pushd $rootdir

# Reset test harness
rm -rf test-harness
git clone --single-branch --branch feature/supportRemoteDocker https://github.com/algorand/algorand-sdk-testing.git test-harness

## Copy feature files into the project resources
mkdir -p test/features
cp -r test-harness/features/* test/features

# Build SDK testing environment
docker build -t py-sdk-testing -f Dockerfile "$(pwd)"

# Start test harness environment
./test-harness/scripts/up.sh

while [ $(docker run --network test-harness_sdk-harness --rm curlimages/curl:7.81.0 -sL -w "%{http_code}\\n" "http://indexer-221-1:8980/v2/accounts" --connect-timeout 3 --max-time 5) -ne "200" ]
do
  sleep 1
done

# Launch SDK testing
docker run -it \
     --network test-harness_sdk-harness \
     py-sdk-testing:latest 
