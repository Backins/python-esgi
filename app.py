from flask import Flask, render_template, request, redirect, url_for, flash
from flask_socketio import SocketIO, emit
from threading import Thread, Event
from scrapper import launch_crawler
from queue import Queue

queue = Queue()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'changeme'
socketio = SocketIO(app)

thread = Thread()
thread_stop_event = Event()


@socketio.on('connect', namespace='/crawler')  # test of the connection of the websocket with the url /crawler
def test_connect():
    print('Client connected')


@socketio.on('crawl_website', namespace='/crawler') # processing of crawling the website from the url
def processurl(message):
    print("PROCESSING!")
    emit('processing', {'target': message.get('url')})
    poll = []
    launch_crawler(message.get('url'), lambda x: print(x))
    print('DONE!')
    print(queue_get_all(queue))


def queue_get_all(q):
    items = []
    while 1:
        try:
            items.append(q.get_nowait())
        except:
            break
    return items


@socketio.on('poll_result', namespace='/crawler')  # get the result of the spider and send to the page
def result(message):
    queue_content = queue_get_all(queue)
    print(queue_content)
    emit('result', {'result': queue_content})


@app.route('/')  # route home of the project
def index():
    return render_template('home.html')


if __name__ == '__maxin__':
    launch_crawler('https://sysdream.com', callback=lambda x: print(x))

if __name__ == '__main__':
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    app.config['FLASK_DEBUG'] = True
    socketio.run(app)