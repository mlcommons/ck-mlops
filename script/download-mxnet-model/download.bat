@echo off

rem
rem Installation script for CK packages.
rem
rem See CK LICENSE.txt for licensing details.
rem See CK Copyright.txt for copyright details.
rem
rem Developer(s):
rem - Grigori Fursin, cTuning foundation / dividiti, 2017
rem

rem ORIGINAL_PACKAGE_DIR (path to original package even if scripts are used from some other package or script)
rem PACKAGE_DIR (path where scripts are reused)
rem INSTALL_DIR

set X1=%MXNET_URL_MODEL_PARAMS%/%MXNET_MODEL_PARAMS%
if not "%MXNET_MODEL_PARAMS%" == "" (

  wget -c %X1% -O %MXNET_MODEL_PARAMS% --no-check-certificate

  if %errorlevel% neq 0 (
   echo.
   echo Error: download failed
   goto err
  )
)

set X2=%MXNET_URL_MODEL_JSON%/%MXNET_MODEL_JSON%
if not "%MXNET_MODEL_JSON%" == "" (

  wget -c %X2% -O %MXNET_MODEL_JSON% --no-check-certificate

  if %errorlevel% neq 0 (
   echo.
   echo Error: download failed
   goto err
  )
)

set X3=%MXNET_URL_MODEL_LABELS%/%MXNET_MODEL_LABELS%
if not "%MXNET_MODEL_LABELS%" == "" (
  wget -c %X3% -O %MXNET_MODEL_LABELS% --no-check-certificate

  if %errorlevel% neq 0 (
   echo.
   echo Error: download failed
   goto err
  )
)

exit /b 0

:err
exit /b 1
