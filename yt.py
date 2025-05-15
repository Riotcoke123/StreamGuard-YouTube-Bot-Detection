import os
import json
import time
import logging
from datetime import datetime, timezone
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# Configuration
API_KEY = 'API-KEY'
CHANNEL_ID = 'yt_channel_id'
DATA_LOG_FILE = os.path.join(os.path.dirname(__file__), 'stream_analysis_log.json')
CHAT_COLLECTION_DURATION_SEC = 30
BOT_ESTIMATION_INTERVAL_SEC = 60
LURKER_ADJUSTMENT_FACTOR = 0.25
MIN_CHAT_VIEWER_RATIO_FOR_PRIMARY_ESTIMATION = 0.02
SUSPICIOUSLY_HIGH_MESSAGE_COUNT_PER_USER = 10

# Initialize logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

# YouTube client
youtube = build('youtube', 'v3', developerKey=API_KEY)

def get_live_stream_id(channel_id):
    try:
        res = youtube.search().list(
            part='id',
            channelId=channel_id,
            eventType='live',
            type='video',
            maxResults=1
        ).execute()

        items = res.get('items', [])
        if items:
            return items[0]['id']['videoId']
        return None
    except HttpError as e:
        logging.error(f"Error fetching live stream ID: {e}")
        return None

def get_stream_stats(video_id):
    try:
        res = youtube.videos().list(
            part='liveStreamingDetails,statistics',
            id=video_id
        ).execute()

        items = res.get('items', [])
        if not items:
            logging.warning(f"No video details found for ID {video_id}")
            return None

        video = items[0]
        stats = video.get('statistics', {})
        details = video.get('liveStreamingDetails', {})

        return {
            'concurrentViewers': int(details.get('concurrentViewers', 0)),
            'activeChatId': details.get('activeLiveChatId')
        }
    except HttpError as e:
        logging.error(f"Error fetching stats for {video_id}: {e}")
        return None

def get_chat_analysis(chat_id, duration_sec):
    unique_authors = {}
    total_messages = 0
    next_page_token = None
    end_time = time.time() + duration_sec

    logging.info(f"Collecting chat messages from chat ID {chat_id}...")

    while time.time() < end_time:
        try:
            res = youtube.liveChatMessages().list(
                liveChatId=chat_id,
                part='snippet,authorDetails',
                pageToken=next_page_token,
                maxResults=200
            ).execute()

            items = res.get('items', [])
            for item in items:
                total_messages += 1
                author_id = item['authorDetails']['channelId']
                if author_id not in unique_authors:
                    unique_authors[author_id] = {
                        'messageCount': 1,
                        'isModerator': item['authorDetails'].get('isChatModerator', False),
                        'isOwner': item['authorDetails'].get('isChatOwner', False),
                    }
                else:
                    unique_authors[author_id]['messageCount'] += 1

            next_page_token = res.get('nextPageToken')
            time.sleep(min(res.get('pollingIntervalMillis', 2000) / 1000.0, end_time - time.time()))

        except HttpError as e:
            logging.error(f"Error fetching chat messages: {e}")
            break

    suspicious_count = sum(1 for a in unique_authors.values()
                           if a['messageCount'] > SUSPICIOUSLY_HIGH_MESSAGE_COUNT_PER_USER and not a['isModerator'] and not a['isOwner'])

    return {
        'uniqueChatterCount': len(unique_authors),
        'totalMessagesCollected': total_messages,
        'averageMessagesPerChatter': total_messages / len(unique_authors) if unique_authors else 0,
        'potentiallySuspiciousChatters': suspicious_count
    }

