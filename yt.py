import os
import json
import time
import logging
import threading
import requests
from datetime import datetime, timezone
from io import BytesIO
from tkinter import Tk, Label, Text, Scrollbar, Frame, RIGHT, LEFT, Y, BOTH, END, TOP
from PIL import Image, ImageTk
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

API_KEY = 'API_KEY'
CHANNEL_ID = 'UCoxFxZirbfLvy9tres71eSA'
CHAT_DURATION = 30
INTERVAL = 60
LOG_FILE = 'stream_analysis_log.json'

logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s',
                    handlers=[logging.StreamHandler()])

youtube = build('youtube', 'v3', developerKey=API_KEY, cache_discovery=False)

def get_channel_info(channel_id):
    try:
        res = youtube.channels().list(part='snippet', id=channel_id).execute()
        items = res.get('items', [])
        if items:
            snippet = items[0]['snippet']
            return snippet['title'], snippet['thumbnails']['default']['url']
    except HttpError as e:
        logging.error(f"Failed to fetch channel info: {e}")
    return None, None

def get_live_stream_id():
    try:
        res = youtube.search().list(part='id', channelId=CHANNEL_ID, eventType='live', type='video').execute()
        items = res.get('items', [])
        if items:
            return items[0]['id']['videoId']
    except HttpError as e:
        logging.error(f"Failed to get live stream ID: {e}")
    return None

def get_stream_stats(video_id):
    try:
        res = youtube.videos().list(part='liveStreamingDetails,statistics', id=video_id).execute()
        items = res.get('items', [])
        if not items:
            return None
        data = items[0]
        stats = data.get('statistics', {})
        details = data.get('liveStreamingDetails', {})
        return {
            'concurrentViewers': int(details.get('concurrentViewers', 0)),
            'activeChatId': details.get('activeLiveChatId')
        }
    except HttpError as e:
        logging.error(f"Failed to get stream stats: {e}")
    return None

def get_chat_analysis(chat_id, duration):
    unique_authors = {}
    total_messages = 0
    next_page_token = None
    end_time = time.time() + duration

    while time.time() < end_time:
        try:
            res = youtube.liveChatMessages().list(
                liveChatId=chat_id,
                part='snippet,authorDetails',
                pageToken=next_page_token,
                maxResults=200
            ).execute()

            for item in res.get('items', []):
                total_messages += 1
                author_id = item['authorDetails']['channelId']
                if author_id not in unique_authors:
                    unique_authors[author_id] = 1
                else:
                    unique_authors[author_id] += 1

            next_page_token = res.get('nextPageToken')
            time.sleep(min(res.get('pollingIntervalMillis', 2000) / 1000.0, end_time - time.time()))
        except HttpError as e:
            logging.error(f"Chat fetch error: {e}")
            break

    return {
        'uniqueChatters': len(unique_authors),
        'totalMessages': total_messages,
        'avgMessages': total_messages / len(unique_authors) if unique_authors else 0
    }

def estimate_bots(viewers, chat_stats):
    unique = chat_stats['uniqueChatters']
    raw_ratio = unique / viewers if viewers > 0 else 0
    estimated_real = round(unique / 0.25) if raw_ratio >= 0.02 else round(viewers * raw_ratio)
    estimated_real = min(estimated_real, viewers)
    estimated_bots = max(0, viewers - estimated_real)

    return {
        'estimatedRealViewers': estimated_real,
        'estimatedBotViewers': estimated_bots,
        'chatToViewerRatio': round(raw_ratio, 4)
    }

class LiveBotGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("YouTube Bot Detection Dashboard")
        self.root.configure(bg='#1e1e1e')

        self.header = Frame(root, bg='#1e1e1e')
        self.header.pack(side=TOP, pady=10)

        try:
            pepe_data = requests.get("https://i.ibb.co/RXn09Xj/pepe-hacker.png").content
            pepe_img = Image.open(BytesIO(pepe_data)).resize((64, 64))
            self.pepe_photo = ImageTk.PhotoImage(pepe_img)
            pepe_label = Label(self.header, image=self.pepe_photo, bg='#1e1e1e')
            pepe_label.pack(side=TOP, pady=(0, 10))
        except Exception as e:
            logging.warning(f"Could not load pepe image: {e}")

        self.profile_label = Label(self.header, bg='#1e1e1e')
        self.profile_label.pack(side=LEFT, padx=10)

        self.info_label = Label(self.header, text="Loading channel info...", fg='white', bg='#1e1e1e', font=('Arial', 12), justify=LEFT)
        self.info_label.pack(side=LEFT)

        self.text_area = Text(root, bg='#252526', fg='white', insertbackground='white', wrap='word', font=('Consolas', 10))
        self.text_area.pack(side=LEFT, fill=BOTH, expand=True)

        scrollbar = Scrollbar(root, command=self.text_area.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.text_area.config(yscrollcommand=scrollbar.set)

        # Start loading channel info in background
        threading.Thread(target=self.load_channel_image, daemon=True).start()
        # Start updating data in background
        threading.Thread(target=self.update_data, daemon=True).start()

    def load_channel_image(self):
        title, url = get_channel_info(CHANNEL_ID)
        if title:
            self.info_label.config(text=f"{title}\nChannel ID: {CHANNEL_ID}")
        else:
            self.info_label.config(text=f"Channel ID: {CHANNEL_ID}")

        if url:
            try:
                img_data = requests.get(url).content
                img = Image.open(BytesIO(img_data)).resize((48, 48))
                photo = ImageTk.PhotoImage(img)
                # Tkinter updates must be done on main thread:
                self.root.after(0, lambda: self.profile_label.config(image=photo))
                self.profile_label.image = photo
            except Exception as e:
                logging.warning(f"Could not load image: {e}")

    def log(self, message):
        self.text_area.insert(END, f"{message}\n")
        self.text_area.see(END)

    def update_data(self):
        while True:
            timestamp = datetime.now(timezone.utc).isoformat()
            self.root.after(0, lambda: self.log(f"[{timestamp}] Starting analysis..."))

            video_id = get_live_stream_id()
            if not video_id:
                self.root.after(0, lambda: self.log("No active live stream found."))
                time.sleep(INTERVAL)
                continue

            stats = get_stream_stats(video_id)
            if not stats:
                self.root.after(0, lambda: self.log("Stream stats unavailable."))
                time.sleep(INTERVAL)
                continue

            chat_stats = get_chat_analysis(stats['activeChatId'], CHAT_DURATION)
            estimates = estimate_bots(stats['concurrentViewers'], chat_stats)

            result = {
                'timestamp': timestamp,
                'concurrentViewers': stats['concurrentViewers'],
                **chat_stats,
                **estimates
            }

            with open(LOG_FILE, 'a') as f:
                f.write(json.dumps(result) + '\n')

            log_message = (f"Viewers: {stats['concurrentViewers']}, Real: {estimates['estimatedRealViewers']}, "
                           f"Bots: {estimates['estimatedBotViewers']}, Ratio: {estimates['chatToViewerRatio']}")
            self.root.after(0, lambda msg=log_message: self.log(msg))

            time.sleep(INTERVAL)

if __name__ == '__main__':
    root = Tk()
    app = LiveBotGUI(root)
    root.mainloop()
