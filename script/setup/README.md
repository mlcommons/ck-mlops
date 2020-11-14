# CK-OpenVINO workflows

# Setup

## Set up system-level dependencies

Setting up system-level requires running system-specific scripts with superuser privileges (or under `sudo`).

### Ubuntu 18.04

```bash
$ sudo ./setup.ubuntu-18.04.sh
```

### Amazon Linux 2

```bash
$ sudo ./setup.amazonlinux-2.sh
```

## Set up user-space dependencies

Setting up user-space dependencies requires running the following script:
```bash
$ ./setup.user.sh
```

## Set up the ImageNet validation dataset (for ResNet)

### Register ImageNet with CK

Unfortunately, ImageNet can [no longer](https://github.com/mlperf/inference_policies/issues/125) be automatically downloaded.
If you have a copy of ImageNet in e.g. `/datasets/dataset-imagenet-ilsvrc2012-val/`, you can register it with CK as follows:

```bash
$ ck detect soft:dataset.imagenet.val \
--full_path=/datasets/dataset-imagenet-ilsvrc2012-val/ILSVRC2012_val_00000001.JPEG
```

### Create a calibration dataset

Choose one of the [two](https://github.com/mlperf/inference/tree/master/calibration/ImageNet)
calibration options with a tag: `mlperf.option1` or `mlperf.option2`:

```bash
$ ck install package --tags=dataset,imagenet,cal,mlperf.option1
```

### Copy labels to ImageNet (as expected by the program)

```bash
$ cp `ck locate env --tags=aux`/val.txt /datasets/dataset-imagenet-ilsvrc2012-val
```
