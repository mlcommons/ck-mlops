@echo off

rem
rem CK installation script
rem
rem See CK LICENSE for licensing details.
rem See CK COPYRIGHT for copyright details.
rem

rem PACKAGE_DIR
rem INSTALL_DIR
rem PYTHON_PACKAGE_NAME
rem PIP_INSTALL_OPTIONS

rem This is where pip will install the modules.
rem It has its own funny structure we don't control :
rem 

set EXTRA_PYTHON_SITE=%INSTALL_DIR%\build

echo **************************************************************
echo.
echo Cleanup: removing %EXTRA_PYTHON_SITE%
if exist "%EXTRA_PYTHON_SITE%" (
 rmdir /S /Q "%EXTRA_PYTHON_SITE%"
)

if not [%PYTHON_PACKAGE_URL%] == [] (

  rem ######################################################################################
  echo.
  echo Downloading wheel %PYTHON_PACKAGE_URL%/%PYTHON_PACKAGE_NAME% ...

  del /Q /S %PYTHON_PACKAGE_NAME%

  wget --no-check-certificate %PYTHON_PACKAGE_URL%/%PYTHON_PACKAGE_NAME%

  set PYTHON_PACKAGE_NAME2=%PYTHON_PACKAGE_NAME%
) else (
  set PYTHON_PACKAGE_NAME2=%ORIGINAL_PACKAGE_DIR%\%PYTHON_PACKAGE_NAME%
)

rem ######################################################################################
echo.
echo Installing %PYTHON_PACKAGE_NAME% and its dependencies to %PACKAGE_LIB_DIR% ...

%CK_ENV_COMPILER_PYTHON_FILE% -m pip install --ignore-installed %PYTHON_PACKAGE_NAME2% -t %EXTRA_PYTHON_SITE% %PIP_INSTALL_OPTIONS%

if %errorlevel% neq 0 (
 echo.
 echo Error: installation failed!
 exit /b 1
)

exit /b 0
