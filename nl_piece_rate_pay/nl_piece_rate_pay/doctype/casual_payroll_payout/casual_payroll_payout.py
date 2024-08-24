# Copyright (c) 2024, Navari Limited and contributors
# For license information, please see license.txt
from datetime import datetime

import frappe
import json
from frappe.model.document import Document

class CasualPayrollPayout(Document):
	def validate(self):
		if not self.attendance_date:
			frappe.throw("Attendance Date is mandatory field")
		if not self.shift_type:
			frappe.throw("Shift Type is mandatory field")

		for row in self.casual_payrol_payout_employee:
			attendance = frappe.db.get_all("Attendance", {"attendance_date": self.attendance_date, "shift": self.shift_type, "company":self.company, "employee": row.employee, "docstatus": 1})
			if attendance:
				attendance = attendance[0]["name"]
				employee_checkin=frappe.get_all("Employee Checkin", filters={"attendance": attendance, "employee":row.employee, "log_type":"IN"}, fields=["time"])
				employee_checkout=frappe.get_all("Employee Checkin", filters={"attendance": attendance, "employee":row.employee, "log_type":"OUT"}, fields=["time"])
		
				if employee_checkin:
					row.checkin = employee_checkin[0]["time"]
				if employee_checkout:
					row.checkout = employee_checkout[0]["time"]


@frappe.whitelist(allow_guest=True)
def get_rate():
	activity=frappe.form_dict.get("activity")
	item=frappe.form_dict.get("item")
	costing=frappe.get_all("Casual Activity Item", filters={"activity_type":activity, "item":item}, fields=["costing_rate"])
	if costing:
		rate=costing[0].costing_rate
		frappe.response['message']=rate
	else:
		frappe.throw("Create Costing for this Activity in Casual Activity Item doctype")


@frappe.whitelist(allow_guest=True)
def fetch_employees():
	total_amount=frappe.form_dict.get("total_amount")
	shift_type=frappe.form_dict.get("shift_type")
	attendance_date=frappe.form_dict.get("attendance_date")
	company=frappe.form_dict.get("company")
	employees_attendance = frappe.get_all("Attendance", filters={"attendance_date": attendance_date, "shift": shift_type, "company":company}, fields=["employee", "employee_name", "shift", "status","name"])
	employee_details=[]
	for employee_attendance in employees_attendance:
   
		employee_checkin=frappe.get_all("Employee Checkin", filters={"attendance": employee_attendance.name, "employee":employee_attendance.employee, "log_type":"IN"}, fields=["time"])
		employee_checkout=frappe.get_all("Employee Checkin", filters={"attendance": employee_attendance.name, "employee":employee_attendance.employee, "log_type":"OUT"}, fields=["time"])
  
		employee_detail={
			"employee":employee_attendance.employee,
			"employee_name":employee_attendance.employee_name,
			"shift_type":employee_attendance.shift,
			"attendance":employee_attendance.name,
			"checkin":employee_checkin[0].time if employee_checkin else None,
			"checkout":employee_checkout[0].time if employee_checkout else None,

		}
		
		employee_details.append(employee_detail)
	frappe.response['message']=employee_details

 
#get activity items related to activity type
@frappe.whitelist(allow_guest=True)
def get_activity_items():
	activity_type = frappe.form_dict.get("activity_type")
	items = frappe.get_all("Casual Activity Item", filters={"activity_type": activity_type}, fields=["item"])

	item_names = [item["item"] for item in items]
	frappe.response['message'] = item_names


# @frappe.whitelist(allow_guest=True)
# def open_monthly_nssf_deduction():
# 	salary_components=frappe.get_all("Salary Component", filters={"name": ["like", "%NSSF%"]}, fields=["name"])
# 	for salary_component in salary_components:
# 		if salary_component.monthly==1:
# 			salary_component_doc=frappe.get_doc("Salary Component", salary_component.name)
# 			salary_component_doc.monthly=0
# 			salary_component_doc.save()
# 			frappe.db.commit()
# 	frappe.msgprint(str(salary_component))

@frappe.whitelist()
def create_casual_salary_assignment(selected_values, attendance_date):
	if isinstance(selected_values, str):
		selected_values = json.loads(selected_values)
	
	if isinstance(attendance_date, str):
		attendance_date = json.loads(attendance_date)

	cs_doc = frappe.new_doc("Casual Salary Structure Assignment Tool")
	cs_doc.start_date = min(attendance_date)
	cs_doc.end_date = max(attendance_date)
	cs_doc.salary_structure = "Casual Piece Rate"

	employee_data = get_employee_data(selected_values)

	for employee in employee_data:
		cs_doc.append("casuals_weekly_amount", {
			"employee": employee,
			"amount": employee_data.get(employee)
		})
	cs_doc.save()

def get_employee_data(casual_payroll):
	employee_data = {}

	for row in casual_payroll:
		payment_records = frappe.db.get_all("Casual Payroll Payout Employee", {"parent": row}, ["employee", "amount"])

		for record in payment_records:
			employee_data.setdefault(record.employee, 0)
			employee_data[record.employee] += record.amount
	
	return employee_data