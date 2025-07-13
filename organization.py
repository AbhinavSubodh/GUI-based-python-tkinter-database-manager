# Organization Databse GUI App with Tkinter + MySQL

import ttkbootstrap as tb
from ttkbootstrap.constants import *
from tkinter import messagebox, filedialog
import mysql.connector as pymy
from mysql.connector import Error
from PIL import Image, ImageTk
import io
import csv
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

# Database Initialization

def create_db():
    try:
        con = pymy.connect(
            host = "localhost",
            user = "project",
            password = "internship"
        )
        cursor = con.cursor()
        cursor.execute("CREATE DATABASE IF NOT EXISTS organization")
        cursor.execute("USE organization")

        # Create department Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS department (
                       d_id INT PRIMARY KEY,
                       dname VARCHAR(5) NOT NULL,
                       dloc varchar(25) NOT NULL,
                       dstrength INT NOT NULL,
                       hod_ssn INT NOT NULL,
                       hod_name VARCHAR(35) NOT NULL,
                       hod_email VARCHAR(50) NOT NULL,
                       hod_phone VARCHAR(15) NOT NULL )
                       """)

        # Create project Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS project (
                       p_id INT PRIMARY KEY,
                       pname VARCHAR(30) NOT NULL,
                       pstrength INT NOT NULL,
                       pstart_date DATE NOT NULL,
                       pend_date DATE DEFAULT NULL,
                       budget bigint NOT NULL,
                       pstatus VARCHAR(20) NOT NULL,
                       dept_id iNT NOT NULL,
                       FOREIGN KEY (dept_id) REFERENCES department(d_id) ON DELETE RESTRICT ON UPDATE CASCADE )
                       """)

        # Create employee Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS employee (
                       ssn INT PRIMARY KEY,
                       ename VARCHAR(35) NOT NULL,
                       email VARCHAR(50) NOT NULL,
                       ephone VARCHAR(15) NOT NULL,
                       eage INT NOT NULL,
                       designation VARCHAR(20) NOT NULL,
                       join_date DATE NOT NULL,
                       salary BIGINT NOT NULL,
                       eloc varchar(25),
                       department_id INT NOT NULL,
                       project_id INT DEFAULT NULL,
                       FOREIGN KEY (department_id) REFERENCES department(d_id) ON DELETE RESTRICT ON UPDATE CASCADE,
                       FOREIGN KEY (project_id) REFERENCES project(p_id) ON DELETE RESTRICT ON UPDATE CASCADE )
                       """)
    
    # Create dependent Table

        cursor.execute("""
        CREATE TABLE IF NOT EXISTS dependent (
                       daadhar BIGINT PRIMARY KEY NOT NULL,
                       dname VARCHAR(35) NOT NULL,
                       dage INT NOT NULL,
                       relation VARCHAR(20) NOT NULL,
                       essn INT NOT NULL,
                       FOREIGN KEY (essn) REFERENCES employee(ssn) ON DELETE RESTRICT ON UPDATE CASCADE )
                       """)
    
        con.commit()
        con.close()
    except Error as e:
        messagebox.showerror("Database Error", f"Error creating database: {e}")
        print(f"Error creating database: {e}")

# Database Connection

def connect_db():
    try:
         return pymy.connect(
            host = "localhost",
            user = "project",
            password = "internship",
            database = "organization"
        )
    except Error as e:
        messagebox.showerror("Database Error", f"Error connecting to database: {e}")
        print(f"Error connecting to database: {e}")
        return None

create_db()

# GUI Application Setup

root = tb.Window(themename="flatly")
root.title("Organization Database Manager")
root.state('zoomed')
root.resizable(True, True)
root.columnconfigure(0, weight = 1)
root.rowconfigure(0, weight = 1)
notebook = tb.Notebook(root)
notebook.pack(fill='both', expand = True)
DEFAULT_FONT = ("Segoe UI", 11)
BG_COLOR = "#f7f7fa"
BUTTON_COLOR = "#4a90e2"
BUTTON_TEXT = "#fff"
root.option_add("*Font", DEFAULT_FONT)
style = tb.Style()
style.configure("TLabel", background=BG_COLOR, foreground="#222")
style.configure("TEntry", fieldbackground="#fff", foreground="#222")
style.configure("TButton", background=BUTTON_COLOR, foreground=BUTTON_TEXT, padding=6)
style.configure("Treeview", font=DEFAULT_FONT, rowheight=28, background="#fff", fieldbackground="#fff")
style.configure("Treeview.Heading", font=("Segoe UI", 11, "bold"), background="#e6e6e6")
root.title("Organization Database Manager")

# Department Tab

department_tab = tb.Frame(notebook)
notebook.add(department_tab, text="Department")
fields = {
    "Department Id" : tb.StringVar(),
    "Department Name" : tb.StringVar(),
    "Department Location" : tb.StringVar(),
    "Department Strength" : tb.StringVar(),
    "HOD SSN" : tb.StringVar(),
    "HOD Name" : tb.StringVar(),
    "HOD Email" : tb.StringVar(),
    "HOD Phone" : tb.StringVar()
}
department_tab.columnconfigure(0, weight = 1)
department_tab.columnconfigure(1, weight = 1)
department_tab.columnconfigure(2, weight = 1)
department_tab.rowconfigure(len(fields) + 1, weight = 1)

for i, (label, var) in enumerate(fields.items()):
    tb.Label(department_tab, text = label).grid(row = i, column = 0, padx = 10, pady = 5, sticky = 'e')
    tb.Entry(department_tab, textvariable = var).grid(row = i, column = 1, padx = 10, pady = 5, sticky = 'ew')

def insert_department():
    values = [var.get() for var in fields.values()]
    if any(v == "" for v in values):
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            INSERT INTO department (d_id, dname, dloc, dstrength, hod_ssn, hod_name, hod_email, hod_phone)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(values)
            )
            con.commit()
            con.close()
            fetch_departments()
            messagebox.showinfo("Success", "Department added successfully.")
            for var in fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error inserting department: {e}")
        print(f"Error inserting department: {e}")

def filter_departments():
    keyword = dept_search_var.get().lower()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM department")
            rows = cursor.fetchall()
            con.close()
            dept_tree.delete(*dept_tree.get_children())
            for row in rows:
                if any(keyword in str(cell).lower() for cell in row):
                    dept_tree.insert("", tb.END, values=row)
        dept_search_var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error filtering departments: {e}")
        print(f"Error filtering departments: {e}")

def get_selected_department():
    selected = dept_tree.focus()
    return dept_tree.item(selected)['values'] if selected else None

def update_department():
    selected = get_selected_department()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a department to update.")
        return
    values = [var.get() for var in fields.values()]
    if any(v == "" for v in values):
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            UPDATE department SET d_id = %s, dname = %s, dloc = %s, dstrength = %s, hod_ssn = %s, hod_name = %s, hod_email = %s, hod_phone = %s
            WHERE d_id = %s
            """, (*tuple(values), selected[0]))
            con.commit()
            con.close()
            fetch_departments()
            messagebox.showinfo("Success", "Department updated successfully.")
            for var in fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error updating department: {e}")
        print(f"Error updating department: {e}")

