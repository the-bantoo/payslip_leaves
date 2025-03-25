from hrms.hr.doctype.leave_application.leave_application import get_leave_balance_on
import frappe

@frappe.whitelist()
def get_all_leave_balances(employee, date=None):
    if not date:
        date = frappe.utils.nowdate()
    
    allocations = frappe.get_all(
        "Leave Allocation",
        filters={
            "employee": employee,
            "docstatus": 1,
            "from_date": ["<=", date],
            "to_date": [">=", date]
        },
        fields=["leave_type"],
        distinct=True
    )
    
    leave_balances = {}
    for alloc in allocations:
        balance = get_leave_balance_on(employee=employee, leave_type=alloc.leave_type, date=date)
        leave_balances[alloc.leave_type] = balance
    
    # Generate HTML table rows
    if leave_balances:
        html = "<tbody>"
        for leave_type, balance in leave_balances.items():
            html += f"<tr><td>{leave_type}</td><td>{balance}</td></tr>"
        html += "</tbody>"
    else:
        html = "<tbody><tr><td colspan='2'>No leave balances available</td></tr></tbody>"
    
    return html

# Hook to update Salary Slip
def update_salary_slip_with_leave_balances(doc, method):
    if doc.employee:
        leave_balances = get_all_leave_balances(employee=doc.employee, date=frappe.utils.nowdate())

        if leave_balances == doc.custom_leave_balances:
            return

        # frappe.db.set_value(
        #     "Salary Slip", doc.name,
        #     "custom_leave_balances",
        #     leave_balances
        # )
        doc.db_set('custom_leave_balances', leave_balances, notify=True)
    else:
        html = "<tbody><tr><td colspan='2'>No leave balances available</td></tr></tbody>"
        if doc.custom_leave_balances != html:
            # frappe.db.set_value(
            #     "Salary Slip", doc.name,
            #     "custom_leave_balances", html
            # )

            doc.db_set('custom_leave_balances', html, notify=True)
        