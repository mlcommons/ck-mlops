rem
rem Installation script for Bazel
rem
rem See CK LICENSE.txt for licensing details.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem Developer(s):
rem - Grigori Fursin, https://fursin.net
rem

rem PACKAGE_DIR
rem INSTALL_DIR

set FULL_PACKAGE_URL=%PACKAGE_URL%/%PACKAGE_NAME%

rem ################################################################################
echo ************************************************************
echo Downloading Bazel from %FULL_PACKAGE_URL% ...
echo.

wget --no-check-certificate -c "%FULL_PACKAGE_URL%" -O "%PACKAGE_NAME%"

if %errorlevel% neq 0 (
 echo.
 echo Error: Downloading Bazel from %FULL_PACKAGE_URL% failed!
 exit /b 1
)

rem ################################################################################
echo ************************************************************
echo Unzipping Bazel ...
echo.

unzip %PACKAGE_NAME%
if %errorlevel% neq 0 (
 echo.
 echo Error: Unzipping Bazel failed!
 exit /b 1
)

rem ################################################################################
echo ************************************************************
echo Cleaning Bazel installer ...
echo.

del /Q /S %PACKAGE_NAME%

rem ###############################################################################
echo ************************************************************
echo Successfully installed Bazel into %INSTALL_DIR%
echo.

