# Lan-Notifications
<h2>A server-client system that sends notification messages in a Lan network through python sockets.</h2>

<h3>A very useful tool for every Lan network admin. 

Sends direct messages to every computer-user in your network as popup notification.</h3>

<h3>Notifier Script (For the network admin)</h3>

### Configure

[OPTIONAL] Create client_list.txt file in the "src/notifier_script" directory: 

`client_list.txt` example:
```
5050
192.168.168.34;ADMIN
192.168.168.67;PC1
```
In the first line is the PORT that the notifier_script will use (default PORT 5050).
After that there is a list with IPs and computer names so that the admin will know the user-PC behind every IP.
Without this file the IPs will presented unnamed.

![lan1](https://user-images.githubusercontent.com/63212423/107270343-80c29e00-6a53-11eb-861e-0b251013c464.PNG)
<br>
<li>Red dot: Notification has not been sent.</li>
<li>Yellow dot: Notification has been sent.</li>
<li>Green dot: User has seen the notification (end respond).</li>
<br>

<h3>View Script (For the network admin)</h3>

### Configure

Populate rooms foldier with JPEG Images of your workplace.
[OPTIONAL] Create client_list.txt file in the "src/view_script" directory: 

`client_list.txt` example:
```
5055
192.168.168.34;ADMIN;(479.0, 250.0);office-1
192.168.168.67;PC1;(734.0, 175.0);office-2
```
In the first line is the PORT that the view_script will use (default PORT 5055).
After that there is a list with IPs, computer names, coordinates and the workplaces room (same with JPEG Image's name).
The list is populated from within the program by double right clicking on the correct spot in the room's picture.

![viewpic](https://user-images.githubusercontent.com/63212423/129741165-85c4e0d5-4d1e-4f99-8cd6-f1948ec8faaf.png)
<br>
<li>Red dot: The machine is offline.</li>
<li>Green dot: The machine is online.</li>
<br>


<h3>Client Script (For the network users)</h3>

### Configure

Create constants.txt file in the "src/client_script" directory: 

`constants.txt` example:
```
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
```
In the above example client_script listens to 3 different server executables from 2 different machines.
HOST is the server's ip. PORT is the port that the connection-communication will take place. MODE 
can only take values 1 or 2 and it concerns the way the notification will be shown in the client
machine. If MODE = 1(recommended), notification will be shown as tkinter GUI window. If MODE = 2,
notification will be shown as windows push-notification.

<li>Mode 1 (Tkinter window)</li>

![lan2](https://user-images.githubusercontent.com/63212423/107272290-25de7600-6a56-11eb-8ce8-e87b6b5dfca2.PNG)
<br>
<li>Mode 2 (Windows notification popup)</li>

![lan3](https://user-images.githubusercontent.com/63212423/107272329-3abb0980-6a56-11eb-9208-be9a4d9f944a.PNG)
<br>
Licensed under the [MIT License](LICENSE)
