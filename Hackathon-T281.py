import os
import json
import csv
from tkinter import *
from tkinter import messagebox, simpledialog, filedialog, ttk
from datetime import datetime
import webbrowser

users = {}
login_timestamps = {}
applications = []
feedback_list = []
user_messages = {}

try:
    with open("users.json", "r") as f:
        users = json.load(f)
except FileNotFoundError:
    pass

try:
    with open("timestamps.json", "r") as f:
        login_timestamps = json.load(f)
except FileNotFoundError:
    pass

def save_users():
    with open("users.json", "w") as f:
        json.dump(users, f)

def save_timestamps():
    with open("timestamps.json", "w") as f:
        json.dump(login_timestamps, f)

root = Tk()
root.title("AYUSH Portal")
root.geometry("700x600")
root.configure(bg="#e0f2f1")
main_frame = Frame(root, bg="#e0f2f1")
main_frame.pack(expand=True)

def reset_main():
    for widget in main_frame.winfo_children():
        widget.destroy()

def styled_label(text, size=14, fg="#004d40"):
    return Label(main_frame, text=text, font=("Segoe UI", size, "bold"), fg=fg, bg="#e0f2f1")

def styled_button(text, command):
    return Button(main_frame, text=text, font=("Segoe UI", 12), width=30, bg="#00796b", fg="white", command=command)

def heading_label(text):
    return Label(main_frame, text=text, font=("Segoe UI", 18, "bold"), bg="#b2dfdb", fg="#004d40", pady=10)

def role_selection_screen():
    reset_main()
    heading_label("Select Your Role").pack(fill=X)

    role_var = StringVar()
    role_dropdown = ttk.Combobox(main_frame, textvariable=role_var, font=("Segoe UI", 12), width=30, state="readonly")
    role_dropdown['values'] = ("", "Admin", "User")
    role_dropdown.current(0)
    role_dropdown.pack(pady=20)

    def continue_action():
        role = role_var.get()
        if role in ["Admin", "User"]:
            login_screen(role)
        else:
            messagebox.showwarning("Input Error", "Please select a role.")

    styled_button("Continue", continue_action).pack(pady=10)
    styled_button("Exit", root.quit).pack(pady=5)

def login_screen(role):
    reset_main()
    heading_label(f"{role} Login").pack(fill=X)

    username_entry = Entry(main_frame, width=35)
    password_entry = Entry(main_frame, width=35, show="*")
    show_pw = BooleanVar()

    Label(main_frame, text="Username", bg="#e0f2f1", font=("Segoe UI", 12)).pack()
    username_entry.pack()
    Label(main_frame, text="Password", bg="#e0f2f1", font=("Segoe UI", 12)).pack()
    password_entry.pack()
    Checkbutton(main_frame, text="Show Password", variable=show_pw, command=lambda: password_entry.config(show="" if show_pw.get() else "*"), bg="#e0f2f1").pack()

    def login():
        username = username_entry.get()
        password = password_entry.get()
        if users.get(username) == password:
            if role != "Admin":
                login_timestamps[username] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                save_timestamps()
            if role == "Admin":
                admin_dashboard()
            else:
                user_dashboard(username)
        else:
            messagebox.showerror("Login Failed", "Invalid username or password.")

    def register():
        username = username_entry.get()
        password = password_entry.get()
        if username in users:
            messagebox.showerror("Error", "Username already exists.")
        elif not username or not password:
            messagebox.showerror("Error", "Both fields are required.")
        else:
            users[username] = password
            save_users()
            messagebox.showinfo("Success", "Registration successful!")
            login_screen(role)

    styled_button("Login", login).pack(pady=5)
    styled_button("Register", register).pack(pady=5)
    styled_button("Back", role_selection_screen).pack(pady=10)

def user_dashboard(username):
    reset_main()
    heading_label("User Dashboard").pack(fill=X)

    Label(main_frame, text=f"Welcome, {username}", font=("Segoe UI", 12), bg="#e0f2f1").pack(pady=5)

    def show_messages():
        msgs = user_messages.get(username, [])
        if not msgs:
            messagebox.showinfo("Messages", "No new messages.")
        else:
            msg = "\n".join([f"From Admin: {m}" for m in msgs])
            messagebox.showinfo("Messages", msg)
            user_messages[username] = []

    def show_resources():
        reset_main()
        heading_label("Resources & Updates").pack(fill=X)
        updates = [
            "• AYUSH Startups now eligible for ₹50L grant!",
            "• New incubation centers announced in Delhi & Pune",
            "• Ministry webinar on traditional medicine on April 15"
        ]
        for u in updates:
            Label(main_frame, text=u, bg="#e0f2f1", font=("Segoe UI", 11)).pack(anchor="w", padx=20)
        styled_button("Back", lambda: user_dashboard(username)).pack(pady=10)

    def submit_application():
        reset_main()
        heading_label("Submit Application").pack(fill=X)

        startup_name = Entry(main_frame, width=40)
        description = Entry(main_frame, width=40)
        file_path = StringVar()

        styled_label("Startup Name").pack()
        startup_name.pack()

        styled_label("Description").pack()
        description.pack()

        styled_label("Selected Document Path").pack()
        path_entry = Entry(main_frame, textvariable=file_path, font=("Segoe UI", 10), state="readonly", width=50)
        path_entry.pack(pady=5)

        def choose_file():
            path = filedialog.askopenfilename()
            if path:
                file_path.set(path)

        styled_button("Choose File", choose_file).pack(pady=5)

        def submit():
            app = {
                "user": username,
                "startup_name": startup_name.get(),
                "description": description.get(),
                "document": file_path.get(),
                "status": "Pending",
                "feedback": ""
            }
            applications.append(app)
            messagebox.showinfo("Submitted", "Application submitted successfully!")
            user_dashboard(username)

        styled_button("Submit", submit).pack(pady=10)
        styled_button("Back", lambda: user_dashboard(username)).pack(pady=10)

    def track_status():
        reset_main()
        heading_label("My Applications").pack(fill=X)
        user_apps = [app for app in applications if app['user'] == username]
        if not user_apps:
            Label(main_frame, text="No applications found.", bg="#e0f2f1").pack()
        else:
            for app in user_apps:
                Label(main_frame, text=f"Startup: {app['startup_name']}\nStatus: {app['status']}\nFeedback: {app['feedback']}", bg="#e0f2f1", justify=LEFT).pack(pady=5)
        styled_button("Back", lambda: user_dashboard(username)).pack(pady=10)

    styled_button("Messages from Admin", show_messages).pack(pady=3)
    styled_button("Submit Application", submit_application).pack(pady=3)
    styled_button("Track My Applications", track_status).pack(pady=3)
    styled_button("Resources", show_resources).pack(pady=3)
    styled_button("Logout", role_selection_screen).pack(pady=10)

