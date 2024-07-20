import tkinter as tk
from tkinter import ttk, messagebox, filedialog
from PIL import Image, ImageTk
from models import Employees, Base, Services, Classes, Class_join, Users, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update, insert, delete
import datetime
import os
from werkzeug.security import check_password_hash, generate_password_hash
from fpdf import FPDF

script_dir = os.path.dirname(os.path.abspath(__file__)) 

class attendancePDF(FPDF):
    def header(self):  
        TODAY = datetime.date.today().strftime("%Y/%m/%d")
        image_name = f"{script_dir}/luxelab.png"
        self.set_font('Times', size=24)
        self.set_text_color(0,0,0)        
        # Calculate the position to center the image
        image_width = 50    # i have no idea why this number works because the image is 200px wide but whatever
        page_width = self.w - 2 * self.l_margin
        x_pos = (page_width - image_width) / 2
        self.image(image_name, x=x_pos) #logo
        self.ln(20) 
        self.cell(text=f"luxelab Attendance {TODAY}",align="C", center=True)        
        self.ln(20) 

class wEnterNames():
    ''' add and edit teachers and students'''
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Enter Employees")
        self.root.geometry("650x600")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW",  self.on_closing )

        self.style = ttk.Style()
        self.style.theme_use('clam') 
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview", font=("Helvetica", 12))
        self.root.tk.call('tk', 'scaling', 1.5)

        # menu bar
        self.menuBar = tk.Menu(self.root)
        self.menuFile = tk.Menu(self.menuBar, tearoff=0)
        self.menuFile.add_command(label="Close window", command=self.on_closing)
        self.menuBar.add_cascade(label="Options", menu=self.menuFile)
        self.root.config(menu=self.menuBar)

        self.label = tk.Label(self.root, text="Employees", font=("Helvetica", 24))
        self.label.pack(padx=20, pady=20)
        
        ### text box and button to add employee
        self.frameAdd = tk.Frame(self.root)
        self.frameAdd.columnconfigure(0, weight=1)
        self.frameAdd.columnconfigure(1, weight=1)
        self.frameAdd.columnconfigure(1, weight=1)
        self.labelAdd = tk.Label(self.frameAdd, text="Add Employee") 
        self.textName = tk.Entry(self.frameAdd)
        self.roleSelected = tk.IntVar()
        self.radioTeacher = ttk.Radiobutton(self.frameAdd, text="Teacher", value=0, variable=self.roleSelected)
        self.radioStudent = ttk.Radiobutton(self.frameAdd, text="Student", value=1, variable=self.roleSelected)
        self.btnAdd = tk.Button(self.frameAdd, text="Add", command=self.add_employee)
        self.labelAdd.grid(row=0, column=0)
        self.textName.grid(row=1, column=0, padx=5)
        self.textName.bind("<KeyPress>", self.shortcut)
        self.radioTeacher.grid(row=0, column=1, padx=5)
        self.radioStudent.grid(row=1, column=1, padx=5)
        self.btnAdd.grid(row=0, column=2, padx=5, rowspan=2, sticky="news")
        self.frameAdd.pack(padx=20, pady=10)
        
        ###### list of teachers and students
        self.frameList = tk.Frame(self.root)
        self.frameList.columnconfigure(0, weight=1)
        self.frameList.columnconfigure(1, weight=1)
        self.treeTeachers = tk.Text(self.frameList)
        self.treeStudents = tk.Text(self.frameList)

        self.treeTeachers2 = ttk.Treeview(self.frameList, show="headings", height=15)
        self.treeTeachers2["columns"] = ("name", "active")
        self.treeTeachers2.heading("name", text="Name", anchor="w")
        self.treeTeachers2.column("name", stretch=tk.YES)
        self.treeTeachers2.heading("active", text="Status", anchor="w")
        self.treeTeachers2.column("active", stretch=tk.YES)
        self.treeTeachers2.bind('<<TreeviewSelect>>', self.toggle_active_teacher)

        self.treeStudents2 = ttk.Treeview(self.frameList, show="headings", height=15)
        self.treeStudents2["columns"] = ("name", "active")
        self.treeStudents2.heading("name", text="Name", anchor="w")
        self.treeStudents2.column("name", stretch=tk.YES)
        self.treeStudents2.heading("active", text="Status", anchor="w")
        self.treeStudents2.column("active", stretch=tk.YES)
        self.treeStudents2.bind('<<TreeviewSelect>>', self.toggle_active_student)
        self.treeTeachers2.grid(row=0, column=0, sticky="news", padx=5)
        self.treeStudents2.grid(row=0, column=1, sticky="news", padx=5)
        self.frameList.pack(padx=20)

        # checkbox to show only active employees
        self.active_status = tk.IntVar()
        self.checkActive = tk.Checkbutton(self.root, text="Show active employees only", variable=self.active_status, onvalue=1, offvalue=0, command=self.toggle_show_active)
        self.active_status.set(1)
        self.checkActive.pack(padx=20, pady=10)

        self.get_employees()
        self.root.mainloop()

    def on_closing(self)->None:
        self.root.destroy()
        wEnterClasses()
        
    def populate_trees(self, stmt)->None:
        with engine.connect() as conn:
            result = conn.execute(stmt)
        employees = result.fetchall()
        
        if employees is None:
            self.root.iconify()
            messagebox.showwarning(message="No employees found")
            self.root.deiconify()
            return
        
        # self.treeStudents.delete(1.0, tk.END)
        # self.treeTeachers.delete(1.0, tk.END)

        for item in self.treeTeachers2.get_children():
            self.treeTeachers2.delete(item)
        for item in self.treeStudents2.get_children():  
            self.treeStudents2.delete(item)

        for row in employees:
            active = "Inactive" if row.active == 0 else "Active"
            empID= row.id
            values = (row.name, active)
            if row.role == 0: 
                self.treeTeachers2.insert(parent="", text=empID, index=tk.END, values=values)
            else:
                self.treeStudents2.insert(parent="", text=empID, index=tk.END, values=values)

    def get_employees(self)->None:
        ''' populate the list of teachers and students'''
        if self.active_status.get() == 0:
            stmt = select(Employees).order_by(Employees.active.desc() , Employees.name)
        else:
            stmt = select(Employees).where(Employees.active == 1).order_by(Employees.name)
        self.populate_trees(stmt) 

    def add_employee(self)->None:

        name = self.textName.get()
        role = self.roleSelected.get()        

        if name is None or name == "":
            return messagebox.showwarning(message="Name cannot be blank")
        
        stmt = text("SELECT * from employees WHERE lower(name) = lower(:name)")
        data = {"name": name}
        with engine.connect() as connection:
            result = connection.execute(stmt, data).fetchone()

        if result is not None:
            return messagebox.showwarning(message=f"{name} already exists")   

        if messagebox.askyesno(message=f"Add {name} as a {'Teacher' if role == 0 else 'Student'}?"):
            stmt = insert(Employees).values(name=name.capitalize(), role=role, active=1)
            with engine.begin() as connection:
                connection.execute(stmt)  

        self.textName.delete(0, tk.END)
        self.get_employees()    

    def toggle_show_active(self)->None:
        ''' show only active employees or all employees'''
        status = self.active_status.get()

        if status == 0:
            stmt = select(Employees).order_by(Employees.active.desc(), Employees.name)       
        else:
            stmt = select(Employees).where(Employees.active == 1).order_by(Employees.name)
        self.get_employees()
    
    def shortcut(self, event)->None:
        ''' enter key press'''
        if event.keysym == "Return":
            self.add_employee()
    
    def toggle_active_teacher(self, _)->None:
        for i in self.treeTeachers2.selection():
        
            if self.treeTeachers2.item(i)["values"][1] == "Active":
                stmt = update(Employees).where(Employees.id == self.treeTeachers2.item(i)["text"]).values(active=0) 
                if messagebox.askyesno(message="Are you sure you want to make this employee inactive?", parent=self.root):
                    with engine.begin() as connection:
                        connection.execute(stmt)
            else:
                stmt = update(Employees).where(Employees.id == self.treeTeachers2.item(i)["text"]).values(active=1)
                if messagebox.askyesno(message="Are you sure you want to make this employee active?", parent=self.root):
                    with engine.begin() as connection:
                        connection.execute(stmt)
        stmt = select(Employees).order_by(Employees.active.desc() , Employees.name)
        self.get_employees()

    def toggle_active_student(self, _)->None:
        for i in self.treeStudents2.selection():        
            if self.treeStudents2.item(i)["values"][1] == "Active":
                stmt = update(Employees).where(Employees.id == self.treeStudents2.item(i)["text"]).values(active=0) 
                if messagebox.askyesno(message="Are you sure you want to make this employee inactive?", parent=self.root):
                    with engine.begin() as connection:
                        connection.execute(stmt)
            else:
                stmt = update(Employees).where(Employees.id == self.treeStudents2.item(i)["text"]).values(active=1)
                if messagebox.askyesno(message="Are you sure you want to make this employee active?", parent=self.root):
                    with engine.begin() as connection:
                        connection.execute(stmt)
        stmt = select(Employees).order_by(Employees.active.desc() , Employees.name)
        self.get_employees()

