from windows import wEnterNames, wEnterServices, wEnterClasses
from models import Employees, Base, Services, Classes, Class_join, Users, engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text, select, update, insert, delete
import sqlalchemy.exc

# Session = sessionmaker()
# Session.configure(bind=engine)
# session = Session()


def main():
 
    windowMain = wEnterClasses()
    # wEnterNames()
if __name__ == "__main__":
    main()

