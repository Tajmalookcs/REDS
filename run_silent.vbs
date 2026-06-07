Dim objShell
Set objShell = CreateObject("WScript.Shell")
objShell.Run "cmd /c cd /d """ & CreateObject("Scripting.FileSystemObject").GetParentFolderName(WScript.ScriptFullName) & """ && venv\Scripts\activate && python manage.py runserver 127.0.0.1:8000", 0, False
