from tkinter import *

master = Tk()

entry = Entry(master)
entry.pack()

def process(data):
    print("processing: {0}".format(data))

def stdin_callback(fd, mask):
    print("stdin")
    data = sys.stdin.readline()
    process(data[:-1])

def socket_callback(fd, mask):
    print("socket")
    try:
        data= sock.recv(1024)
        if data:
            process (data)
        else:
            close_socket ()
    except socket.error as ex:
        close_socket ()

def close_socket():
    #closing socket without removing filehandler may hurt
    sock.close()
    master.deletefilehandler(fileno)

def entry_callback(event):
    print("entry")
    process(event.widget.get())

entry.bind("<Return>", entry_callback)
#master.createfilehandler(sys.stdin,READABLE, stdin_callback)

print(dir(tkinter))
#master.eval("set sock [socket -async google.com 80]")
#sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
#sock.connect(("localhost", 5678))
#fileno = sock.fileno()
#master.createfilehandler(fileno, READABLE, socket_callback)

master.mainloop()
