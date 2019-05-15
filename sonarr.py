import requests
import json

class SonarrApi:
    baseUrl = ""
    apiKey = ""

    indexer = ""
    network = ""
    episodeId = None

    def __init__(self, baseUrl, apiKey):
        self.baseUrl = baseUrl
        self.apiKey = apiKey

    def getEpisodeId(self, seriesId, episodeFileId):
        if not seriesId or not episodeFileId:
            return ""
        payload = {"apikey": self.apiKey, "seriesId": seriesId}
        response = requests.get(self.baseUrl + "/episode", params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = json.loads(response.text)
        for record in data:
            record = dict(record)
            recordEpisodeFileId = record.get("episodeFileId", None)
            if recordEpisodeFileId == int(episodeFileId):
                return record.get("id", "")
        return ""


    def setIndexer(self, episodeId, downloadId):
        if not episodeId or not downloadId:
            return
        payload = {"apikey": self.apiKey, "episodeId": episodeId, "sortKey": "date", "sortDir": "desc"}
        response = requests.get(self.baseUrl + "/history", params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        for record in data.get("records", []):
            record = dict(record)
            recordDownloadId = record.get("downloadId", None)
            if recordDownloadId == downloadId:
                self.network = record.get("series", {}).get("network", "")
                indexer = record.get("data", {}).get("indexer")
                if indexer is not None:
                    self.indexer = indexer
                    return

    def loadData(self, seriesId, episodeFileId, downloadId):
        self.episodeId = self.getEpisodeId(seriesId, episodeFileId)
        self.setIndexer(self.episodeId, downloadId)

    def getWantedMissingEpisodes(self):
        payload = {"apikey": self.apiKey, "pageSize": 100, "sortKey": "series.title"}
        response = requests.get(self.baseUrl + "/wanted/missing", params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        data = dict(json.loads(response.text))
        recordIds = []
        for record in data.get("records", []):
            record = dict(record)
            if record.get("monitored", False):
                recordId = record.get("id", None)
                if recordId is not None:
                    recordIds.append(recordId)
        return recordIds

    def forceMissingEpisodeSearch(self):
        episodes = self.getWantedMissingEpisodes()
        payload = {"apikey": self.apiKey, "name": 100, "episodeIds": episodes}
        headers = {'Content-type': 'application/json', 'Accept': 'text/plain', 'X-Api-Key': self.apiKey}
        response = requests.post(self.baseUrl + "command", data=json.dumps(payload), headers=headers)
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def getEpisode(self):
        if self.episodeId is None:
            return {}
        payload = {"apikey": self.apiKey}
        response = requests.get(self.baseUrl + "/episode/" + str(self.episodeId), params=payload)
        if response.status_code != 200:
            raise ValueError(
                'Request returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )
        return json.loads(response.text)

    def unmonitorEpisode(self, episode):
        episode["monitored"] = False
        headers = {'Content-type': 'application/json', 'X-Api-Key': self.apiKey}
        response = requests.put(self.baseUrl + "/episode/" + str(episode["id"]), data=json.dumps(episode), headers=headers)
        if response.status_code != 202:
            raise ValueError(
                'Request returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    def unmonitorMovieIfNeeded(self, event):
        if event == "Download":
            episode = self.getEpisode()
            if episode.get("monitored", False):
                self.unmonitorEpisode(episode)
