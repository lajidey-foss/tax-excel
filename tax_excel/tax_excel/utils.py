from __future__ import unicode_literals
import frappe
import xlsxwriter as xw
from frappe.utils import (
    today,
    format_time,
    global_date_format,
    now,
    get_first_day,
)
from frappe import _
import datetime




@frappe.whitelist()
def pension_remittance(company=None, from_date=None, to_date=None):
    """"""
    #condition_pm = " WHERE 1=1 "
    condition_date = ""
    if not from_date:
        from_date = get_first_day(today()).strftime("%Y-%m-%d")
    if not to_date:
        to_date = today()
    
    date_time = global_date_format(now()) + " " + format_time(now())
    currency = frappe.db.get_value("Company", company, "default_currency")

    condition_date = "where start_date BETWEEN '"+ from_date + \
        "' AND '" + to_date + "'"
    fp ='Pension_Report.xlsx'
    wbook = xw.Workbook(name_path(fp))
    nw_data = "SELECT * FROM (select s.name, s.employee_name, s.employee, s.start_date, s.end_date,e.pension_id,v.contrib, v.liabil,e.name_of_pension_manager,e.pension_manager,e.employee_name as femployee,s.docstatus from `tabSalary Slip` s left join `tabEmployee` e on s.employee = e.name\
			LEFT JOIN\
				(SELECT Distinct k.parent,\
					IFNULL((select d.amount from `tabSalary Detail` d where d.parentfield='deductions'and d.salary_component ='Pension contribution Employee' and d.parent=k.parent),0) as contrib,\
					IFNULL((select d.amount from `tabSalary Detail` d where d.parentfield='earnings'and d.salary_component = 'Pension Employer Contr.'and d.parent=k.parent),0) as liabil\
				FROM (select\
				d.amount,\
				d.parent,\
				d.salary_component\
				from `tabSalary Detail` d\
				where d.salary_component\
				in ('Pension contribution Employee','Pension Employer Contr.')\
				) k\
			) v ON s.name = v.parent ) a {} ".format(condition_date)
    #data = frappe.db.sql(nw_data, as_dict=1,)
    data = frappe.db.sql(nw_data, as_dict=1,)

    pm_lst =[]
    headers_list =[
		'Salary Slip ID','Employee','Employee Name','Start Date','End Date','Pension ID',
		'Pension EYRR','Pension EYEE','Total'
	]
    
    #header format
    heading_format= wbook.add_format({
        "bottom":1,
        "bold": True,
    })
    #data formater
    date_format=wbook.add_format({'num_format': 'mm/dd/yyyy'})
    #money formater
    money_format= wbook.add_format({'num_format':'#,##0'})
    total_format = wbook.add_format({
        "bottom":1,
        "top":1,
        "bold": True,
        'num_format':'#,##0',
    })
    for e in data:
        if e['name_of_pension_manager'] not in pm_lst:
            pm_lst.append(e['name_of_pension_manager'])
    for pm in pm_lst:
        ws = wbook.add_worksheet(pm)
        ws.write_row(3,0, headers_list,heading_format)

        rwnum = 4
        colnum = 0 
		#cal_start = 4
        dr_size = 2
        t_contr = 0
        t_liabil = 0
        populate = [x for x in data if x['name_of_pension_manager']==pm]
        for i in range(len(populate)):
            t_con = populate[i]['contrib'] or 0
            t_bill = populate[i]['liabil'] or 0
            ws.write(rwnum,colnum,populate[i]['name'])
            ws.write(rwnum,colnum+1,populate[i]['employee'])
            ws.write(rwnum,colnum+2,populate[i]['employee_name'])
            ws.write(rwnum,colnum+3,populate[i]['start_date'],date_format)
            ws.write(rwnum,colnum+4,populate[i]['end_date'],date_format)
            ws.write(rwnum,colnum+5,populate[i]['pension_id'])
            ws.write(rwnum,colnum+6,t_con,money_format)
            ws.write(rwnum,colnum+7,t_bill,money_format)
            ws.write(rwnum,colnum+8,t_con+t_bill,money_format)

            rwnum += 1
            t_contr +=t_con
            t_liabil +=t_bill

        ws.write_number(rwnum+dr_size, 6, t_contr,total_format)
        ws.write_number(rwnum+dr_size, 7, t_liabil,total_format)
        ws.write_number(rwnum+dr_size, 8, t_contr+t_liabil,total_format)
        
        ws.write("A1","Pension Manager")
        ws.write("B1", pm)

    #print("\n\n got her been here \n\n\n")
    wbook.close()
    
    return file_path_return(fp)


