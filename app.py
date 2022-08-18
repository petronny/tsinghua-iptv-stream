from flask import Flask

from config import url
from iptv import channels_m3u8, epg_xml, session

app = Flask(__name__)


@app.route("/channels")
def get_channels():
    return channels_m3u8


@app.route("/epg.xml")
def get_epg():
    return epg_xml


@app.route("/<path:path>")
def forward(path):
    return session.get(f"{url}/{path}").content
