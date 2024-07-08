
from flask import Flask, jsonify, render_template, request, abort, send_file, make_response

from linebot.v3 import (
    WebhookParser
)
from linebot.v3.exceptions import (
    InvalidSignatureError
)
from linebot.v3.messaging import (
    Configuration,
    ApiClient,
)

from event_handler import handle_events

import logging
from secret import LINE_CHANNEL_ACCESS_TOKEN, LINE_CHANNEL_SECRET
from save_review_and_menu import save_review_and_menu_to_doc

app = Flask(__name__)
logging.basicConfig(filename="debug.log", level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s %(name)s: %(message)s\n')


# @app.route("/log")
# def view_log():
#     with open("debug.log", "r") as f:
#         lines = f.readlines()  # Read the file content into a list of lines
#     return render_template("log.html", lines=lines)


@app.route('/backend')
def view_backend():
    return render_template('upload.html')


@app.route('/upload', methods=['POST'])
def upload():
    menu = request.files['file1']
    review = request.files['file2']
    title = request.form['string_input']

    menu = menu.read().decode('utf-8')
    review = review.read().decode('utf-8')
    id = save_review_and_menu_to_doc(menu, review, title)

    # Create response with QR code image
    return jsonify({"message": id})


# @app.route("/view_image")
# def view_image():
#     return render_template("image.html")


# @app.route("/test")
# def test():
#     app.logger.debug("Test")
#     return "Hello, World!"


@app.route("/", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    configuration = Configuration(access_token=LINE_CHANNEL_ACCESS_TOKEN)
    parser = WebhookParser(LINE_CHANNEL_SECRET)
    signature = request.headers['X-Line-Signature']
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.debug("Request body: " + body)

    # handle webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        app.logger.debug(
            "Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    with ApiClient(configuration) as api_client:
        handle_events(events, api_client, app.logger)

    return 'OK'


if __name__ == "__main__":
    app.run(debug=False)
