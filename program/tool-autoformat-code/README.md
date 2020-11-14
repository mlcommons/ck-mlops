# Automatic code formatting tool

This program uses [astyle](http://astyle.sourceforge.net) to format C-family source files and [autopep8](https://github.com/hhatto/autopep8) to format Python source files.

## Requirements

To enable formatting of C-family sources:
```
sudo apt install astyle
```

To enable formatting of Python sources:
```
sudo pip install autopep8
```

## Usage

To format a single file, run:
```
ck run program:tool-autoformat-code --env.CK_FILE=/path/to/source/code/file.cpp
```

To format all files in a directory recursively, run:
```
ck run program:tool-autoformat-code --env.CK_DIR=/path/to/source/code/dir
```

To format a CK program with a particular UOA, run:
```
ck run program:tool-autoformat-code --env.CK_PROGRAM=program-uoa
```

In `CK_DIR` or `CK_PROGRAM` mode you can specify processing file extensions via `CK_FILTER`:
```
ck run program:tool-autoformat-code --env.CK_PROGRAM=program-uoa --env.CK_FILTER=cpp,hpp
```
By default `CK_FILTER=cpp,c,h,py`
