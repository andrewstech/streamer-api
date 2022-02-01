import functools
import logging
import traceback
import sys
import requests

from flask import Flask, Blueprint, current_app, jsonify, request, redirect, abort, render_template, url_for, flash, redirect, Response
import youtube_dl
from youtube_dl import YoutubeDL
from youtube_dl.version import __version__ as youtube_dl_version

from .version import __version__

ytdl_audio = {
    'format': 'bestaudio/best',
    'restrictfilenames': False,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}

ytdla = YoutubeDL(ytdl_audio)

ytdl_video = {
    'format': '18/best',
    'restrictfilenames': False,
    'noplaylist': False,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto'
}

ytdlv = YoutubeDL(ytdl_video)



api = Blueprint('api', __name__)


def route_api(subpath, *args, **kargs):
    return api.route('/api/' + subpath, *args, **kargs)


def set_access_control(f):
    @functools.wraps(f)
    def wrapper(*args, **kargs):
        response = f(*args, **kargs)
        response.headers['Access-Control-Allow-Origin'] = '*'
        return response
    return wrapper


@api.errorhandler(youtube_dl.utils.DownloadError)
@api.errorhandler(youtube_dl.utils.ExtractorError)
def handle_youtube_dl_error(error):
    logging.error(traceback.format_exc())
    result = jsonify({'error': str(error)})
    result.status_code = 500
    return result


class WrongParameterTypeError(ValueError):
    def __init__(self, value, type, parameter):
        message = '"{}" expects a {}, got "{}"'.format(parameter, type, value)
        super(WrongParameterTypeError, self).__init__(message)


@api.errorhandler(WrongParameterTypeError)
def handle_wrong_parameter(error):
    logging.error(traceback.format_exc())
    result = jsonify({'error': str(error)})
    result.status_code = 400
    return result


@api.before_request
def block_on_user_agent():
    user_agent = request.user_agent.string
    forbidden_uas = current_app.config.get('FORBIDDEN_USER_AGENTS', [])
    if user_agent in forbidden_uas:
        abort(429)


  
@route_api('audio-search')
@set_access_control
def audiosearch():
  search = request.args['search']
  data = ytdla.extract_info(f"ytsearch1:{search}", download=False)
  search_results = data['entries']
  result = search_results[0]
  song_name = result['title']
  channel_name = result['uploader']
  searchr = [data['entries'][0]['url'], result['title'], result['uploader'] ]
  return jsonify(searchr)

@route_api('video-search')
@set_access_control
def search():
  search = request.args['search']
  data = ytdlv.extract_info(f"ytsearch5:{search}", download=False)
  search_results = data['entries']
  result = search_results[0]
  song_name = result['title']
  channel_name = result['uploader']
  searchr = [data['entries'][0]['url'], result['title'], result['uploader'] ]
  return jsonify(searchr)

@route_api('info')
@set_access_control
def info():
    url = request.args['url']
    video_details = ytdlv.extract_info(url, download=False)
    print(url)
    return jsonify(video_details)

@route_api('/proxy/<path:url>')
@set_access_control
def proxy(url):
    req = requests.get(url, stream = True)
    return Response(stream_with_context(req.iter_content(chunk_size=1024)), content_type = req.headers['content-type'])

@route_api('version')
@set_access_control
def version():
    result = {
        'youtube-dl': youtube_dl_version,
        'version': __version__,
    }
    return jsonify(result)

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'),404

@app.errorhandler(405)
def not_found_error(error):
    return render_template('405.html'),405

app.register_blueprint(api)
app.config.from_pyfile('../application.cfg', silent=True)
