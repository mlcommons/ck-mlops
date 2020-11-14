@echo off

rem  CK installation script for TensorFlow package
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem

set PACKAGE_LIB_DIR=%INSTALL_DIR%\lib

rem ######################################################################################
echo.
echo Downloading and installing deps ...
echo.

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --ignore-installed numpy pyyaml mkl mkl-include setuptools cmake cffi typing -t %PACKAGE_LIB_DIR%
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing deps ...
 exit /b 1
)

rem ######################################################################################
echo.
echo Cloning ...
echo.

cd /d %INSTALL_DIR%
git clone --recursive %PACKAGE_URL%

cd pytorch

set NO_CUDA=%NO_CUDA%

rem ######################################################################################
echo.
echo Building ...
echo.

set CMAKE_GENERATOR=%CK_CMAKE_GENERATOR%
set DISTUTILS_USE_SDK=1

%CK_ENV_COMPILER_PYTHON_FILE% setup.py install --prefix=%PACKAGE_LIB_DIR%
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed building ...
 exit /b 1
)

exit /b 0