class wEnterServices():
    ''' view and add servcices window'''
    def __init__(self):        
        self.root = tk.Tk()
        self.root.title("Enter Services")
        self.root.geometry("550x600")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW",  self.on_closing )

        self.style = ttk.Style()
        self.style.theme_use('clam') 
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview", font=("Helvetica", 12))
        self.root.tk.call('tk', 'scaling', 1.5)
        # menu bar
        self.menuBar = tk.Menu(self.root)
        self.menuFile = tk.Menu(self.menuBar, tearoff=0)
        self.menuFile.add_command(label="Close window", command=self.on_closing)       
        self.menuBar.add_cascade(label="Options", menu=self.menuFile)
        self.root.config(menu=self.menuBar)

        self.label = tk.Label(self.root, text="Services", font=("Helvetica", 24))
        self.label.pack(padx=20, pady=20)
        self.frmLogin= tk.Frame(self=root)
        
        ### text box and button to addd employee
        self.frameAdd = tk.Frame(self.root)
        self.frameAdd.columnconfigure(0, weight=1)
        self.frameAdd.columnconfigure(1, weight=1)
        self.labelAdd = tk.Label(self.frameAdd, text="Add Service") 
        self.textName = tk.Entry(self.frameAdd)
        self.roleSelected = tk.IntVar()
        self.radioTeacher = ttk.Radiobutton(self.frameAdd, text="Role", value=0, variable=self.roleSelected)
        self.radioStudent = ttk.Radiobutton(self.frameAdd, text="Model", value=1, variable=self.roleSelected)
        self.btnAdd = tk.Button(self.frameAdd, text="Add", command=self.add_service)
        self.labelAdd.grid(row=0, column=0)
        self.textName.grid(row=1, column=0, padx=5)
        self.textName.bind("<KeyPress>", self.shortcut)
        self.style.configure("TRadiobutton", font=("Helvetica", 12))
        self.radioTeacher.grid(row=0, column=1, padx=5, sticky="w")
        self.radioStudent.grid(row=1, column=1, padx=5, sticky="w")
        self.btnAdd.grid(row=0, column=2, padx=5, rowspan=2, sticky="news")
        self.frameAdd.pack(padx=20, pady=10, fill="both")
        
        ###### list of teachers and students
        self.frameList = tk.Frame(self.root)
        self.frameList.columnconfigure(0, weight=1)
        self.frameList.columnconfigure(1, weight=1)
        self.treeTeachers = tk.Text(self.frameList)
        self.treeStudents = tk.Text(self.frameList)
        self.treeTeachers = ttk.Treeview(self.frameList, show="headings", height=15)
        self.treeTeachers["columns"] = ("name")
        self.treeTeachers.heading("name", text="Name", anchor="w")
        self.treeTeachers.column("name", stretch=tk.YES)        
        self.treeStudents = ttk.Treeview(self.frameList, show="headings", height=15)
        self.treeStudents["columns"] = ("name")
        self.treeStudents.heading("name", text="Name", anchor="w")
        self.treeStudents.column("name", stretch=tk.YES)
        self.treeTeachers.grid(row=0, column=0, sticky="news", padx=5)
        self.treeStudents.grid(row=0, column=1, sticky="news", padx=5)
        self.frameList.pack(padx=20, fill="both")
        self.populate_trees()
        self.root.mainloop()

    def on_closing(self)->None:
        self.root.destroy()
        wEnterClasses()
        
    def populate_trees(self)->None:

        ''' populate the lists of services'''
        #########################
        # code to deal with exmpty database
        #########################
        stmt = select(Services)
        with engine.connect() as conn:
            result = conn.execute(stmt)
        services = result.fetchall()
        if services is None:
            return 
        
        stmt = select(Services).order_by(Services.service_type, Services.service)
        with engine.connect() as conn:
            result = conn.execute(stmt)
            employees = result.fetchall()

        for item in self.treeTeachers.get_children():
            self.treeTeachers.delete(item)
        for item in self.treeStudents.get_children():  
            self.treeStudents.delete(item)

        for row in employees:          
            empID= row.id
            values = (f'{row.service}',)
            if row.service_type == 0: 
                self.treeTeachers.insert(parent="", text=empID, index=tk.END, values=values)
            else:
                self.treeStudents.insert(parent="", text=empID, index=tk.END, values=values)

    def add_service(self)->None:
        name = self.textName.get()
        role = self.roleSelected.get()

        if name is None or name == "":
            return messagebox.showwarning(message="Name cannot be blank")
        stmt = text("SELECT * from services WHERE lower(service) = lower(:service)")
        data = {"service": name}
 
        with engine.connect() as connection:
            result = connection.execute(stmt, data).fetchone()

        if result is not None:
            return messagebox.showwarning(message="Service already exists")   
        
        if messagebox.askyesno(message=f"Add {name} as a {'Subject' if self.roleSelected.get() == 0 else 'Model'}?"):
            stmt = insert(Services).values(service=name.capitalize(), service_type=role)
            with engine.begin() as connection:
                connection.execute(stmt)  

        self.textName.delete(0, tk.END)
        self.populate_trees()    

    def shortcut(self, event)->None:
        ''' add employee on enter key press'''
        if event.keysym == "Return":
            self.add_service()

