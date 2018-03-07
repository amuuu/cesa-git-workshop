var proc = new Process
{
    StartInfo = new ProcessStartInfo
    {
        FileName = @"C:\Program Files\Microsoft Visual Studio 14.0\Common7\IDE\tf.exe",
        Arguments = "checkout AndroidManifest.xml",
        UseShellExecute = false,
        RedirectStandardOutput = true,
        CreateNoWindow = true,
        WorkingDirectory = @"C:\MyAndroidApp\"
    }
};

proc.Start();