rem ck add repo:ck-experiments --quiet

rem NEED mlperf-mobilenets for experiments since hardwired in module:mlperf*

FOR /F "tokens=*" %%a in ('ck where repo:mlperf-mobilenets') do SET CK_HOST_REPO_EXPERIMENTS=%%a

echo %CK_HOST_REPO_EXPERIMENTS%

set CK_LOCAL_DOCKER_SCRIPT=docker-helper.sh
set CK_HOST_RUN_SCRIPT=%cd%\%CK_LOCAL_DOCKER_SCRIPT%
set CK_HOST_DATASETS=X:\datasets

docker run ^
       --volume %CK_HOST_REPO_EXPERIMENTS%:/home/ckuser/ck-experiments ^
       --volume %CK_HOST_RUN_SCRIPT%:/home/ckuser/%CK_LOCAL_DOCKER_SCRIPT% ^
       -it octoml/ck-mlperf-local-dashboard-demo2 ^
       "./%CK_LOCAL_DOCKER_SCRIPT%"
