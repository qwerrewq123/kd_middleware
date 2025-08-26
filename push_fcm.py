import os
import firebase_admin
from firebase_admin import credentials
from firebase_admin import messaging
from typing import List
import logging
from fcm_dto import FcmDto

class PushFcm:
    def __init__(self):
        self.path = os.path.join(os.getcwd(), 'simbizmall-5717f-firebase-adminsdk-45is2-597a4fbefc.json')
        
        # Firebase 초기화 (처음 호출시에만)
        if not firebase_admin._apps:
            cred = credentials.Certificate(self.path)
            firebase_admin.initialize_app(cred, {
                'databaseURL': 'https://simbizmall-5717f.firebaseio.com'
            })

    def push(self, fcm_list: List[FcmDto]) -> bool:
        try:
            success_count = 0
            fail_count = 0
            
            for fcm in fcm_list:
                try:
                    # 데이터 페이로드 생성
                    data = {
                        'key1': 'value1',
                        'key2': 'value2'
                    }
                    
                    logging.info(f"test title: {fcm.title}")
                    logging.info(f"test content: {fcm.content}")
                    
                    # 메시지 생성
                    message = messaging.Message(
                        data=data,
                        notification=messaging.Notification(
                            title=fcm.title,
                            body=fcm.content
                        ),
                        android=messaging.AndroidConfig(
                            ttl=3600,
                            priority='normal',
                            notification=messaging.AndroidNotification(
                                icon='stock_ticker_update',
                                color='#f45342',
                                sound='default'
                            )
                        ),
                        apns=messaging.APNSConfig(
                            payload=messaging.APNSPayload(
                                aps=messaging.Aps(
                                    sound='default'
                                )
                            )
                        ),
                        token=fcm.token_id
                    )
                    
                    # 메시지 전송
                    response = messaging.send(message)
                    logging.info(f"Successfully sent message: {response}")
                    success_count += 1
                    
                except Exception as e:
                    logging.info(f"Failed to send message to {fcm.token_id}: {e}")
                    fail_count += 1
            
            logging.info(f"Push completed - Success: {success_count}, Failed: {fail_count}")
            return fail_count == 0


        except Exception as e:
            logging.info(f"Push error: {e}")
            return False




