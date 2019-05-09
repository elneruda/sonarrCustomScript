#!/usr/bin/env python2.7

from slack import Slack, SlackMessage
from sonarr import SonarrApi
from tmdb import TmdbApi
from tvmaze import TvMazeApi
import json
import requests
import os
import argparse

def _argparse():
    parser = argparse.ArgumentParser(
        description='Sonarr Custom Script : perform Slack rich notification'
    )
    parser.add_argument(
        '--webhook-url', '-wu',
        help='Slack webhook url'
    )
    parser.add_argument(
        '--sonarr-url', '-se',
        help='Sonarr API endpoint : https://xxxx/api'
    )
    parser.add_argument(
        '--sonarr-key', '-sk',
        help='Sonarr API key, find it on Sonarr > Settings > General'
    )
    parser.add_argument(
        '--tmdb-key', '-tk',
        help='TMDB API Key, register app on tmdb to obtain API Key'
    )
    args = parser.parse_args()
    return args


args = _argparse()

networkLogoUrl = None
tmdb = TmdbApi(args.tmdb_key)
networkLogoUrl = tmdb.getNetworkLogoFullPath(os.environ.get("sonarr_series_tvdbid"))

sonarr = SonarrApi(args.sonarr_url, args.sonarr_key)
sonarr.loadData(os.environ.get("sonarr_series_id", ""), os.environ.get("sonarr_episodefile_id", ""), os.environ.get("sonarr_download_id", ""))

networkName = tmdb.normalizeNetworkName(sonarr.network)
tmdb.downloadImageIfNeeded(networkLogoUrl, networkName)

season = os.environ.get("sonarr_episodefile_seasonnumber", "")
episode = os.environ.get("sonarr_episodefile_episodenumbers", "")

link = ""
tvMaze = TvMazeApi(os.environ.get("sonarr_series_tvmazeid", ""))
link = tvMaze.getEpisodeUrl(season, episode)

message = SlackMessage(args.webhook_url)
message.package("*" +os.environ.get("sonarr_series_title", "") + " - " + season +"x"+ episode +" - " + os.environ.get("sonarr_episodefile_episodetitles", "") + "* ["+os.environ.get("sonarr_episodefile_quality", "")+"]")
message.constructor("`"+ sonarr.indexer +"` _" + os.environ.get("sonarr_episodefile_releasegroup", "") + "_ " + sonarr.network)
message.link(link)
message.iconUrl = networkLogoUrl
message.save()

message.notify()