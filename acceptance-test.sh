#stop the script on error
set -e

#set the host to connect during tests (in gitlab CI must use 'docker')
if [ -z ${TEST_HOST+x} ]; then
  echo "TEST_HOST is unset, will use localhost";
  export TEST_HOST=localhost
fi

#set the pytest command
if [ -z ${PYTEST_COMMAND+x} ]; then
  echo "PYTEST_COMMAND is unset, will use pytest-3";
  export PYTEST_COMMAND=pytest-3
fi

# export TEST_USING_SQLITE=true
# set the environment
echo "USING SQLITE"
export db_type=sqlite
export meal_db_path=/tmp/acceptance-test.db

#run tests
$PYTEST_COMMAND -m "acceptance"

