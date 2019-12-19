import os
from twilio.rest import Client


class Twilio:
    def __init__(self):
        account_sid    = os.environ.get('TWILIO_ACCOUNT_SID')
        auth_token     = os.environ.get('TWILIO_AUTH_TOKEN')
        self.client    = Client(account_sid, auth_token)
        self.sender    = '+19157012107',
        self.recipient = '+18043639816'

    def sendAlert(self, ftemp, ctemp):
        body = "Your home brew has reached the goal temperature of " + \
                str(ftemp) + chr(176) + "F and " + str(ctemp) + chr(176) + "C!"
        
        try:       
            message = client.messages \
                        .create(
                            body=body,
                            from_=self.sender,
                            to=self.recipient
                        )
            return True
        except:
            return False
