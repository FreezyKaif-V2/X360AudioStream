Option Explicit
Dim shell, files, folder, launcher
Set shell = CreateObject("WScript.Shell")
Set files = CreateObject("Scripting.FileSystemObject")
folder = files.GetParentFolderName(WScript.ScriptFullName)
launcher = files.BuildPath(folder, "Audio-Control.pyw")
shell.CurrentDirectory = folder
On Error Resume Next
shell.Run "pythonw.exe """ & launcher & """", 0, False
If Err.Number <> 0 Then
    MsgBox "Cannot start Python. Install Python with Tkinter and add it to PATH." & vbCrLf & Err.Description, vbExclamation, "Xbox 360 Audio"
End If
