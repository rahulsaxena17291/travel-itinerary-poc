from flask import Flask, request, jsonify, render_template
import os
from openai import OpenAI
from dotenv import load_dotenv
import markdown  # pip install markdown

# Load environment variables
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("❌ OPENAI_API_KEY not found in .env file.")

print(f"✅ OPENAI_API_KEY loaded: {api_key[:8]}...")

# Initialize Flask and OpenAI Client
app = Flask(__name__)
client = OpenAI(api_key=api_key)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/generate_itinerary", methods=["POST"])
def generate_itinerary():
    try:
        data = request.json
        departure = data.get("departure")
        destination = data.get("destination")
        start_date = data.get("start_date")
        end_date = data.get("end_date")

        if not departure or not destination or not start_date or not end_date:
            return jsonify({"error": "Please provide departure, destination, start_date, and end_date"}), 400

        # 🧠 Prompt with departure info included
        prompt = f"""
        Create a detailed travel itinerary for a trip from {departure} to {destination} 
        from {start_date} to {end_date}.
        Include:
        - Flight options (with airlines, timings, approximate duration)
        - Hotel options (with images and ratings)
        - Sightseeing & activities (with images)
        - Optional dining recommendations
        Format it using Markdown with headings (#, ##, ###), images (with real image URLs if possible), 
        bullet points, and short descriptive paragraphs.
        """

        # ✅ New style OpenAI call
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": prompt}]
        )

        itinerary_markdown = response.choices[0].message.content.strip()
        itinerary_html = markdown.markdown(itinerary_markdown, extensions=["extra"])

        return jsonify({"itinerary": itinerary_html})

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    app.run(debug=True)
