import java.io.*;
import javax.servlet.http.*;
import javax.servlet.*;

public class HelloServlet extends HttpServlet
{
    public void doGet (HttpServletRequest req, HttpServletResponse res) throws ServletException, IOException
    {
        String input = req.getHeader(“USERINPUT”);

        PrintWriter out = res.getWriter();
        out.println(input);  // echo User input.
        out.close();
    }
}