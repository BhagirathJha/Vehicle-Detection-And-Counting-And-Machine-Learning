from tkinter import *
from tkinter import ttk
from tkinter import messagebox
import sqlite3
from PIL import Image, ImageTk
import cv2
import pickle
import cvzone
import numpy as np
import tkinter as tk
from tkinter import ttk
from threading import Thread
from tkinter import messagebox
from PIL import Image, ImageTk

# Load video feed
cap = cv2.VideoCapture('carPark.mp4')
is_processing = False  # Flag to control processing

# Load parking space positions from a pickle file
with open('CarParkPos', 'rb') as f:
    posList = pickle.load(f)

# Load the balloon image with an alpha channel
balloon_img = cv2.imread('balloon.png', cv2.IMREAD_UNCHANGED)

# Dimensions of each parking space
width, height = 107, 48

def checkParkingSpace(img, imgPro):
    spaceCounter = 0

    for pos in posList:
        x, y = pos

        imgCrop = imgPro[y:y + height, x:x + width]
        count = cv2.countNonZero(imgCrop)

        if count < 900:
            color = (0, 255, 0)
            thickness = 5
            spaceCounter += 1

            # Overlay the balloon image on empty parking spaces
            balloon_resized = cv2.resize(balloon_img, (width, height))
            mask = balloon_resized[:, :, 3] / 255  # Extract the alpha channel
            img[y:y + height, x:x + width] = \
                (1 - mask)[:, :, np.newaxis] * img[y:y + height, x:x + width] + \
                mask[:, :, np.newaxis] * balloon_resized[:, :, :3]

        else:
            color = (0, 0, 255)
            thickness = 2

        cv2.rectangle(img, pos, (pos[0] + width, pos[1] + height), color, thickness)
        cvzone.putTextRect(img, str(count), (x, y + height - 3), scale=0,
                           thickness=2, offset=0, colorR=color)

    cvzone.putTextRect(img, f'Free: {spaceCounter}/{len(posList)}', (0, 50), scale=3,
                       thickness=5, offset=20, colorR=(0, 0, 0))
    if spaceCounter > 0:
        cvzone.putTextRect(img, f'There : {spaceCounter} Free lines', (390, 50), scale=4,
                           thickness=5, offset=20, colorR=(0, 0, 0))

processing_thread = None

def start_processing():
    global is_processing, processing_thread, cap
    if not is_processing:
        is_processing = True
        if cap.isOpened():  # Release the current video capture
            cap.release()
        cap = cv2.VideoCapture('carPark.mp4')  # Reopen the video capture
        processing_thread = Thread(target=process_video)
        processing_thread.start()

def stop_processing():
    global is_processing, processing_thread, cap
    is_processing = False
    if processing_thread:
        processing_thread.join()  # Wait for the thread to complete
        processing_thread = None
    if cap.isOpened():  # Release the video capture
        cap.release()

def confirm_exit():
    result = messagebox.askyesno("Exit Confirmation", "Are you sure you want to exit?")
    if result:
        stop_processing()
        root.destroy()

def process_video():
    while is_processing:
        success, img = cap.read()
        if success:
            imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            imgBlur = cv2.GaussianBlur(imgGray, (3, 3), 1)
            imgThreshold = cv2.adaptiveThreshold(imgBlur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                                 cv2.THRESH_BINARY_INV, 25, 16)
            imgMedian = cv2.medianBlur(imgThreshold, 5)
            kernel = np.ones((3, 3), np.uint8)
            imgDilate = cv2.dilate(imgMedian, kernel, iterations=1)
            checkParkingSpace(img, imgDilate)  # Pass the img variable to the function
            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
            cv2.imshow("Parking Space Detection", img)
            cv2.waitKey(10)
        else:
            break

def main():
    global root
    root = tk.Tk()
    root.geometry("1900x900")
    root.title("Parking Space Detection")
    

# Get the screen width and height
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()


# Load the background image
    background_image = Image.open(r'Images/carParkImg.png')

# Resize the image to fit the screen
    background_image = background_image.resize((screen_width, screen_height), Image.ANTIALIAS)

# Create a PhotoImage object from the resized image
    background_image = ImageTk.PhotoImage(background_image)

# Create a label to display the background image
    background_label = tk.Label(root, image=background_image)
    background_label.place(x=0, y=0, relwidth=1, relheight=1)

