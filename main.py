#!/usr/bin/env python2.7

from slack import Slack
from slack import SlackMessage
from sonarr import SonarrApi
import json
import requests
import os
import sys

if len(sys.argv) < 5:
    print ("You must set arguments!!!")
    exit()

webhook_url = sys.argv[1]
sonarrApiBaseUrl = sys.argv[2]
sonarrApiKey = sys.argv[3]
tmdbApiKey = sys.argv[4]
    
class TvMazeApi:
    baseUrl = ""

    def __init__(self, tvmazeId):
        if tvmazeId is None:
            return
        self.baseUrl = "http://api.tvmaze.com/shows/"+tvmazeId
    
    def getEpisodeUrl(self, season, number):
        if not season or not number:
            return ""
        payload = {"season": season, "number": number}
        response = requests.get(self.baseUrl + "/episodebynumber", params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        return data.get("url", "")

        

class TmdbApi:
    baseURL = "https://api.themoviedb.org/3"
    imageURL = "http://image.tmdb.org/t/p"
    imageSize = "w185"
    apiKey = ""

    def __init__(self, apiKey):
        if apiKey is None:
            return
        self.apiKey = apiKey

    def getShowId(self, tmdbId):
        if tmdbId is None:
            return None
        payload = {"api_key": self.apiKey, "external_source": "tvdb_id"}
        response = requests.get(self.baseURL + "/find/" + tmdbId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        return dict(next(iter(data.get("tv_results", [])), {})).get("id", None)

    def getNetworkLogoPath(self, showId):
        if showId is None or showId == str(None):
            return None
        payload = {"api_key": self.apiKey}
        response = requests.get(self.baseURL + "/tv/" + showId, params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        return dict(next(iter(data.get("networks", [])), None)).get("logo_path", "")

    def getNetworkLogoFullPath(self, tmdbId):
        showId = self.getShowId(tmdbId)
        logoPath = self.getNetworkLogoPath(str(showId))
        if not logoPath:
            return None
        return self.imageURL+"/"+self.imageSize+logoPath


networkLogoUrl = None
tmdb = TmdbApi(tmdbApiKey)
networkLogoUrl = tmdb.getNetworkLogoFullPath(os.environ.get("sonarr_series_tvdbid"))

sonarr = SonarrApi(sonarrApiBaseUrl, sonarrApiKey)
sonarr.loadData(os.environ.get("sonarr_series_id", ""), os.environ.get("sonarr_episodefile_id", ""), os.environ.get("sonarr_download_id", ""))

season = os.environ.get("sonarr_episodefile_seasonnumber", "")
episode = os.environ.get("sonarr_episodefile_episodenumbers", "")

link = ""
tvMaze = TvMazeApi(os.environ.get("sonarr_series_tvmazeid", ""))
link = tvMaze.getEpisodeUrl(season, episode)

message = SlackMessage(webhook_url)
message.package("*" +os.environ.get("sonarr_series_title", "") + " - " + season +"x"+ episode +" - " + os.environ.get("sonarr_episodefile_episodetitles", "") + "* ["+os.environ.get("sonarr_episodefile_quality", "")+"]")
message.constructor("`"+ sonarr.indexer +"` _" + os.environ.get("sonarr_episodefile_releasegroup", "") + "_ " + sonarr.network)
message.link(link)
message.iconUrl = networkLogoUrl
message.save()
message.newLine("icon url : " + str(networkLogoUrl))

message.notify()