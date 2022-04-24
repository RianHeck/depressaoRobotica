@echo off
title DepressaoRobotica
:1

for /f "tokens=2 delims==" %%a in ('wmic OS Get localdatetime /value') do set "dt=%%a"
set "YYYY=%dt:~0,4%" & set "MM=%dt:~4,2%" & set "DD=%dt:~6,2%"
set "HH=%dt:~8,2%" & set "Min=%dt:~10,2%" & set "Sec=%dt:~12,2%"

set "fullstamp=%YYYY%-%MM%-%DD% - %HH%:%Min%:%Sec%"

echo "%fullstamp%"

python index.py
echo Reiniciando bot...
timeout 5
echo:
goto 1