# Tested versions

## 20210427 [gfursin]

* CPU: x86-64
* OS: Ubuntu 18.04

### With LLVM built from sources

* LLVM: 12.0.0 built from sources using GCC 7.5.0

```
ck install package --tags=compiler,llvm,src,v12.0.0
```

* TVM: r-a1b4f0e8f2bfcc583f98f0f9272adcc0c12f70a5 or higher (v0.7.0 is not working!)

```
ck install package --tags=compiler,tvm,r-a1b4f0e8f2bfcc583f98f0f9272adcc0c12f70a5
```

### With prebuilt LLVM

* LLVM: 12.0.0 prebuilt

Pre-requisites:
```
sudo apt install libxml2
```

```
ck install package --tags=compiler,llvm,prebuilt,v12.0.0
```

* TVM: r-a1b4f0e8f2bfcc583f98f0f9272adcc0c12f70a5 or higher (v0.7.0 is not working!)

```
ck install package --tags=compiler,tvm,r-a1b4f0e8f2bfcc583f98f0f9272adcc0c12f70a5
```
