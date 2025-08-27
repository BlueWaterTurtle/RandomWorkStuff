@echo off
REM print_zpl_pause_on_fail.bat
REM Purpose: Send a ZPL file to a locally shared Zebra printer (e.g. GC420d) via its Windows share.
REM Behavior: Closes automatically on success; pauses (so the window stays open) only on error conditions.
REM Notes:
REM   - Removed prior DIR-based share check because printer shares do not enumerate like file shares and can return misleading errors.
REM   - COPY /B is the authoritative test; if it succeeds (1 file(s) copied.), the job was handed to the print spooler.
REM   - Adjust PRINTER_SHARE_NAME below if your share name changes.
REM   - Optional sanity warning if the file does not start with ^XA (common ZPL start sequence) but we do NOT fail on that.
REM   - ErrorLevels:
REM       1 = No argument supplied
REM       2 = File not found
REM       3 = Copy (print submission) failed
REM
REM Usage examples:
REM   print_zpl_pause_on_fail.bat "C:\Labels\shipping_label.zpl"
REM   (Drag & drop a .zpl file onto the .bat also works.)

setlocal
set "PRINTER_SHARE_NAME=ZDesignerGC420dNP"
set "TARGET=\\%COMPUTERNAME%\\%PRINTER_SHARE_NAME%"

REM ---- Argument presence check ----
if "%~1"=="" (
  echo ERROR: No file argument provided.
  echo Usage: %~nx0 "FullPathToLabel.zpl"
  pause
  exit /b 1
)

REM ---- Resolve and validate file path ----
set "FILE=%~1"
if not exist "%FILE%" (
  echo ERROR: File not found: %FILE%
  pause
  exit /b 2
)

REM ---- Optional simple ZPL sanity (non-fatal) ----
REM Typical ZPL starts with ^XA and ends with ^XZ. We only warn if ^XA missing.
findstr /b /c:"^XA" "%FILE%" >nul || echo WARNING: File does not start with ^XA (may still be valid ZPL).

echo Sending "%FILE%" to %TARGET% ...
copy /b "%FILE%" "%TARGET%" >nul
if errorlevel 1 (
  echo.
  echo ERROR: Failed to copy raw data to %TARGET%
  echo        Possible causes: wrong share name, printer paused/offline, spooler stopped, or File and Printer Sharing blocked by firewall.
  echo        Troubleshooting quick list:
  echo          1. Ensure printer is shared as %PRINTER_SHARE_NAME% (Printer Properties > Sharing).
  echo          2. Confirm Print Spooler service is running (sc query spooler).
  echo          3. Ensure printer queue is not Paused or Offline.
  echo          4. Check Windows Firewall allows File and Printer Sharing on this network profile.
  pause
  exit /b 3
)

echo Success: Label sent.
endlocal
exit /b 0
