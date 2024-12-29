from flask import Flask, render_template, jsonify
import subprocess
import json
from datetime import datetime
from pymongo import MongoClient

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")  
db = client["twitter_trends"]
collection = db["trending_topics"]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run-script')
def run_script():
    result = subprocess.run(['python', 'selenium_script.py'], capture_output=True, text=True)
    
    latest_record = collection.find_one(sort=[('_id', -1)])
    
    if latest_record:
        trends = latest_record['trends']
        timestamp = latest_record['timestamp']
        unique_id = latest_record['unique_id']
        ip_address = latest_record.get('ip_address', 'N/A')
    else:
        trends = []
        timestamp = "No data"
        unique_id = "N/A"
        ip_address = "N/A"

    trends_str = "\n".join([f"- {trend}" for trend in trends[:5]])
    timestamp_str = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else "N/A"

    json_data = json.dumps(latest_record, default=str)

    return render_template('index.html', 
                           trends=trends_str, 
                           timestamp=timestamp_str, 
                           ip_address=ip_address,
                           json_data=json_data)

if __name__ == '__main__':
    app.run(debug=True)
