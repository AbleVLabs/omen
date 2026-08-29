@echo off
REM ── Publishes the OMEN code to github.com/AbleVLabs/omen ──
cd /d C:\Users\an9ie\Desktop\omen
echo.
echo  BEFORE running this: create an EMPTY public repo named "omen"
echo  at https://github.com/new  (owner AbleVLabs, no README/gitignore/license)
echo.
pause
if not exist ".git" git init
git add .
git commit -m "OMEN: naming standard, reference encoder, tests, white paper"
git branch -M main
git remote remove origin 2>nul
git remote add origin https://github.com/AbleVLabs/omen.git
git push -u origin main
echo.
echo ── Done. Check: https://github.com/AbleVLabs/omen
echo.
pause
