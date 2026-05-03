from flask import Flask, render_template, redirect, request,session, url_for,flash
from werkzeug.security import generate_password_hash,check_password_hash
from database import add_user_to_db,login_user_from_db,save_password_to_db, load_passwords_from_db
app = Flask(__name__)
app.secret_key = "mysecret"

def load_common_passwords():
    common_passwords = set()
    with open("rockyou_utf8.txt", "r", encoding="utf-8", errors="ignore") as file:
        for line in file:
            common_passwords.add(line.strip().lower())

    return common_passwords


COMMON_PASSWORDS = load_common_passwords()
print("Loaded common passwords:", len(COMMON_PASSWORDS))

def is_common_password(password):
    return password.lower() in COMMON_PASSWORDS


def check_password_strength(password):
    
    length = len(password)
    has_upper = False
    has_lower = False
    has_digit = False
    has_special = False

    special_chars = "@#$%_-!/"

    for ch in password:
        if ch.isupper():
            has_upper = True
        elif ch.islower():
            has_lower = True
        elif ch.isdigit():
            has_digit = True
        elif ch in special_chars:
            has_special = True

    if is_common_password(password):
        strength = "Weak❌"
        suggestion = (
                    "This password is commonly used and has appeared in data breaches. "
                    "Please choose a more unique password."
        )

    elif length >= 8 and has_upper and has_lower and has_digit and has_special:
        strength = "Strong✅"
        suggestion = (
            "Great choice! Your password meets all security requirements. "
            "It includes uppercase and lowercase letters, numbers, and special characters, "
            "making it highly secure and difficult to guess."
        )

    elif length >= 6 and has_lower and has_digit:
        strength = "Medium⚠️"
        suggestion = (
            "Your password provides basic security but can be improved. "
            "To make it stronger, add at least one uppercase letter and one special character "
            "such as @, #, or $. Your password must contain atleast 8 characters"
        )

    else:
        strength = "Weak❌"
        suggestion = (
            "Your password is weak and easy to guess. "
            "For better security, use a longer password that includes a combination of "
            "uppercase letters, lowercase letters, numbers, and special characters."
        )

    return strength, suggestion


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        password = request.form.get("password")

        if not password:
            return render_template("home.html", error="Password cannot be empty")

        strength, suggestion = check_password_strength(password)

        return render_template(
            "home.html",
            strength=strength,
            suggestion=suggestion
        )
    return render_template("home.html")


@app.route("/save")
def save():
    user_id = session.get("user_id")

    if user_id is None:
        return redirect(url_for("login"))
    
    passwords = load_passwords_from_db(user_id)
    return render_template('save.html', passwords = passwords)


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "GET":
        return render_template("login.html")

    email = request.form.get("email")
    password = request.form.get("passwords")

    result = login_user_from_db(email)

    if not result:
        flash("User not found. Please go to Sign Up.", "error")
        return redirect(url_for("login"))

    if not check_password_hash(result.passwords, password):
        flash("Incorrect password. Try again.", "error")
        return redirect(url_for("login"))

    session["user_id"] = result.id
    session["email"] = result.email


    flash("Login successful!", "success")
    return redirect(url_for("home"))

@app.route("/signup", methods=["GET", "POST"])
def signup():

    if request.method == "POST":
        hashed_password = generate_password_hash(
            request.form.get("passwords")
        )

        form_data = {
            "email": request.form.get("email"),
            "passwords": hashed_password
        }

        try:
            add_user_to_db(form_data)
            flash("Signup successful! Please login.", "success")
            return redirect(url_for("login"))

        except Exception as e:
            print("Signup error:", e)
            flash("Email already registered", "error")
            return redirect(url_for("signup"))

    return render_template("signup.html")



@app.route("/save-password", methods=["GET", "POST"])
def save_password():

    if "user_id" not in session:
        flash("Please login first", "error")
        return redirect(url_for("login"))

    if request.method == "POST":
        pass_name = request.form.get("password_name")
        raw_password = request.form.get("password_value")

        print("USER ID:", session.get("user_id"))
        print("PASS NAME:", pass_name)
        print("RAW PASSWORD:", raw_password)


        if not pass_name or not raw_password:
            flash("All fields are required", "error")
            return redirect(url_for("save_password"))

        try:
            save_password_to_db(
                session["user_id"],
                pass_name,
                raw_password
            )
            flash("Password saved securely!", "success")
            return redirect(url_for("home"))

        except Exception as e:
            print("DB ERROR:", e)
            flash("Failed to save password", "error")
            return redirect(url_for("save_password"))

    return render_template("save_password.html")