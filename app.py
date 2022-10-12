import sys
import datetime
import requests

from flask import Flask
from flask import request, jsonify
from flask_cors import CORS

# TODO: make queue for requests
#import redis
#from rq import Queue
#from redis import Redis
#from worker import run_worker
#from rq.job import Job

from youtubesearchpython import *

app = Flask(__name__)
CORS(app)

#redis_conn = Redis(host="127.0.0.1", port=6379)
#q = Queue(connection=redis_conn)

from pytube import YouTube
from pytube import Channel
import time
import json

def parseSubscriberCount(subs):
    subs = subs.replace(" subscribers", "")
    subs_i = 0
    multiplier = 1

    try:
        if subs[-1] == "B":
            multiplier = 1000000000
        if subs[-1] == "M":
            multiplier = 1000000
        if subs[-1] == "K":
            multiplier = 1000
        subs = subs[:-1]

        subs_i = float(subs) * multiplier
    except Exception as e:
        raise(e)
        subs_i = 1

    return subs_i


def getVideoInfo(url):
    yt = YouTube('https://www.youtube.com/watch?v=koxXu5Wa11I')
    ch = Channel(yt.channel_url)

    res = {}
    res["id"] = yt.vid_info["videoDetails"]["videoId"]
    res["title"] = yt.title
    res["duration_seconds"] = yt.length
    res["published_at"] = time.mktime(yt.publish_date.timetuple())
    res["thumbnail_url"] = yt.thumbnail_url
    res["description_long"] = yt.description
    res["view_count"] = yt.views
    res["author_id"] = ch.channel_id
    res["author_name"] = ch.channel_name
    try:
        res["author_thumbnail_url"] = ch.initial_data["header"]["c4TabbedHeaderRenderer"]["avatar"]["thumbnails"][-1]["url"]
        res["author_subscriptions_count"] = parseSubscriberCount(ch.initial_data["header"]["c4TabbedHeaderRenderer"]["subscriberCountText"]["simpleText"])
    except Exception as e:
        raise(e)
        res["author_thumbnail_url"] = res["id"]
        res["author_subscriptions_count"] = 0

    try:
        res["like_count"] = int(yt.initial_data["engagementPanels"][1]["engagementPanelSectionListRenderer"]["content"]["structuredDescriptionContentRenderer"]["items"][0]["videoDescriptionHeaderRenderer"]["factoid"][0]["factoidRenderer"]["value"]["simpleText"])
    except Exception as e:
        res["like_count"] = 1

    return res


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/search', methods=['GET', 'POST']  )
def search():
    if request.method != 'POST':
        response = jsonify({
            "error": "Unknown request method"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    query = str(request.json.get('query', ''))
    videosSearch = VideosSearch(query, limit = 15)

    response = jsonify(videosSearch.result())
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/comments', methods=['GET', 'POST']  )
def comments():
    if request.method != 'POST':
        response = jsonify({
            "error": "Unknown request method"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    video_id = str(request.json.get('video_id', ''))

    response = jsonify(Comments.get(video_id))
    response.headers.add('Access-Control-Allow-Origin', '*')
    return response


@app.route('/info', methods=['GET', 'POST'])
def info():
    if request.method != 'POST':
        response = jsonify({
            "error": "Unknown request method"
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response

    video_id = str(request.json.get('video_url', ''))
    video_id = video_id.replace("clipzag.com", "youtube.com")

    try:
        response = jsonify(getVideoInfo(video_id))
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response
    except Exception as e:
        response = jsonify({
            "error": "Failed to get video info: " + str(e)
        })
        response.headers.add('Access-Control-Allow-Origin', '*')
        return response


#def schedule_task(things, stream):
#    job = Job.create(
#        run_worker,
#        args=(things,),
#        kwargs={'stream': stream},
#        result_ttl=5000,
#        timeout=10000,
#        connection=redis_conn,
#        on_success=report_success,
#        on_failure=report_failure
#    )

#    try:
#        q.enqueue_job(job)
#    except redis.exceptions.ConnectionError as e:
#        return {
#            "status": StatusCode.TaskSchedulingFailed,
#            "eta": '',
#            "analysis_id": ''
#        }

#    return {
#        "status": StatusCode.NoError,
#        "eta": 40*len(things),
#        "analysis_id": job.id
#    }


#def ping_task(analysis_id):
#    try:
#        obj_id = ObjectId(analysis_id)
#    except bson.errors.InvalidId as e:
#        return {
#                    "analysis_id": analysis_id,
#                    "status": StatusCode.IdIsNotValidObjectId,
#                    "eta": "",
#                    "data": {}
#                }

#    analysis = mongo_db.analyses.find_one({'_id': obj_id})

#    if analysis is None:
#        return {
#                    "analysis_id": analysis_id,
#                    "status": StatusCode.IdIsNotFoundInDatabase,
#                    "eta": "",
#                    "data": {}
#                }

#    db_stat = analysis.get('status')
#    db_data = analysis.get('data')

#    # Second condition is a fallback for old-style statuses
#    if db_stat not in [ StatusCode.NoError, StatusCode.InProgress, StatusCode.Deferred ] or str(db_stat) in ["canceled", "done", "error"]:
#        return {
#                    "analysis_id": analysis_id,
#                    "status": db_stat,
#                    "eta": "",
#                    "data": db_data
#                }

#    # Job is not in any of stopped states => fetch the data from the worker
#    job = Job.fetch(analysis.get("analysis_id"), connection=redis_conn)

#    stat = worker_stat_to_db_stat(job.get_status())

#    if stat != db_stat:
#        mongo_db.analyses.update_one(
#            {
#                '_id': ObjectId(analysis_id)
#            },
#            {
#                "$set": {'status': stat}
#            }
#        )

#        if stat == StatusCode.Done:
#            mongo_db.analyses.update_one(
#                {
#                    '_id': ObjectId(analysis_id)
#                },
#                {
#                    "$set": {
#                        'data': job.result,
#                        'finished_at': str(datetime.datetime.now().timestamp())
#                    }
#                }
#            )
#
#    if stat in [StatusCode.InProgress, StatusCode.Deferred, StatusCode.Canceled, StatusCode.InternalWorkerError]:
#        return {"status": stat, "analysis_id": analysis_id, "eta": "", "data": db_data}
#
#    if stat == StatusCode.Done:
#        return {"status": stat, "analysis_id": analysis_id, "eta": "", "data": job.result}
#
#    return {"status": StatusCode.UnknownWorkerStatus, "eta": "", "analysis_id": analysis_id, "data": db_data}
