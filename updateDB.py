import sys
from time import sleep
from tempDB import tempDB
from ds18b20 import thermSensor
from datetime import datetime
from twilio_sms import Twilio

# Initialize db connection
db = tempDB('mylib', 'temperatures', 'read')
temp = thermSensor()
sms = Twilio()

while True:
    try:
        # Get read value
        read = db.getRead()

        if read:
            # Get current temp reading
            newC, newF = temp.getTemp()

            # Get alert data
            alert = db.getAlert()
            unit = alert['unit']
            threshold = alert['threshold']

            if alert['alert_active']:
                if (unit == 'fahr' and newF >= threshold) or (unit == 'cels' and newC >= threshold):
                    sms.sendAlert(newF, newC)
                    newValues = {'$set': {'alert_active': False}}
                    db.updateAlert(newValues)
                    


            # Current datetime
            now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            now = datetime.strptime(now, '%Y-%m-%d %H:%M:%S')

            # Add temp to database
            db.insertTemp(now, newC, newF)
            print("Added " + str(newF) + chr(176) + 'F and ' +\
                    str(newC) + chr(176) + 'C to the database.')
        sleep(5)
    except KeyboardInterrupt:
        break

print('Goodbye!')
sys.exit()