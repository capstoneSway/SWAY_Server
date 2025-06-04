from firebase_admin import messaging

def send_fcm_notification(token, title, body, image_url=None):
    # FCM 푸시 메시지 설정
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body,
        ),
        data={
            'image_url': image_url or '',  # 이미지 URL이 없으면 빈 문자열 전달
        },
        token=token,
    )
    
    try:
        # FCM 서버로 푸시 알림 전송
        response = messaging.send(message)
        print("FCM 전송 성공:", response)
    except Exception as e:
        # 에러 발생 시 처리
        print("FCM 전송 실패:", e)