from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user

app = Flask(__name__)
app.secret_key = 'supersecretkey'

login_manager = LoginManager()
login_manager.init_app(app)

class User(UserMixin):
    def __init__(self, id):
        self.id = id

users = {'admin': {'password': 'admin123'}}

@login_manager.user_loader
def load_user(user_id):
    return User(user_id)

@app.route('/')
def home():
    return render_template("form.html")

@app.route('/submit', methods=["POST"])
def submit():
    name = request.form["name"]
    phone = request.form["phone"]
    status = request.form["status"]
    reason = request.form["reason"] if status == "Absent" else ""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    df = pd.DataFrame([[timestamp, name, phone, status, reason]],
                      columns=["DateTime", "Name", "Phone", "Status", "Reason"])
    
    try:
        existing = pd.read_excel("static/attendance.xlsx")
        df = pd.concat([existing, df], ignore_index=True)
    except FileNotFoundError:
        pass

    df.to_excel("static/attendance.xlsx", index=False)

    return "Submitted successfully!"

@app.route('/admin', methods=["GET", "POST"])
def admin():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        if username in users and users[username]["password"] == password:
            user = User(username)
            login_user(user)
            return redirect(url_for("download"))
        return "Invalid credentials", 403
    return '''
        <form method="POST">
            <input name="username" required>
            <input name="password" type="password" required>
            <button type="submit">Login</button>
        </form>
    '''

@app.route('/download')
@login_required
def download():
    return '''
        <a href="/static/attendance.xlsx" download>Download Attendance Excel</a><br>
        <a href="/logout">Logout</a>
    '''

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
