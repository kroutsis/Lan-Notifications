# Konstantinos Routsis
import socket
import sys
import threading
import time
import tkinter as tk

# take the server name and port name 
HOST = socket.gethostbyname(socket.gethostname())
PORT = 5050

# create a socket at server side using TCP / IP protocol 
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
# bind the socket with server and port number 
s.bind((HOST, PORT))

client_list = []
connections = {}
check_buttons = {}

window = tk.Tk()
text_header = tk.StringVar()
text_message_wid = tk.Text(window, height=5, width=40, font="Calibri")
cb_frame = tk.Frame(window)
check_button_all_var = tk.BooleanVar()


def gui(start_server_thread=False):
    if start_server_thread:
        # create server thread
        server_thread = threading.Thread(target=start_server)
        server_thread.start()
        # static tkinter widgets
        window.title('LAN-Notifier')
        window.resizable(width=False, height=False)
        lbl_text = "SERVER", HOST, "(", PORT, ")"
        lbl = tk.Label(window, text=lbl_text, font=("Arial Bold", 12))
        lbl.grid(column=0, row=0)
        text_header_wid = tk.Entry(window, width=40, textvariable=text_header, font=("Calibri"))
        text_header_wid.grid(column=0, row=3, pady=5)
        text_message_wid.grid(column=0, row=4, padx=10, pady=5)
        clear_btn = tk.Button(window, text="    NEW     ", command=lambda: clear_it())
        clear_btn.grid(column=0, row=5, sticky="nw", padx=10, pady=5)
        send_btn = tk.Button(window, text="    SEND    ", command=lambda: send_it())
        send_btn.grid(column=0, row=5, sticky="ne", padx=10, pady=5)

    def set_cb_values(key):
        if key['var'].get() is True:
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
                msg_lines[i] = line[:tmp_line.rfind(" ")] + "\n" + line[tmp_line.rfind(" ") + 1:40] + line[40:]
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
            messagebox.showwarning('Send Message',
                                   'Write a header and a message.\n Select clients.\n Then press SEND button.')
            return False
        date_time = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
        msg = date_time + "|" + txt_head + "|" + txt_msg
        print("\nMessage: ", msg, " sent to user(s):")
        for addr in check_buttons:
            if check_buttons[addr]['checked'] == True and check_buttons[addr]['color'] != "green":
                print(addr)
                already_sent = False
                check_buttons[addr]['sock'].send(msg.encode())
                time.sleep(1)
                if check_buttons[addr]['color'] == "":
                    check_buttons[addr]['color'] = "red"
                    check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                             fill=check_buttons[addr]['color'])
        if already_sent is True:
            from tkinter import messagebox
            messagebox.showwarning('Send Message',
                                   'This message is already sent to all selected clients.\n Press NEW button to send a new message.')
            print("NONE")
            return False

    def clear_it():
        text_message_wid.config(state=tk.NORMAL)
        # text_header_wid.delete(0, tk.END)
        text_message_wid.delete("1.0", "end-1c")
        for addrl in check_buttons:
            check_buttons[addrl]['color'] = ""
            check_buttons[addrl]['canvas'].itemconfig(check_buttons[addrl]['indicator'],
                                                      fill=check_buttons[addrl]['color'])

    def check_all():
        if check_button_all_var.get() is True:
            for addrl in check_buttons:
                check_buttons[addrl]['checked'] = True
                check_buttons[addrl]['widget'].select()

    def all_checked():
        for addrl in check_buttons:
            if check_buttons[addrl]['checked'] is True:
                continue
            else:
                return False
        return True

    # destroy previous checkbutton widgets
    for child in cb_frame.winfo_children():
        child.destroy()
    # remove checkbuttons
    cb_del = check_buttons.keys() - connections.keys()
    if cb_del:
        del check_buttons[cb_del.pop()]

    # check_all checkbutton
    check_button_all = tk.Checkbutton(cb_frame, text="All",
                                      onvalue=True, offvalue=False,
                                      var=check_button_all_var,
                                      command=lambda: check_all())
    check_button_all.grid(column=0, row=0)
    # show checkbuttons and indicators
    for row, addrl in enumerate(connections.keys()):
        checkbutton_text = addrl[0]
        # check client_list for address' name
        for client in client_list:
            if client[0] == addrl[0]:
                client_name = client[1]
                checkbutton_text = addrl[0] + " [" + client_name + "]"

        row += 1  # row 0: check_all checkbutton
        if addrl in check_buttons:  # old checkbuttons
            check_buttons[addrl]['widget'] = tk.Checkbutton(cb_frame, text=checkbutton_text,
                                                            onvalue=True, offvalue=False,
                                                            var=check_buttons[addrl]['var'],
                                                            command=lambda key=check_buttons[addrl]: set_cb_values(key))
            if check_buttons[addrl]['checked'] is True:
                check_buttons[addrl]['widget'].select()
            check_buttons[addrl]['canvas'] = tk.Canvas(cb_frame, width=20, height=28)
            check_buttons[addrl]['indicator'] = check_buttons[addrl]['canvas'].create_oval(10, 10, 20, 20,
                                                                                           fill=check_buttons[addrl][
                                                                                               'color'])
        else:  # new checkbuttons
            check_buttons[addrl] = {}
            check_buttons[addrl]['sock'] = connections[addrl]
            check_buttons[addrl]['var'] = tk.BooleanVar()
            check_buttons[addrl]['widget'] = tk.Checkbutton(cb_frame, text=checkbutton_text,
                                                            onvalue=True, offvalue=False,
                                                            var=check_buttons[addrl]['var'],
                                                            command=lambda key=check_buttons[addrl]: set_cb_values(key))
            if check_button_all_var.get() is True:
                check_buttons[addrl]['checked'] = True
                check_buttons[addrl]['widget'].select()
            else:
                check_buttons[addrl]['checked'] = False
            check_buttons[addrl]['color'] = ""
            check_buttons[addrl]['canvas'] = tk.Canvas(cb_frame, width=20, height=28)
            check_buttons[addrl]['indicator'] = check_buttons[addrl]['canvas'].create_oval(10, 10, 20, 20,
                                                                                           fill=check_buttons[addrl][
                                                                                               'color'])
        check_buttons[addrl]['widget'].grid(column=0, row=row)
        check_buttons[addrl]['canvas'].grid(column=1, row=row)

    cb_frame.grid(column=0, row=1)

    window.mainloop()