def admin_dashboard():
    reset_main()
    heading_label("Admin Dashboard").pack(fill=X)

    def review_apps():
        reset_main()
        heading_label("Review Applications").pack(fill=X)

        pending_apps = [app for app in applications if app['status'] == "Pending"]
        if not pending_apps:
            Label(main_frame, text="No pending applications.", bg="#e0f2f1").pack()
            styled_button("Back", admin_dashboard).pack(pady=10)
            return

        selected = StringVar()
        combo = ttk.Combobox(main_frame, textvariable=selected, width=50, state="readonly")
        combo['values'] = [f"{app['user']} - {app['startup_name']}" for app in pending_apps]
        combo.pack(pady=10)

        def review_selected():
            index = combo.current()
            if index == -1:
                messagebox.showwarning("Select", "Please select an application")
                return
            app = pending_apps[index]

            def open_document():
                try:
                    if os.path.exists(app['document']):
                        os.startfile(app['document'])
                    else:
                        messagebox.showerror("Error", "File not found.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

            reset_main()
            heading_label("Application Review").pack(fill=X)
            Label(main_frame, text=f"User: {app['user']}\nStartup: {app['startup_name']}\nDesc: {app['description']}\nFile: {app['document']}", bg="#e0f2f1").pack(pady=5)
            styled_button("Open Document", open_document).pack(pady=5)

            def approve():
                feedback = simpledialog.askstring("Feedback", "Enter feedback:")
                app['status'] = 'Approved'
                app['feedback'] = feedback or "Approved"
                admin_dashboard()

            def reject():
                feedback = simpledialog.askstring("Rejection Reason", "Enter rejection reason:")
                app['status'] = 'Rejected'
                app['feedback'] = feedback or "Rejected"
                admin_dashboard()

            styled_button("Approve", approve).pack(pady=3)
            styled_button("Reject", reject).pack(pady=3)
            styled_button("Back", review_apps).pack(pady=10)

        styled_button("Review Selected Application", review_selected).pack(pady=5)
        styled_button("Back", admin_dashboard).pack(pady=10)

    def view_all_apps():
        reset_main()
        heading_label("All Applications").pack(fill=X)
        if not applications:
            Label(main_frame, text="No applications found.", bg="#e0f2f1").pack()
        else:
            for app in applications:
                Label(main_frame, text=f"User: {app['user']}\nStartup: {app['startup_name']}\nStatus: {app['status']}\nFeedback: {app['feedback']}", bg="#e0f2f1", justify=LEFT).pack(pady=5)
        styled_button("Back", admin_dashboard).pack(pady=10)

    def view_users():
        reset_main()
        heading_label("User Logins").pack(fill=X)
        for user, ts in login_timestamps.items():
            Label(main_frame, text=f"{user} logged in at {ts}", bg="#e0f2f1").pack(anchor="w", padx=20)
        styled_button("Back", admin_dashboard).pack(pady=10)

    def export_to_csv():
        with open("applications.csv", "w", newline='') as file:
            writer = csv.DictWriter(file, fieldnames=["user", "startup_name", "description", "document", "status", "feedback"])
            writer.writeheader()
            writer.writerows(applications)
        messagebox.showinfo("Exported", "Applications exported to applications.csv")

    def send_message():
        usernames = [u for u in users if u != "Admin"]
        if not usernames:
            messagebox.showinfo("Info", "No users to message.")
            return
        selected_user = simpledialog.askstring("Send Message", "Enter username to message:")
        if selected_user not in users:
            messagebox.showerror("Error", "User not found.")
            return
        msg = simpledialog.askstring("Message", f"Enter message for {selected_user}:")
        if selected_user not in user_messages:
            user_messages[selected_user] = []
        user_messages[selected_user].append(msg)
        messagebox.showinfo("Sent", "Message sent successfully.")

    styled_button("Review Applications", review_apps).pack(pady=3)
    styled_button("View All Applications", view_all_apps).pack(pady=3)
    styled_button("View Users & Timestamps", view_users).pack(pady=3)
    styled_button("Send Message to User", send_message).pack(pady=3)
    styled_button("Export Applications", export_to_csv).pack(pady=3)
    styled_button("Logout", role_selection_screen).pack(pady=10)

role_selection_screen()
root.mainloop()