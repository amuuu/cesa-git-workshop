var proc1 = new ProcessStartInfo();
string anyCommand;
proc1.UseShellExecute = true;

proc1.WorkingDirectory = @"C:\Windows\System32";

proc1.FileName = @"C:\Windows\System32\cmd.exe";
proc1.Verb = "runas";
proc1.Arguments = "/c "+anyCommand;
proc1.WindowStyle = ProcessWindowStyle.Hidden;
Process.Start(proc1);