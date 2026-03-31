import os
from flask import Flask, request, jsonify, redirect
from db import init_db, create_short_url, get_long_url, increment_clicks, get_url_stats, get_all_urls

app = Flask(__name__)

BASE_URL = os.getenv("BASE_URL", "http://127.0.0.1:5000")


@app.route("/")
def home():
    return "URL Shortener Backend is running!"


@app.route("/shorten", methods=["POST"])
def shorten_url():
    data = request.get_json()

    if not data or "long_url" not in data:
        return jsonify({"error": "long_url is required"}), 400

    long_url = data["long_url"].strip()

    if not long_url.startswith("http://") and not long_url.startswith("https://"):
        return jsonify({"error": "URL must start with http:// or https://"}), 400

    short_code = create_short_url(long_url)
    short_url = f"{BASE_URL}/{short_code}"

    return jsonify({
        "short_code": short_code,
        "short_url": short_url,
        "long_url": long_url
    })


@app.route("/<short_code>")
def redirect_to_long_url(short_code):
    long_url = get_long_url(short_code)

    if not long_url:
        return "Short URL not found", 404

    increment_clicks(short_code)
    return redirect(long_url)


@app.route("/stats/<short_code>")
def stats(short_code):
    row = get_url_stats(short_code)

    if not row:
        return jsonify({"error": "Short code not found"}), 404

    return jsonify({
        "short_code": row["short_code"],
        "long_url": row["long_url"],
        "clicks": row["clicks"],
        "created_at": row["created_at"]
    })


@app.route("/all")
def all_urls():
    rows = get_all_urls()

    result = []
    for row in rows:
        result.append({
            "short_code": row["short_code"],
            "short_url": f"{BASE_URL}/{row['short_code']}",
            "long_url": row["long_url"],
            "clicks": row["clicks"],
            "created_at": row["created_at"]
        })

    return jsonify(result)


if __name__ == "__main__":
    init_db()
    port = int(os.getenv("PORT", 5000))
    app.run(host="0.0.0.0", port=port)