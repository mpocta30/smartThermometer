import os
from twilio.rest import Client


class Twilio:
    def __init__(self):
        account_sid    = "AC9bee1a68881895400bec3c57357a5bc0"
        auth_token     = "3efe8e0c483fd3805e9ad887d4b0c7b2"
        self.client    = Client(account_sid, auth_token)
        self.sender    = '+19157012107',
        self.recipient = '+18043639816'

    def sendAlert(self, ftemp, ctemp):
        body = "Your home brew has reached the goal temperature of " + \
                str(ftemp) + chr(176) + "F and " + str(ctemp) + chr(176) + "C!"
        
        try:       
            message = self.client.messages \
                        .create(
                            body=body,
                            from_=self.sender,
                            to=self.recipient
                        )
            return True
        except:
            return False
