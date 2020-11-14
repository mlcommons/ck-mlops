# CK package for Arm Compute Library

## This package builds and installs a desired version of Arm CL using SCons

Selection of the desired release and desired backend support is now done via combining relevant tags.

### Release tags:

Please select exactly one of the following: { `release` | `rel.18.08` | `rel.18.11` | `rel.19.02` | `rel.19.05` | `dev` }

### Backend (CPU and GPU acceleration) tags:

Please select any combination, possibly empty, of the following: { `neon` , `opencl` }


## Examples:
```
ck install package --tags=lib,armcl,viascons,rel.18.11          # Release 18.11 without acceleration (reference implementation)

ck install package --tags=lib,armcl,viascons,rel.19.02,neon     # Release 19.02 with CPU acceleration

ck install package --tags=lib,armcl,viascons,release,opencl     # Current release with GPU acceleration

ck install package --tags=lib,armcl,viascons,dev,neon,opencl    # Current development with CPU and GPU acceleration
```

## Note:

If you are intending to simultaneously maintain same-release versions with and without `neon`/`opencl` support, start compiling ones without the support, gradually adding these capabilities. It is currently a known CK constraint that a new package should not be added with a subset of tags of another currently installed environment.
