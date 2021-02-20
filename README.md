# Lan-Notifications
<h2>A server-client system that sends notification messages in a Lan network through python sockets.</h2>

<h3>A very useful tool for every Lan network admin. 

Sends direct messages to every computer-user in your network as popup notification.</h3>

<h3>Server Script (For the network admin)</h3>

## Configure

You need to create these files in the "src" directory: 
`constants.txt` example:

```
HOST = 192.168.0.123
PORT = 5050
MODE = 2
```
MODE 1 - show a custom window as a notification

MODE 2 - show a normal notification

`client_list.txt` example:

```
192.168.0.1 = ADMIN
192.168.0.2 = PC1
```

This is in general to know what IP is what computer.

![lan1](https://user-images.githubusercontent.com/63212423/107270343-80c29e00-6a53-11eb-861e-0b251013c464.PNG)
<br>

<li>Red dot: Notification has not been sent.</li>
<li>Yellow dot: Notification has been sent.</li>
<li>Green dot: User has seen the notification (end respond).</li>
<br>
<h3>Client Script (For the network users)</h3>
<li>Mode 1 (Tkinter window)</li>

![lan2](https://user-images.githubusercontent.com/63212423/107272290-25de7600-6a56-11eb-8ce8-e87b6b5dfca2.PNG)
<br>
<li>Mode 2 (Windows notification popup)</li>

![lan3](https://user-images.githubusercontent.com/63212423/107272329-3abb0980-6a56-11eb-9208-be9a4d9f944a.PNG)
<br>
