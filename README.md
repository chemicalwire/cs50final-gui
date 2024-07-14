# luxelab Class Attendance GUI Edition
## Video Demo: https://youtu.be/Bvq_U1P4eYg
### Description:
Initially,  I created a simpler version of this as a CLI app for the CS50Py class, however none
of my coworkers were able to successfully navigate a command line so I wanted to do it again, making
it simpler to navigate. Also, several asked me if the command line was "hacking".
I then decided designed this as a flask app for this project, I finished it and almost submitted it, but I didn't want
to have to run a dedicated flask server at work and also I wanted to learn how to create a GUI. (And also my html pages
all just look terrible)
After several unsuccessul fights with Glade, I spent a few days learning the basics of tkinter and put this 
together. I plan on redoing the app again to teach myself wxPython and QT, but the learning curve for that is much
steeper, so I figured tkinter was the best way to go for this project.
When opening the app, if the database doesnt exist, the ORM creates the database as a new file, and populates in
some default data for teachers and services.
There are two separate windows for entering students/teachers and services in class, and then a main window
for entering attendance for teachers and students at class (this will actually help us track student 
attendance over time and allow me to do some trend reporting for performance reviews).
I thought about making this just one window with separate tabs for adding classes, employees, and services but it was easier
for me to organize the code in my head by making it separate window classes. I will probably rewrite it with a tabbed 
interface at some point (I'm basically re-doing this app in a few different languages to help learn).
The app also lets you generate a pdf file of the selected classes attendance sheet.
There are two main files, windows.py (which contains all the definitions for the windows and their related functions) and models.py
(which contains all the databse ORM database information and a function to create and prepopulate the
db file if none is detected, I originally crated this for the flask app so I was just able to use the same file).
Then there is project.py which just makes a call to the login window class.