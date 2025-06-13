from flask import Flask
from handlers import register_blueprints
from test import test_bp

app = Flask(__name__)
register_blueprints(app)
app.register_blueprint(test_bp)


@app.route("/")
def home():
    return "🟢 Сервер работает"


if __name__ == "__main__":
    app.run(debug=True)
