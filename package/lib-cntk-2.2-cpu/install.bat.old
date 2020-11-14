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

%CK_PYTHON_PIP_BIN% install --upgrade pip
%CK_PYTHON_PIP_BIN% install requests matplotlib jupyter

set URL=https://cntk.ai/PythonWheel/%CNTK_PACKAGE_TYPE%/cntk-%CNTK_PACKAGE_VER%-%CNTK_PACKAGE_FILE_EXT%

echo.
echo Downloading and installing CNTK prebuilt binaries (%URL%) ...
echo.

%CK_PYTHON_PIP_BIN% install %URL% --ignore-installed --prefix %INSTALL_DIR%\lib
if %errorlevel% neq 0 (
 echo.
 echo Error: Failed installing CNTK ...
 exit /b 1
)

exit /b 0
