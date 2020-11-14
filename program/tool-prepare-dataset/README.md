# Tensor shape datasets preparation

This is an utility program that initializes or updates `ck-nntest` tensor shape datasets:
```
ck search dataset --tags=nntest
```

A dataset can contain a table file `data.csv` and if it does, the tool will read the file line by line and produce pair of shape files `shape-*` and `shape-*.json`. Set of columns in the `data.csv` file and exact names of resulting files are depend on a test program the dataset is intended for.

The program searches for datasets by tag `nntest` and you have to choose one that is needed to be updated. Then it removes all the existed `shape-*` files, so be warned if you have added some shapes manually, they will be erased.

**Note:** The tool does not update a remote repo, so after execution you have to stage changes and commit them by yourself.

## Run
```
ck run program:tool-prepare-dataset
```

or one can explicitly specify which dataset should be processed:
```
ck run program:tool-prepare-dataset --env.CK_DATASET=tensor-fullyconnected-0001
```
