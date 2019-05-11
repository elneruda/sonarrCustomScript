import json
import requests
import os

class TmdbApi:
    baseURL = "https://api.themoviedb.org/3"
    imageURL = "http://image.tmdb.org/t/p"
    imageSize = "w185"
    apiKey = ""

    networkName = ""
    logoPath = ""

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
        network = dict(next(iter(data.get("networks", [])), None))
        self.networkName = network.get("name")
        return network.get("logo_path")
    
    def normalizeNetworkName(self, name=None):
        if not self.logoPath:
            return
        if name is None:
            name = self.networkName
            if name is None:
                return
        fileExtension = os.path.splitext(self.logoPath)[1]
        return str(name).lower().translate(None, "(){}<>[]").replace(" ", "-") + fileExtension

    def getNetworkLogoFullPath(self, tmdbId):
        showId = self.getShowId(tmdbId)
        self.logoPath = self.getNetworkLogoPath(str(showId))
        if not self.logoPath:
            return None
        return self.imageURL+"/"+self.imageSize+self.logoPath

    def downloadImageIfNeeded(self, url, filename, relativePath="networkImages/"):
        if url is None or filename is None:
            return
        absolutePath = os.path.dirname(__file__) + "/" + relativePath
        filepath = absolutePath+str(filename)
        if os.path.isfile(filepath):
            return
        self.downloadImage(url, filepath)
    
    def downloadImage(self, url, filepath):
        img_data = requests.get(url).content
        with open(filepath, 'wb') as handler:
            handler.write(img_data)