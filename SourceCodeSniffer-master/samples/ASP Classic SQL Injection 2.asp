<!DOCTYPE html>
<html>
<body>

<%
set conn=Server.CreateObject("ADODB.Connection")
conn.Provider="Microsoft.Jet.OLEDB.4.0"
conn.Open(Server.Mappath("/db/northwind.mdb"))

set rs=Server.CreateObject("ADODB.recordset")
sql="SELECT DISTINCT Country FROM Customers ORDER BY Country"
rs.Open sql,conn

country=request.form("country")

%>

<form method="post">
Choose Country <select name="country">
<%  do until rs.EOF
    response.write("<option")
    if rs.fields("country")=country then
      response.write(" selected")
    end if
    response.write(">")
    response.write(rs.fields("Country"))
    rs.MoveNext
loop
rs.Close
set rs=Nothing %>
</select>
<input type="submit" value="Show customers">
</form>

<%
if country<>"" then
   sql="SELECT Companyname,Contactname,Country FROM Customers WHERE country='" & country & "'"
   set rs=Server.CreateObject("ADODB.Recordset")
   rs.Open sql,conn
%>
   <table width="100%" cellspacing="0" cellpadding="2" border="1">
   <tr>
     <th>Companyname</th>
     <th>Contactname</th>
     <th>Country</th>
   </tr>
<%
do until rs.EOF
   response.write("<tr>")
   response.write("<td>" & rs.fields("companyname") & "</td>")
   response.write("<td>" & rs.fields("contactname") & "</td>")
   response.write("<td>" & rs.fields("country") & "</td>")
   response.write("</tr>")
   rs.MoveNext
loop
rs.close
conn.Close
set rs=Nothing
set conn=Nothing%>
</table>
<%  end if %>

</body>
</html>