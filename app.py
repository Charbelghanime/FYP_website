from flask import Flask, render_template, send_file, request
from pymongo import MongoClient
from gridfs import GridFS
from bson import ObjectId

app = Flask(__name__, template_folder='/Templates')

# Connect to MongoDB Atlas
client = MongoClient('MONGO_URI')
db = client['video_db']  # Use your MongoDB Atlas database name
fs = GridFS(db)

@app.route('/')
def index():
    page = request.args.get('page', 1, type=int)
    per_page = 12

    # Fetch videos for the current page
    videos = []
    total_videos = db.fs.files.count_documents({})  # Correctly count the total number of videos
    cursor = fs.find().skip((page - 1) * per_page).limit(per_page)
    for file in cursor:
        videos.append({
            'filename': file.filename,
            'id': file._id
        })

    # Calculate total pages
    total_pages = (total_videos + per_page - 1) // per_page

    return render_template('index.html', videos=videos, page=page, total_pages=total_pages)

@app.route('/video/<video_id>')
def video(video_id):
    # Stream the video file from GridFS
    video_file = fs.get(ObjectId(video_id))
    return send_file(video_file, mimetype='video/mp4')

@app.route('/download/<video_id>')
def download(video_id):
    # Download the video file from GridFS
    video_file = fs.get(ObjectId(video_id))
    return send_file(video_file, mimetype='video/mp4', as_attachment=True, download_name=video_file.filename)

if __name__ == '__main__':
    app.run(debug=True)
