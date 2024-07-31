from sqlalchemy.orm import sessionmaker, DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import create_engine, ForeignKey, String, text, Integer, Column, func, insert
from datetime import date
from typing import Optional
import os

script_dir = os.path.dirname(os.path.abspath(__file__))

class Base(MappedAsDataclass, DeclarativeBase):
    pass

class Employees(Base):
    __tablename__ = "employees"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    name: Mapped[str]
    role: Mapped[int] 
    active: Mapped[int]
    class_joins = relationship("Class_join", back_populates="employees")

    def __repr__(self):
        return f"{{'id': {self.id}, 'name': {self.name}, 'role': {self.role}, 'active': {self.active}}}"

class Services(Base):
    __tablename__ = "services"
    id: Mapped[int] = mapped_column(primary_key=True,init=False)
    service: Mapped[str]
    service_type: Mapped[int]
    class_joins = relationship("Class_join", back_populates="services")

    def __repr__(self):
        return f"{{'id': {self.id}, 'service': {self.service}, 'service_type': {self.service_type}}}"

class Classes(Base):
    __tablename__ = "classes"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    class_date: Mapped[date]
    theory_topic: Mapped[Optional[str]]
    notes: Mapped[Optional[str]]
    class_joins = relationship("Class_join", back_populates="classes")

    def __repr__(self):
        return f"{{'id': {self.id}, 'class_date': {self.class_date}, 'theory_topic': {self.theory_topic}, 'notes': {self.notes}}}"


class Class_join(Base):
    __tablename__ = "class_join"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)
    class_id: Mapped[int] = mapped_column(ForeignKey("classes.id"))
    employee_id: Mapped[int] = mapped_column(ForeignKey("employees.id")) 
    service_id: Mapped[int] = mapped_column(ForeignKey("services.id"))
    classes: Mapped[list["Classes"]]= relationship("Classes", back_populates="class_joins")
    employees: Mapped[list["Employees"]] = relationship("Employees", back_populates="class_joins")
    services: Mapped[list["Services"]] = relationship("Services", back_populates="class_joins")

    def __repr__(self):
        return f"{{'id': {self.id}, 'class_id': {self.class_id}, 'employee_id': {self.employee_id}, 'service_id': {self.service_id}}}"

class Users(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(primary_key=True, init=False)   
    username: Mapped[str]
    password_hash: Mapped[str]


PROJECT_DIRECTORY = os.getenv("ATTENDANCE_PROJECT_DIRECTORY")
engine = create_engine(f"sqlite:///{script_dir}/attendance.db")
Base.metadata.create_all(bind=engine)

# If tables are empty, fill in default services and teachers
checkServices = text("SELECT True from services")
checkEmployees = text("SELECT True from employees")

with engine.begin() as connection:
    result = connection.execute(checkServices).fetchone()
if result is None:    
    stmt1 = text("""
        INSERT INTO services (service, service_type) VALUES 
        ('Theory', 0), 
        ('Haircutting', 0), 
        ('Color', 0), 
        ('Haircutting Shadow', 0), 
        ('Color Shadow', 0), 
        ('Styling', 0), 
        ('Blowdry/Up-do', 1), 
        ('Cut and Style', 1), 
        ('Barbering', 1), 
        ('Single Process', 1), 
        ('Highlights', 1), 
        ('Balayage', 1), 
        ('Mannequin', 1), 
        ('Absent', 1), 
        ('Excused', 1), 
        ('Creative Color', 1),
        ('Dollhead - Cut', 1),
        ('Dollhead - Color', 1)
    """)

    with engine.begin() as connection:
        connection.execute(stmt1)

checkEmployees = text("SELECT True from employees")
with engine.begin() as connection:
    result = connection.execute(checkEmployees).fetchone()
if result is None:    
    stmt2 = text("""
        INSERT INTO employees (name, role, active) VALUES
        ('Billy', 0, 1),
        ('Anna', 0, 1),
        ('Michael', 0, 1),
        ('Julie', 0, 1),
        ('Aimee', 0, 1),
        ('Cheryl', 0, 1),
        ('Kelsie', 0, 1),
        ('Craig', 0, 1)
    """)  
    with engine.begin() as connection:
        connection.execute(stmt2)