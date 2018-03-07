public class DoStuff {
public string executeCommand(String userName)
{	try {
		String myUid = userName;
		Runtime.exec("cmd.exe /C doStuff.exe " +"-" +myUid);
	}catch(Exception e)
		{
e.printStackTrace();
		}
	}
}