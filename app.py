from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv
from google import genai
from google.genai import types
import os

# --------------------------------------------------
# Load .env file
# --------------------------------------------------
load_dotenv()

app = Flask(__name__)

# --------------------------------------------------
# Gemini API Key
# --------------------------------------------------
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError(
        "GEMINI_API_KEY not found. Please add it to your .env file."
    )

# --------------------------------------------------
# Gemini Client
# --------------------------------------------------
client = genai.Client(api_key=API_KEY)

# Current stable Gemini Flash model
MODEL_NAME = "gemini-3.1-flash-lite"


# --------------------------------------------------
# Domain restriction
# --------------------------------------------------
SYSTEM_INSTRUCTION = """
You are "Job & Career Assistant", a helpful career guidance chatbot.

Your ONLY domain is JOBS AND CAREERS.

You can answer questions about:

- Job search
- Career guidance
- Resume / CV
- Cover letters
- Interview preparation
- Interview questions
- HR interviews
- Technical interviews
- Skills development
- Soft skills
- Communication skills
- Internships
- Fresher jobs
- Career paths
- Job roles
- LinkedIn and professional profiles
- Salary discussions
- Job applications
- Workplace skills
- Professional growth
- Career switching
- Higher studies related to career
- Certifications related to jobs
- General employment advice

If the user asks something unrelated to jobs or careers,
politely say:

"Sorry, I can only help with jobs and career-related questions."

Do NOT answer unrelated questions about:
- Politics
- Entertainment
- Movies
- Sports
- Cooking
- General coding
- General mathematics
- General science
- Personal medical advice
- Other unrelated topics

If a question is partly related to career, answer only the
career-related part.

Keep answers simple, useful, and beginner-friendly.

If the user is a fresher, explain things in an easy way.

Never claim that you can guarantee a job.

Do not invent job openings, companies, salaries, or statistics.
"""


# --------------------------------------------------
# Home page
# --------------------------------------------------
@app.route("/")
def home():
    return render_template("index.html")


# --------------------------------------------------
# Chat API
# --------------------------------------------------
@app.route("/chat", methods=["POST"])
def chat():

    try:
        # Get JSON data
        data = request.get_json()

        if not data:
            return jsonify({
                "reply": "Please enter a message."
            }), 400

        user_message = data.get("message", "").strip()

        # Empty message
        if not user_message:
            return jsonify({
                "reply": "Please type a question."
            }), 400

        # Basic message length protection
        if len(user_message) > 2000:
            return jsonify({
                "reply": "Please keep your question under 2000 characters."
            }), 400

        # --------------------------------------------------
        # Send request to Gemini
        # --------------------------------------------------
        response = client.models.generate_content(
            model=MODEL_NAME,
            contents=user_message,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.7,
                max_output_tokens=500
            )
        )

        # Get Gemini response
        reply = response.text

        if not reply:
            reply = "Sorry, I could not generate a response. Please try again."

        return jsonify({
            "reply": reply
        })


    # --------------------------------------------------
    # API / Gemini errors
    # --------------------------------------------------
    except Exception as e:

        error_message = str(e)

        print("Gemini Error:", error_message)

        # 503 - Model temporarily busy
        if "503" in error_message or "UNAVAILABLE" in error_message:
            return jsonify({
                "reply": (
                    "Sorry, Gemini is temporarily busy. "
                    "Please wait a few seconds and try again."
                )
            }), 503

        # 429 - Too many requests / quota
        elif "429" in error_message or "RESOURCE_EXHAUSTED" in error_message:
            return jsonify({
                "reply": (
                    "The Gemini API request limit has been reached. "
                    "Please try again later."
                )
            }), 429

        # 401 / 403 - API key problem
        elif (
            "401" in error_message
            or "403" in error_message
            or "API key" in error_message
            or "PERMISSION_DENIED" in error_message
        ):
            return jsonify({
                "reply": (
                    "There is a problem with the Gemini API key. "
                    "Please check your .env file."
                )
            }), 500

        # Other errors
        else:
            return jsonify({
                "reply": (
                    "Sorry, something went wrong while connecting "
                    "to the AI. Please try again."
                )
            }), 500


# --------------------------------------------------
# Run Flask application
# --------------------------------------------------
if __name__ == "__main__":
    app.run(debug=True)