export CK_HOST_REPO_EXPERIMENTS=`ck where repo:ck-experiments`

echo ${CK_HOST_REPO_EXPERIMENTS}

export CK_LOCAL_DOCKER_SCRIPT=docker-helper.sh
export CK_HOST_RUN_SCRIPT=$PWD/${CK_LOCAL_DOCKER_SCRIPT}
export CK_HOST_DATASETS=~/datasets

docker run \
       --volume ${CK_HOST_REPO_EXPERIMENTS}:/home/ckuser/ck-experiments \
       --volume ${CK_HOST_RUN_SCRIPT}:/home/ckuser/${CK_LOCAL_DOCKER_SCRIPT} \
       -it octoml/ck-mlperf-local-dashboard-demo2 \
       "./${CK_LOCAL_DOCKER_SCRIPT}"
