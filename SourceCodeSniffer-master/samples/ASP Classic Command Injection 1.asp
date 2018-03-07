
sSQL = "Select ProductID, SUM(Quantity) as TotalQuantity FROM OrderDetails Where CAST(orderDate AS DATE) Between '"&sStartDate&"' And '"&sEndDate&"' GROUP BY ProductID"
Set rs = Server.CreateObject("ADODB.RecordSet")
rs.Open sSQL, cnn, adOpenStatic, adLockReadOnly, adCmdText

<tr>
<td>
<%Response.Write(rs.Fields("ProductID"))%>
</td>
<td>
<%= rs.Fields("TotalQuantity") %>
</td>