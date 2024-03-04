# nist_ai

- Dash app developed with the intention of helping members of NIST (National Institute of Standards and Technology) to store and analyze video data captured from disaster relief sites. 

- Allows users to upload video, audio files, and metadata associated with video to an SQL database. Text transcription is done on the backend with the Whisper model to support querying for specific words or phrases. The app also supports querying for specific metadata and visualizing the data in the database.

- Allows querying for thumbnail based on text transcript segment

- Captures GPS data from video metadata and displays interactive map, so that the steps of the disaster relief team can potentially be re-traced and visualized.

- Uses Dash for the frontend, SQL and Python on the backend for analysis.