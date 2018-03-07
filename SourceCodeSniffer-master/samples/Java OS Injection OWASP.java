public class DoStuff {
public string executeCommand(String userName)
{	try {
		String myUid = userName;
		Runtime rt = Runtime.getRuntime();
		rt.exec("cmd.exe /C doStuff.exe " +"-" +myUid); // Call exe with userID
	}catch(Exception e)
		{
e.printStackTrace();
		}
	}
}

public class DoStuff {
public string executeCommand(String userName)
{	try {
		String myUid = userName;
		Runtime rt = Runtime.getRuntime();
		rt.exec("doStuff.exe " +"-" +myUid); // Call exe with userID
	}catch(Exception e)
		{
e.printStackTrace();
		}
	}
}