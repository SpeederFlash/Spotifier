import fuckit

import argparse, math, os

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
	parser.add_argument('artist', metavar='Artist', type=str, help='Artist name')
	parser.add_argument('playlist', metavar='PlaylistName', type=str, help='Playlist name')
	parser.add_argument('--quiet', '-Q', action='store_true', help='no print output')
	parser.add_argument('--version', '-V', action='version', version='%(prog)s 1.0')

	parser.parse_args(namespace=user)

	quiet = user.quiet

	your_username = user.username
	scopes = 'user-library-read user-top-read playlist-modify-private playlist-read-private'
	client_id = "8413522c23d044a4be0e7751a90590ea"
	client_secret = "4aee244c6953486aaa266e698d332ffe"
	redirect_uri = "http://localhost:8888/callback"

	token = util.prompt_for_user_token(

	        username=your_username,
	        scope=scopes,
	        client_id=client_id,
	        client_secret=client_secret,
	        redirect_uri=redirect_uri

	        )

	spotify = spotipy.Spotify(auth=token)

	startArtist = spotify.search(user.artist, limit=1, type='artist')
	startistInfo = startArtist['artists']['items'][0]
	artistList = []
	artistList.append(startistInfo['uri'])

	def artistRunner(artistList, k):
		offset = 0
		lastOffset = 0
		a=0
		lastEnd = ""
		while k <= 950:
			items = spotify.artist_related_artists(artistList[offset])
			for i in range(len(items['artists'])):
				uri = items['artists'][i]['uri']
				if uri in artistList:
					pass
				else:
					artistList.append(uri)
					if offset == lastOffset:
						offset = len(artistList) - 1
					else:
						pass
					k+=1
			lastOffset = offset
			if lastEnd == artistList[len(artistList)-1]:
				a+=1
				if a == 20:
					return artistList
			lastEnd = artistList[-1]
		return artistList

	def addTracks(trackURIs, playlistID):
		offset=0
		trackno1 = 1
		trackno2 = 50
		iterations = math.ceil(float(len(trackURIs))/float(50))
		for i in range(iterations):
			tracks = []
			for j in range(50):
				if (i+1) == iterations:
					for l in range(len(trackURIs)%50):
						tracks.append(trackURIs[l+offset])
				else:
					tracks.append(trackURIs[j+offset])
			
			print("Adding tracks no.", trackno1, "to", trackno2)
			spotify.user_playlist_add_tracks(user.username, playlistID, tracks)
			trackno1 = offset+1
			if (i+1) == iterations:
				trackno2 = offset + (len(trackURIs)%50)
			else:
				trackno2 = offset+50
			offset+=50

	playlistName = user.playlist
	def playlistCreate(playlistname):
		playlist = spotify.user_playlist_create(user.username, playlistname, public=False)
		playlistID = playlist['id']
		return playlistID

	def artistTrackFinder(uri):
		trackUriList = []
		items = spotify.artist_top_tracks(uri)
		tracks = items['tracks']
		for track in tracks:
			trackUriList.append(track['uri'])
		return trackUriList

	addlist = artistRunner(artistList, 0)
	trackList = []
	k=0

	for artisturi in addlist:
		tempList = []
		tempList = artistTrackFinder(artisturi)
		trackList.extend(tempList)

	playlistid = playlistCreate(playlistName)

	noDupes = list(set(trackList))

	with fuckit:
		addTracks(noDupes, playlistid)

	print(len(noDupes), "tracks added to", playlistName)

if __name__ == '__main__':
	main()