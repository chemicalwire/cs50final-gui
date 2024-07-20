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
The user is greeted with a login window (and the option to register a new account if they know the passcode).
The user is then taken to a main window where they can enter a new class or scroll through previous classes in the
database. There are also two separate windows for entering students/teachers and services in class.
I thought about making this just one window with separate tabs for adding classes, employees, and services but it was easier
for me to organize the code in my head by making it separate window classes. I will probably rewrite it with a tabbed 
interface at some point (I'm basically re-doing this app in a few different ways and languages to help learn).
The app also lets you generate a pdf file of the selected classes attendance sheet.
There are two main files, windows.py (which contains all the definitions for the windows and their related functions) and models.py
(which contains all the databse ORM database information and a function to create and prepopulate the
db file if none is detected, I originally crated this for the flask app so I was just able to use the same file).
Then there is project.py which just makes a call to the login window class.
I used primarily youtube tutorials to teach myself tkinter but when I had questions and got sick of reading through
technical docs, I would get answers to questions from GPT (which I then had to usually verify by reading the tech docs 
I was trying to avoid)