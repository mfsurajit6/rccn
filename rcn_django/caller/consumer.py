import json
from time import sleep
from multiprocessing import Process
from decouple import config
from ringcentral.subscription import Events
from ringcentral import SDK

from channels.generic.websocket import WebsocketConsumer
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync


class CallerConsumer(WebsocketConsumer):

    def connect(self):
        self.pubnubcall();
        self.room_name = 'callers';
        self.room_group_name = 'callers_group'

        async_to_sync(self.channel_layer.group_add)(
            self.room_group_name,
            self.channel_name
        )
        self.accept()

    def disconnect(self, code):
        async_to_sync(self.channel_layer.group_discard)(
            self.room_group_name,
            self.channel_name
        )

    def receive(self, text_data):
        text_data = json.dumps(text_data)
        text_data_json = json.loads(text_data)
        message = text_data_json.get('uuid')
        async_to_sync(self.channel_layer.group_send)(
            self.room_group_name, {
                "type": 'send_message_to_frontend',
                "message": message
            }
        )

    def send_message_to_frontend(self, event):
        message = event['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

    def event_trigger(self, data, ajax=False):
        print(data)
        caller_number = ""
        status = ""
        if not ajax:
            caller_number = data['body']['parties'][0]['from']['phoneNumber']
            status = data['body']['parties'][0]['status']['code']
            sequence = data['body']['sequence']

            # status == "Answered" or "Proceeding":
            if status == "Proceeding":
                status = "Ringing"
            elif status == "Disconnected" or status == "Voicemail":
                status = "Disconnected"
        else:
            caller_number = data["number"]
            status = data["status"]
            self.channel_layer = get_channel_layer()

        async_to_sync(self.channel_layer.group_send)(
            'callers_group',
            {
                'type': 'send_message_to_frontend',
                'message': json.dumps({"number": caller_number, "status": status})
            }
        )

    def pubnub(self):
        try:
            s = self.rcsdk.create_subscription()
            s.add_events([
                "/restapi/v1.0/account/~/telephony/sessions",
                "/restapi/v1.0/account/~/extension/~/presence?detailedTelephonyState=true&sipData=true"
            ])
            s.on(Events.notification, self.event_trigger)
            res = s.register()
            try:
                print("Wait for notification...")
            except Exception as e:
                print(e)
            while True:
                sleep(0.1)

        except KeyboardInterrupt:
            print("Pubnub listener stopped...")

    def pubnubcall(self):
        self.client_id = config('RINGCENTRAL_CLIENTID')
        self.client_secret = config('RINGCENTRAL_CLIENTSECRET')
        self.server = config('RINGCENTRAL_SERVER')

        self.username = config('RINGCENTRAL_USERNAME')
        self.password = config('RINGCENTRAL_PASSWORD')
        self.extension = config('RINGCENTRAL_EXTENSION')

        self.rcsdk = SDK(self.client_id, self.client_secret, self.server)
        platform = self.rcsdk.platform()
        platform.login(self.username, self.extension, self.password)

        p = Process(target=self.pubnub)
        try:
            p.start()
        except KeyboardInterrupt:
            p.terminate()
            print("Stopped by User")
