import os
from twilio.rest import Client


class Twilio:
    def __init__(self):
        account_sid    = "c6097bdfb37ec8aa8b7972ef95ab2f51"
        auth_token     = "000b0531325f0c663648a1ce738d005f"
        self.client    = Client(account_sid, auth_token)
        self.sender    = 'SENDER_PHONE_#',
        self.recipient = 'RECEIPIENT_PHONE_#'

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
