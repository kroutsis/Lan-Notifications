#Konstantinos Routsis
import socket, threading, sys, os, time
import tkinter as tk
from tkinter import ttk
from PIL import ImageTk, Image

# office rooms image filenames
ROOM_FILES = os.listdir('./rooms')
ROOMS = [i[:-4] for i in ROOM_FILES]

connections = {}
client_list = []

input_window = None
room_choice = ROOMS[0]
window = tk.Tk()

img = []
img_size = []

def gui(room_img, change_room = False, start_server_thread = False):
    
    rooms_client_list = []
    i = ROOMS.index(room_img)

    if start_server_thread:
        #create server thread
        server_thread = threading.Thread(target=start_server)
        server_thread.daemon = True
        server_thread.start()
        window.title("LAN-Viewer SERVER "+HOST+" ("+str(PORT)+")")
    else:
        widget_count = len(window.winfo_children())
        for child in window.winfo_children():
            if widget_count < 4:
                child.destroy()
            widget_count -= 1
    
    if change_room:
        for child in window.winfo_children():
            child.destroy()
        global canvas
        canvas = tk.Canvas(width=800, height=600)
        canvas.create_image(0, 0, image=img[i], anchor=tk.NW)
    
    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()
            #sys.exit()
            os._exit(0)
    
    def create_ind(name, ip, pos, active):
        x, y = pos
        text = " "+name+"\n IP: "+ip+"\n Active: "+str(active)
        if active == True:
            color_fill = "green"
        else:
            color_fill = "red"
        oval = canvas.create_oval(x-8, y-8, x+8, y+8, fill=color_fill, tags=ip)
        text_item = canvas.create_text(x+10, y-8, anchor="nw", text=text, tags=ip)
        bbox = canvas.bbox(text_item)
        rect_item = canvas.create_rectangle(bbox, outline="black", fill="white", tags=ip)
        canvas.tag_raise(text_item,rect_item)
    
    def scroll_start(event):
        canvas.scan_mark(event.x, event.y)

    def scroll_move(event):
        canvas.scan_dragto(event.x, event.y, gain=1)
    
    def choose_room(selection):
        global room_choice
        room_choice = selection
        gui(room_choice, True)
    
    def prev_room():
        global room_choice
        i = ROOMS.index(room_choice)
        room_choice = ROOMS[i-1]
        gui(room_choice, True)
    
    def next_room():
        global room_choice
        i = ROOMS.index(room_choice)
        if i == len(ROOMS)-1:
            room_choice = ROOMS[0]
        else:
            room_choice = ROOMS[i+1]
        gui(room_choice, True)
    
    def help_b():
        from tkinter import messagebox
        messagebox.showinfo(title="Help", message="Press double right click to add a new computer.\nPress right click on existing computer to change its values or delete it.\nUse arrows or menu list to navigate through rooms.\nPress print to take a snapshot of current state of the room.")
        
    def print_b():
        t = time.strftime("%d-%m-%Y_%H-%M-%S", time.localtime())
        file_name = room_choice+"_"+t+".eps"
        canvas.yview_moveto('0.0')
        canvas.xview_moveto('0.0')

        img_info = "SERVER: "+HOST+" PORT: "+str(PORT)+"\n"+room_choice+"\n"+text_info_room+"\n"+time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
        text_item = canvas.create_text(15, 15, anchor="nw", justify='center', text=img_info)
        bbox = canvas.bbox(text_item)
        rect_item = canvas.create_rectangle(bbox, outline="black", fill="white")
        canvas.tag_raise(text_item,rect_item)
        canvas.postscript(file=file_name, width=img_size[i][0], height=img_size[i][1])
        canvas.delete(text_item,rect_item)
        #img = Image.open("room.eps")
        #img.save("room.jpg")
    
    #Mouse events
    for num,client in enumerate(client_list):
        canvas.tag_bind(client[0],"<ButtonPress-3>", lambda event, num=num, client=client:create_input_window(event, client, num))
    canvas.bind("<Double-ButtonPress-3>",lambda event:create_input_window(event))
    canvas.bind("<ButtonPress-1>", scroll_start)
    canvas.bind("<B1-Motion>", scroll_move)
    
    #Manage clients
    for client in client_list:
        active = False
        for addr in connections.keys():
            if client[0] == addr[0]:
                active = True
        ip = client[0]
        name = client[1]
        pos = eval(client[2])
        if client[3] == room_img:
            rooms_client_list.append((client, active))
            create_ind(name, ip, pos, active)

    #Scrollbars
    xsb = tk.Scrollbar(orient="horizontal", command=canvas.xview)
    ysb = tk.Scrollbar(orient="vertical", command=canvas.yview)
    canvas.configure(yscrollcommand=ysb.set, xscrollcommand=xsb.set)
    canvas.configure(scrollregion=(0,0,img_size[i][0],img_size[i][1]))
    xsb.grid(row=1, column=0, sticky="ew")
    ysb.grid(row=0, column=1, sticky="ns")
    window.grid_rowconfigure(0, weight=1)
    window.grid_columnconfigure(0, weight=1)
    #Info Frame
    info_frame = tk.Frame(window, borderwidth=2, relief="raised")
    variable = tk.StringVar()
    variable.set(room_img) # default value
    #Room selection
    w = tk.OptionMenu(info_frame, variable, *ROOMS, command=choose_room)
    w.pack()
    #Room's info
    label_frame_room = ttk.LabelFrame(info_frame, text = room_choice) 
    label_frame_room.pack(expand = 'yes', fill = 'both') 
    active_clients_in_room = 0
    for rooms_client in rooms_client_list:
        if rooms_client[1] == True:
            active_clients_in_room +=1
    text_info_room = str(len(rooms_client_list))+" Computers\n"+str(active_clients_in_room)+" Online\n"+str(len(rooms_client_list) - active_clients_in_room)+" Offline"
    label_room = tk.Label(label_frame_room, text=text_info_room, anchor="e", justify=tk.LEFT)
    label_room.pack()
    #Total info
    label_frame_all = ttk.LabelFrame(info_frame, text = "Total") 
    label_frame_all.pack(expand = True, fill = 'both') 
    text_info_all = str(len(ROOMS))+" Rooms\n"+str(len(client_list))+" Computers\n"+str(len(connections))+" Online\n"+str(len(client_list)-len(connections))+" Offline"
    label_total = tk.Label(label_frame_all, text=text_info_all, anchor="e", justify=tk.LEFT)
    label_total.pack()
    info_frame.place(x = 10, y = 10)
    #Prev Next Buttons
    button_frame = tk.Frame(info_frame)
    b_previous = tk.Button(button_frame, text ="  <<   ", command=prev_room)
    b_previous.pack(side=tk.LEFT)
    b_next = tk.Button(button_frame, text ="   >>  ", command=next_room)
    b_next.pack(side=tk.RIGHT)
    button_frame.pack()
    #Help Print Buttons
    help_frame = tk.Frame(info_frame)
    help_button = tk.Button(help_frame, text =" Help ", command=help_b)
    print_button = tk.Button(help_frame, text =" Print ", command=print_b)
    help_button.pack(side=tk.LEFT)
    print_button.pack(side=tk.RIGHT)
    help_frame.pack()
    '''
    #Server-Port info
    info_frame.update()
    lbl_frame = tk.Frame(window, borderwidth=2, relief="raised")
    lbl_text = "SERVER",HOST,"(",PORT,")"
    lbl = tk.Label(lbl_frame, text=lbl_text, font=("Arial Bold", 12))
    lbl.pack()
    lbl_frame.place(x = info_frame.winfo_width() + 30, y = 10)
    '''
    canvas.grid(row=0, column=0, sticky="nsew")
    
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    window.mainloop()

