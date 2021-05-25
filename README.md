# Creating a Spotify Playlist from a days worth of Triple J play

This project came about because the Australian radio station TripleJ had once again kicked off Requestival. For anyone who hasn't experienced Requestival, it is a week when TripleJ only plays songs requested by listeners, which results in all sorts of weird and wonderful tracks being played (see a wrap up of Requestival 2021 [here](https://www.abc.net.au/triplej/news/musicnews/requestival-2021-the-biggest-reactions-trends-and-takeaways/13347482)). After listening to a couple of days, I realised these would make for some fun, eclectic playlists later on, but I found that if I wanted them I would have to make them myself.

Enter python.

## Files

* triplej_playlist.py - This is the main file that needs to run to generate the playlist. Run using "python triplej_playlist.py"
* utils.py - A file with a couple of helper functions to tidy up the main script
* requirements.txt - The python libraries required by this project. Install using "pip install -r requirements.txt"
* chromedriver/ - This directory holds the chromedriver executable used under the hood to direct the user to the Spotify login page when required

## Workflow

The scripts follow a fairly straightforward process:

1. Authentication
  * This first step uses the helper function get_spotify_authtoken from the utils.py file to navigate the Spotify OAuth process.
  * For this step to be successful, a CLIENT_ID and CLIENT_SECRET are required to be supplied in the main script. N.B. Currently they are set up to be read from environment variables for security, however they can be hardcoded (lines 32 & 33).
    * To obtain these values or read more about the API & Authentication process see [Spotify API](https://developer.spotify.com/documentation/web-api/)
  * If there is no existing refresh token (see API documentation for more info) then the user will be prompted to sign-in on the Spotify website to Authorise the application. Successful authentication will pass an authorisation token back to the main script as well as a refresh token, which will be saved as a file, and used in future to skip the sign-in.
  
2. Get Spotify User Details
  * The next step makes a quick request to the Spotify API to grab the internal user ID of the authenticated user.
	 * This is used for future API calls.
	 
3. Create new Spotify Playlist
  * This step uses the spotify API to create a new playlist for the user. The name of the playlist can be set by setting the PLAYLIST_NAME variable in the main script (line 38)
  * If this step is successful the playlist id will be returned for future use, otherwise an exception will be raised.
  
4. Get the songs played by TripleJ & add to playlist
  * This final step is where most of the heavy lifting takes place.
  * The main part of the step is a loop over the generator function generate_triplej() from the utils.py file.
    * The decision to make this a generator function rather than pulling all of the songs into an iterable before the loop was in an effort to reduce memory usage, and also just for the exercise of using generator functions.
	* The function itself makes a series of GET requests against the interal (undocumented - as far as I know) API of the TripleJ website to pull the list of songs played between 6am and 9pm on the date set by the play_date variable in the main script.
  * The function will yield pairs of titles and artists of the songs played on Triple J, which are then sequentially search for using the Spotify Search API, and the top result is added to the playlist.
    * N.B. The title and artist may not always produce a result in spotify due to typographical errors or perhaps missing featuring artists. If a song cannot be found, it is skipped and an error message is printed to the console.

## Notes

This was just a bit of a passion project, so it is not the most robust script. There is a lot of scope for more graceful error handling, which I might get around to when next year's Requestival comes around. Also, I am aware that there are some existing Spotify API libraries, however I chose not to use them to understand the process more deeply. Lastly, one future improvement I would like to make is to make the process of adding songs to a playlist more generic by accepting any sort of iterable of (title, artist) tuples rather than the hardcoded tripleJ generator.
	