def delete_department():
    selected = get_selected_department()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a department to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the department '{selected[1]}'?")
    if not confirm:
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM department WHERE d_id = %s", (selected[0],))
            con.commit()
            con.close()
            fetch_departments()
            messagebox.showinfo("Success", "Department deleted successfully.")
    except Error as e:
        messagebox.showerror("Database Error", f"Error deleting department: {e}")
        print(f"Error deleting department: {e}")

def fetch_departments():
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM department")
            rows = cursor.fetchall()
            con.close()
            dept_tree.delete(*dept_tree.get_children())
            for row in rows:
                dept_tree.insert("", tb.END, values = row)
    except Error as e:
        messagebox.showerror("Database Error", f"Error fetching departments: {e}")
        print(f"Error fetching departments: {e}")

tb.Button(department_tab, text = "Insert Department", command = insert_department, bootstyle='primary').grid(row = len(fields), column = 0, padx = 10, pady = 10, sticky = 'ew')
tb.Button(department_tab, text = "Update", command = update_department, bootstyle='info').grid(row = len(fields), column = 1, padx = 10, pady = 10, sticky = 'ew')
tb.Button(department_tab, text = "Delete Department", command = delete_department, bootstyle='danger').grid(row = len(fields), column = 2, padx = 10, pady = 10, sticky = 'ew')
department_tab.columnconfigure(2, weight=1)
dept_tree = tb.Treeview(department_tab, columns = ("SSN", "Name", "Location", "Strength", "HOD SSN", "HOD NAME", "HOD EMAIL", "HOD PHONE"), show = "headings")

for col in dept_tree["columns"]:
    dept_tree.heading(col, text = col)
    dept_tree.column(col, width=120, anchor='center')

dept_search_var = tb.StringVar()
tb.Entry(department_tab, textvariable = dept_search_var).grid(row = len(fields) + 2, column = 0, padx = 10, pady = 5, sticky = 'ew')
tb.Button(department_tab, text = "Search", command = filter_departments, bootstyle='secondary').grid(row = len(fields) + 2, column = 1, padx = 10, pady = 5, sticky = 'ew')
dept_tree.grid(row = len(fields) + 1, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = 'nsew')
fetch_departments()
department_tab.columnconfigure(0, weight=1)
department_tab.columnconfigure(1, weight=1)
department_tab.columnconfigure(2, weight=1)
department_tab.rowconfigure(len(fields) + 1, weight=1)

for i in range(len(fields)):
    department_tab.grid_slaves(row=i, column=0)[0].grid_configure(padx=15, pady=7, sticky='e')
    department_tab.grid_slaves(row=i, column=1)[0].grid_configure(padx=15, pady=7, sticky='ew')