def create_database_and_table():
    # Create a new SQLite database and a 'register' table if they don't exist.
    conn = sqlite3.connect('mydata.db')
    reg_cursor = conn.cursor()
    reg_cursor.execute('''
        CREATE TABLE IF NOT EXISTS register (
            first_name TEXT,
            last_name TEXT,
            contact_no TEXT,
            email TEXT PRIMARY KEY,
            securityQ TEXT,
            securityA TEXT,
            password TEXT
        )
    ''')
    conn.commit()
    conn.close()

class LoginWindow:
    # Existing code for the LoginWindow class
    def __init__(self, root):
        self.root = root
        self.root.title("Login")
        self.root.iconbitmap('Images/CAR.ico')
        self.root.geometry("1500x800+0+0")

        self.bg = ImageTk.PhotoImage(file="Images/CPP.jpg")
        lbl_bg = Label(self.root, image=self.bg, bg='black')
        lbl_bg.place(x=0, y=0, relheight=1, relwidth=1)

        self.bg1 = ImageTk.PhotoImage(file="Images/Login1.png")
        left_lbl = Label(self.root, image=self.bg1, width=470, height=550)
        left_lbl.place(x=250, y=150)
        
        frame = Frame(self.root, bg="black")
        frame.place(x=725, y=150, width=470, height=555)
        

        img1 = Image.open("Images/r.png")
        img1 = img1.resize((100, 100), Image.LANCZOS)
        self.photoimage1 = ImageTk.PhotoImage(img1)
        lblimg1 = Label(image=self.photoimage1, bg="black", borderwidth=0)
        lblimg1.place(x=910, y=175, width=100, height=100)

        get_str = Label(frame, text="Get Started", font=("times new roman", 20, "bold"), fg="white", bg="black")
        get_str.place(x=160, y=125)

        username = lbl = Label(frame, text="Username/Email", font=("times new roman", 15, "bold"), fg="white", bg="black")
        username.place(x=125, y=190)

        self.textuser = ttk.Entry(frame, font=("times new roman", 15, "bold"))
        self.textuser.place(x=100, y=225, width=270)

        password = lbl = Label(frame, text="Password", font=("times new roman", 15, "bold"), fg="white", bg="black")
        password.place(x=125, y=265)

        self.textpass = ttk.Entry(frame, font=("times new roman", 15, "bold"), show="*")
        self.textpass.place(x=100, y=300, width=270)

        img2 = Image.open("Images/r.png")
        img2 = img2.resize((25, 25), Image.LANCZOS)
        self.photoimage2 = ImageTk.PhotoImage(img2)
        lblimg2 = Label(image=self.photoimage2, bg="black", borderwidth=0)
        lblimg2.place(x=825, y=345, width=25, height=25)

        img3 = Image.open("Images/lock.png")
        img3 = img3.resize((25, 25), Image.LANCZOS)
        self.photoimage3 = ImageTk.PhotoImage(img3)
        lblimg3 = Label(image=self.photoimage3, bg="black", borderwidth=0)
        lblimg3.place(x=825, y=420, width=25, height=25)

        loginbtn = Button(frame, command=self.login, text="Login", font=("times new roman", 15, "bold"), bd=5, relief=RIDGE,
                          bg="red", fg="white", activebackground="red", activeforeground="white")
        loginbtn.place(x=190, y=350, width=90, height=40)

        forgotbtn = Button(frame, command=self.forgot_password_window, text="Forget Password",
                           font=("times new roman", 12, "bold"), borderwidth=0, bg="black", fg="white",
                           activebackground="black", activeforeground="white")
        forgotbtn.place(x=15, y=410, width=160,)

        newregbtn = Button(frame, command=self.register_window, text="Creat New Account",
                           font=("times new roman", 12, "bold"), borderwidth=0, bg="black", fg="white",
                           activebackground="black", activeforeground="white")
        newregbtn.place(x=22, y=450, width=160,)

    def register_window(self):
        self.new_window = Toplevel(self.root)
        self.app = Register(self.new_window)

    def login(self):
        if self.textuser.get() == "" or self.textpass.get() == "":
            messagebox.showerror("Error", "All Fields are Required")
        else:
            conn = sqlite3.connect('mydata.db')
            reg_cursor = conn.cursor()
            reg_cursor.execute("select * from register where email=? and password=?", (
                self.textuser.get(),
                self.textpass.get()
            ))

            row = reg_cursor.fetchone()
            if row is None:
                messagebox.showerror("Error", "Invalid Username and Password.")
            else:
                open_main = messagebox.askyesno("Yes NO", "Access Only Admin")
                if open_main > 0:
                    self.new_window = Toplevel(self.root)
                    self.app = Home(self.new_window)
                else:
                    if not open_main:
                        return
            conn.commit()
            conn.close()

    def forgot_password_window(self):
        email = self.textuser.get()
        if email == "":
            messagebox.showerror("Error", "Please Enter the Email Address To Reset Password")
        else:
            conn = sqlite3.connect('mydata.db')
            reg_cursor = conn.cursor()
            query = "select * from register where email=?"
            value = (email,)
            reg_cursor.execute(query, value)
            row = reg_cursor.fetchone()

            if row is None:
                messagebox.showerror("Error", "Please Enter the Valid Username/Email name.")
            else:
                conn.close()
                self.root2 = Toplevel()
                self.root2.title("Forget Password")
                self.root2.iconbitmap('Images/CAR.ico')
                self.root2.geometry("340x450+610+170")

                fglbl = Label(self.root2, text="Forget Password", font=("times new roman", 18, "bold"), bg="black", fg="red")
                fglbl.place(x=0, y=10, relwidth=1)

                security_Q = Label(self.root2, text='Select Security Questions', font=('times new roman', 15, 'bold'),
                                   fg='black')
                security_Q.place(x=50, y=80)

                self.combo_securiy_Q = ttk.Combobox(self.root2, font=('times new roman', 13, 'bold'))
                self.combo_securiy_Q['state'] = 'readonly'
                self.combo_securiy_Q['values'] = ('Select Your Security Questions',
                                                 'What is your Birth date?',
                                                 'What is your Birth place?',
                                                 'What is your Girlfried name?',
                                                 'What is your Father name?',
                                                 'What is your Mother name?',
                                                 'What is your pet name?',
                                                 'What is your favrite game?',
                                                 )
                self.combo_securiy_Q.current(0)
                self.combo_securiy_Q.place(x=50, y=110, width=250)

                security_A = Label(self.root2, text='Security Answer', font=('times new roman', 15, 'bold'), fg='black')
                security_A.place(x=50, y=150)

                self.txt_security = ttk.Entry(self.root2, font=('times new roman', 15, 'bold'))
                self.txt_security.place(x=50, y=180, width=250)

                new_password = Label(self.root2, text='New Password', font=('times new roman', 15, 'bold'), fg='black')
                new_password.place(x=50, y=220)

                self.txt_newpass = ttk.Entry(self.root2, font=('times new roman', 15, 'bold'))
                self.txt_newpass.place(x=50, y=250, width=250)

                btn = Button(self.root2, command=self.reset_pass, text="Reset", font=("times new roman", 15, "bold"),
                             bd=5, fg="white", bg="green")
                btn.place(x=130, y=290)

    def reset_pass(self):
        if self.combo_securiy_Q.get() == "Select Your Security Questions":
            messagebox.showerror("Error", "Please Select Your Security Questions.", parent=self.root2)
        elif self.txt_security.get() == "":
            messagebox.showwarning("Warning", "Please Enter The Answer.", parent=self.root2)
        elif self.txt_newpass.get() == "":
            messagebox.showwarning("Warning", "Please Enter The New Password.", parent=self.root2)
        else:
            conn = sqlite3.connect('mydata.db')
            reg_cursor = conn.cursor()
            query = "select * from register where email=? and securityQ=? and securityA=?"
            value = (self.textuser.get(), self.combo_securiy_Q.get(), self.txt_security.get())
            reg_cursor.execute(query, value)
            row = reg_cursor.fetchone()
            if row is None:
                messagebox.showwarning("Warning", "Please Enter The Correct Answer.", parent=self.root2)
            else:
                query = "update register set password=? where email=?"
                value = (self.txt_newpass.get(), self.textuser.get())
                reg_cursor.execute(query, value)
                conn.commit()
                conn.close()
                messagebox.showinfo("Info", "Your Password has been reset Successfully,\nPlease Login with New Password.",
                                    parent=self.root2)
                self.root2.destroy() 
