frappe.listview_settings["Casual Payroll Payout"] = {
    onload: function (list_view) {
		let me = this;
		list_view.page.add_inner_button(__("Crate Casual Assignment"), function () {
            selected_values = list_view.get_checked_items();
            casual_payroll = []
            attendance_date = []
            selected_values.forEach(element => {
                if (element.docstatus === 1){
                    casual_payroll.push(element.name)
                    attendance_date.push(element.attendance_date)
                }
            });
            if (casual_payroll){
                frappe.call({
                    method:
                        "nl_piece_rate_pay.nl_piece_rate_pay.doctype.casual_payroll_payout.casual_payroll_payout.create_casual_salary_assignment",
                    args: {
                        selected_values: casual_payroll,
                        attendance_date : attendance_date
                    },
                    freeze: true,
                    freeze_message: __("Creating Casual Salary Structure Assignment Entry"),
                    callback: function (r) {
                        if (!r.exc) {
                            frappe.msgprint(__("Casual Salary Structure Assignment Entry created successfully."))
                        }
                    },
                });
            }
        })
    }
}