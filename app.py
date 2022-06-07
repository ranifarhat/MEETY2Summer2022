from flask import Flask, render_template, request, redirect, url_for, flash
from flask import session as login_session
import pyrebase, time

fbconfig = {
  "apiKey": "AIzaSyBhPIOR9vTcplgYIRYOTwzXSPrXLDnDgWY",
  "authDomain": "meety2taproj.firebaseapp.com",
  "projectId": "meety2taproj",
  "storageBucket": "meety2taproj.appspot.com",
  "messagingSenderId": "1750814656",
  "appId": "1:1750814656:web:863485c8b76231c14b0225",
  "measurementId": "G-HWVSHRX26B",
  "databaseURL": "https://meety2taproj-default-rtdb.europe-west1.firebasedatabase.app/"
}

# Initialize Firebase
fbapp = pyrebase.initialize_app(fbconfig);
fbauth = fbapp.auth()
db = fbapp.database()

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'gab867d'


@app.route('/', methods=['GET', 'POST'])
def landing():
    user_active = False

    # Posting on the website
    if request.method =="POST":
        content = request.form["post"]

        # Check to make sure the user is signed in
        try:

            # Check to make sure the post isn't empty
            if len(content) > 1:
                post = {"posterID": login_session["user"]["localId"], "poster": db.child("Users").child(login_session["user"]["localId"]).get().val()["uname"], "content": content}
                db.child("Posts").push(post)
                return redirect(url_for("landing"))
            else:
                postlenerror = "Post can't be empty"
                user_active = True
                return render_template("landing.html", user_active = user_active, lenerror = postlenerror, user = db.child("Users").child(login_session["user"]["localId"]).get().val()["uname"], posts = list(db.child("Posts").get().val().values())[::-1])
        
        # If the user isn't signed in
        except:
            postaccerror = "Please log in or sign up to post"
            try:
                return render_template("landing.html", user_active = user_active, accerror = postaccerror, posts = list(db.child("Posts").get().val().values())[::-1])
            except:
                return render_template("landing.html", user_active = user_active, accerror = postaccerror, noposterror = "There is an issue where the posts don't show. Simply refresh the page, or sign up/log in to fix the issue.")

    # Rendering the actual page with the user info, posts, and so on
    else:
        try:
            posts = list(db.child("Posts").get().val().values())[::-1]
            # If signed in
            try:
                user_active = True
                return render_template("landing.html", user_active = user_active, user = db.child("Users").child(login_session["user"]["localId"]).get().val()["uname"], posts = posts)

            # If not signed in
            except:
                user_active = False
                return render_template("landing.html", user_active = user_active, posts = posts)
        except:
            user_active = False
            return render_template("landing.html", user_active = user_active, noposterror = "There is an issue where the posts don't show. Simply refresh the page, or sign up/log in to fix the issue.")

@app.route('/signup', methods=['GET', 'POST'])
def signup():

    # Sign up with name, username, email, password
    if request.method == "POST":
        name = request.form["name"]
        uname = request.form["uname"]
        email = request.form["email"]
        password = request.form["pword"]
        confpass = request.form["confpword"]

        # Make sure passwords matches confirmation, and that no fields are empty
        if password == confpass and name != "" and uname != "" and email != "" and password != "" and confpass != "":
            try:
                login_session["user"] = fbauth.create_user_with_email_and_password(email, password)
                user = {"name": name, "uname": uname, "email": email, "password": password}
                db.child("Users").child(login_session["user"]["localId"]).set(user)
                return redirect(url_for("landing"))
            
            # In case of error with Firebase
            except:
                error = "Sign up failed"
                return render_template("signup.html", error = error)
        else:
            passerror = "Passwords do not match or missing fields"
            return render_template("signup.html", passerror = passerror)

    return render_template("signup.html")

@app.route('/login', methods=['GET', 'POST'])
def login():

    # Login with email and password
    if request.method == "POST":
        email = request.form["email"]
        password = request.form["pword"]
        try:
            login_session["user"] = fbauth.sign_in_with_email_and_password(email, password)
            return redirect(url_for("landing"))
    
        # In case of error with Firebase
        except:
            error = "Login failed"
            return render_template("login.html", error = error)
    
    else:
        return render_template("login.html")

@app.route('/bye', methods=['GET', 'POST'])
def signout():

    # Signs out of current user and redirects to main page
    login_session["user"] = None
    fbauth.current_user = None
    return redirect(url_for("landing"))

# @app.route('/display', methods=['GET', 'POST'])
# def display():

#     # Debugging and making sure databases are working as they should

#     # user = db.child("Users").child(login_session["user"]["localId"]).get().val()["uname"]
#     # user = db.child("Users").child(login_session["user"]["localId"]).get().val()
#     user = ""
#     users = db.child("Users").get().val()
#     posts = list(db.child("Posts").get().val().values())[::-1]
#     return render_template("dbdisplay.html", users = users, curr_user = user, posts = posts)

if __name__ == '__main__':
    app.run(debug=True, port = 5050)