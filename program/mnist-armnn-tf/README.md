# MNIST classification example for ArmNN/TF

## Compile (4 versions) :

```
$ ck compile program:mnist-armnn-tf                                     # compile reference implementation (works on Intel)

$ ck compile program:mnist-armnn-tf --env.USE_NEON                      # compile for using CPU acceleration (Arm only)

$ ck compile program:mnist-armnn-tf --env.USE_OPENCL                    # compile for using GPU acceleration (Arm only)

$ ck compile program:mnist-armnn-tf --env.USE_NEON --env.USE_OPENCL     # compile for using both CPU and GPU acceleration
```

## Run (4 versions, should match `USE_*` parameters during compilation) :

```
$ ck run program:mnist-armnn-tf --env.CK_FILE_NUMBER=0                  # run reference implementation (works on Intel)

$ ck run program:mnist-armnn-tf --env.USE_NEON                          # run for using CPU acceleration (Arm only)

$ ck run program:mnist-armnn-tf --env.USE_OPENCL --env.CK_FILE_NUMBER=0 # run for using GPU acceleration (Arm only)

$ ck run program:mnist-armnn-tf --env.USE_NEON --env.USE_OPENCL         # run for using both CPU and GPU acceleration
```

## Note:

`CK_FILE_NUMBER` is the file number in MNIST dataset (0..9999)
