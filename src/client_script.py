# Konstantinos Routsis
import os
import socket
import sys
import threading
import tkinter as tk
from tkinter import ttk
import netifaces as ni

# custom modules
import threads_handle
import files_handle

# from subprocess import Popen, PIPE
from PIL import ImageTk, Image

if sys.platform == "win32":
        import win32con
        import win32api
        import win32gui
        from win10toast import ToastNotifier
        # import winsound

sleep_flag = False
threads_list = []


def detect_sleep():
    def wndproc(hwnd, msg, wparam, lparam):
        global sleep_flag
        if msg:
            # win32 message num 536 WM_POWERBROADCAST
            sleep_flag = True

    hinst = win32api.GetModuleHandle(None)
    wndclass = win32gui.WNDCLASS()
    wndclass.hInstance = hinst
    wndclass.lpszClassName = "testWindowClass"
    message_map = {win32con.WM_QUERYENDSESSION: wndproc,
                  win32con.WM_ENDSESSION: wndproc,
                  win32con.WM_POWERBROADCAST: wndproc}
    wndclass.lpfnWndProc = message_map
    try:
        my_window_class = win32gui.RegisterClass(wndclass)
        hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT,
                                       my_window_class,
                                       "testMsgWindow",
                                       0, 0, 0,
                                       win32con.CW_USEDEFAULT,
                                       win32con.CW_USEDEFAULT,
                                       # win32con.HWND_MESSAGE,
                                       0, 0, hinst, None)
    except Exception as e:
        print(e)


run_threads = True


def check_sleep_sig():
    detect_sleep()
    while run_threads is True:
        win32gui.PumpWaitingMessages()
        if sleep_flag:
            print("System sleeps")
            os.execv(sys.executable, ['python', __file__])


# this function will search all interfaces and return the first that starts with "192."
def get_lan_ip():
    for int in ni.interfaces():
        got_ip = ni.ifaddresses(int)[ni.AF_INET][0]['addr']
        if got_ip.startswith("192."):
            return got_ip
    return None


def check_network_con():
    online_flag = True
    while online_flag and run_threads is True:
        ipaddress = get_lan_ip()
        if ipaddress is None:
            print("No interface starts with 192.")
            return 1
        if ipaddress != my_lan_ip:
            online_flag = False
            print("Network connection lost")
    if online_flag is False:
        os.execv(sys.executable, ['python', __file__])
    '''
    online_flag = True
    while online_flag:
        #Ping Host address every 15 mins
        ping = Popen("ping -n 1 " + HOST, stdout=PIPE, stderr=PIPE)
        exit_code = ping.wait()
        time.sleep(15*60)
        if exit_code != 0:
            online_flag = False
    os.execv(sys.executable, ['python', __file__])
    '''


my_lan_ip = None


def connect():
    # create a socket at client side using TCP / IP protocol 
    # AF_INET refers to the address family ipv4. The SOCK_STREAM means connection oriented TCP protocol
    c = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    global my_lan_ip
    my_lan_ip = get_lan_ip()
    if my_lan_ip is None:
        print("No interface starts with 192.")
        return 1
    connected = False
    count = 0
    while not connected:
        try:
            # connect it to server
            c.connect((HOST, PORT))
            connected = True
            return c
        except (OSError, ConnectionError) as e:
            print(e)
            count += 1
            if count == 3:
                print("3 attempts to connect passed")
                break


def respond(c, window=None):
    try:
        c.send("ROGER".encode())
        if window is not None:
            window.destroy()
    except ConnectionResetError:
        os.execv(sys.executable, ['python', __file__])

def gui(c, message):
    window = tk.Tk()

    def center_window(width=300, height=200):
        # get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()

        # calculate position x and y coordinates
        x = screen_width-width-16
        y = screen_height-height-73
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    window.title(message[0])
    window.attributes('-toolwindow', True)
    window.attributes('-topmost', True)
    # winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
    window.resizable(width=False, height=False)
    root_frame = tk.Frame(window)

    top_frame = tk.Frame(root_frame)
    try:
        img = Image.open("logo.ico")
        img = img.resize((60, 60), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(top_frame, width=60, height=60)
        canvas.pack(side=tk.LEFT)
        canvas.create_image(1, 1, anchor=tk.NW, image=img)
    except Exception as e:
        print(e)

    msg_frame = tk.Frame(top_frame)
    lbl1 = tk.Label(msg_frame, text=message[1], font=("Arial Bold", 14))
    lbl1.pack()
    lbl2 = tk.Label(msg_frame, text=message[2], font=("Arial", 12), anchor="e", justify=tk.LEFT)
    lbl2.pack()
    msg_frame.pack(side=tk.RIGHT)
    top_frame.pack()

    bot_frame = tk.Frame(root_frame)
    bot_frame.pack(fill=tk.BOTH, expand=True)
    roger_btn = tk.Button(bot_frame, text="  ROGER  ", command=lambda: respond(c, window))
    roger_btn.pack(side=tk.RIGHT, padx=5, pady=5)

    root_frame.pack()
    root_frame.update()
    # separator = ttk.Separator(window).place(x=0, y=top_frame.winfo_height(), relwidth=1)
    center_window(root_frame.winfo_width() + 20, root_frame.winfo_height())
    window.lift()
    window.mainloop()


mode_var = 0


def recv_msg(c, mode=1):
    global threads_list
    global run_threads
    check_sleep_thread = threading.Thread(target=check_sleep_sig)
    check_sleep_thread.start()
    threads_list.append(check_sleep_thread)
    check_network_thread = threading.Thread(target=check_network_con)
    check_network_thread.start()
    threads_list.append(check_network_thread)
    while True:
        try:
            msg = c.recv(1024)
            if msg:
                c.send("k".encode())
        except (OSError, ConnectionError, AttributeError) as e:
            print(e)
            break
        else:
            # print("RECEIVED: ", msg.decode())
            message = msg.decode().split("|")

            if mode == 1:
                gui(c, message)
                continue
            elif mode == 2:
                t = ToastNotifier()
                t.show_toast(message[1], message[2] + "\n[" + message[0] + "]",
                             icon_path="logo.ico", threaded=False)
            else:
                print("Error! Constants.txt file corrupted.")
                break

    try:
        c.close()
    except (OSError, ConnectionError, AttributeError) as e:
        print(e)
    run_threads = False


HOST = None
PORT = None
MODE = None


def read_constants():
    global HOST
    global PORT
    global MODE
    global mode_var
    constants_list = files_handle.get_constants("constants.txt")
    HOST = constants_list[0]
    PORT = constants_list[1]
    MODE = constants_list[2]
    mode_var = MODE


if __name__ == "__main__":
    read_constants()
    recv_msg(connect(), mode_var)
    threads_handle.finish_threads(threads_list)
