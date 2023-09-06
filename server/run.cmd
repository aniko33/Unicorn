@echo off
taskkill /IM python.exe /F
start /B python.exe -m uvicorn unicorn:app --reload
npm start