import requests
import json
import time
import hmac
import hashlib
import base64


def push_to_dingtalk(webhook, secret, content):
    # 1. 生成签名和时间戳
    timestamp = str(round(time.time() * 1000))
    sign = generate_signature(secret, timestamp)

    # 2. 构建请求URL
    url = f"{webhook}&timestamp={timestamp}&sign={sign}"

    # 3. 构造消息体
    message = {
        "msgtype": "text",
        "text": {"content": content},
        "at": {"isAtAll": False}  # 不@所有人
    }

    # 4. 发送请求
    headers = {'Content-Type': 'application/json'}
    try:
        response = requests.post(url, data=json.dumps(message), headers=headers)
        return response.json()
    except Exception as e:
        return {"error": str(e)}


def generate_signature(secret, timestamp):
    string_to_sign = f"{timestamp}\n{secret}"
    hash_val = hmac.new(secret.encode('utf-8'),
                        string_to_sign.encode('utf-8'),
                        hashlib.sha256).digest()
    return base64.b64encode(hash_val).decode('utf-8')


# 使用示例
if __name__ == "__main__":
    # 替换为你的实际Webhook和Secret
    webhook_url = "https://oapi.dingtalk.com/robot/send?access_token=6db38ae5dd1e052b2619c22347de61972c414654252f26fdee26aedf377d8bb6"
    secret_key = "SECd10b911a5e56411137193e442dc393b57ea26d9832e45e7177d190d08fb80f72"

    # 推送消息
    result = push_to_dingtalk(webhook_url, secret_key, "这是一条测试消息，当前时间是：2025-05-15 15:50:51")
    print("推送结果:", result)