@frappe.whitelist()
def pay_roll_tax_report(company=None, from_date=None, to_date=None):
    """"""
    condition_date = ""
    if not from_date:
        from_date = get_first_day(today()).strftime("%Y-%m-%d")
    if not to_date:
        to_date = today()
    
    date_time = global_date_format(now()) + " " + format_time(now())
    currency = frappe.db.get_value("Company", company, "default_currency")

    condition_date = "where start_date BETWEEN '"+ from_date + \
        "' AND '" + to_date + "'"
    
    fp ='Tax_report.xlsx'
    wbook = xw.Workbook(name_path(fp))
    nw_data = "SELECT * FROM (select \
		s.name,s.employee,s.employee_name,s.start_date,s.end_date,s.docstatus, \
		e.tax_id,e.date_of_joining,e.department,e.current_state_of_abode_ as branch,e.designation,e.grade, e.pension_id,e.name_of_pension_manager,e.pension_manager,e.employee_name as femployee, \
		v.contrib, v.liabil,v.parent \
 		from `tabSalary Slip` s left join `tabEmployee` e on s.employee = e.name \
		LEFT JOIN \
				(SELECT Distinct k.parent, \
        					IFNULL((select d.amount from `tabSalary Detail` d where d.parentfield='deductions'and d.salary_component ='Tax' and d.parent=k.parent),0) as contrib, \
        					IFNULL((select d.amount from `tabSalary Detail` d where d.parentfield='deductions'and d.salary_component = 'Overtime Tax'and d.parent=k.parent),0) as liabil \
        FROM (select d.amount,d.parent,d.salary_component from `tabSalary Detail` d where d.salary_component in ('Tax','Overtime Tax') ) k \
			) v ON s.name = v.parent ) a {} ".format(condition_date)
    data = frappe.db.sql(nw_data, as_dict=1,)

    state_lst =[]
    headers_list =[
		'Salary Slip ID', 'Employee','Employee Name','Tax ID','Date of Joining',
		'Designation','Grade','Start Date','End Date','Tax','Overtime Tax'
	]

    #header format
    heading_format= wbook.add_format({
        "bottom":1,
        "bold": True,
    })
    #data formater
    date_format=wbook.add_format({'num_format': 'mm/dd/yyyy'})
    #money formater
    money_format= wbook.add_format({'num_format':'#,##0'})
    total_format = wbook.add_format({
        "bottom":1,
        "top":1,
        "bold": True,
        'num_format':'#,##0',
    })
    for s in data:
        if s['branch'] not in state_lst:
            state_lst.append(s['branch'])
    for cs in state_lst:
        populate = []
        ws = wbook.add_worksheet(cs)
        ws.write_row(3,0, headers_list,heading_format)

        rwnum = 4
        colnum = 0 
        dr_size = 2
        t_contr = 0
        t_liabil = 0
        populate = [x for x in data if x['branch']==cs]
        for i in range(len(populate)):
            t_con = populate[i]['contrib'] or 0
            t_bill = populate[i]['liabil'] or 0
            ws.write(rwnum,colnum,populate[i]['name'])
            ws.write(rwnum,colnum+1,populate[i]['employee'])
            ws.write(rwnum,colnum+2,populate[i]['employee_name'])
            ws.write(rwnum,colnum+3,populate[i]['tax_id'])
            ws.write(rwnum,colnum+4,populate[i]['date_of_joining'],date_format)
            #ws.write(rwnum,colnum+4,populate[i]['department'])
            ws.write(rwnum,colnum+5,populate[i]['designation'])
            ws.write(rwnum,colnum+6,populate[i]['grade'])
            ws.write(rwnum,colnum+7,populate[i]['start_date'],date_format)
            ws.write(rwnum,colnum+8,populate[i]['end_date'],date_format)
            ws.write(rwnum,colnum+9,t_con,money_format)
            ws.write(rwnum,colnum+10,t_bill,money_format)

            rwnum += 1
            t_contr +=t_con
            t_liabil +=t_bill

        ws.write_number(rwnum+dr_size, 9, t_contr,total_format)
        ws.write_number(rwnum+dr_size, 10, t_liabil,total_format)

        ws.write("A2", "State")
        ws.write("B2", cs)

    wbook.close()
    return file_path_return(fp)

def name_path(fp):
    """"""
    #f_path = frappe.get_site_path(fp)
    f_path = frappe.get_site_path()+'/private/'+fp
    #print(f"\n\n\n site path{frappe.get_site_path()+'/private/'+fp}\n\n\n")    
    return f_path

def file_path_return (cf):
    file_path = frappe.utils.get_bench_path() + '/' + \
        frappe.utils.get_site_name(frappe.local.site) + \
            '/private/'+cf 
    return file_path


@frappe.whitelist()
def pay_printslip_formatter (company=None, from_date=None, to_date=None):    
    """    
    get slip id 
    report_ps_filters = {
        "company": company,
        "doc": [customer_name],
        "from_date": from_date,
        "to_date": to_date,
        
    } 
    #frappe.db.get_value("Company", company, "default_currency")
    
    #ps_report = frappe.get_doc("Salary Slip", "Sal Slip/EMP-00001/00005") 
    pss_report = frappe.get_doc("DocType", "Salary Slip").get_data(
        limit=500, user="Administrator", filters="{'name':'Sal Slip/EMP-00001/00005'}", as_dict=True
    )
     data_ps = ps_report.get_data(
        limit=500, user="Administrator", filters="Sal Slip/EMP-00001/00005", as_dict=True
    ) """
    #data_ps =ps_report.get_all()
    #ps_report = frappe.db.get_value("Salary Slip", "Sal Slip/EMP-00001/00005")
    #ps_report = frappe.get_value("Salary Slip")
    #print(f'\n\n\n\n inside  : {pss_report} \n\n\n\n')
    ps = frappe.db.get_list('Salary Slip', filters={'name':'Sal Slip/EMP-00001/00005' },
    fields=['*'])
    print(f'\n\n\n\n inside  : {ps} \n\n\n\n')
    


    return True