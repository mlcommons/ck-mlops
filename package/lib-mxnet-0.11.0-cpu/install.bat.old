@echo off

rem  CK installation script for MXNet package
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem

set MXNET_LIB_DIR=%INSTALL_DIR%\lib

rem ######################################################################################
echo.
echo Downloading and installing misc deps ...
echo.

%CK_PYTHON_PIP_BIN% install --upgrade pip
%CK_PYTHON_PIP_BIN% install requests matplotlib jupyter

rem Sometimes issues with OpenCV on Anaconda
if NOT "%CK_CONDA_BIN_FULL%" == "" (
 %CK_PYTHON_PIP_BIN% uninstall opencv-python
 %CK_CONDA_BIN_FULL% install -c conda-forge opencv
) else (
 %CK_PYTHON_PIP_BIN% install opencv-python
)

echo.
echo Downloading and installing MXNET prebuilt binaries
echo.

rem --ignore-installed 

%CK_PYTHON_PIP_BIN% install mxnet%MXNET_EXTRA%==%MXNET_PACKAGE_VER% -t %INSTALL_DIR%\lib
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing MXNet ...
 exit /b 1
)

exit /b 0
