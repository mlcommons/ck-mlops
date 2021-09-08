#! /bin/bash

echo "*********************************************************"

export CK_PROGRAM_TMP_DIR=$PWD

${CK_ENV_COMPILER_PYTHON_FILE} -m pip freeze > ck-pip-freeze.txt
ck > ck-version.txt

if [ -f "user-generated.conf" ]; then
  cp -f user-generated.conf user.conf
elif [ "x${CK_MLPERF_USER_CONF}" != "x" ] ; then
  cp -f ${CK_MLPERF_USER_CONF} user.conf
else
  # reference app uses command line instead of user.conf
  # However we need to generate an empty file 
  # so that the MLPerf checker doesn't complain ;)
  echo "# empty" > user.conf
fi

if [ "x${CK_MLPERF_AUDIT_CONF}" != "x" ] ; then
  cp -f ${CK_MLPERF_AUDIT_CONF} audit.config
fi

if [ "${CK_ENV_OCTOMIZER_WHEEL}" != "" ] ; then
  export MODEL_DIR=${CK_ENV_OCTOMIZER_WHEEL}
else
  export MODEL_DIR=${ML_MODEL_ROOT}
fi

export DATA_DIR=${CK_ENV_DATASET_ROOT}