department_tab.grid_slaves(row=len(fields), column=0)[0].grid_configure(padx=10, pady=10, sticky='ew')
department_tab.grid_slaves(row=len(fields), column=1)[0].grid_configure(padx=10, pady=10, sticky='ew')
department_tab.grid_slaves(row=len(fields), column=2)[0].grid_configure(padx=10, pady=10, sticky='ew')
dept_tree.grid_configure(row=len(fields) + 1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
department_tab.grid_slaves(row=len(fields) + 2, column=0)[0].grid_configure(padx=10, pady=5, sticky='ew')
department_tab.grid_slaves(row=len(fields) + 2, column=1)[0].grid_configure(padx=10, pady=5, sticky='ew')

# Project Tab

project_tab = tb.Frame(notebook)
notebook.add(project_tab, text = "Project")
project_fields = {
    "Project Id" : tb.StringVar(),
    "Project Name" : tb.StringVar(),
    "Project Strength" : tb.StringVar(),
    "Project Start Date" : tb.StringVar(),
    "Project End Date" : tb.StringVar(),
    "Budget" : tb.StringVar(),
    "Status" : tb.StringVar(),
    "Department Id" : tb.StringVar()
}
project_tab.columnconfigure(0, weight = 1)
project_tab.columnconfigure(1, weight = 1)
project_tab.columnconfigure(2, weight=1)
project_tab.rowconfigure(len(project_fields) + 1, weight = 1)

for i, (label, var) in enumerate(project_fields.items()):
    tb.Label(project_tab, text = label).grid(row = i, column = 0, padx = 10, pady = 5, sticky = 'e')
    tb.Entry(project_tab, textvariable = var).grid(row = i, column = 1, padx = 10, pady = 5, sticky = 'ew')

def insert_project():
    required_indices = [0, 1, 2, 3, 5, 6, 7]
    values = [var.get() for var in project_fields.values()]
    if any(values[i] == "" for i in required_indices) or not values[7].isdigit():
        messagebox.showwarning("Input Error", "All fields except end date are required.")
        return
    if values[4].strip().lower() in ("", "null", "none"):
        values[4] = None
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            INSERT INTO project (p_id, pname, pstrength, pstart_date, pend_date, budget, pstatus, dept_id)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
            """, tuple(values))
            con.commit()
            con.close()
            fetch_projects()
            messagebox.showinfo("Success", "Project added successfully.")
            for var in project_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error inserting project: {e}")
        print(f"Error inserting project: {e}")

def filter_projects():
    keyword = project_search_var.get().lower()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM project")
            rows = cursor.fetchall()
            con.close()
            project_tree.delete(*project_tree.get_children())
            for row in rows:
                if any(keyword in str(cell).lower() for cell in row):
                    project_tree.insert("", tb.END, values=row)
        project_search_var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error filtering projects: {e}")
        print(f"Error filtering projects: {e}")

def get_selected_project():
    selected = project_tree.focus()
    return project_tree.item(selected)['values'] if selected else None

def update_project():
    selected = get_selected_project()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a project to update.")
        return
    values = [var.get() for var in project_fields.values()]
    required_indices = [0, 1, 2, 3, 5, 6, 7]
    if any(values[i] == "" for i in required_indices) or not values[7].isdigit():
        messagebox.showwarning("Input Error", "All fields except end date are required.")
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            UPDATE project SET p_id = %s, pname = %s, pstrength = %s, pstart_date = %s, pend_date = %s, budget = %s, pstatus = %s, dept_id = %s
            WHERE p_id = %s
            """, (*tuple(values), selected[0]))
            con.commit()
            con.close()
            fetch_projects()
            messagebox.showinfo("Success", "Project updated successfully.")
            for var in project_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error updating project: {e}")
        print(f"Error updating project: {e}")

def delete_project():
    selected = get_selected_project()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a project to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the project '{selected[1]}'?")
    if not confirm:
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM project WHERE p_id = %s", (selected[0],))
            con.commit()
            con.close()
            fetch_projects()
            messagebox.showinfo("Success", "Project deleted successfully.")
    except Error as e:
        messagebox.showerror("Database Error", f"Error deleting project: {e}")
        print(f"Error deleting project: {e}")

def fetch_projects():
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM project")
            rows = cursor.fetchall()
            con.close()
            project_tree.delete(*project_tree.get_children())
            for row in rows:
                project_tree.insert("", tb.END, values = row)
    except Error as e:
        messagebox.showerror("Database Error", f"Error fetching projects: {e}")
        print(f"Error fetching projects: {e}")

tb.Button(project_tab, text = "Insert Project", command = insert_project, bootstyle='primary').grid(row = len(project_fields), column = 0, padx = 10, pady = 10, sticky = 'ew')
tb.Button(project_tab, text = "Update", command = update_project, bootstyle='info').grid(row = len(project_fields), column = 1, padx = 10, pady = 10, sticky = 'ew')
tb.Button(project_tab, text = "Delete Project", command = delete_project, bootstyle='danger').grid(row = len(project_fields), column = 2, padx = 10, pady = 10, sticky = 'ew')
project_tab.columnconfigure(2, weight=1)
project_tree = tb.Treeview(project_tab, columns = ("Id", "Name", "Strength", "Start Date", "End Date", "Budget", "Status", "Department Id"), show = "headings")

for col in project_tree["columns"]:
    project_tree.heading(col, text = col)
    project_tree.column(col, width=120, anchor='center')

project_search_var = tb.StringVar()
tb.Entry(project_tab, textvariable = project_search_var).grid(row = len(project_fields) + 2, column = 0, padx = 10, pady = 5, sticky = 'ew')
tb.Button(project_tab, text = "Search", command = filter_projects, bootstyle='secondary').grid(row = len(project_fields) + 2, column = 1, padx = 10, pady = 5, sticky = 'ew')
project_tree.grid(row = len(project_fields) + 1, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = 'nsew')
fetch_projects()
project_tab.columnconfigure(0, weight=1)
project_tab.columnconfigure(1, weight=1)
project_tab.columnconfigure(2, weight=1)
project_tab.rowconfigure(len(project_fields) + 1, weight=1)

for i in range(len(project_fields)):
    project_tab.grid_slaves(row=i, column=0)[0].grid_configure(padx=15, pady=7, sticky='e')
    project_tab.grid_slaves(row=i, column=1)[0].grid_configure(padx=15, pady=7, sticky='ew')

