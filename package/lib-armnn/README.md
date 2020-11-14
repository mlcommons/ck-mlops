# CK package for ArmNN library

## This package builds and installs a desired version of ArmNN library

Selection of the desired release, desired frontend support and desired backend is now done via combining relevant tags.

### Release tags:

Please select exactly one of the following: { `release` | `rel.18.08` | `rel.18.11` | `rel.19.02` | `rel.19.05` | `dev` }

### Frontend tags:

Please select any combination, but at least one, of the following: { `tf` , `tflite`, `onnx` }

### Backend (CPU and GPU acceleration) tags:

Please select any combination, possibly empty, of the following: { `neon` , `opencl` }


## Examples:
```
ck install package --tags=lib,armnn,rel.18.08,tf                # Release 18.08, TF frontend, no acceleration (reference implementation)

ck install package --tags=lib,armnn,rel.19.05,tf,tflite,neon    # Release 19.05, TF and TFLite frontends, CPU acceleration

ck install package --tags=lib,armnn,release,tf,onnx,opencl      # Current release, TF and ONNX frontends, GPU acceleration

ck install package --tags=lib,armnn,dev,tflite,neon,opencl      # Current development, TFLite frontend, CPU and GPU acceleration
```

## Notes:

1. Asking for a non-trivial backend support (either `neon`, `opencl` or both) will automatically trigger building of the same-release version of ArmCL. This should only be attempted on an Arm platform (whereas a "backendless" version should compile and run on an Intel platform as well).

2. If you are intending to simultaneously maintain same-release versions with and without `neon`/`opencl` support, start compiling ones without the support, gradually adding these capabilities. It is currently a known CK constraint that a new package should not be added with a subset of tags of another currently installed environment.

3. The same applies to same-release versions with and without specific frontends: if you want to have them simultaneously, make sure you never build a subset of tags after you've built its proper superset.
