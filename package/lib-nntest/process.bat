@echo off

rem
rem Copyright (c) 2015-2017 cTuning foundation.
rem See CK COPYRIGHT.txt for copyright details.
rem
rem SPDX-License-Identifier: BSD-3-Clause.
rem See CK LICENSE.txt for licensing details.
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
