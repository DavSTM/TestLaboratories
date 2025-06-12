from flask import Flask
from handlers.role_routes import role_bp

app = Flask(__name__)
app.register_blueprint(role_bp)

@app.route("/")
def home():
    return "🟢 Сервер работает"

if __name__ == "__main__":
    app.run(debug=True)
