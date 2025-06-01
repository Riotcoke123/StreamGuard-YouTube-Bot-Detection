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
    <li><strong>Immediate GUI popup:</strong> The graphical interface launches instantly without waiting for data fetching.</li>
    <li><strong>Background data loading:</strong> Channel info and stream statistics load asynchronously in separate threads, ensuring a responsive UI.</li>
  </ul>

  <h2>Requirements</h2>
  <ul>
    <li>Python 3.8 or later</li>
    <li>Google API Client Library for Python (<code>google-api-python-client</code>)</li>
    <li>YouTube Data API v3 Key</li>
    <li>Additional dependencies: <code>requests</code>, <code>Pillow</code> (PIL fork)</li>
  </ul>

  <h2>Getting a YouTube Data API Key</h2>
  <p>
    To use this script, you need to obtain a YouTube Data API v3 key. Follow these steps:
  </p>
  <ol>
    <li>Go to the <a href="https://console.cloud.google.com/" target="_blank" rel="noopener noreferrer">Google Cloud Console</a>.</li>
    <li>Create a new project or select an existing one.</li>
    <li>Enable the YouTube Data API v3 under "APIs & Services".</li>
    <li>Navigate to "Credentials" and create an API key.</li>
    <li>Use this key in the <code>API_KEY</code> configuration of the script.</li>
  </ol>

  <h2>Installation</h2>
  <pre><code>pip install google-api-python-client requests Pillow</code></pre>

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
    <li><code>CHAT_DURATION</code>: Duration (seconds) to collect chat messages during each analysis cycle.</li>
    <li><code>INTERVAL</code>: Time interval (seconds) between consecutive bot detection runs.</li>
  </ul>

  <h2>Implementation Details</h2>
  <p>The updated script now:</p>
  <ul>
    <li>Launches the GUI window immediately on start without delay.</li>
    <li>Loads channel thumbnail and name in a background thread, updating the interface once available.</li>
    <li>Runs the live chat analysis and viewer estimation in a background thread, logging results and updating the GUI asynchronously.</li>
    <li>Uses <code>threading.Thread</code> and <code>Tkinter's root.after()</code> to safely update UI from background threads.</li>
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


