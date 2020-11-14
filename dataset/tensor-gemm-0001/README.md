## test-shape-2-3-4-1-0

In this test, we multiply small matrices: `C[3][4] = A[3][2] * B[2][4]`.

We initialize `A` in row-major order with numbers in the range `0-5`, `B` in the range `6-13`, `C` in the range `14-25`:

```bash
$ python -c "import struct; s = struct.pack('f'*3*2, *[ float(i) for i in range(0,3*2) ]); f = open('test-shape-2-3-4-1-0.A', 'wb'); f.write(s); f.close()"
$ python -c "import struct; s = struct.pack('f'*2*4, *[ float(i) for i in range(3*2,3*2+2*4) ]); f = open('test-shape-2-3-4-1-0.B', 'wb'); f.write(s); f.close()"
$ python -c "import struct; s = struct.pack('f'*3*4, *[ float(i) for i in range(3*2+2*4,3*2+2*4+3*4) ]); f = open('test-shape-2-3-4-1-0.C', 'wb'); f.write(s); f.close()"
```

By default, we request to print the input and output tensors:

```bash
$ ck run program:gemm-armcl-opencl --dataset_file=test-shape-2-3-4-1-0 \
&& cat `ck find program:gemm-armcl-opencl`/tmp/tmp-stdout.tmp

M = 3, K = 2, N = 4, alpha = 1.000000, beta = 0.000000
A:
-----------------------------------
Shape (N*C*H*W): 1*1*3*2
N=0, C=0:
       0               1
       2               3
       4               5
-----------------------------------
A source: /home/anton/CK_REPOS/ck-nntest/dataset/tensor-gemm-0001/test-shape-2-3-4-1-0.A

B:
-----------------------------------
Shape (N*C*H*W): 1*1*2*4
N=0, C=0:
       6               7               8               9
      10              11              12              13
-----------------------------------
B source: /home/anton/CK_REPOS/ck-nntest/dataset/tensor-gemm-0001/test-shape-2-3-4-1-0.B

C:
-----------------------------------
Shape (N*C*H*W): 1*1*3*4
N=0, C=0:
      14              15              16              17
      18              19              20              21
      22              23              24              25
-----------------------------------
C source: /home/anton/CK_REPOS/ck-nntest/dataset/tensor-gemm-0001/test-shape-2-3-4-1-0.C

OUTPUT:
-----------------------------------
Shape (N*C*H*W): 1*1*3*4
N=0, C=0:
      10              11              12              13
      42              47              52              57
      74              83              92             101
-----------------------------------
time-0, setup: 0.555022
time-1, test:  0.001055
```
