import org.apache.struts.action.*;
import org.apache.commons.beanutils.BeanUtils;
import javax.servlet.http.HttpServletRequest;
import javax.servlet.http.HttpServletResponse;

public final class InsertEmployeeAction extends Action
{

    public ActionForward execute(ActionMapping mapping, ActionForm form,
        HttpServletRequest request, HttpServletResponse response) throws Exception
    {

        // Setting up objects and vairables.

        Obj1 service = new Obj1();
        ObjForm objForm = (ObjForm) form;
        InfoADT adt = new InfoADT ();
        BeanUtils.copyProperties(adt, objForm);

        String searchQuery = objForm.getqueryString();
        String payload = objForm.getPayLoad();
        try {
            service.doWork(adt);  / /do something with the data
            ActionMessages messages = new ActionMessages();
            ActionMessage message = new ActionMessage("success", adt.getName() );
            messages.add( ActionMessages.GLOBAL_MESSAGE, message );
            saveMessages( request, messages );
            request.setAttribute("Record", adt);
            return (mapping.findForward("success"));
        }
        catch( DatabaseException de )
        {
            ActionErrors errors = new ActionErrors();
            ActionError error = new ActionError("error.employee.databaseException" + “Payload: “+payload);
            errors.add( ActionErrors.GLOBAL_ERROR, error );
            saveErrors( request, errors );
            return (mapping.findForward("error: "+ searchQuery));
        }
    }
}