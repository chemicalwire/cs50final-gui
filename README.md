# luxelab Class Attendance GUI Edition
## Video Demo:
### Description:
Initially,  I created a simpler version of this as a CLI app for the CS50Py class, however none
of my coworkers were able to successfully navigate a command line so I wanted to do it again, making
it simpler to navigate. Also, several asked me if the command line was "hacking"
I initially designed this as a flask app but I didn't want to have to run a dedicated flask server at work,
also I wanted to learn how to create a GUI.
After several unsuccessul fights with Glade, I spent a few days learning the basics of tkinter and put this 
together. I plan on redoing the app again to teach myself QT, but the learning curve for that is much
steeper, so I figured tkinter was the best way to go for this project.
When opening the app, if the database doesnt exist, the ORM creates the database as a new file, and populates in
some default data for teachers and services.
There are two separate windows for entering students/teachers and services in class, and then a main window
for entering attendance for teachers and students at class (this will actually help us track student 
attendance over time).
The app also lets you generate a pdf file of the selected classes attendance sheet.