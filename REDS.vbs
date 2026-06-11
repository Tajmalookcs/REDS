Dim WshShell, projectDir
Set WshShell = CreateObject("WScript.Shell")
projectDir = "D:\REDS"

' Kill any existing Django server on port 8000
WshShell.Run "cmd /c for /f ""tokens=5"" %a in ('netstat -aon ^| findstr :8000') do taskkill /F /PID %a", 0, True

' Brief startup popup (auto-closes after 2 seconds, no button needed)
WshShell.Popup "REDS is starting..." & vbCrLf & "Browser will open automatically.", 2, "REDS", 64

' Run migrations silently
WshShell.Run "cmd /c cd /d """ & projectDir & """ && venv\Scripts\python.exe manage.py migrate --run-syncdb >nul 2>&1", 0, True

' Start Django server hidden in background
WshShell.Run "cmd /c cd /d """ & projectDir & """ && venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000", 0, False

' Wait for server to be ready then open browser
WScript.Sleep 2500
WshShell.Run "http://127.0.0.1:8000"

Set WshShell = Nothing
