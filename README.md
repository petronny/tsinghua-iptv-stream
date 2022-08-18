# tsinghua-iptv-stream
Convert iptv.tsinghua.edu.cn into a standard IPTV stream to watch on IPTV clients such as the simple IPTV client in Kodi.

## Usage

* Copy `config.py.sample` to `config.py` to set your user id, password the bind address in your local network.

* Then run `flask run --host=::` to start the stream server.

* In your IPTV client, set `your_bind_address/channels` as the channel list.
