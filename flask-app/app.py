from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)

# Display the form
@app.route("/")
def home():
    return render_template("form.html")

# Handle form submission
@app.route("/submit", methods=["POST"])
def submit():
    try:
        name = request.form.get("name")
        email = request.form.get("email")

        if not name or not email:
            return "Name and Email are required!", 400

        # Save to SQLite database
        conn = sqlite3.connect("data.db")
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
        conn.commit()
        conn.close()

        return f"Thank you, {name}! Your details have been saved."

    except Exception as e:
        return f"An error occurred: {str(e)}", 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
