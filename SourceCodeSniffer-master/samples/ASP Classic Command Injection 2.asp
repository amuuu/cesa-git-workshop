<%
Dim oShell, sCommand
sCommand = "wzzip.exe C:\Output\File.zip C:\SourceFiles\File.txt"
Set oShell = Server.CreateObject("WScript.Shell")
oShell.Run sCommand, , True
Set oShell = Nothing
%>