import fuckit

import argparse, os, operator, math, time

fuckit('progressbar')

import ast

import requests

import spotipy
import spotipy.util as util


def main():
	with fuckit:
		os.remove('.cache-speederflash')
	class User:
		pass
	user = User()

	parser = argparse.ArgumentParser(description="Playlist creator from an algorithm")
	parser.add_argument('username', metavar='Username', type=str, help='Username of the user')
	parser.add_argument('playlist', metavar='PlaylistName', type=str, help='Playlist name')
	parser.add_argument('--quiet', '-Q', action='store_true', help='no print output')
	parser.add_argument('--version', '-V', action='version', version='%(prog)s 1.0')

	parser.parse_args(namespace=user)

	quiet = user.quiet

	your_username = user.username
	scopes = 'user-library-read user-top-read playlist-modify-private playlist-read-private'
	client_id = "52b6498829dd4cefad7eea42ba30ec1e"
	client_secret = "06a5edf955af46c8acafc75c97783436"
	redirect_uri = "http://localhost:8888/callback"

	token = util.prompt_for_user_token(

	        username=your_username,
	        scope=scopes,
	        client_id=client_id,
	        client_secret=client_secret,
	        redirect_uri=redirect_uri

	        )
	headers = {"Authorization": "Bearer " + token, "Accept": "application/json"}
	spotify = spotipy.Spotify(auth=token)

	def top50mostPopular(sortedTracks):
		pass


	def clarifyTracks(result, trackList=[], dictList=[]):
		items = result['items']
		for i in range(len(items)):
			NewDict = {}
			temp = items[i]
			try:
				temp = temp['track']
				artist = temp['artists'][0]['name']
			except:
				temp = temp
			track = temp['name']
			NewDict['TrackName'] = track
			NewDict['Artist'] = artist
			popularity = temp['popularity']
			NewDict['Popularity'] = popularity
			NewDict['id'] = temp['id']
			NewDict['URI'] = temp['uri']
			listCheck = [track,artist,popularity]
			trackList.append(listCheck)
			dictList.append(NewDict)
		return trackList,dictList


	tracks = []
	trackDictionaries = []
	totalNumb = spotify.current_user_saved_tracks(limit=1)
	totalNumb = totalNumb['total']
	iterations = math.ceil(float(totalNumb)/float(50))

	for i in range(iterations):
		offset = (i*50)
		results = spotify.current_user_saved_tracks(limit=50, offset=offset)
		clarifiedTracks, tracksDictList = clarifyTracks(results)
		trackDictionaries = tracksDictList
		tracks.append(clarifiedTracks)
	#	Add each group of tracks via showTracks()
	#	Then sort
	tracks[0].sort(key = operator.itemgetter(2))
	tracks[0].reverse()
	sortedTracks = tracks[0]

	trackDictionaries.sort(key = operator.itemgetter('Popularity'))
	trackDictionaries.reverse()


	"""
	--------------------------------------------------------------------------
	"""
	#	BPM search

	bar = progressbar.ProgressBar(max_value=len(sortedTracks), redirect_stdout=True)

	for i in range(len(sortedTracks)):
		featureHref = "https://api.spotify.com/v1/audio-features/" + trackDictionaries[i]['id']
		r = requests.get(featureHref, headers = headers)
		tracktext = str(r.json())
		literal = ast.literal_eval(tracktext)
		bpm = literal['tempo']
		danceVal = literal['danceability']
		energy = literal['energy']
		trackDictionaries[i]['Danceability'] = danceVal
		trackDictionaries[i]['BPM'] = bpm
		trackDictionaries[i]['Energy'] = energy
		if quiet:
			pass
		else:
			bar.update(i)


	playlistName = user.playlist
	def playlistCreate(playlistname):
		playlist = spotify.user_playlist_create('speederflash', playlistname, public=False)
		playlistID = playlist['id']
		return playlistID

	bar2 = progressbar.ProgressBar(max_value=len(trackDictionaries), redirect_stdout=True)

	def addTracks(trackDictionaries, playlistID):
		k = 0
		for i in range(len(trackDictionaries)):
			uri = []
			energy = float(trackDictionaries[i]['Energy'])
			bpm = float(trackDictionaries[i]['BPM'])
			danceability = float(trackDictionaries[i]['Danceability'])
			popularity = float(trackDictionaries[i]['Popularity'])
			uri.append(trackDictionaries[i]['URI'])

			addingfactor = bpm/float(100) + 1.2*danceability + .8*energy + .9*popularity/float(100)
			if addingfactor >= float(3.3):
				spotify.user_playlist_add_tracks(your_username, playlistID, uri)
				k+=1
			if quiet:
				k=k
			else:
				bar2.update(i)

		return k

	playlistid = playlistCreate(playlistName)
	numberOfTracksAdded = addTracks(trackDictionaries, playlistid)
	if quiet:
		pass
	else:
		print(numberOfTracksAdded, "tracks added to", playlistName)

if __name__ == "__main__":
	main()