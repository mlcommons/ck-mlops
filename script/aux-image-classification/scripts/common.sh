TRAIN_DIR=./log

if [ "$2" = "" ]
then
        export PREFIX=
        export SUFFIX=

elif [ "$2" = "--profile" ]
then
        mkdir -p measurements
        export PREFIX="${CK_ENV_COMPILER_CUDA_BIN}/nvprof --profile-from-start off \
                --export-profile measurements/profile.nvvp -f --print-summary"
        export SUFFIX=" --nvprof_on=True"

elif [ "$2" = "--profile-fp32" ]
then
        mkdir -p measurements
        export PREFIX="${CK_ENV_COMPILER_CUDA_BIN}/nvprof --profile-from-start off \
                --export-profile measurements/profile.nvvp -f \
                --metrics single_precision_fu_utilization"
        export SUFFIX=" --nvprof_on=True"

else
        echo "Invalid input argument. Valid ones are --profile/--profile-fp32."; exit -1
fi