project_tab.grid_slaves(row=len(project_fields), column=0)[0].grid_configure(padx=10, pady=10, sticky='ew')
project_tab.grid_slaves(row=len(project_fields), column=1)[0].grid_configure(padx=10, pady=10, sticky='ew')
project_tab.grid_slaves(row=len(project_fields), column=2)[0].grid_configure(padx=10, pady=10, sticky='ew')
project_tree.grid_configure(row=len(project_fields) + 1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
project_tab.grid_slaves(row=len(project_fields) + 2, column=0)[0].grid_configure(padx=10, pady=5, sticky='ew')
project_tab.grid_slaves(row=len(project_fields) + 2, column=1)[0].grid_configure(padx=10, pady=5, sticky='ew')

# Employee Tab

employee_tab = tb.Frame(notebook)
notebook.add(employee_tab, text = "Employee")
employee_fields = {
    "SSN" : tb.StringVar(),
    "Name" : tb.StringVar(),
    "Email" : tb.StringVar(),
    "Phone" : tb.StringVar(),
    "Age" : tb.StringVar(),
    "Designation" : tb.StringVar(),
    "Join Date (YYYY-MM-DD)" : tb.StringVar(),
    "Salary" : tb.StringVar(),
    "Location" : tb.StringVar(),
    "Department Id" : tb.StringVar(),
    "Project Id" : tb.StringVar(),
    "Photo" : tb.StringVar()
}
employee_tab.columnconfigure(0, weight = 1)
employee_tab.columnconfigure(1, weight = 1)
employee_tab.columnconfigure(2, weight = 1)
employee_tab.rowconfigure(len(employee_fields) + 1, weight = 1)

for i, (label, var) in enumerate(employee_fields.items()):
    if label == "Photo":
        continue
    tb.Label(employee_tab, text = label).grid(row = i, column = 0, padx = 10, pady = 5, sticky = 'e')
    tb.Entry(employee_tab, textvariable = var).grid(row = i, column = 1, padx = 10, pady = 5, sticky = 'ew')

def select_employee_photo():
    file_path = filedialog.askopenfilename(
        title = "Select Employee Photo",
        filetypes = [("Image Files", "*.jpg;*.jpeg;*.png;*.gif")]
    )
    if file_path:
        employee_fields["Photo"].set(file_path)

tb.Button(employee_tab, text = "Select Photo", command = select_employee_photo, bootstyle='secondary').grid(row = len(employee_fields), column = 3, padx = 10, pady = 10, sticky = 'ew')

def insert_employee():
    values = [var.get() for var in employee_fields.values()]
    if any(values[i] == "" for i in range(10)):
        messagebox.showwarning("Input Error", "All fields except project id are required.")
        return
    photo_path = employee_fields["Photo"].get()
    photo_data = None
    if photo_path:
        with open(photo_path, 'rb') as f:
            photo_data = f.read()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            INSERT INTO employee (ssn, ename, email, ephone, eage, designation, join_date, salary, eloc, department_id, project_id, photo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            """, (*values[:-1], photo_data,))
            con.commit()
            con.close()
            fetch_employees()
            for item in employee_tree.get_children():
                vals = employee_tree.item(item)['values']
                if str(vals[0]) == str(employee_fields["SSN"].get()):
                    employee_tree.selection_set(item)
                    employee_tree.focus(item)
                    show_employee_photo(None)
                    break
            messagebox.showinfo("Success", "Employee added successfully.")
            for var in employee_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error inserting employee: {e}")
        print(f"Error inserting employee: {e}")

def filter_employees():
    keyword = employee_search_var.get().lower()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM employee")
            rows = cursor.fetchall()
            con.close()
            employee_tree.delete(*employee_tree.get_children())
            for row in rows:
                if any(keyword in str(cell).lower() for cell in row):
                    employee_tree.insert("", tb.END, values=row)
        employee_search_var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error filtering employees: {e}")
        print(f"Error filtering employees: {e}")

def get_selected_employee():
    selected = employee_tree.focus()
    return employee_tree.item(selected)['values'] if selected else None

def update_employee():
    selected = get_selected_employee()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select an employee to update.")
        return
    values = [var.get() for var in employee_fields.values()]
    if any(values[i] == "" for i in range(10)):
        messagebox.showwarning("Input Error", "All fields except project id are required.")
        return
    photo_path = employee_fields["Photo"].get()
    photo_data = None
    if photo_path:
        with open(photo_path, 'rb') as f:
            photo_data = f.read()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            UPDATE employee SET ename = %s, email = %s, ephone = %s, eage = %s, designation = %s, join_date = %s, salary = %s, eloc = %s, department_id = %s, project_id = %s, photo = %s
            WHERE ssn = %s
            """, (*values[1:-1], photo_data, selected[0]))
            con.commit()
            con.close()
            fetch_employees()
            for item in employee_tree.get_children():
                vals = employee_tree.item(item)['values']
                if str(vals[0]) == str(employee_fields["SSN"].get()):
                    employee_tree.selection_set(item)
                    employee_tree.focus(item)
                    show_employee_photo(None)
                    break
            messagebox.showinfo("Success", "Employee updated successfully.")
            for var in employee_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error updating employee: {e}")
        print(f"Error updating employee: {e}")

def delete_employee():
    selected = get_selected_employee()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select an employee to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the employee '{selected[1]}'?")
    if not confirm:
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM employee WHERE ssn = %s", (selected[0],))
            con.commit()
            con.close()
            fetch_employees()
            messagebox.showinfo("Success", "Employee deleted successfully.")
    except Error as e:
        messagebox.showerror("Database Error", f"Error deleting employee: {e}")
        print(f"Error deleting employee: {e}")

def show_employee_photo(event):
    selected = get_selected_employee()
    if not selected:
        return
    ssn = selected[0]
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT photo FROM employee WHERE ssn = %s", (ssn,))
            result = cursor.fetchone()
            con.close()
            if result and result[0]:
                image = Image.open(io.BytesIO(result[0]))
                image = image.resize((150, 150))
                photo_img = ImageTk.PhotoImage(image)
                employee_photo_label.config(image = photo_img, text = "")
                employee_photo_label.image = photo_img
            else:
                employee_photo_label.config(image = "", text = "No Photo")
    except Exception as e:
        employee_photo_label.config(image = "", text = "Error loading photo")

employee_photo_label = tb.Label(employee_tab, text = "No Photo")
employee_photo_label.grid(row = len(employee_fields) + 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'nsew')

def fetch_employees():
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM employee")
            rows = cursor.fetchall()
            con.close()
            employee_tree.delete(*employee_tree.get_children())
            for row in rows:
                employee_tree.insert("", tb.END, values = row)
    except Error as e:
        messagebox.showerror("Database Error", f"Error fetching employees: {e}")
        print(f"Error fetching employees: {e}")

tb.Button(employee_tab, text = "Insert Employee", command = insert_employee, bootstyle='primary').grid(row = len(employee_fields), column = 0, padx = 10, pady = 10, sticky = 'ew')
tb.Button(employee_tab, text = "Update", command = update_employee, bootstyle='info').grid(row = len(employee_fields), column = 1, padx = 10, pady = 10, sticky = 'ew')
tb.Button(employee_tab, text = "Delete Employee", command = delete_employee, bootstyle='danger').grid(row = len(employee_fields), column = 2, padx = 10, pady = 10, sticky = 'ew')
employee_tree = tb.Treeview(employee_tab, columns = ("SSN", "Name", "Email", "Phone", "Age", "Designation", "Join Date", "Salary", "Location", "Department Id", "Project Id"), show = "headings")

for col in employee_tree["columns"]:
    employee_tree.heading(col, text = col)
    employee_tree.column(col, width=120, anchor='center')

employee_search_var = tb.StringVar()
tb.Entry(employee_tab, textvariable = employee_search_var).grid(row = len(employee_fields) + 2, column = 0, padx = 10, pady = 5, sticky = 'ew')
tb.Button(employee_tab, text = "Search", command = filter_employees, bootstyle='secondary').grid(row = len(employee_fields) + 2, column = 1, padx = 10, pady = 5, sticky = 'ew')
employee_tree.grid(row = len(employee_fields) + 1, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = 'nsew')
employee_tree.bind("<<TreeviewSelect>>", show_employee_photo)
fetch_employees()
employee_tab.columnconfigure(0, weight=1)
employee_tab.columnconfigure(1, weight=1)
employee_tab.columnconfigure(2, weight=1)
employee_tab.rowconfigure(len(employee_fields) + 1, weight=1)

for i in range(len(employee_fields)):
    if list(employee_fields.keys())[i] == "Photo":
        continue
    employee_tab.grid_slaves(row=i, column=0)[0].grid_configure(padx=15, pady=7, sticky='e')
    employee_tab.grid_slaves(row=i, column=1)[0].grid_configure(padx=15, pady=7, sticky='ew')

employee_tab.grid_slaves(row=len(employee_fields), column=0)[0].grid_configure(padx=10, pady=10, sticky='ew')
employee_tab.grid_slaves(row=len(employee_fields), column=1)[0].grid_configure(padx=10, pady=10, sticky='ew')
employee_tab.grid_slaves(row=len(employee_fields), column=2)[0].grid_configure(padx=10, pady=10, sticky='ew')
employee_tree.grid_configure(row=len(employee_fields) + 1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
employee_photo_label.grid_configure(row=len(employee_fields) + 3, column=0, columnspan=3, padx=10, pady=15, sticky='n')
employee_tab.grid_slaves(row=len(employee_fields) + 2, column=0)[0].grid_configure(padx=10, pady=5, sticky='ew')
employee_tab.grid_slaves(row=len(employee_fields) + 2, column=1)[0].grid_configure(padx=10, pady=5, sticky='ew')

# Dependent Tab

dependent_tab = tb.Frame(notebook)
notebook.add(dependent_tab, text = "Dependent")
dependent_fields = {
    "Aadhar" : tb.StringVar(),
    "Name" : tb.StringVar(),
    "Age" : tb.StringVar(),
    "Relation" : tb.StringVar(),
    "Employee SSN" : tb.StringVar(),
    "Photo" : tb.StringVar()
}
dependent_tab.columnconfigure(0, weight=1)
dependent_tab.columnconfigure(1, weight=1)
dependent_tab.columnconfigure(2, weight=1)
dependent_tab.rowconfigure(len(dependent_fields) + 1, weight=1)

for i, (label, var) in enumerate(dependent_fields.items()):
    if label == "Photo":
        continue
    tb.Label(dependent_tab, text = label).grid(row = i, column = 0, padx = 10, pady = 5, sticky = 'e')
    tb.Entry(dependent_tab, textvariable = var).grid(row = i, column = 1, padx = 10, pady = 5, sticky = 'ew')

def select_dependent_photo():
    file_path = filedialog.askopenfilename(
        title = "Select Dependent Photo",
        filetypes = [("Image Files", "*.jpg;*.jpeg;*.png;*.gif")]
    )
    if file_path:
        dependent_fields["Photo"].set(file_path)

tb.Button(dependent_tab, text = "Select Photo", command = select_dependent_photo, bootstyle='secondary').grid(row = len(dependent_fields), column = 3, padx = 10, pady = 10, sticky = 'ew')

def insert_dependent():
    values = [var.get() for var in dependent_fields.values()]
    if any(v == "" for v in values):
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    photo_path = dependent_fields["Photo"].get()
    photo_data = None
    if photo_path:
        with open(photo_path, 'rb') as f:
            photo_data = f.read()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            INSERT INTO dependent (daadhar, dname, dage, relation, essn, photo)
            VALUES (%s, %s, %s, %s, %s, %s)
            """, (*values[:-1], photo_data))
            con.commit()
            con.close()
            fetch_dependents()
            for item in dependent_tree.get_children():
                vals = dependent_tree.item(item)['values']
                if str(vals[0]) == str(dependent_fields["Aadhar"].get()):
                    dependent_tree.selection_set(item)
                    dependent_tree.focus(item)
                    show_dependent_photo(None)
                    break
            messagebox.showinfo("Success", "Dependent added successfully.")
            for var in dependent_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error inserting dependent: {e}")
        print(f"Error inserting dependent: {e}")

def filter_dependents():
    keyword = dependent_search_var.get().lower()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM dependent")
            rows = cursor.fetchall()
            con.close()
            dependent_tree.delete(*dependent_tree.get_children())
            for row in rows:
                if any(keyword in str(cell).lower() for cell in row):
                    dependent_tree.insert("", tb.END, values=row)
        dependent_search_var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error filtering dependents: {e}")
        print(f"Error filtering dependents: {e}")

def get_selected_dependent():
    selected = dependent_tree.focus()
    return dependent_tree.item(selected)['values'] if selected else None

def update_dependent():
    selected = get_selected_dependent()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a dependent to update.")
        return
    values = [var.get() for var in dependent_fields.values()]
    if any(v == "" for v in values):
        messagebox.showwarning("Input Error", "Please fill all fields.")
        return
    photo_path = dependent_fields["Photo"].get()
    photo_data = None
    if photo_path:
        with open(photo_path, 'rb') as f:
            photo_data = f.read()
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("""
            UPDATE dependent SET dname = %s, dage = %s, relation = %s, essn = %s, photo = %s
            WHERE daadhar = %s
            """, (*values[1:-1], photo_data, selected[0]))
            con.commit()
            con.close()
            fetch_dependents()
            for item in dependent_tree.get_children():
                vals = dependent_tree.item(item)['values']
                if str(vals[0]) == str(dependent_fields["Aadhar"].get()):
                    dependent_tree.selection_set(item)
                    dependent_tree.focus(item)
                    show_dependent_photo(None)
                    break
            messagebox.showinfo("Success", "Dependent updated successfully.")
            for var in dependent_fields.values():
                var.set("")
    except Error as e:
        messagebox.showerror("Database Error", f"Error updating dependent: {e}")
        print(f"Error updating dependent: {e}")

def delete_dependent():
    selected = get_selected_dependent()
    if not selected:
        messagebox.showwarning("Selection Error", "Please select a dependent to delete.")
        return
    confirm = messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete the dependent '{selected[1]}'?")
    if not confirm:
        return
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("DELETE FROM dependent WHERE daadhar = %s", (selected[0],))
            con.commit()
            con.close()
            fetch_dependents()
            messagebox.showinfo("Success", "Dependent deleted successfully.")
    except Error as e:
        messagebox.showerror("Database Error", f"Error deleting dependent: {e}")
        print(f"Error deleting dependent: {e}")

def show_dependent_photo(event):
    selected = get_selected_dependent()
    if not selected:
        return
    aadhar = selected[0]
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT photo FROM dependent WHERE daadhar = %s", (aadhar,))
            result = cursor.fetchone()
            con.close()
            if result and result[0]:
                image = Image.open(io.BytesIO(result[0]))
                image = image.resize((150, 150))
                photo_img = ImageTk.PhotoImage(image)
                dependent_photo_label.config(image = photo_img, text = "")
                dependent_photo_label.image = photo_img
            else:
                dependent_photo_label.config(image = "", text = "No Photo")
    except Exception as e:
        dependent_photo_label.config(image = "", text = "Error loading photo")

dependent_photo_label = tb.Label(dependent_tab, text = "No Photo")
dependent_photo_label.grid(row = len(dependent_fields) + 3, column = 0, columnspan = 2, padx = 10, pady = 10, sticky = 'nsew')

def fetch_dependents():
    try:
        con = connect_db()
        if con:
            cursor = con.cursor()
            cursor.execute("SELECT * FROM dependent")
            rows = cursor.fetchall()
            con.close()
            dependent_tree.delete(*dependent_tree.get_children())
            for row in rows:
                dependent_tree.insert("", tb.END, values = row)
    except Error as e:
        messagebox.showerror("Database Error", f"Error fetching dependents: {e}")
        print(f"Error fetching dependents: {e}")

tb.Button(dependent_tab, text = "Insert Dependent", command = insert_dependent, bootstyle='primary').grid(row = len(dependent_fields), column = 0, padx = 10, pady = 10, sticky = 'ew')
tb.Button(dependent_tab, text = "Update", command = update_dependent, bootstyle='info').grid(row = len(dependent_fields), column = 1, padx = 10, pady = 10, sticky = 'ew')
tb.Button(dependent_tab, text = "Delete Dependent", command = delete_dependent, bootstyle='danger').grid(row = len(dependent_fields), column = 2, padx = 10, pady = 10, sticky = 'ew')
dependent_tab.columnconfigure(2, weight=1)
dependent_tree = tb.Treeview(dependent_tab, columns = ("Aadhar", "Name", "Age", "Relation", "Employee SSN"), show = "headings")

for col in dependent_tree["columns"]:
    dependent_tree.heading(col, text = col)
    dependent_tree.column(col, width=120, anchor='center')

dependent_search_var = tb.StringVar()
tb.Entry(dependent_tab, textvariable = dependent_search_var).grid(row = len(dependent_fields) + 2, column = 0, padx = 10, pady = 5, sticky = 'ew')
tb.Button(dependent_tab, text = "Search", command = filter_dependents, bootstyle='secondary').grid(row = len(dependent_fields) + 2, column = 1, padx = 10, pady = 5, sticky = 'ew')
dependent_tree.grid(row = len(dependent_fields) + 1, column = 0, columnspan = 3, padx = 10, pady = 10, sticky = 'nsew')
dependent_tree.bind("<<TreeviewSelect>>", show_dependent_photo)
fetch_dependents()
dependent_tab.columnconfigure(0, weight=1)
dependent_tab.columnconfigure(1, weight=1)
dependent_tab.columnconfigure(2, weight=1)
dependent_tab.rowconfigure(len(dependent_fields) + 1, weight=1)

for i in range(len(dependent_fields)):
    if list(dependent_fields.keys())[i] == "Photo":
        continue
    dependent_tab.grid_slaves(row=i, column=0)[0].grid_configure(padx=15, pady=7, sticky='e')
    dependent_tab.grid_slaves(row=i, column=1)[0].grid_configure(padx=15, pady=7, sticky='ew')

dependent_tab.grid_slaves(row=len(dependent_fields), column=0)[0].grid_configure(padx=10, pady=10, sticky='ew')
dependent_tab.grid_slaves(row=len(dependent_fields), column=1)[0].grid_configure(padx=10, pady=10, sticky='ew')
dependent_tab.grid_slaves(row=len(dependent_fields), column=2)[0].grid_configure(padx=10, pady=10, sticky='ew')
dependent_tree.grid_configure(row=len(dependent_fields) + 1, column=0, columnspan=3, padx=10, pady=10, sticky='nsew')
dependent_photo_label.grid_configure(row=len(dependent_fields) + 3, column=0, columnspan=3, padx=10, pady=15, sticky='n')
dependent_tab.grid_slaves(row=len(dependent_fields) + 2, column=0)[0].grid_configure(padx=10, pady=5, sticky='ew')
dependent_tab.grid_slaves(row=len(dependent_fields) + 2, column=1)[0].grid_configure(padx=10, pady=5, sticky='ew')

def import_departments_from_csv():
    file_path = filedialog.askopenfilename(title="Select Department CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    imported = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                values = [
                    row['Department Id'],
                    row['Department Name'],
                    row['Department Location'],
                    row['Department Strength'],
                    row['HOD SSN'],
                    row['HOD Name'],
                    row['HOD Email'],
                    row['HOD Phone']
                ]
                con = connect_db()
                if con:
                    cursor = con.cursor()
                    cursor.execute("""
                        INSERT INTO department (d_id, dname, dloc, dstrength, hod_ssn, hod_name, hod_email, hod_phone)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(values))
                    con.commit()
                    con.close()
                    imported += 1
            except Exception as e:
                print(f"Error importing row: {row} - {e}")
    fetch_departments()
    messagebox.showinfo("Import Complete", f"Imported {imported} departments from CSV.")

def import_projects_from_csv():
    file_path = filedialog.askopenfilename(title="Select Project CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    imported = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                values = [
                    row['Project Id'],
                    row['Project Name'],
                    row['Project Strength'],
                    row['Project Start Date'],
                    row['Project End Date'] if row['Project End Date'] else None,
                    row['Budget'],
                    row['Status'],
                    row['Department Id']
                ]
                con = connect_db()
                if con:
                    cursor = con.cursor()
                    cursor.execute("""
                        INSERT INTO project (p_id, pname, pstrength, pstart_date, pend_date, budget, pstatus, dept_id)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(values))
                    con.commit()
                    con.close()
                    imported += 1
            except Exception as e:
                print(f"Error importing row: {row} - {e}")
    fetch_projects()
    messagebox.showinfo("Import Complete", f"Imported {imported} projects from CSV.")

def import_employees_from_csv():
    file_path = filedialog.askopenfilename(title="Select Employee CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    imported = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                values = [
                    row['SSN'], row['Name'], row['Email'], row['Phone'], row['Age'], row['Designation'],
                    row['Join Date (YYYY-MM-DD)'], row['Salary'], row['Location'], row['Department Id'], row['Project Id'], None
                ]
                con = connect_db()
                if con:
                    cursor = con.cursor()
                    cursor.execute("""
                        INSERT INTO employee (ssn, ename, email, ephone, eage, designation, join_date, salary, eloc, department_id, project_id, photo)
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """, tuple(values))
                    con.commit()
                    con.close()
                    imported += 1
            except Exception as e:
                print(f"Error importing row: {row} - {e}")
    fetch_employees()
    messagebox.showinfo("Import Complete", f"Imported {imported} employees from CSV.")

def import_dependents_from_csv():
    file_path = filedialog.askopenfilename(title="Select Dependent CSV", filetypes=[("CSV Files", "*.csv")])
    if not file_path:
        return
    imported = 0
    with open(file_path, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            try:
                values = [
                    row['Aadhar'],
                    row['Name'],
                    row['Age'],
                    row['Relation'],
                    row['Employee SSN'],
                    None
                ]
                con = connect_db()
                if con:
                    cursor = con.cursor()
                    cursor.execute("""
                        INSERT INTO dependent (daadhar, dname, dage, relation, essn, photo)
                        VALUES (%s, %s, %s, %s, %s, %s)
                    """, tuple(values))
                    con.commit()
                    con.close()
                    imported += 1
            except Exception as e:
                print(f"Error importing row: {row} - {e}")
    fetch_dependents()
    messagebox.showinfo("Import Complete", f"Imported {imported} dependents from CSV.")

def on_tab_changed(event):
    tab = event.widget.tab(event.widget.index('current'))['text']
    if tab == "Department":
        if messagebox.askyesno("Import CSV", "Do you want to import Department data from CSV?"):
            import_departments_from_csv()
    elif tab == "Project":
        if messagebox.askyesno("Import CSV", "Do you want to import Project data from CSV?"):
            import_projects_from_csv()
    elif tab == "Employee":
        if messagebox.askyesno("Import CSV", "Do you want to import Employee data from CSV?"):
            import_employees_from_csv()
    elif tab == "Dependent":
        if messagebox.askyesno("Import CSV", "Do you want to import Dependent data from CSV?"):
            import_dependents_from_csv()

notebook.bind("<<NotebookTabChanged>>", on_tab_changed)

def download_all_employees_as_pdfs():
    import os
    import tempfile
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
    folder = filedialog.askdirectory(title='Select Folder to Save Employee PDFs')
    if not folder:
        return
    try:
        con = connect_db()
        if not con:
            messagebox.showerror("Database Error", "Could not connect to database.")
            return
        cursor = con.cursor(dictionary=True)
        cursor.execute("SELECT * FROM employee")
        employees = cursor.fetchall()
        for emp in employees:
            filename = f"{emp['ename'].replace(' ', '_')}_SSN_{emp['ssn']}.pdf"
            file_path = os.path.join(folder, filename)
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter
            y = height - 40
            c.setFont("Helvetica-Bold", 16)
            c.drawString(30, y, f"Employee Report: {emp['ename']} (SSN: {emp['ssn']})")
            y -= 30
            if emp.get('photo'):
                try:
                    img_bytes = emp['photo']
                    with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                        tmp_img.write(img_bytes)
                        tmp_img.flush()
                        c.drawImage(tmp_img.name, width-150, y-10, width=100, height=100, preserveAspectRatio=True, mask='auto')
                    y -= 110
                except Exception as e:
                    c.setFont("Helvetica", 8)
                    c.drawString(width-150, y, "[Photo error]")
                    y -= 10
            c.setFont("Helvetica-Bold", 12)
            c.drawString(30, y, "Employee Details:")
            y -= 18
            c.setFont("Helvetica", 10)
            for key, value in emp.items():
                if key == "photo":
                    continue
                c.drawString(40, y, f"{key}: {value}")
                y -= 13
            y -= 10

            # Department

            cursor.execute("SELECT * FROM department WHERE d_id = %s", (emp['department_id'],))
            dept = cursor.fetchone()
            if dept:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, y, "Department Info:")
                y -= 18
                c.setFont("Helvetica", 10)
                for k, v in dept.items():
                    c.drawString(40, y, f"{k}: {v}")
                    y -= 12
                y -= 10

            # Projects

            if emp['project_id']:
                cursor.execute("SELECT * FROM project WHERE p_id = %s", (emp['project_id'],))
                proj = cursor.fetchone()
                if proj:
                    c.setFont("Helvetica-Bold", 12)
                    c.drawString(30, y, "Project Info:")
                    y -= 18
                    c.setFont("Helvetica", 10)
                    for k, v in proj.items():
                        c.drawString(40, y, f"{k}: {v}")
                        y -= 12
                    y -= 10

            # Dependents

            cursor.execute("SELECT * FROM dependent WHERE essn = %s", (emp['ssn'],))
            dependents = cursor.fetchall()
            if dependents:
                c.setFont("Helvetica-Bold", 12)
                c.drawString(30, y, "Dependents:")
                y -= 18
                c.setFont("Helvetica", 10)
                for dep in dependents:
                    for k, v in dep.items():
                        if k == "photo" and v:
                            try:
                                img_bytes = v
                                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp_img:
                                    tmp_img.write(img_bytes)
                                    tmp_img.flush()
                                    c.drawImage(tmp_img.name, width-200, y-10, width=60, height=60, preserveAspectRatio=True, mask='auto')
                                y -= 65
                            except Exception as e:
                                c.setFont("Helvetica", 8)
                                c.drawString(width-200, y, "[Photo error]")
                                y -= 10
                        elif k != "photo":
                            c.drawString(40, y, f"{k}: {v}")
                            y -= 12
                    y -= 5
            c.save()
        con.close()
        messagebox.showinfo("Export Complete", f"All employee PDFs exported to {folder}")
    except Exception as e:
        messagebox.showerror("Export Error", f"Failed to export PDFs: {e}")

tb.Button(employee_tab, text="Download All Employees as Individual PDFs", command=download_all_employees_as_pdfs, bootstyle='secondary').grid(row=len(employee_fields)+8, column=0, columnspan=3, padx=10, pady=5, sticky='ew')

root.mainloop()
