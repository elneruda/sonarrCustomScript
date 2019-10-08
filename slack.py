import json
import requests

class Slack:

    baseUrl = ""

    def __init__(self, baseUrl):
        self.baseUrl = baseUrl

    def notify(self, message, iconUrl=None, iconEmoji=None):
        payload={"text": message, "unfurl_links": True, "mrkdwn": True}
        if (iconEmoji is not None):
            payload["icon_emoji"] = iconEmoji
        elif (iconUrl is not None):
            payload["icon_url"] = iconUrl
        jsonData = json.dumps(payload)
        response = requests.post(
            self.baseUrl,
            data=jsonData,
            headers={'Content-Type': 'application/json'}
        )
        if response.status_code != 200:
            raise ValueError(
                'Request to slack returned an error %s, the response is:\n%s'
                % (response.status_code, response.text)
            )

    
class SlackMessage(object):

    _webhookUrl = ""
    
    _package = ":package: "
    _constructor = ":male-construction-worker: "
    _link = ":books: "
    iconUrl = None
    iconEmoji = None

    _message = []

    def __init__(self, webhookUrl):
        self._webhookUrl = webhookUrl

    def save(self):
        self._message.append(self._package)
        self._message.append(self._constructor)
        self._message.append(self._link)


    def __repr__(self):
        return "\n".join(self._message)

    def newLine(self, value):
        self._message.append(value)

    def package(self, value):
        self._package+=value
    
    def constructor(self, value):
        self._constructor+=value

    def link(self, value):
        self._link+=value

    def notify(self):
        Slack(self._webhookUrl).notify(str(self), self.iconUrl, self.iconEmoji)
