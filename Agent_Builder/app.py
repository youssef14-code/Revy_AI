# run_agent.py
from flask import Flask
from models.models import db, User
from Agent_Builder.create_agent import RevyAgent

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///revy.db"  # ← غيّر لو عندك URI تاني
db.init_app(app)

if __name__ == "__main__":
    with app.app_context():
        db.create_all()

        user = User.query.first()
        if not user:
            user = User(name="Terminal User")
            db.session.add(user)
            db.session.commit()

        agent = RevyAgent(user)
        print("🤖 RevyAI Agent is running. Type 'exit' to quit.\n")

        while True:
            msg = input("You: ")
            if msg.lower() == "exit":
                break

            reply = agent.chat(msg)
            print(f"RevyAI: {reply}\n")