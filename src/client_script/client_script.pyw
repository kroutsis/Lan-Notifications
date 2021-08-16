#Konstantinos Routsis
import socket, time, threading, sys, os
import tkinter as tk
from tkinter import ttk
try:
    from PIL import ImageTk, Image
except ImportError:
    pass
if sys.platform == "win32":
    try:
        import win32con
        import win32api
        import win32gui
        from win10toast import ToastNotifier
        #import winsound
    except ImportError:
        pass

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
    messageMap = { win32con.WM_QUERYENDSESSION : wndproc,
                   win32con.WM_ENDSESSION : wndproc,
                   win32con.WM_POWERBROADCAST : wndproc }
    wndclass.lpfnWndProc = messageMap
    try:
        myWindowClass = win32gui.RegisterClass(wndclass)
        hwnd = win32gui.CreateWindowEx(win32con.WS_EX_LEFT,
                                       myWindowClass, 
                                       "testMsgWindow", 
                                       0, 0, 0, 
                                       win32con.CW_USEDEFAULT, 
                                       win32con.CW_USEDEFAULT, 
                                       #win32con.HWND_MESSAGE, 
                                       0, 0, hinst, None)
    except:
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

def connect(HOST, PORT):
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
        except:
            pass
 
def respond(c, window=None):
    try:
        c.send("ROGER".encode())
        if window != None:
            window.destroy()
    except ConnectionResetError:
        os.execv(sys.executable, ['python', __file__])

def gui(c, title, message):

    window = tk.Tk()
    def center_window(width=300, height=200):
        # get screen width and height
        screen_width = window.winfo_screenwidth()
        screen_height = window.winfo_screenheight()
    
        # calculate position x and y coordinates
        x = (screen_width) - (width) - 16
        y = (screen_height) - (height) - 73
        window.geometry('%dx%d+%d+%d' % (width, height, x, y))

    window.title(title)
    window.attributes('-toolwindow', True)
    window.attributes('-topmost', True)
    #winsound.PlaySound('SystemExclamation', winsound.SND_ALIAS)
    window.resizable(width=False, height=False)
    root_frame = tk.Frame(window)
    
    top_frame = tk.Frame(root_frame)
    try:
        img = Image.open("logo.ico")
        img = img.resize((60,60), Image.ANTIALIAS)
        img = ImageTk.PhotoImage(img)
        canvas = tk.Canvas(top_frame, width = 60, height = 60)  
        canvas.pack(side=tk.LEFT)
        canvas.create_image(1, 1, anchor=tk.NW, image=img)
    except:
        pass
    
    msg_frame = tk.Frame(top_frame)
    lbl1 = tk.Label(msg_frame, text=message[1], font=("Arial Bold", 14))
    lbl1.pack()
    lbl2 = tk.Label(msg_frame, text=message[2]+"\n["+message[0]+"]", font=("Arial", 12), anchor="e", justify=tk.LEFT)
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
    center_window(root_frame.winfo_width()+20, root_frame.winfo_height())
    window.mainloop()

def recv_msg(c, HOST, PORT, NAME, MODE):
    title = NAME+" ["+HOST+"]"
    while True:
        try:
            msg = c.recv(1024)
            if msg:
                c.send("k".encode())
            message = msg.decode().split("|")

            if MODE == 1:
                gui(c, title, message)
                continue
            elif MODE == 2:
                t = ToastNotifier()
                # Toast-Notifications callback module code change
                # https://github.com/Charnelx/Windows-10-Toast-Notifications/blob/
                # 98b894b694cb58c125a92497b1ed05bd438f9c36/win10toast/__init__.py
                t.show_toast(message[1], message[2] + "\n" + title + "\n[" + message[0] + "]", 
                             icon_path="logo.ico", threaded=False,
                             callback_on_click=lambda: respond(c))
            else:
                print("Error! Constants.txt file corrupted.")
        except Exception as e:
            c.close()
            c = connect(HOST, PORT)

def init(HOST, PORT, NAME, MODE):
    #constants = [HOST, PORT, NAME, MODE]
    c = connect(HOST, int(PORT))
    recv_msg(c, HOST, int(PORT), NAME, int(MODE))

def read_constants():
    const_temp_list = []
    with open("constants.txt", "r") as f:
        for const in f.readlines():
            const_temp_list.append(const.strip().split(" = ")[1])
    constants = [const_temp_list[i:i+4] for i in range(0, len(const_temp_list), 4)]
    return constants

if __name__ == "__main__":
    constants = read_constants()
    for const in constants:
        threading.Thread(target=init, args=const).start()
    #check_sleep_thread = threading.Thread(target=check_sleep_sig).start()
    #check_network_thread = threading.Thread(target=check_network_con).start()
