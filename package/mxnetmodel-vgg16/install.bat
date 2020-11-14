@echo off

rem  CK installation script for MXNet package
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem

cd /d %INSTALL_DIR%

%CK_ENV_COMPILER_PYTHON_FILE% %PACKAGE_DIR%\model.py

del /Q %MXNET_MODEL_LABELS%

wget %MXNET_URL_MODEL_LABELS%/%MXNET_MODEL_LABELS%

exit /b 0
