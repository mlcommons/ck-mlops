@echo off

rem
rem Copyright (c) 2015-2017 cTuning foundation.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem See CK LICENSE for licensing details.
rem See CK COPYRIGHT for copyright details.
rem
rem Installation script for CK packages.
rem
rem Developer(s): Grigori Fursin, 2015
rem

rem %PACKAGE_DIR%
rem %INSTALL_DIR%

echo.
echo Copying NNTest to src dir ...
echo.

mkdir %INSTALL_DIR%\install\include

copy /B %PACKAGE_DIR%\*.h %INSTALL_DIR%\install\include
copy /B %PACKAGE_DIR%\README* %INSTALL_DIR%