class wEnterClasses():
    def __init__(self) -> None:        
        self.root = tk.Tk()
        self.root.title("Enter Classes")
        self.root.geometry("1000x900")
        # self.root.eval('tk::PlaceWindow . center')  # this will not work for some reason
        self.root.resizable(False, False)

        self.classID = tk.StringVar()
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview", font=("Helvetica", 12))
        self.root.tk.call('tk', 'scaling', 1.5)        ############
        # menu bar
        self.menuBar = tk.Menu(self.root)
        self.menuFile = tk.Menu(self.menuBar, tearoff=0)
        self.menuFile.add_command(label="New Class", command=self.new_class)
        self.menuFile.add_command(label="Enter Employees", command=self.enter_employees_window)
        self.menuFile.add_command(label="Enter Services", command=self.enter_services_window)
        self.menuFile.add_separator()
        self.menuFile.add_command(label="Create PDF", command=self.createPDF)
        self.menuFile.add_separator()
        self.menuFile.add_command(label="Close window", command=self.root.destroy)
        self.menuBar.add_cascade(label="Options", menu=self.menuFile)
        self.root.config(menu=self.menuBar)

        # date selector frame
        self.frameDate =  tk.Frame(self.root)
        self.frameDate.columnconfigure(0, weight=1)
        self.frameDate.columnconfigure(1, weight=1)
        self.frameDate.columnconfigure(2, weight=1)
        self.frameDate.columnconfigure(3, weight=1)
        self.labelMain = tk.Label(self.frameDate, text="Enter Classes", font=("Helvetica", 24))
        self.labelMain.grid(row=0, column=0, padx=5, sticky="w")
        self.labelDate = tk.Label(self.frameDate, text="Select Class Date")
        self.classDate = tk.StringVar()
        self.selectClass = ttk.Combobox(self.frameDate, values=["Select Class"], text="Select Class Date", textvariable=self.classDate, state="disabled")
        self.selectClass.bind("<<ComboboxSelected>>", lambda event: self.load_class(self.classDate.get()))
        self.labelDate.grid(row=0, column=1)
        self.selectClass.grid(row=0, column=2)
        self.frameDate.pack(padx=20, pady=15)

        ##navigation frame
        self.frameNav = tk.Frame(self.root)
        self.frameNav.columnconfigure(0, weight=1)
        self.frameNav.columnconfigure(1, weight=1)
        self.btnLeft = tk.Button(self.frameNav, text="<", command=self.previous_class, state="disabled")
        self.btnRight = tk.Button(self.frameNav, text=">", command=self.next_class, state="disabled")
        self.btnLeft.grid(row=0, column=0)
        self.btnRight.grid(row=0, column=1)
        self.frameNav.pack(padx=20, pady=10)

        ### text box and button to add employee
        self.roleSelected = tk.IntVar()
        self.frameAdd = tk.Frame(self.root)
        self.frameAdd.columnconfigure(0, weight=1)
        self.frameAdd.columnconfigure(1, weight=1)
        self.frameAdd.columnconfigure(1, weight=1)
        self.labelAdd = tk.Label(self.frameAdd, text="Add Employee") 
        self.selectName = ttk.Combobox(self.frameAdd, values=["Select Employee"], state="disabled", text="Select Employee")
        self.selectService = ttk.Combobox(self.frameAdd, values=["Select Service"], state="disabled", text="Select Service")    
        self.radioTeacher = ttk.Radiobutton(self.frameAdd, text="Teacher", value=0, variable=self.roleSelected, command=self.populate_employees)
        self.radioStudent = ttk.Radiobutton(self.frameAdd, text="Student", value=1, variable=self.roleSelected, command=self.populate_employees)
        self.radioStudent["state"] = 'disabled'
        self.radioTeacher["state"] = 'disabled'
        self.btnAdd = tk.Button(self.frameAdd, text="Add", command=self.add_entry)
        self.labelAdd.grid(row=0, column=1)
        self.roleSelected.set(-1)
        self.selectName.grid(row=1, column=1, padx=5)
        self.radioTeacher.grid(row=0, column=0, padx=5)
        self.radioStudent.grid(row=1, column=0, padx=5)
        self.btnAdd.grid(row=0, column=3, padx=5, rowspan=2, sticky="news")
        self.selectService.grid(row=1, column=2, padx=5)
        self.frameAdd.pack(padx=20, pady=10)
        self.btnAdd["state"] = 'disabled'
        self.frameClass = tk.Frame(self.root)
        self.frameClass.columnconfigure(0, weight=1)
        self.frameClass.columnconfigure(1, weight=1)

        self.treeTeachers = ttk.Treeview(self.frameClass, show="headings", height=15)
        self.treeTeachers["columns"] = ("name", "service")
        self.treeTeachers.heading("name", text="Name", anchor="w")
        self.treeTeachers.column("name", stretch=tk.YES)
        self.treeTeachers.heading("service", text="Service", anchor="w")
        self.treeTeachers.column("service", stretch=tk.YES)
        self.treeTeachers.bind('<Delete>', self.delete_entry_teacher)
        self.treeStudents = ttk.Treeview(self.frameClass, show="headings", height=15)
        self.treeStudents["columns"] = ("name", "service")
        self.treeStudents.heading("name", text="Name", anchor="w")
        self.treeStudents.column("name", stretch=tk.YES)
        self.treeStudents.heading("service", text="Service", anchor="w")
        self.treeStudents.bind('<Delete>', self.delete_entry_student)
        self.treeStudents.column("service", stretch=tk.YES)
        self.treeTeachers.grid(row=1, column=0, sticky="news", padx=5)
        self.treeStudents.grid(row=1, column=1, sticky="news")        
        self.frameClass.pack(padx=20, pady=20, fill="both", expand=True)
        self.frameClassDetails = tk.Frame(self.root)
        self.frameClassDetails.columnconfigure(0, weight=1)
        self.frameClassDetails.columnconfigure(1, weight=1)
        self.labelTheory = tk.Label(self.frameClassDetails, text="Theory Topic")
        self.labelNotes = tk.Label(self.frameClassDetails, text="Notes")
        self.txtTheory = tk.Entry(self.frameClassDetails, width=50)
        self.txtNotes = tk.Text(self.frameClassDetails, height=10, width=50)
        self.btnUpdate = tk.Button(self.frameClassDetails, text="Update", command=self.update_class)
        self.btnUpdate["state"] = 'disabled'
        self.labelTheory.grid(row=0, column=0)
        self.labelNotes.grid(row=0, column=1)
        self.txtTheory.grid(row=1, column=0, sticky="n", padx=5)
        self.txtNotes.grid(row=1, column=1, sticky="news", padx=5, rowspan=2)
        self.btnUpdate.grid(row=2, column=0, pady=5)
        self.frameClassDetails.pack(padx=20, pady=20)
        
        
        self.populate_dates()
        self.root.mainloop()

    def createPDF(self)->None:
        if self.classDate.get().strip() is None or self.classDate.get().strip() == "":
            return messagebox.showwarning(message="There is no active class loaded")

        # i tried to use the filedialog but it even shows hidden directories
        # and i did not want to show that to the user
        # response = filedialog.askdirectory()
        
        PDFFILENAME = f"{script_dir}/attendance.pdf"
        
        stmt = text("SELECT classes.class_date, employees.name AS employee_name, " \
        "services.service AS service_name, employees.role as employee_role , classes.theory_topic AS theory_topic, "\
        "classes.notes AS notes FROM class_join " \
        "JOIN classes ON classes.id = class_join.class_id " \
        "JOIN employees ON employees.id = class_join.employee_id " \
        "JOIN services ON services.id = class_join.service_id " \
        "WHERE classes.class_date = :date " \
        "ORDER BY employees.role, employees.name")
        cDate = {"date": datetime.datetime.strptime(self.classDate.get(), "%Y/%m/%d").date()}      
        with engine.connect() as connection:
            class_attendance = connection.execute(stmt, cDate)

        if not class_attendance:
            return messagebox.showwarning(message="No data to print")
        attendance_list = ""
        for employee in class_attendance:
            
            attendance_list += f"{employee[1]} - {employee[2]}\n"

        attendance_list += f"\nTheory Topic: {self.txtTheory.get()}\n\n" 
        attendance_list += f"Notes: {self.txtNotes.get(1.0, tk.END)}"

        try:
            pdf = attendancePDF(orientation="portrait", format="A4")
            pdf.add_page()
            pdf.set_font('Times', "B", size=18)
            pdf.set_text_color(0,0,0)
            pdf.multi_cell(0,10,text=attendance_list)
            pdf.output(PDFFILENAME)
            return messagebox.showinfo(message=f"PDF created at {PDFFILENAME}")
        except ValueError:
            return messagebox.showerror("ERROR", "OMG KERNEL PANIC! Just kidding. There was a problem creating the PDF.")

    def previous_class(self)->None:
        selection = self.selectClass.current()
        last = len(self.selectClass["values"]) - 1
        try:
            self.selectClass.current(selection - 1)
        except tk.TclError:
            self.selectClass.current(last)
        self.load_class(self.classDate.get())

    def next_class(self)->None:
        selection = self.selectClass.current()
        try:
            self.selectClass.current(selection + 1)
        except tk.TclError:
            self.selectClass.current(0)
        self.load_class(self.classDate.get())
        
    def delete_entry_student(self, _)->None:
        ''' delete the selected student entry from the class'''
        for i in self.treeStudents.selection():
            joinID = self.treeStudents.item(i)["text"]
            stmt = delete(Class_join).where(Class_join.id == joinID)
            if messagebox.askyesno(message="Are you sure you want to delete this entry?"):
                with engine.begin() as connection:
                    connection.execute(stmt)
            self.load_class(self.classDate.get())  

    def delete_entry_teacher(self, _)->None:      
        ''' delete the selected teacher entry from the class'''
        for i in self.treeTeachers.selection():
            joinID = self.treeTeachers.item(i)["text"]
            stmt = delete(Class_join).where(Class_join.id == joinID)
            name = self.treeTeachers.item(i)["values"][0]
            if messagebox.askyesno(message=f"Are you sure you want to delete {name} from this class?"):
                with engine.begin() as connection:
                    connection.execute(stmt)
        
        self.load_class(self.classDate.get())

    def new_class(self)->None:
        today = datetime.date.today()

        stmt = select(Classes.class_date).where(Classes.class_date == today)
        with engine.connect() as conn:
            result = conn.execute(stmt).fetchone()  
        
        if result is not None:
            return messagebox.showwarning(message="Class already exists for today.")
        else:
            stmt = insert(Classes).values(class_date=today)
            with engine.begin() as conn:
                result = conn.execute(stmt)
                self.classID = str(result.inserted_primary_key[0])
        
        updated_dates = list(self.selectClass['values'])
        updated_dates.append(today.strftime("%Y/%m/%d"))
        self.selectClass['values'] = updated_dates
        self.selectClass.set(today.strftime("%Y/%m/%d"))    

        self.load_class(today.strftime("%Y/%m/%d"))

    def populate_dates(self)->None:

        ##########################
        # deal with empty database
        ##########################

        checkClass = text("SELECT True from classes")
        with engine.connect() as conn:
            result = conn.execute(checkClass).fetchone()
        if result is None:
            # self.root.iconify()
            # messagebox.showinfo(message="There are currenly no classes in the database.")
            # self.root.deiconify()
            return

        stmt = select(Classes.class_date, Classes.id).order_by(Classes.class_date)
        with engine.connect() as conn:
            dates = []
            with conn.execute(stmt) as result:
                for row in result:
                    date = row[0].strftime("%Y/%m/%d")            
                    dates.append(date)                        
            self.selectClass["values"] = dates

        if self.classDate.get() == "":
            #get latest class date
            stmt=select(Classes.class_date).order_by(Classes.class_date.desc()).limit(1)
            with engine.connect() as conn:
                strDate = conn.execute(stmt).fetchone()[0].strftime("%Y/%m/%d")
                self.classDate.set(strDate)
            self.load_class(strDate)

            self.btnAdd["state"] = 'normal'
            self.btnUpdate["state"] = 'normal'
            self.selectClass["state"] = "readonly"
            self.btnLeft["state"] = 'normal'
            self.btnRight["state"] = 'normal'
            self.radioStudent["state"] = 'normal'
            self.radioTeacher["state"] = 'normal'

    def load_class(self, class_date)->None:
        ''' load the class data for the selected date'''
        try:  #probably unnecessary but just in case
            stmt=select(Classes.id).where(Classes.class_date == datetime.datetime.strptime(class_date, "%Y/%m/%d").date())
        except ValueError: # this shouldn't happen unless something is really wrong
            self.root.iconify()
            messagebox.showwarning(message="Date conversion or database error.")
            self.root.deiconify()
            return
        with engine.connect() as conn:
            classID = conn.execute(stmt).fetchone()[0]
            self.classID = classID

        # get class data for specified class - I tried to write this using ORM and it was just ridiculous
        stmt = text("SELECT class_join.id AS class_join_id, classes.id as classID, " \
        "classes.class_date, employees.id, employees.name AS employee_name, " \
        "services.service AS service_name, services.service_type as servicetpye, classes.theory_topic AS theory_topic, "\
        "classes.notes AS notes FROM class_join " \
        "JOIN classes ON classes.id = class_join.class_id " \
        "JOIN employees ON employees.id = class_join.employee_id " \
        "JOIN services ON services.id = class_join.service_id " \
        "WHERE classes.class_date = :date " \
        "ORDER BY employees.role, employees.name")
        cDate = {"date": datetime.datetime.strptime(class_date, "%Y/%m/%d").date()}      
        with engine.connect() as connection:
            classes = connection.execute(stmt, cDate).fetchall()

        # Clear existing data
        for item in self.treeTeachers.get_children():
            self.treeTeachers.delete(item)
        for item in self.treeStudents.get_children():  
            self.treeStudents.delete(item)
        self.txtTheory.delete(0, tk.END)
        self.txtNotes.delete(1.0, tk.END)

        for row in classes:
            if row.servicetpye == 0:
                self.treeTeachers.insert(parent="", index=tk.END, text=row.class_join_id, values=(row.employee_name, row.service_name))
            else:
                self.treeStudents.insert(parent="", index=tk.END, text=row.class_join_id, values=(row.employee_name, row.service_name))
            self.txtTheory.delete(0, tk.END)
            if row.theory_topic is not None:
                self.txtTheory.insert(0, row.theory_topic)
            self.txtNotes.delete(1.0, tk.END)
            if row.notes is not None:
                self.txtNotes.insert(tk.END, row.notes)
            # self.classID = row.classID
            self.btnUpdate["state"] = 'normal'

    def populate_employees(self)-> None:
        ''' populate the list of teachers and students, along with related services'''       
 
        role = self.roleSelected.get()
        if role == 0:
            stmt1 = select(Employees.name, Employees.id).where(Employees.role == 0, Employees.active == 1)
            stmt2 = select(Services.service, Services.id).where(Services.service_type == 0)
        else:
            stmt1 = select(Employees).where(Employees.role == 1, Employees.active == 1)
            stmt2 = select(Services.service, Services.id).where(Services.service_type == 1)
        with engine.connect() as conn:
            employees = conn.execute(stmt1).fetchall()
            services = conn.execute(stmt2).fetchall()

        if not employees or not services:
            self.selectName["state"] = "disabled"
            self.selectService["state"] = "disabled"
            self.btnAdd["state"] = 'disabled'
            return messagebox.showwarning(message="No employees or services found")
        
        self.selectName["state"] = "readonly"
        self.selectService["state"] = "readonly"
        self.btnAdd["state"] = 'normal'
        self.btnLeft["state"] = 'normal'
        self.btnRight["state"] = 'normal'
        self.selectName["values"] = [employee.name for employee in employees]
        # self.selectName["textvariable"] = [employee.id for employee in employees] # for some reason this only populates every other value
        self.selectService["values"] = [service.service for service in services]
        # self.selectService["textvariable"] = [service.id for service in services]

    def update_class(self)->None:
        ''' update the class data'''
        theory = self.txtTheory.get()

        notes = self.txtNotes.get(1.0, tk.END)
        try:
            cDate = datetime.datetime.strptime(self.classDate.get(), "%Y/%m/%d").date()
        except ValueError: # date field is not a date therefore no class is loaded
            return
        stmt = update(Classes).where(Classes.class_date == cDate).values(theory_topic=theory.strip(), notes=notes.strip()) 
        with engine.begin() as connection:
            connection.execute(stmt)
         
    def add_entry(self)->None:
        name = self.selectName.get()
        service = self.selectService.get()
        role = self.roleSelected.get()
        #validate data
        if name == "" or service == "":
            return messagebox.showwarning(message="Please select a name and service")

        stmt = select(Employees.id).where(Employees.name == name)
        with engine.connect() as conn:
            employeeID = conn.execute(stmt).fetchone()[0]
        stmt = select(Services.id).where(Services.service == service) 
        with engine.connect() as conn:
            serviceID = conn.execute(stmt).fetchone()[0]

        stmt = insert(Class_join).values(class_id=self.classID, employee_id=employeeID, service_id=serviceID)
        with engine.begin() as conn:
            conn.execute(stmt)
        self.load_class(self.classDate.get())
        self.selectName.set("")  
        self.selectService.set("")

    def enter_employees_window(self)->None:
        self.root.destroy()
        wEnterNames()
        # self.root.deiconify()
        # print("done")

    def enter_services_window(self)->None:
        self.root.destroy()
        wEnterServices()


    def shortcut(self, event)->None:
        ''' add employee on enter key press'''
        if event.keysym == "Return":
            self.add_employee()
            
