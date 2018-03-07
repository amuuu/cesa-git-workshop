<form name="search" method="post" onsubmit="return attention();">
<table width="60%" border="0" cellpadding="2" cellspacing="0" style="margin:0 auto">
<tr>
    <td colspan="2"><h1 style="color:#003399;">Search for Certificate of Analysis</h1></td>
</tr>
<tr>
    <td valign="bottom">Product number <sup style="color:#EE0000;font-size:1.3em">*</sup></td>
    <td valign="bottom">Lot number</td>
</tr>
<tr>
    <td width="30%" valign="top">
        <input type="text" name="input1" size="20"/>
    </td>
    <td valign="top">
        <input type="text" size="20" name="input2"/> 
        <input style="background-color:#ffffff;border:0px;cursor:pointer" size="10" type="submit" name="sub" value=">>" />
    </td>
</tr>

</table>
<%
    if request.Form("sub") <> "" then
    Dim fname, lname
    fname= request.Form("input1")
    lname= request.Form("input2")
    session("n") = fname & lname
    sql = "Select * from search where cat_no_batch_no LIKE '"&request.Form("input1")&"%' OR cat_no_batch_no='"&session("n")&"'"
    rs.open sql, con, 1, 2
    if rs.eof then

    response.write("Please provide a valid Cat No.")    

    else



            do while not rs.eof
        %>
            <table border="1" cellpadding="5" cellspacing="0" width="60%" style="margin:0 auto; border-collapse:collapse;border-color:#999999">
            <tr>
                <td width="50%"><%=rs("cat_no_batch_no")%></td>
                <td width="10%">Click to open <a target="_blank" href="http://localhost/search1/<%=rs("pdf_path")%>"><%=rs("cat_no_batch_no")%></a></td>
            </tr>
            </table>

        <%
            rs.movenext
            loop
        end if
    rs.close
    end if
%>
</form>