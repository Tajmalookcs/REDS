Dim WshShell, projectDir
Set WshShell = CreateObject("WScript.Shell")
projectDir = "D:\REDS"

' Run migrations silently (wait to finish before starting server)
WshShell.Run "cmd /c cd /d """ & projectDir & """ && venv\Scripts\python.exe manage.py migrate --run-syncdb", 0, True

' Start Django server hidden in background (no terminal window)
WshShell.Run "cmd /c cd /d """ & projectDir & """ && venv\Scripts\python.exe manage.py runserver 127.0.0.1:8000", 0, False

' Wait 2 seconds for server to be ready, then open browser
WScript.Sleep 2000
WshShell.Run "http://127.0.0.1:8000"

Set WshShell = Nothing
