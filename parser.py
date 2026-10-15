import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent

import time

ua = UserAgent()


cookies = {
    'csv': '2',
    'edgebucket': 'EccAQ9SaD0Uu7lUl5z',
    'loid': '000000000m7meb3bj5.2.1697864792065.Z0FBQUFBQnA0OHVORWN0QnNZUjlHRmxjM3N5THRsN2ZiNURlMVdXY3ZwclNmYTVjYVVEVmtvMS1OOGI2RlpRX1FmNmJacnJnRnRqTWhjV2NUU2t4UnVzWkFsSERKUVVlVmcwdXV3X1FBTFNnaWx6eWpicWRZMHNLajNnbDFzNHNGVEpUSlJFbF9qWlc',
    't2_m7meb3bj5_recentclicks3': 't3_1dhho5x',
    'reddit_supported_media_codecs': 'video/avc%2Cvideo/vp9',
    'eu_cookie_opted': '1',
    'ads_cookie': '1',
    'reddit_session': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml9tN21lYjNiajUiLCJleHAiOjE4MDcxMTc4NjguNjUwNTExLCJpYXQiOjE3OTE0Nzk0NjguNjUwNTExLCJqdGkiOiJua3pDaXF2VUc0ZS1paDVOMFlhQnRFa2R3Tllub3ciLCJhdCI6MSwiY2lkIjoiY29va2llIiwibGNhIjoxNjk3ODY0NzkyMDY1LCJzY3AiOiJlSndBQWdEOV8xdGRBd0FCRlFDNSIsImZsbyI6MywiYW1yIjpbInNzbyJdfQ.Iaklofr9JP-dYg4mjgdZZDT3gmDgCh8YqdJlMAmEe1HbusviHddM5YMjS0_HAzF9Vz0BOWQatAvL5R8hJ-4qkwlbBKjInC8TCNaNxRfWXPsgRl5fkUQ5ys_VBBOdqfRzGzvS7d0kAwgIIc31yt3zld5uDvgjUPG07_SH8X9bNmDO0SsV6rD-kkk_lB88eTPIm_mduliuAWrvy9mf68663r7s2zH3xjNpZEERtYB80YnFRwT2qW866GgW9dw3tOAjRHLSzsocv2Nl6kO1E5bK6fRc59uYquep6ENReT_mHtFzTZPr9Q4lPnwiuXEcklEiUZu5qa71ggXLqXeUhdTEMg',
    'reddit_chat_view': 'closed',
    'csrf_token': 'a0a10358214046fe63d64c35026638b0',
    'token_v2': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwczovL3d3dy5yZWRkaXQuY29tIiwic3ViIjoidXNlciIsImV4cCI6MTc5MjAwMTU5My4zMDU1NDUsImlhdCI6MTc5MTkxNTE5My4zMDU1NDUsImp0aSI6Im1aanpqd201QWhrRlEwODJrSlZXeHIxeFpZVEhGUSIsImNpZCI6IjBSLVdBTWh1b28tTXlRIiwibGlkIjoidDJfbTdtZWIzYmo1IiwiYWlkIjoidDJfbTdtZWIzYmo1IiwiYXQiOjEsImxjYSI6MTY5Nzg2NDc5MjA2NSwic2NwIjoiZUp4a2tWSE8zREFJaE9fQ3MwX1FxMVJWNWRoa0Z6VTJFZUNzOXZZVldaT045TDhOOEdVTWs5LVFxMklsZy1SS01GZElnQzNUQmdsMkl1LVh3cU9mUk84OGVzR0czUlFTRk1GYTZaVFRZOTB5Q1NSNGtockxHeEpReFc1a0xqYzZzT1dlSHdnSkd0ZkNmYVhIcFUxb0djYmlkbzFyV0RXdUcwOXE3dFc0ZHJicHd2YkUtR1pudFNrVnRfV2pUUEs2VXZrVUxfcm5ON1czanVXN19TNTBaTU9HcXZtQjNwbEpDTzRzZnJybXc5OVRrMUZzQ0ZhMTkzYVNPcFoyM3E1ajBTSzBPSGQ4MXZQWFpqSXVwMmw1WnZ0MTF5OGh3MXVlMXpEcUFHYXNNWTh5eHBGMXpLODZnTVlWSlJ0TEVOOUdJRmN1Zl8yWFlMODJfVG00ZmVLSDcwYmM5WWJmbW9GNkxrR2MtaVZrQ0hfLUR3QVExZVRSIiwicmNpZCI6IkhfejRXQ3VOQ1pPU3llSWlPQ0lPeDRLZlFQcHZiZDdtekNpVm5zeGNJREEiLCJmbG8iOjJ9.ApRZ8pWeW8QQ0YyszHt6auG4oxhOD7j9hDcIYo2hB56DebHKeYozfXLjSdPkhIZRjpYpePJaRBSQi4AXeeH4Y9r6dRQuHr1sa0DySMwZ7JdAukANDCzHwBSsihlApL8SoS41jB1pM3C5jIopLG75Kl86sdySB49ckhVSUKV0XXhUAePb4F0XSiOtSM8SNyVkBNKksLL3DJ3VUC8VYllS0ZnGw9knipaSSKI9YEtjBzKPYRbzxd-iSFbjIoKosngIWWHR7XTRc1aY7WkmATuoUGdFTmbBvcrIUsbpKSUpr3sMIJcJeOanaH1-4HOxQUPBDWPQU3yUarN078dcJg0A1A',
    'g_state': '{"i_l":0,"i_ll":1791915194117,"i_e":{"enable_itp_optimization":24},"i_et":1791915194117,"i_b":"ZzknHrILD9yrZSIFJh1U8zk4Ckxr/lfDaWWiCnq3B+I"}',
    'session_tracker': 'jmenpqradiirgblqjd.0.1791915226458.Z0FBQUFBQnF6blRhNUNFaHdxX1VVTnpmbEUwbWFrQWZOeGJaWmp4MTBjMjBSQndCNk9VNmJuaHNnWjRRZmlTVmlRVGFKWGZkdzhINjlUbWloSkJyVDdxa05vcjYzd2ZwdzFBLXhyS3VoWVlnaFpQSjFMTnZaQWh1SnF4cmNUdkdIWHlraG5FdGJLWXo',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,ru-RU;q=0.6',
    'available-dictionary': ':m4DZoH8SVUAY7ntSfCk3ER+klA7NWrA0kZyi8XDjNuQ=:',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'referer': 'https://www.google.com/',
    'sec-ch-ua': '"Microsoft Edge";v="155", "Chromium";v="155", "Not(A:Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/155.0.0.0 Safari/537.36 Edg/155.0.0.0',
    # 'cookie': 'csv=2; edgebucket=EccAQ9SaD0Uu7lUl5z; loid=000000000m7meb3bj5.2.1697864792065.Z0FBQUFBQnA0OHVORWN0QnNZUjlHRmxjM3N5THRsN2ZiNURlMVdXY3ZwclNmYTVjYVVEVmtvMS1OOGI2RlpRX1FmNmJacnJnRnRqTWhjV2NUU2t4UnVzWkFsSERKUVVlVmcwdXV3X1FBTFNnaWx6eWpicWRZMHNLajNnbDFzNHNGVEpUSlJFbF9qWlc; t2_m7meb3bj5_recentclicks3=t3_1dhho5x; reddit_supported_media_codecs=video/avc%2Cvideo/vp9; eu_cookie_opted=1; ads_cookie=1; reddit_session=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml9tN21lYjNiajUiLCJleHAiOjE4MDcxMTc4NjguNjUwNTExLCJpYXQiOjE3OTE0Nzk0NjguNjUwNTExLCJqdGkiOiJua3pDaXF2VUc0ZS1paDVOMFlhQnRFa2R3Tllub3ciLCJhdCI6MSwiY2lkIjoiY29va2llIiwibGNhIjoxNjk3ODY0NzkyMDY1LCJzY3AiOiJlSndBQWdEOV8xdGRBd0FCRlFDNSIsImZsbyI6MywiYW1yIjpbInNzbyJdfQ.Iaklofr9JP-dYg4mjgdZZDT3gmDgCh8YqdJlMAmEe1HbusviHddM5YMjS0_HAzF9Vz0BOWQatAvL5R8hJ-4qkwlbBKjInC8TCNaNxRfWXPsgRl5fkUQ5ys_VBBOdqfRzGzvS7d0kAwgIIc31yt3zld5uDvgjUPG07_SH8X9bNmDO0SsV6rD-kkk_lB88eTPIm_mduliuAWrvy9mf68663r7s2zH3xjNpZEERtYB80YnFRwT2qW866GgW9dw3tOAjRHLSzsocv2Nl6kO1E5bK6fRc59uYquep6ENReT_mHtFzTZPr9Q4lPnwiuXEcklEiUZu5qa71ggXLqXeUhdTEMg; reddit_chat_view=closed; csrf_token=a0a10358214046fe63d64c35026638b0; token_v2=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwczovL3d3dy5yZWRkaXQuY29tIiwic3ViIjoidXNlciIsImV4cCI6MTc5MjAwMTU5My4zMDU1NDUsImlhdCI6MTc5MTkxNTE5My4zMDU1NDUsImp0aSI6Im1aanpqd201QWhrRlEwODJrSlZXeHIxeFpZVEhGUSIsImNpZCI6IjBSLVdBTWh1b28tTXlRIiwibGlkIjoidDJfbTdtZWIzYmo1IiwiYWlkIjoidDJfbTdtZWIzYmo1IiwiYXQiOjEsImxjYSI6MTY5Nzg2NDc5MjA2NSwic2NwIjoiZUp4a2tWSE8zREFJaE9fQ3MwX1FxMVJWNWRoa0Z6VTJFZUNzOXZZVldaT045TDhOOEdVTWs5LVFxMklsZy1SS01GZElnQzNUQmdsMkl1LVh3cU9mUk84OGVzR0czUlFTRk1GYTZaVFRZOTB5Q1NSNGtockxHeEpReFc1a0xqYzZzT1dlSHdnSkd0ZkNmYVhIcFUxb0djYmlkbzFyV0RXdUcwOXE3dFc0ZHJicHd2YkUtR1pudFNrVnRfV2pUUEs2VXZrVUxfcm5ON1czanVXN19TNTBaTU9HcXZtQjNwbEpDTzRzZnJybXc5OVRrMUZzQ0ZhMTkzYVNPcFoyM3E1ajBTSzBPSGQ4MXZQWFpqSXVwMmw1WnZ0MTF5OGh3MXVlMXpEcUFHYXNNWTh5eHBGMXpLODZnTVlWSlJ0TEVOOUdJRmN1Zl8yWFlMODJfVG00ZmVLSDcwYmM5WWJmbW9GNkxrR2MtaVZrQ0hfLUR3QVExZVRSIiwicmNpZCI6IkhfejRXQ3VOQ1pPU3llSWlPQ0lPeDRLZlFQcHZiZDdtekNpVm5zeGNJREEiLCJmbG8iOjJ9.ApRZ8pWeW8QQ0YyszHt6auG4oxhOD7j9hDcIYo2hB56DebHKeYozfXLjSdPkhIZRjpYpePJaRBSQi4AXeeH4Y9r6dRQuHr1sa0DySMwZ7JdAukANDCzHwBSsihlApL8SoS41jB1pM3C5jIopLG75Kl86sdySB49ckhVSUKV0XXhUAePb4F0XSiOtSM8SNyVkBNKksLL3DJ3VUC8VYllS0ZnGw9knipaSSKI9YEtjBzKPYRbzxd-iSFbjIoKosngIWWHR7XTRc1aY7WkmATuoUGdFTmbBvcrIUsbpKSUpr3sMIJcJeOanaH1-4HOxQUPBDWPQU3yUarN078dcJg0A1A; g_state={"i_l":0,"i_ll":1791915194117,"i_e":{"enable_itp_optimization":24},"i_et":1791915194117,"i_b":"ZzknHrILD9yrZSIFJh1U8zk4Ckxr/lfDaWWiCnq3B+I"}; session_tracker=jmenpqradiirgblqjd.0.1791915226458.Z0FBQUFBQnF6blRhNUNFaHdxX1VVTnpmbEUwbWFrQWZOeGJaWmp4MTBjMjBSQndCNk9VNmJuaHNnWjRRZmlTVmlRVGFKWGZkdzhINjlUbWloSkJyVDdxa05vcjYzd2ZwdzFBLXhyS3VoWVlnaFpQSjFMTnZaQWh1SnF4cmNUdkdIWHlraG5FdGJLWXo',
}

