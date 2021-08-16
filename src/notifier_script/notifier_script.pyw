#Konstantinos Routsis
import socket, threading, sys, time, os
import tkinter as tk

client_list = []
connections = {}
check_buttons = {}

window = tk.Tk()
text_header = tk.StringVar()
text_message_wid = tk.Text(window, height=5, width=40, font=("Calibri"))
outer_frame = tk.Frame(window)
cb_canvas = tk.Canvas(outer_frame, bd=0, height=180, width=300)
cb_frame = tk.Frame(cb_canvas)
check_button_all_var = tk.BooleanVar()

def gui(start_server_thread = False):

    if start_server_thread:
        #create server thread
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        #static tkinter widgets
        window.title('LAN-Notifier')
        window.resizable(width=False, height=False)
        lbl_text = "SERVER",HOST,"(",PORT,")"
        lbl = tk.Label(window, text=lbl_text, font=("Arial Bold", 12))
        lbl.grid(column=0, row=0)
        text_header_wid = tk.Entry(window, width=40, textvariable=text_header, font=("Calibri"))
        text_header_wid.grid(column=0, row=3, pady=5)
        text_message_wid.grid(column=0, row=4, padx=10, pady=5)
        clear_btn = tk.Button(window, text="    NEW     ", command= lambda: clear_it())
        clear_btn.grid(column=0, row=5, sticky="nw", padx=10, pady=5)
        send_btn = tk.Button(window, text="    SEND    ", command= lambda: send_it())
        send_btn.grid(column=0, row=5, sticky="ne", padx=10, pady=5)
        ysb = tk.Scrollbar(outer_frame, orient="vertical", command=cb_canvas.yview)
        ysb.grid(column=1, row=0, sticky="ns")
        cb_canvas.configure(yscrollcommand=ysb.set)
        cb_canvas.grid(column=0, row=0, padx=2)
        outer_frame.grid(column=0, row=2)

    def on_closing():
        from tkinter import messagebox
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            window.destroy()
            #sys.exit()
            os._exit(0)
    
    def set_cb_values(key):
        if key['var'].get() == True:
            key['checked'] = True
        else:
            key['checked'] = False
            check_button_all.deselect()
        if all_checked():
            check_button_all.select()
    
    def manage_msg(txt_msg):
        msg_lines = txt_msg.split("\n")
        count = 0
        for i, line in enumerate(msg_lines):
            if len(line) > 40:
                count += 1
                tmp_line = line[:40]
                msg_lines[i] = line[:tmp_line.rfind(" ")]+"\n"+line[tmp_line.rfind(" ")+1:40]+line[40:]
                txt_msg = "\n".join(msg_lines)
                return manage_msg(txt_msg)
        if count == 0:
            return txt_msg

    def send_it():
        already_sent = True
        text_message_wid.config(state=tk.DISABLED)
        txt_head = text_header.get()
        txt_msg = text_message_wid.get("1.0", "end-1c")
        txt_msg = manage_msg(txt_msg)
        if txt_head == "" or txt_msg == "":
            from tkinter import messagebox
            messagebox.showwarning('Send Message','Write a header and a message.\n Select clients.\n Then press SEND button.')
            return False
        send_time = time.strftime("%H:%M:%S", time.localtime())
        msg = send_time + "|" + txt_head + "|" + txt_msg
        txt_msg = txt_msg.replace('\n', ' ')
        log = "["+get_time()+"] MESSAGE: "+txt_head+"|"+txt_msg+" sent to user(s):\n"
        write_log_file(log)
        for addr in check_buttons:
            if check_buttons[addr]['checked'] == True and check_buttons[addr]['color'] != "green":
                log = str(addr)+", "
                write_log_file(log)
                already_sent = False
                check_buttons[addr]['sock'].send(msg.encode())
                time.sleep(1)
                if check_buttons[addr]['color'] == "":
                    check_buttons[addr]['color'] = "red"
                    check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                             fill=check_buttons[addr]['color'])
        write_log_file("\n")
        if already_sent == True:
            from tkinter import messagebox
            messagebox.showwarning('Send Message','This message is already sent to all selected clients.\n Press NEW button to send a new message.')
            return False

    def clear_it():
        text_message_wid.config(state=tk.NORMAL)
        #text_header_wid.delete(0, tk.END)
        text_message_wid.delete("1.0", "end-1c")
        for addr in check_buttons:
            check_buttons[addr]['color'] = ""
            check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                     fill=check_buttons[addr]['color'])
    
    def check_all():
        if check_button_all_var.get() == True:
            for addr in check_buttons:
                check_buttons[addr]['checked'] = True
                check_buttons[addr]['widget'].select()

    def all_checked():
        for addr in check_buttons:
            if check_buttons[addr]['checked'] == True:
                continue
            else:
                return False
        return True

    def on_mousewheel(event):
        cb_canvas.yview_scroll(-1*(event.delta//120), "units")
        
    #destroy previous checkbutton widgets
    for child in cb_frame.winfo_children():
        child.destroy()
    #remove checkbuttons
    cb_del = check_buttons.keys() - connections.keys()
    if cb_del:
        del check_buttons[cb_del.pop()]
    
    #check_all checkbutton
    check_button_all = tk.Checkbutton(window, text="All", 
                    onvalue=True, offvalue=False,
                    var=check_button_all_var,
                    command=lambda: check_all())
    check_button_all.grid(column=0, row=1)

    #show checkbuttons and indicators
    for row, addr in enumerate(connections.keys()):
        checkbutton_text = addr[0]
        #check client_list for address' name 
        for client in client_list:
            if client[0] == addr[0]:
                client_name = client[1]
                checkbutton_text = addr[0] + " [" + client_name + "]"
        row += 1 #row 0: check_all checkbutton
        if addr in check_buttons: #old checkbuttons
            check_buttons[addr]['widget'] = tk.Checkbutton(cb_frame, text=checkbutton_text, 
                                            onvalue=True, offvalue=False,
                                            var=check_buttons[addr]['var'],
                                            command=lambda key=check_buttons[addr]: set_cb_values(key))
            if check_buttons[addr]['checked'] == True:
                check_buttons[addr]['widget'].select()
            check_buttons[addr]['canvas'] = tk.Canvas(cb_frame, width=20, height=28)
            check_buttons[addr]['indicator'] = check_buttons[addr]['canvas'].create_oval(10, 10, 20, 20,
                                               fill=check_buttons[addr]['color'])
        else: #new checkbuttons
            check_buttons[addr] = {}
            check_buttons[addr]['sock'] = connections[addr]
            check_buttons[addr]['var'] = tk.BooleanVar()
            check_buttons[addr]['widget'] = tk.Checkbutton(cb_frame, text=checkbutton_text, 
                                            onvalue=True, offvalue=False,
                                            var=check_buttons[addr]['var'],
                                            command=lambda key=check_buttons[addr]: set_cb_values(key))
            if check_button_all_var.get() == True:
                check_buttons[addr]['checked'] = True
                check_buttons[addr]['widget'].select()
            else:
                check_buttons[addr]['checked'] = False
            check_buttons[addr]['color'] = ""
            check_buttons[addr]['canvas'] = tk.Canvas(cb_frame, width=20, height=28)
            check_buttons[addr]['indicator'] = check_buttons[addr]['canvas'].create_oval(10, 10, 20, 20,
                                               fill=check_buttons[addr]['color'])
        check_buttons[addr]['widget'].grid(row=row, column=0)
        check_buttons[addr]['canvas'].grid(row=row, column=1)

    #manage checkbutton canvas
    cb_frame.update()
    cb_canvas.configure(scrollregion=(1,1,0,cb_frame.winfo_height()))
    cb_canvas.bind_all("<MouseWheel>", on_mousewheel)
    cb_canvas.create_window(outer_frame.winfo_width()//2, 0, window=cb_frame, anchor='n')
    
    window.protocol("WM_DELETE_WINDOW", on_closing)
    
    window.mainloop()      

def handle_client(conn, addr):
    # display client address
    connections[addr] = conn
    log = "["+get_time()+"] NEW CONNECTION: "+str(addr[0])+"\n"
    write_log_file(log)
    while True:
        try:
            # receave message from client
            sig = conn.recv(64).decode()
            if sig == "k":
                check_buttons[addr]['color'] = "yellow"
                check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                         fill=check_buttons[addr]['color'])
                log = "["+get_time()+"] "+str(addr)+": got the message\n"
                write_log_file(log)
            elif sig == "ROGER":
                check_buttons[addr]['color'] = "green"
                check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                         fill=check_buttons[addr]['color'])
                log = "["+get_time()+"] "+str(addr)+": read the message\n"
                write_log_file(log)
        except Exception as e:
            # disconnect the server
            conn.close()
            del connections[addr]
            log = "["+get_time()+"] "+str(addr)+": "+str(e)+"\n"
            write_log_file(log)
            window.after(0, gui)
            # kill thread
            sys.exit()

def start_server():
    log = "\n=============== STARTING SERVER: "+HOST+" "+str(PORT)+" ["+get_time()+"] ===============\n"
    write_log_file(log)
    # allow maximum 3 connections to the socket 
    s.listen(10)
    while True:
        # wait till a client accept connection 
        conn, addr = s.accept()
        # create a thread to handle each connection 
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()
        
        window.after(0, gui)

def get_time():
    t = time.strftime("%d-%m-%Y %H:%M:%S", time.localtime())
    return t

def write_log_file(text):
    with open("log.txt", "a") as lf:
        lf.write(text)

def read_client_list():
    global PORT
    try:
        with open("client_list.txt", "r") as f:
            if len(f.readline()) <= 6:
                f.seek(0)
                PORT = int(next(f))
            else:
                f.seek(0)
                PORT = 5050
            for client in f.readlines():
                client_list.append(client.strip().split(";"))
    except FileNotFoundError:
        PORT = 5050
    
if __name__ == "__main__":
    read_client_list()
    # take the server name and port name 
    HOST = socket.gethostbyname(socket.gethostname())
    #PORT = 5050
    # create a socket at server side using TCP / IP protocol 
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # bind the socket with server and port number 
    s.bind((HOST, PORT))
    gui(True)