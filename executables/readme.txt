#======================================================================================================#


                                      LAN-NOTIFICATIONS/LAN-VIEWER


#======================================================================================================#

                                      *** INSTALLATION PROCESS ***

#======================================================================================================#

*Put NOTISRV foldier in your server machine (in the local disk).
	[Optional]
	Create/Open client_list.txt and write the PORT you want to use in the first line.
	Use different PORT than LANVIEW (default PORT 5050).
	Write the ip's and computer names of your network machines like below.

	5050
	192.168.168.34;ADMIN
	192.168.168.67;PC1
	.
	.
	.

*Run NOTISRV.exe.

#======================================================================================================#

*Put LANVIEW foldier in your server machine (in the local disk).
*Populate rooms foldier with JPEG Images of your offices.

	[Optional]
	Create/Open client_list.txt and write the PORT you want to use in the first line.
	Use different PORT than NOTISRV (default PORT 5055).

*Run LANVIEW.exe.
*Choose your room and populate it with your network machines (double right click).

#======================================================================================================#

*Create/Open constants.txt and write the info of every server machine (server executable) like below.

HOST = 192.168.168.34
PORT = 5050
NAME = srvname
MODE = 1
HOST = 192.168.168.34
PORT = 5055
NAME = srvname
MODE = 2
HOST = 192.168.168.36
PORT = 5060
NAME = othername
MODE = 2

[In the above example client listens to 3 different server executables from 2 different machines.
HOST is the server's ip. PORT is the port that the connection-communication will take place. MODE 
can only take values 1 or 2 and it concerns the way the notification will be shown in the client
machine. If MODE = 1(recommended), notification will be shown as tkinter GUI window. If MODE = 2,
notification will be shown as windows push-notification.]

*Put NOTICL foldier in every client machine in your lan network (in the local disk).
*Create an NOTICL.exe shortcut and paste it in windows Startup foldier.
*Double click to execute NOTICL.exe. If an error regarding multiprocessing occurs,
	install Windows6.1-KB3126587-x64 Microsoft Update and restart the machine.

[NOTICL.exe will automatically start with every computer startup.]

#======================================================================================================#

                                *** PROBLEMS AND CODE IMPROVEMENTS ***

#======================================================================================================#

*Compiled and tested in Windows 7 and Python 3.8.1

*client_script.py requirements (pip install):
	Pillow==8.2.0
	pywin32==300
	win10toast==0.9
[For the Toast-Notifications callback module code replace __init__.py file from win10toast module with:
https://github.com/Charnelx/Windows-10-Toast-Notifications/blob/98b894b694cb58c125a92497b1ed05bd438f9c36
/win10toast/__init__.py]

*view_script.py requirements (pip install):
	Pillow==8.2.0

*In order to make the python scripts executables use (pip install):
	pyinstaller==4.3

*Modules can be found in "\codes\virenv\Lib\site-packages" path.

*Check network traffic while using the scripts.
*Check windows 10 compatibility of ATANOTICL.EXE. client_script.py. The threads regarding network and sleep
	signals are commented out.
*High CPU usage from ATANOTICL.EXE. client_script.py should become more lightweight regarding CPU usage.
*ATANOTISRV.exe could use user grouping if the number of users is too big.