class wLogin():

        
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Login")
        self.root.geometry("500x600")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW",  self.on_closing )
        self.classID = tk.StringVar()
        self.style = ttk.Style()
        self.style.theme_use('clam') 
        self.style.configure("Treeview", rowheight=25)
        self.style.configure("Treeview", font=("Helvetica", 12))
        self.root.tk.call('tk', 'scaling', 1.5)

        self.logo_image = Image.open(f"{script_dir}/logo_clear.png")
        self.test = ImageTk.PhotoImage(self.logo_image)
        self.labelImage = tk.Label(self.root, image=self.test)
        self.labelImage.pack(padx=20, pady=20)

        # self.imgLogo.
        self.label = tk.Label(self.root, text="Enter username and password", font=("Helvetica", 24), wraplength=400) 
        self.entryUsername = tk.Entry(self.root)    
        self.entryPassword = tk.Entry(self.root, show="*")  
        self.entryPassword.bind("<KeyPress>", self.checkKeypress)
        self.btnFrame = tk.Frame(self.root)
        self.btnLogin = tk.Button(self.btnFrame, text="Login", command=self.login)
        self.btnRegister = tk.Button(self.btnFrame, text="Register", command=self.register_user)
        self.btnLogin.grid(row=0, column=0, padx=5)
        self.btnRegister.grid(row=0, column=1, padx=5)        
        self.label.pack(padx=20, pady=20)
        self.entryUsername.pack(padx=20, pady=10)
        self.entryPassword.pack(padx=20, pady=10)
        self.btnFrame.pack(padx=20, pady=20)
      
        self.root.mainloop()

    def on_closing(self)->None:
        self.root.destroy()


    def checkKeypress(self, event)->None:
        ''' login with enter key '''
        if event.keysym == "Return":
            self.login()


    def login(self)->None:

        if self.entryUsername.get() == "" or self.entryPassword.get() == "":
            return messagebox.showwarning(message="Username and password cannot be blank")
        
        stmt = select(Users).where(Users.username == self.entryUsername.get())
        with engine.connect() as conn:
            result = conn.execute(stmt).fetchone()
        if result is None: 
            return messagebox.showwarning(message="User not found")
        
        if check_password_hash(result.password_hash, self.entryPassword.get()):
            self.root.destroy()
            wEnterClasses()
        else:
            return messagebox.showwarning(message="Incorrect password")


    def register_user(self)->None:
        self.root.destroy()
        wRegister()

