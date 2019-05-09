import requests
import json

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