def create_input_window(event, client=None, num=None):

    global input_window
    if input_window is not None:
        input_window.destroy()
    input_window = tk.Toplevel(window)
    
    input_window.resizable(width=False, height=False)
    input_window.attributes('-toolwindow', True)
    input_window.lift(aboveThis=window)
    
    pos_text = tk.StringVar()
    room_text = tk.StringVar()
    name_text = tk.StringVar()
    ip_text = tk.StringVar()
    
    if client == None:
        delete_state = tk.DISABLED
        input_window.title("New Computer")
        x, y = canvas.canvasx(event.x), canvas.canvasy(event.y)
        pos_text.set(str((x, y)))
        room_text.set(room_choice)
    else:
        delete_state = tk.NORMAL
        input_window.title("Change/Delete Computer")
        ip_text.set(client[0])
        name_text.set(client[1])
        pos_text.set(client[2])
        room_text.set(client[3])

    def delete_computer():
        f = open("client_list.txt", "r")
        lines = f.readlines()
        f.close()
        del lines[num]
        f = open("client_list.txt", "w")
        last_line = len(lines)
        for i,line in enumerate(lines):
            if i+1 == last_line and num == last_line:
                f.write(line[:-1])
            else:
                f.write(line)
        f.close()
        canvas.delete(client[0])
    
    def save_input():
        if (len(name_text.get()) != 0) and (len(ip_text.get()) != 0) and (len(room_text.get()) != 0):
            input_window.destroy()
            if client != None:
                delete_computer()
            with open("client_list.txt", "a") as f:
                f.write("\n"+ip_text.get()+";"+name_text.get()+";"+pos_text.get()+";"+room_text.get())
            client_list.clear()
            read_client_list()
            gui(room_choice)
        else:
            from tkinter import messagebox
            messagebox.showwarning('Submit new computer','Write a computer name and IP.\n Then press Submit button.')
            return False

    tk.Label(input_window, text="Position").grid(row=0, pady=1)
    tk.Label(input_window, text="Name").grid(row=1, pady=1)
    tk.Label(input_window, text="IP").grid(row=2, pady=1)
    tk.Label(input_window, text="Room").grid(row=3, pady=1)
    
    e1 = tk.Entry(input_window, textvariable=pos_text)
    e2 = tk.Entry(input_window, textvariable=name_text)
    e3 = tk.Entry(input_window, textvariable=ip_text)
    e4 = tk.Entry(input_window, textvariable=room_text)

    e1.grid(row=0, column=1, padx=4, pady=1)
    e2.grid(row=1, column=1, padx=4, pady=1)
    e3.grid(row=2, column=1, padx=4, pady=1)
    e4.grid(row=3, column=1, padx=4, pady=1)
    
    quit_button = tk.Button(input_window, text=' Quit ', command=input_window.destroy)
    quit_button.grid(row=4, column=1, sticky='ne', padx=4, pady=4)
    clear_button = tk.Button(input_window, text=' Delete ', state=delete_state, command = lambda:[delete_computer(), input_window.destroy()])
    clear_button.grid(row=4, column=1, sticky='nw', padx=4, pady=4)
    submit_button = tk.Button(input_window, text=' Submit ', command=save_input)
    submit_button.grid(row=4, column=0, padx=4, pady=4)

