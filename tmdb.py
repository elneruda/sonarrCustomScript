import json
import requests

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

    def downloadImage(self, url, to):
        img_data = requests.get(url).content
        with open('image_name.jpg', 'wb') as handler:
            handler.write(img_data)