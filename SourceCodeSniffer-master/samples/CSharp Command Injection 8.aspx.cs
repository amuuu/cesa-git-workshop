namespace ExternalExecution
{
class CallExternal
{
static void Main(string[] args)
{
String arg1=args[0];
System.Diagnostics.Process.Start("doStuff.exe", arg1);
}
}
}