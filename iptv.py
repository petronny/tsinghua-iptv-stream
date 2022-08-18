import re
from datetime import datetime, timezone
from xml.etree.ElementTree import Element, SubElement, tostring

import requests

from config import bind_url, password, url, username

epg_date_format = "%Y%m%d%H%M%S"
session = requests.Session()


def get_redirect(content):
    return re.search(r'"(https://[^"]*)"', content).group(1)


def get_channels():
    response = session.get(url)
    _url = get_redirect(response.content.decode("utf-8"))

    response = session.get(_url)
    data = {"i_user": username, "i_pass": password}
    response = session.post(
        "https://id.tsinghua.edu.cn/do/off/ui/auth/login/check", data=data
    )
    _url = get_redirect(response.content.decode("utf-8"))

    response = session.get(_url)

    channels = session.get(f"{url}/channels_tsinghua.json").json()

    return channels


def get_epg(channels):
    vids = [
        channel["Vid"]
        for category in channels["Categories"]
        for channel in category["Channels"]
    ]

    epg = session.get(f"{url}/epg/todayepg.json").json()
    epg = [epg[vid] if vid in epg else [] for vid in vids]

    return epg


def convert_to_m3u8(channels, epg, bind_url):
    lines = [f'#EXTM3U url-tvg = "{bind_url}/epg.xml"']
    channel_id = 1
    for category in channels["Categories"]:
        category_name = category["Name"]
        for channel in category["Channels"]:
            channel_name = channel["Name"]
            channel_vid = channel["Vid"]
            lines.append(
                f'#EXTINF:0 tvg-id="{channel_id}" tvg-name="{channel_name}" tvg-logo="{bind_url}/snapshot/{channel_vid}.jpg",group-title="{category_name}",{channel_name}'
            )
            lines.append(f"{bind_url}/hls/{channel_vid}.m3u8")
            channel_id += 1
    return "\n".join(lines)


def convert_to_xml(channels, epg):
    tv = Element("tv")
    channel_id = 1
    for category in channels["Categories"]:
        for channel in category["Channels"]:
            channel_xml = SubElement(tv, "channel", {"id": f"{channel_id}"})
            display_name = SubElement(channel_xml, "display-name", {"lang": "zh"})
            display_name.text = channel["Name"]

    for i, programmes in enumerate(epg):
        for programme in programmes:
            start = (
                datetime.fromtimestamp(programme["start"]).strftime(epg_date_format)
                + " +0800"
            )
            stop = (
                datetime.fromtimestamp(programme["stop"]).strftime(epg_date_format)
                + " +0800"
            )
            programme_xml = SubElement(
                tv, "programme", {"start": start, "stop": stop, "channel": f"{i}"}
            )
            title = SubElement(programme_xml, "title", {"lang": "zh"})
            title.text = programme["title"]
            desc = SubElement(programme_xml, "title", {"lang": "zh"})
            desc.text = " "

    # from util import prettify
    # print(prettify(tv))
    return tostring(tv)


def check_channels(channels):
    for i, category in enumerate(channels["Categories"]):
        for j, channel in enumerate(category["Channels"]):
            channel_name = channel["Name"]
            channel_vid = channel["Vid"]
            response = session.get(f"{url}/hls/{channel_vid}.m3u8")
            if response.status_code != 200:
                print(channel_name, channel_vid, response.status_code)
                del channels["Categories"][i]["Channels"][j]
                continue
            lines = response.content.decode("utf-8").split("\n")
            ts = [line for line in lines if line.endswith(".ts")][-1]
            response = session.get(f"{url}/hls/{channel_vid}.m3u8")

    return channels


channels = get_channels()
channels = check_channels(channels)
epg = get_epg(channels)
channels_m3u8 = convert_to_m3u8(channels, epg, bind_url)
epg_xml = convert_to_xml(channels, epg)