class Register:
    # Existing code for the Register class
    def __init__(self, root):
        self.root = root
        self.root.title("Register")
        self.root.iconbitmap('Images/CAR.ico')
        self.root.geometry("1500x800+0+0")

        self.var_fname = StringVar()
        self.var_lname = StringVar()
        self.var_contact = StringVar()
        self.var_email = StringVar()
        self.var_securityQ = StringVar()
        self.var_SecrityA = StringVar()
        self.var_pass = StringVar()
        self.var_confpass = StringVar()
        self.var_check = IntVar()

        self.bg = ImageTk.PhotoImage(file="Images/CPP.jpg")
        bg_lbl = Label(self.root, image=self.bg, bg='black')
        bg_lbl.place(x=0, y=0, relwidth=1, relheight=1)

        self.bg1 = ImageTk.PhotoImage(file="Images/Login1.png")
        left_lbl = Label(self.root, image=self.bg1, width=470, height=550)
        left_lbl.place(x=155, y=120)

        frame = Frame(self.root, bg="black", width=760, height=555)
        frame.place(x=630, y=120)
        

        register_lbl = Label(frame, text='REGISTER HERE', font=('ITC Motter Corpus Regular', 25, 'bold'), fg='#d90429', bg='black')
        register_lbl.place(x=220, y=20)

        fname = Label(frame, text='First Name', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        fname.place(x=80, y=80)
        fname_entry = ttk.Entry(frame, textvariable=self.var_fname, font=('times new roman', 15, 'bold'))
        fname_entry.place(x=80, y=110, width=250)

        lname = Label(frame, text='Last Name', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        lname.place(x=420, y=80)
        lname_entry = ttk.Entry(frame, textvariable=self.var_lname, font=('times new roman', 15, 'bold'))
        lname_entry.place(x=420, y=110, width=250)

        contact = Label(frame, text='Contact No.', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        contact.place(x=80, y=150)
        contact_entry = ttk.Entry(frame, textvariable=self.var_contact, font=('times new roman', 15, 'bold'))
        contact_entry.place(x=80, y=180, width=250)

        email = Label(frame, text='Email', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        email.place(x=420, y=150)
        email_entry = ttk.Entry(frame, textvariable=self.var_email, font=('times new roman', 15, 'bold'))
        email_entry.place(x=420, y=180, width=250)

        secur_que = Label(frame, text='Select Security Questions', font=('times new roman', 15, 'bold'), fg='white',
                          bg='black')
        secur_que.place(x=80, y=220)
        secur_que_entry = ttk.Combobox(frame, textvariable=self.var_securityQ, font=('times new roman', 13, 'bold'))
        secur_que_entry['state'] = 'readonly'
        secur_que_entry['values'] = ('Select Your Security Questions',
                                     'What is your Birth date?',
                                     'What is your Birth place?',
                                     'What is your Girlfried name?',
                                     'What is your Father name?',
                                     'What is your Mother name?',
                                     'What is your pet name?',
                                     'What is your favrite game?',
                                     )
        secur_que_entry.current(0)
        secur_que_entry.place(x=80, y=250, width=250)

        secure_ans = Label(frame, text='Security Answer', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        secure_ans.place(x=420, y=220)
        secure_ans_entry = ttk.Entry(frame, textvariable=self.var_SecrityA, font=('times new roman', 15, 'bold'))
        secure_ans_entry.place(x=420, y=250, width=250)

        passwd = Label(frame, text='Password', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        passwd.place(x=80, y=290)
        passwd_entry = ttk.Entry(frame, textvariable=self.var_pass, font=('times new roman', 15, 'bold'))
        passwd_entry.place(x=80, y=320, width=250)

        confirm_passwd = Label(frame, text='Confirm Password', font=('times new roman', 15, 'bold'), fg='white', bg='black')
        confirm_passwd.place(x=420, y=290)
        confirm_passwd_entry = ttk.Entry(frame, textvariable=self.var_confpass, font=('times new roman', 15, 'bold'))
        confirm_passwd_entry.place(x=420, y=320, width=250)

        checkbtn = Checkbutton(frame, variable=self.var_check, text="I Agree the Terms & Conditions", bg='black',
                               fg='blue', font=('times new roman', 13, 'bold'), onvalue=1, offvalue=0)
        checkbtn.place(x=80, y=360)

        img = Image.open("Images/Register1.png")
        img = img.resize((200, 50), Image.Resampling.LANCZOS)
        self.photoimage = ImageTk.PhotoImage(img)
        reg = Button(frame, command=self.register_data, image=self.photoimage, borderwidth=0, cursor='hand2', bg='black',
                     fg='black', font=('times new roman', 13, 'bold'))
        reg.place(x=90, y=400)

        img1 = Image.open("Images/login.png")
        img1 = img1.resize((150, 50), Image.Resampling.LANCZOS)
        self.photoimage1 = ImageTk.PhotoImage(img1)
        reg1 = Button(frame, command=self.login_window, image=self.photoimage1, borderwidth=0, cursor='hand2', bg='black',
                      fg='black', font=('times new roman', 13, 'bold'))
        reg1.place(x=420, y=400)

    def login_window(self):
        self.new_window = Toplevel(self.root)
        self.app = LoginWindow(self.new_window)

    def register_data(self):
        if self.var_fname.get() == "":
            messagebox.showerror("Required", "First Name is Required.")
        elif self.var_lname.get() == "":
            messagebox.showerror("Required", "Last Name is Required.")
        elif self.var_email.get() == "":
            messagebox.showerror("Required", "Email is Required.\nFor Example: username12@gmail.com")
        elif self.var_securityQ.get() == "Select Your Security Questions":
            messagebox.showerror("Error", "Select your Security Questions.")
        elif self.var_SecrityA.get() == "":
            messagebox.showerror("Required", "Security Answer is Required.")
        elif self.var_pass.get() == "":
            messagebox.showerror("Required", "Password is Required.")
        elif self.var_pass.get() != self.var_confpass.get():
            messagebox.showerror("Error", "Password and Confirm Password must be the same.")
        elif self.var_check.get() == 0:
            messagebox.showerror("Error", "Please agree to our Terms and Conditions.")
        else:
            conn = sqlite3.connect('mydata.db')
            reg_cursor = conn.cursor()
            query = "select * from register where email=?"
            value = (self.var_email.get(),)
            reg_cursor.execute(query, value)
            row = reg_cursor.fetchone()
            if row is not None:
                messagebox.showerror("Error", "User already exists, please try another email.")
            else:
                query = "insert into register values(?,?,?,?,?,?,?)"
                values = (self.var_fname.get(), self.var_lname.get(), self.var_contact.get(), self.var_email.get(),
                          self.var_securityQ.get(), self.var_SecrityA.get(), self.var_pass.get())
                reg_cursor.execute(query, values)
                conn.commit()
                conn.close()
                messagebox.showinfo("Success", "Registered Successfully.")

class Home:
    # Existing code for the Home class
    def __init__(self, root):
        self.root = root
        self.root.title("Home")
        self.root.iconbitmap('Images/CAR.ico')
        self.root.geometry("1500x800+0+0")

        self.bg = ImageTk.PhotoImage(file="Images/CP.png")
        lbl_bg = Label(self.root, image=self.bg)
        lbl_bg.place(x=0, y=0, relheight=1, relwidth=1)


        # Add a Start button
        start_button = Button(self.root, text="Start", font=("times new roman", 30, "bold"), bd=5, relief=RIDGE, bg="blue", fg="white", activebackground="blue", activeforeground="white", command=start_processing)
        start_button.place(x=350, y=400, width=240, height=60)

        # Add a Stop button
        stop_button = Button(self.root, text="Stop", font=("times new roman", 30, "bold"), bd=5, relief=RIDGE, bg="red", fg="white", activebackground="red", activeforeground="white", command=confirm_exit)
        stop_button.place(x=900, y=400, width=240, height=60)

    def start_function(self):
        # Add code for the Start button functionality here
        print("Start button clicked")

    def stop_function(self):
        # Add code for the Stop button functionality here
        print("Stop button clicked")
		
def main():
    create_database_and_table()  # Ensure the database and table are created before the main application
    win = Tk()
    app = LoginWindow(win)
    win.mainloop()

if __name__ == '__main__':
    main()
    
# Release the video feed and close all windows
cap.release()
cv2.destroyAllWindows()