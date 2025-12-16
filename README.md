# Music Player Project

A music player built with python using GUI Qt(Pyside6) Pillow, and requests. 

Main - Control center managing the upload
API - Accesses the apple music API, gets title and artist
Visual Effects - Creates dynamic background using PIL to get the color in the users image
Music Player - Give the user the ability to create playlists and add image filters to said playlist covers

How to Run
1. Install requirements:
- pip install Pillow
- pip install requests
- pip install Pyside6

2. Run main.py 
- python main.py

How to control
1. Main Menu
- Select playlist to veiw playlist with saved audio files
- Select Upload to upload your own audio and thumbnail

2. Playlist
- Note: Must upload an audio file before use 
- Select song from drop down menu 
- Press play to play audio 
- Press pause to pause audio

3. Upload 
- Select Choose Audio File to open files and selct an audio file 
- Selcet Choose Image File to upload any image to make the thumbnail for selsected audio file
- Search Apple Music Api to find song titles and artist names 

4. Playlist Manager
- Had plans to expan upon but never came around to them