def handle_client(conn, addr):
    # display client address
    print("NEW CONNECTION: ", addr[0])
    connections[addr] = conn

    while True:
        try:
            # receave message from client
            sig = conn.recv(64).decode()
            if sig == "k":
                check_buttons[addr]['color'] = "yellow"
                check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                         fill=check_buttons[addr]['color'])
                print(str(addr) + ": " + "got the message")
            elif sig == "ROGER":
                check_buttons[addr]['color'] = "green"
                check_buttons[addr]['canvas'].itemconfig(check_buttons[addr]['indicator'],
                                                         fill=check_buttons[addr]['color'])
                print(str(addr) + ": " + "read the message")
        except Exception as e:
            print(addr, ":", e)
            # disconnect the server
            conn.close()
            del connections[addr]

            window.after(0, gui)
            # kill thread
            sys.exit()


def start_server():
    print("STARTING SERVER: ", HOST, PORT)
    # allow maximum 3 connections to the socket 
    s.listen(4)
    while True:
        # wait till a client accept connection 
        conn, addr = s.accept()
        # create a thread to handle each connection 
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

        # show thread count(connections) subtract master thread
        # print("ACTIVE THREADS: ", threading.activeCount())

        window.after(0, gui)


def read_client_list():
    try:
        with open("client_list.txt", "r") as f:
            for client in f.readlines():
                client_list.append(client.strip().split(" = "))
    except FileNotFoundError:
        print("File client_list.txt not found!")


if __name__ == "__main__":
    read_client_list()
    gui(True)