class wRegister():
    def __init__(self) -> None:
        self.root = tk.Tk()
        self.root.title("Register")
        self.root.geometry("500x400")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW",  self.on_closing )

        self.frmLogin = tk.Frame(self.root)
        self.style = ttk.Style()
        self.label = tk.Label(self.root, text="Choose a username and password", font=("Helvetica", 24), wraplength=400) 
        self.frmRegister = tk.Frame(self.root)
        self.lblUsername = tk.Label(self.frmRegister, text="Username: ")
        self.entryUsername = tk.Entry(self.frmRegister)     
        self.lblPassword = tk.Label(self.frmRegister, text="Password: ")
        self.entryPassword = tk.Entry(self.frmRegister, show="*")  
        self.lblConfirm = tk.Label(self.frmRegister, text="Confirm: ")
        self.txtConfirm = tk.Entry(self.frmRegister, show="*")
        self.lblKey = tk.Label(self.frmRegister, text="Secret Key: ")
        self.entryKey = tk.Entry(self.frmRegister, show="*")
        self.entryKey.bind("<KeyPress>", self.checkKeypress)

        self.btnFrame = tk.Frame(self.root)
        self.btnLogin = tk.Button(self.btnFrame, text="Register", command=self.create_login)
        self.btnRegister = tk.Button(self.btnFrame, text="Cancel", command=self.cancel)
        self.btnLogin.grid(row=0, column=0, padx=5)
        self.btnRegister.grid(row=0, column=1, padx=5)
        self.label.pack(padx=20, pady=20)
        self.lblUsername.grid(row=0, column=0, sticky="e")
        self.entryUsername.grid(row=0, column=1)
        self.lblPassword.grid(row=1, column=0, sticky="e")
        self.entryPassword.grid(row=1, column=1)
        self.lblConfirm.grid(row=2, column=0, sticky="e")
        self.txtConfirm.grid(row=2, column=1)
        self.lblKey.grid(row=3, column=0, sticky="e")
        self.entryKey.grid(row=3, column=1)
        self.frmRegister.pack(padx=20, pady=20)
        self.btnFrame.pack(padx=20, pady=20)      
        self.root.mainloop()

    def on_closing(self)->None:
        self.root.destroy()
        wLogin()

    def cancel(self)->None:
        self.root.destroy()
        wLogin()

    def checkKeypress(self, event)->None:
        ''' login with enter key '''
        if event.keysym == "Return":
            self.create_login()

    def create_login(self)->None:

        if self.entryKey.get() != "1408":
            self.root.iconify()
            messagebox.showwarning(message="Invalid key. Cannot create account.")
            self.root.deiconify()  
            return
        
        if self.entryUsername.get() == "" or self.entryPassword.get() == "" or self.txtConfirm.get() == "":
            self.root.iconify()
            messagebox.showwarning(message="Username and password cannot be blank")
            self.root.deiconify()
            return

        if not (self.entryPassword.get() == self.txtConfirm.get()):
            self.root.iconify()
            messagebox.showwarning(message="Passwords do not match")
            self.root.deiconify()
            return
        # checks the database to see if the username already exists
        stmt = select(Users).where(Users.username == self.entryUsername.get())
        with engine.connect() as conn:
            result = conn.execute(stmt).fetchone()
        if result is not None:
            return messagebox.showwarning(message="Username already exists")
        
        stmt = insert(Users).values(username=self.entryUsername.get(), password_hash=generate_password_hash(self.entryPassword.get()))
        with engine.begin() as conn:
            conn.execute(stmt)
        messagebox.showinfo(message="Account created successfully. Logging you in automatically")
        self.root.destroy()
        wEnterClasses()


def main():
    wEnterClasses()
    # wLogin()
    # wEnterNames()     
    # wEnterServices()
if __name__ == "__main__":
    main()
