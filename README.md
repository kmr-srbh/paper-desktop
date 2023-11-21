# Paper Desktop
A simple and lightweight attendance management system for schools built as my class 12th project. The name _Paper_ is an irone to what the software helps avoid.

## With Paper Desktop you can:
- Mark attendance the usual way - check or uncheck students to take attendance.
- Keep a track of every student's attendance.
- Monitor class attendance.
- Periodically backup and export attendance records.

## Running the software:
The software currently relies completely on an independent installation of MySQL Server for it's backend functionality. Hence, installation of MySQL Server is a pre-requisite. [Download MySQL Server Community Edition.](https://dev.mysql.com/downloads/installer/)<br><br>

- Make sure that Python is added to path and `pip` is functional. To install the software dependencies open a new Terminal window in the software directory and type `pip install -r requirements.txt`. 
- Open the software folder in a code editor and edit `main.py`. Here, find the `server.connect(host=localhost, username=root, password=password)` function. Change the function parameters to that of your MySQL Server installation.
- Save and execute `main.py` from the software directory.