def manage_room_images():
    global img
    global img_size
    for option in ROOM_FILES:
        option = "rooms/"+option
        raw_img = Image.open(option)
        img_width, img_height = raw_img.size
        img_size.append((img_width, img_height))
        img.append(ImageTk.PhotoImage(raw_img))

def handle_client(conn, addr):
    connections[addr] = conn
    while True:
        try:
            # receave message from client
            sig = conn.recv(64)
        except Exception as e:
            print(addr, ":", e)
            # disconnect the server
            conn.close()
            del connections[addr]
            
            window.after(0, lambda:gui(room_choice))
            # kill thread
            sys.exit()

def start_server():
    # allow maximum 3 connections to the socket 
    s.listen(4)
    while True:
        # wait till a client accept connection 
        conn, addr = s.accept()
        # create a thread to handle each connection 
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        window.after(0, lambda:gui(room_choice))

def read_client_list():
    global PORT
    try:
        with open("client_list.txt", "r") as f:
            if len(f.readline()) <= 6:
                f.seek(0)
                PORT = int(next(f))
            else:
                f.seek(0)
                PORT = 5055
            for client in f.readlines():
                client_list.append(client.strip().split(";"))
    except FileNotFoundError:
        PORT = 5055

if __name__ == "__main__":
    read_client_list()
    # take the server name and port name 
    HOST = socket.gethostbyname(socket.gethostname())
    #PORT = 5055
    # create a socket at server side using TCP / IP protocol 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket with server and port number 
    s.bind((HOST, PORT))
    manage_room_images() 
    gui(room_choice, True, True)