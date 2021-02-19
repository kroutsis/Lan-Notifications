# Konstantinos Routsis
import os
import socket
import sys
import threading
import tkinter as tk
from tkinter import ttk

# from subprocess import Popen, PIPE
from PIL import ImageTk, Image

if sys.platform == "win32":
        import win32con
        import win32api
        import win32gui
        from win10toast import ToastNotifier
        # import winsound

sleep_flag = False


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
        pass


def check_sleep_sig():
    detect_sleep()
    while True:
        win32gui.PumpWaitingMessages()
        if sleep_flag:
            os.execv(sys.executable, ['python', __file__])


def check_network_con():
    online_flag = True
    while online_flag:
        ipaddress = socket.gethostbyname(socket.gethostname())
        if ipaddress != my_lan_ip:
            online_flag = False
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
    my_lan_ip = socket.gethostbyname(socket.gethostname())
    connected = False
    while not connected:
        try:
            # connect it to server
            c.connect((HOST, PORT))
            connected = True
            return c
        except ConnectionError as e:
            print(e)
            pass


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
        img = Image.open("logo.png")
        img = img.resize((60, 60), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(top_frame, width=60, height=60)
        canvas.pack(side=tk.LEFT)
        canvas.create_image(1, 1, anchor=tk.NW, image=img)
    except Exception as e:
        print(e)
        pass

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
    separator = ttk.Separator(window).place(x=0, y=top_frame.winfo_height(), relwidth=1)
    center_window(root_frame.winfo_width() + 20, root_frame.winfo_height())
    window.mainloop()


mode_var = 0


def recv_msg(c, mode=1):
    global mode_var
    check_sleep_thread = threading.Thread(target=check_sleep_sig).start()
    check_network_thread = threading.Thread(target=check_network_con).start()
    while True:
        try:
            msg = c.recv(1024)
            if msg:
                c.send("k".encode())
            # print("RECEIVED: ", msg.decode())
            message = msg.decode().split("|")

            if mode == 1:
                gui(c, message)
                continue
            elif mode == 2:
                t = ToastNotifier()
                # Toast-Notifications callback module code change
                # https://github.com/Charnelx/Windows-10-Toast-Notifications/blob/
                # 98b894b694cb58c125a92497b1ed05bd438f9c36/win10toast/__init__.py
                t.show_toast(message[1], message[2] + "\n[" + message[0] + "]",
                             icon_path="logo.ico", threaded=False,
                             callback_on_click=lambda: respond(c))
            else:
                print("Error! Constants.txt file corrupted.")

            mode_var = mode
        except Exception as e:
            c.close()
            c = connect()
            print(e)
            break


def init():
    c = connect()
    recv_msg(c, mode_var)


HOST = None
PORT = None
MODE = None


def read_constants():
    global HOST
    global PORT
    global MODE

    const_list = []
    with open("constants.txt", "r") as f:
        for const in f.readlines():
            const_list.append(const.strip().split(" = ")[1])
    HOST = const_list[0]
    PORT = int(const_list[1])
    MODE = int(const_list[2])


if __name__ == "__main__":
    read_constants()
    init()
