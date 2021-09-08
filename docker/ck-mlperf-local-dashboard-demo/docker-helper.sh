echo "======================================================================="
echo "Fixing access to datasets and ck-experiments ..."
echo ""
time sudo chmod -R 777 ck-experiments

echo "====================================================================="
echo "Adding external ck-experiments repository ..."
echo ""

ck add repo:ck-experiments --path=/home/ckuser/ck-experiments --quiet

ck ls repo

pwd

ls

# Download the MobileNet TF/TFLite models (non-quantized and quantized).
# https://github.com/mlperf/inference/blob/master/edge/object_classification/mobilenets/tflite/README.md#install-the-mobilenet-models-for-tflite
ck install package --tags=image-classification,model,tf,tflite,mlperf,mobilenet,non-quantized,from-zenodo
ck install package --tags=image-classification,model,tf,tflite,mlperf,mobilenet,quantized,from-google

# Benchmark the performance of the non-quantized MobileNet model.
ck benchmark program:image-classification-tflite \
--repetitions=10 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=2 \
--dep_add_tags.weights=mlperf,image-classification,mobilenet,non-quantized,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-mobilenet-non-quantized-tflite-performance \
--tags=mlperf,image-classification,mobilenet,non-quantized,tflite,performance \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the accuracy of the non-quantized MobileNet model.
ck benchmark program:image-classification-tflite \
--repetitions=1 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=500 \
--dep_add_tags.weights=mlperf,image-classification,mobilenet,non-quantized,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-mobilenet-non-quantized-tflite-accuracy \
--tags=mlperf,image-classification,mobilenet,non-quantized,tflite,accuracy \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the performance of the quantized MobileNet model.
ck benchmark program:image-classification-tflite \
--repetitions=10 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=2 \
--dep_add_tags.weights=mlperf,image-classification,mobilenet,quantized,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-mobilenet-quantized-tflite-performance \
--tags=mlperf,image-classification,mobilenet,quantized,tflite,performance \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the accuracy of the quantized MobileNet model.
ck benchmark program:image-classification-tflite \
--repetitions=1 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=500 \
--dep_add_tags.weights=mlperf,image-classification,mobilenet,quantized,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-mobilenet-quantized-tflite-accuracy \
--tags=mlperf,image-classification,mobilenet,quantized,tflite,accuracy \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Download the ResNet TFLite models (with and without the ArgMax operator).
# https://github.com/mlperf/inference/blob/master/edge/object_classification/mobilenets/tflite/README.md#install-the-resnet-model
ck install package --tags=image-classification,model,tflite,mlperf,resnet,downloaded,with-argmax
ck install package --tags=image-classification,model,tflite,mlperf,resnet,downloaded,no-argmax

# Benchmark the performance of the ResNet model with the ArgMax operator.
ck benchmark program:image-classification-tflite \
--repetitions=10 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=2 \
--dep_add_tags.weights=mlperf,image-classification,resnet,with-argmax,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-resnet-with-argmax-tflite-performance \
--tags=mlperf,image-classification,resnet,with-argmax,tflite,performance \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the accuracy of the ResNet model with the ArgMax operator.
ck benchmark program:image-classification-tflite \
--repetitions=1 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=500 \
--dep_add_tags.weights=mlperf,image-classification,resnet,with-argmax,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-resnet-with-argmax-tflite-accuracy \
--tags=mlperf,image-classification,resnet,with-argmax,tflite,accuracy \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the performance of the ResNet model without the ArgMax operator.
ck benchmark program:image-classification-tflite \
--repetitions=10 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=2 \
--dep_add_tags.weights=mlperf,image-classification,resnet,no-argmax,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-resnet-no-argmax-tflite-performance \
--tags=mlperf,image-classification,resnet,no-argmax,tflite,performance \
--skip_print_timers --skip_stat_analysis --process_multi_keys

# Benchmark the accuracy of the ResNet model without the ArgMax operator.
ck benchmark program:image-classification-tflite \
--repetitions=1 --env.CK_BATCH_SIZE=1 --env.CK_BATCH_COUNT=500 \
--dep_add_tags.weights=mlperf,image-classification,resnet,no-argmax,tflite \
--record --record_repo=ck-experiments --record_uoa=mlperf-image-classification-resnet-no-argmax-tflite-accuracy \
--tags=mlperf,image-classification,resnet,no-argmax,tflite,accuracy \
--skip_print_timers --skip_stat_analysis --process_multi_keys
