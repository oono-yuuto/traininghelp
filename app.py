from flask import Flask, request, jsonify, render_template, send_from_directory
import pandas as pd
import re
import os

app = Flask(__name__, static_folder='static')

def load_data():
    df = pd.read_excel("トレ内容（改変済み）.xlsx")
    sheets = pd.read_excel("トレ内容（改変済み）.xlsx", sheet_name=None)


    difficulty_map = {
        "初級": "beginner",
        "中級": "intermediate",
        "上級": "advanced"
    }

    target_area_keywords = {
        "arms": [ "腕"],
        "chest": ["胸"],
        "back": ["背筋"],
        "abs": ["お腹"],
        "legs": ["足"],
        "shoulders": ["肩", "肩とれ"],
        "full-body": ["全身"]
    }

    def classify_duration(title):
        match = re.search(r"(\d+)\s*分", title)
        if match:
            minutes = int(match.group(1))
            if minutes <= 15:
                return "short"
            elif minutes <= 30:
                return "medium"
            else:
                return "long"
        return "all"

    def detect_target_area(title):
        for area, keywords in target_area_keywords.items():
            if any(kw in title for kw in keywords):
                return area
        return "full-body"

    df["difficulty"] = df["レベル"].map(difficulty_map).fillna("all")
    df["duration"] = df["タイトル"].apply(classify_duration)
    df["target_area"] = df["タイトル"].apply(detect_target_area)
    return df

# データをロード
df = load_data()

# トップページ：training.html を表示
@app.route("/")
def index():
    return render_template("training.html")

# 検索API：条件に合うトレーニングをJSONで返す
@app.route("/search", methods=["POST"])
def search():
    data = request.get_json()
    area = data.get("target_area", "all")
    difficulty = data.get("difficulty", "all")
    duration = data.get("duration", "all")

    result_df = df.copy()
    if area != "all":
        result_df = result_df[result_df["target_area"] == area]
    if difficulty != "all":
        result_df = result_df[result_df["difficulty"] == difficulty]
    if duration != "all":
        result_df = result_df[result_df["duration"] == duration]

    result = result_df[["タイトル", "URL", "difficulty", "duration", "target_area"]]
    return jsonify(result.to_dict(orient="records"))

# 静的ファイルの提供（style.css）
@app.route("/static/<path:filename>")
def static_files(filename):
    return send_from_directory("static", filename)

if __name__ == "__main__":
    app.run(debug=True)