def estimate_viewers(concurrent_viewers, chat_analysis):
    if concurrent_viewers <= 0:
        return {
            'estimatedRealViewers': 0,
            'estimatedBotViewers': 0,
            'estimationMethod': 'No concurrent viewers',
            'rawChatToViewerRatio': 0,
            'adjustedChatToViewerRatio': 0
        }

    unique = chat_analysis['uniqueChatterCount']
    suspicious = chat_analysis['potentiallySuspiciousChatters']
    adjusted = max(0, unique - suspicious)
    raw_ratio = unique / concurrent_viewers
    adjusted_ratio = adjusted / concurrent_viewers if concurrent_viewers > 0 else 0

    if adjusted == 0:
        real = 0
        method = "No reliable chatters"
    elif adjusted_ratio >= MIN_CHAT_VIEWER_RATIO_FOR_PRIMARY_ESTIMATION:
        real = round(adjusted / LURKER_ADJUSTMENT_FACTOR)
        method = f"Lurker Factor ({LURKER_ADJUSTMENT_FACTOR})"
    else:
        real = round(concurrent_viewers * adjusted_ratio)
        method = "Fallback Ratio"

    real = min(max(real, adjusted), concurrent_viewers)
    bots = max(0, concurrent_viewers - real)

    return {
        'estimatedRealViewers': real,
        'estimatedBotViewers': bots,
        'estimationMethod': method,
        'rawChatToViewerRatio': round(raw_ratio, 4),
        'adjustedChatToViewerRatio': round(adjusted_ratio, 4)
    }

def log_to_file(data):
    if os.path.exists(DATA_LOG_FILE):
        with open(DATA_LOG_FILE, 'r', encoding='utf-8') as f:
            try:
                log = json.load(f)
                if not isinstance(log, list):
                    log = []
            except json.JSONDecodeError:
                log = []
    else:
        log = []

    log.append(data)

    with open(DATA_LOG_FILE, 'w', encoding='utf-8') as f:
        json.dump(log, f, indent=2)

def run_detection_loop():
    logging.info("Starting YouTube Live Stream Bot Detection")
    logging.info(f"Channel ID: {CHANNEL_ID}")
    logging.info(f"Interval: {BOT_ESTIMATION_INTERVAL_SEC}s | Chat Duration: {CHAT_COLLECTION_DURATION_SEC}s")
    logging.info(f"Log File: {DATA_LOG_FILE}\n")

    while True:
        timestamp = datetime.now(timezone.utc).isoformat()
        logging.info(f"[{timestamp}] Starting analysis...")

        video_id = get_live_stream_id(CHANNEL_ID)
        if not video_id:
            logging.info("No active live stream found.")
            time.sleep(BOT_ESTIMATION_INTERVAL_SEC)
            continue

        stats = get_stream_stats(video_id)
        if not stats:
            logging.info("Failed to get stream stats.")
            time.sleep(BOT_ESTIMATION_INTERVAL_SEC)
            continue

        if not stats.get('activeChatId'):
            logging.info("No chat ID found. Estimating all as bots.")
            result = {
                'timestamp': timestamp,
                'channelId': CHANNEL_ID,
                'videoId': video_id,
                'concurrentViewers': stats['concurrentViewers'],
                'uniqueChatterCount': 0,
                'totalMessagesCollected': 0,
                'averageMessagesPerChatter': 0,
                'potentiallySuspiciousChatters': 0,
                'estimatedRealViewers': 0,
                'estimatedBotViewers': stats['concurrentViewers'],
                'rawChatToViewerRatio': 0,
                'adjustedChatToViewerRatio': 0,
                'estimationMethod': 'No chat available'
            }
            log_to_file(result)
            time.sleep(BOT_ESTIMATION_INTERVAL_SEC)
            continue

        chat_analysis = get_chat_analysis(stats['activeChatId'], CHAT_COLLECTION_DURATION_SEC)
        estimates = estimate_viewers(stats['concurrentViewers'], chat_analysis)

        result = {
            'timestamp': timestamp,
            'channelId': CHANNEL_ID,
            'videoId': video_id,
            'concurrentViewers': stats['concurrentViewers'],
            **chat_analysis,
            **estimates
        }

        logging.info(f"[{timestamp}] Real: {estimates['estimatedRealViewers']}, Bots: {estimates['estimatedBotViewers']} ({estimates['estimationMethod']})")
        log_to_file(result)
        time.sleep(BOT_ESTIMATION_INTERVAL_SEC)

if __name__ == "__main__":
    try:
        run_detection_loop()
    except KeyboardInterrupt:
        logging.info("Shutting down.")
