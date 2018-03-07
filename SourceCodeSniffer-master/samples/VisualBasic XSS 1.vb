' SearchResult.aspx.vb 
Imports System 
Imports System.Web 
Imports System.Web.UI 
Imports System.Web.UI.WebControls 

Public Class SearchPage Inherits System.Web.UI.Page 

Protected txtInput As TextBox 
Protected cmdSearch As Button 
Protected lblResult As Label Protected 

Sub cmdSearch _Click(Source As Object, _ e As EventArgs) 
	
// Do Search…..
	// …………

lblResult.Text="You Searched for: " & txtInput.Text 

// Display Search Results…..
// …………

End Sub 
End Class