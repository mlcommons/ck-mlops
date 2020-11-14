@echo off

rem  CK installation script for CNTK package
rem
rem Developer(s):
rem  * Grigori Fursin, dividiti/cTuning foundation
rem

set CNTK_LIB_DIR=%INSTALL_DIR%\lib

rem ######################################################################################
echo.
echo Downloading and installing misc deps ...
echo.

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --upgrade pip

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --ignore-installed requests matplotlib jupyter opencv-python -t %INSTALL_DIR%\lib

set URL=https://cntk.ai/PythonWheel/%CNTK_PACKAGE_TYPE%/cntk%CNTK_PACKAGE_EXT%-%CNTK_PACKAGE_VER%-%CNTK_PACKAGE_FILE_EXT%

echo.
echo Downloading and installing CNTK prebuilt binaries (%URL%) ...
echo.

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install %URL% --ignore-installed  -t %INSTALL_DIR%\lib
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing CNTK ...
 exit /b 1
)

rem ######################################################################################
set URL2=https://cntk.ai/BinaryDrop/%CNTK_PACKAGE_BINARY_ARC%

echo.
echo "Downloading and installing CNTK prebuilt binaries (%URL2%) ..."
echo.

cd %INSTALL_DIR%

wget --no-check-certificate %URL2%
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed downloading CNTK binaries ...
 exit /b 1
)

echo.
echo Unzipping %CNTK_PACKAGE_BINARY_ARC% ...
echo.
unzip -o %CNTK_PACKAGE_BINARY_ARC%

del /Q %CNTK_PACKAGE_BINARY_ARC%

exit /b 0