import os
names = set(os.listdir("images"))
after = ""
count = 0
while count < 5000:
    time.sleep(1)
    if after != "":
        response = requests.get(f"https://www.reddit.com/r/hardimages2/top.json?t=all&limit=100&after={after}", cookies=cookies, headers=headers)
    else:
        response = requests.get(f"https://www.reddit.com/r/hardimages2/top.json?t=all&limit=100", cookies=cookies, headers=headers)
    if response.status_code == 200:
        data = response.json()
        after = data["data"]["after"]
        names = set(os.listdir("images"))
        for child in data["data"]["children"]:
            try:
                image_url = child["data"]["url_overridden_by_dest"]
            except KeyError:
                print(f"Не нашел ключ url_overridden_by_dest в {response.url}")
            if image_url.split("/")[-1] in names:
                print(f"{image_url.split("/")[-1]} уже был")
                continue
            try:
                time.sleep(1)
                img_response = requests.get(image_url)

                if img_response.status_code == 200:
                    filename = image_url.split("/")[-1]
                    with open(f"images/{filename}", "wb") as file:
                        file.write(img_response.content)

                    print(f"Успешно: {image_url}")
                    count += 1
                else:
                    print(f"Пропущено (сервер вернул не картинку): {image_url}")

            except Exception as e:
                print(f"Ошибка при скачивании {image_url}: {e}")
            
        

        print(count)
    else:
        print(f"Ошибка при запросе: {response.status_code}")
