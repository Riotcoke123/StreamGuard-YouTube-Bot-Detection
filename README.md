<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />

</head>
<body>
  <h1>StreamGuard - YouTube Bot Detection</h1>
  <p>
    StreamGuard is a Python script designed to analyze YouTube live chat streams and estimate the number of real viewers versus potential bot accounts. 
    It collects live chat messages, analyzes chat activity patterns, and provides an estimation of viewer authenticity based on chat behavior.
  </p>

  <h2>Features</h2>
  <ul>
    <li>Automatically detects active YouTube live streams on a specified channel.</li>
    <li>Collects and analyzes live chat messages over a configurable time window.</li>
    <li>Detects suspicious chat activity indicating potential bots.</li>
    <li>Estimates real viewers and bots based on chat-to-viewer ratios.</li>
    <li>Logs analysis results in a JSON file for further inspection.</li>
  </ul>

  <h2>Requirements</h2>
  <ul>
    <li>Python 3.8 or later</li>
    <li>Google API Client Library for Python (`google-api-python-client`)</li>
    <li>YouTube Data API v3 Key</li>
  </ul>

  <h2>Installation</h2>
  <pre><code>pip install google-api-python-client</code></pre>

  <h2>Usage</h2>
  <ol>
    <li>Clone the repository:
      <pre><code>git clone https://github.com/Riotcoke123/StreamGuard-YouTube-Bot-Detection.git</code></pre>
    </li>
    <li>Set your YouTube Data API key and target channel ID in the script configuration.</li>
    <li>Run the script:
      <pre><code>python yt.py</code></pre>
    </li>
  </ol>

  <h2>Configuration</h2>
  <p>The main configuration parameters can be adjusted at the top of the script:</p>
  <ul>
    <li><code>API_KEY</code>: Your YouTube Data API v3 key.</li>
    <li><code>CHANNEL_ID</code>: The YouTube channel ID to monitor.</li>
    <li><code>CHAT_COLLECTION_DURATION_SEC</code>: Duration in seconds to collect chat messages during each analysis.</li>
    <li><code>BOT_ESTIMATION_INTERVAL_SEC</code>: Time interval between bot detection runs.</li>
  </ul>

  <h2>License</h2>
  <p>This project is licensed under the <a href="https://www.gnu.org/licenses/gpl-3.0.en.html" target="_blank" rel="noopener noreferrer">GNU General Public License v3.0</a>.</p>

  <h2>Repository</h2>
  <p>Find the project on GitHub: <a href="https://github.com/Riotcoke123/StreamGuard-YouTube-Bot-Detection" target="_blank" rel="noopener noreferrer">https://github.com/Riotcoke123/StreamGuard-YouTube-Bot-Detection</a></p>

  <footer>
    &copy; 2025 StreamGuard Project. Licensed under GPLv3.
  </footer>
</body>
</html>
