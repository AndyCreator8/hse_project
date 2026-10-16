import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import json
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
    'csrf_token': 'e3a8bed97ea3fb2bd76c5d111c3d2406',
    'token_v2': 'eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwczovL3d3dy5yZWRkaXQuY29tIiwic3ViIjoidXNlciIsImV4cCI6MTc5MjI2NDMxMS43Mzg3NDMsImlhdCI6MTc5MjE3NzkxMS43Mzg3NDMsImp0aSI6IkdqNDV0R0NyNTRjaENzTGlpeC1ZaVlxNmlVOEJlUSIsImNpZCI6IjBSLVdBTWh1b28tTXlRIiwibGlkIjoidDJfbTdtZWIzYmo1IiwiYWlkIjoidDJfbTdtZWIzYmo1IiwiYXQiOjEsImxjYSI6MTY5Nzg2NDc5MjA2NSwic2NwIjoiZUp4a2tWSE8zREFJaE9fQ3MwX1FxMVJWNWRoa0Z6VTJFZUNzOXZZVldaT045TDhOOEdVTWs5LVFxMklsZy1SS01GZElnQzNUQmdsMkl1LVh3cU9mUk84OGVzR0czUlFTRk1GYTZaVFRZOTB5Q1NSNGtockxHeEpReFc1a0xqYzZzT1dlSHdnSkd0ZkNmYVhIcFUxb0djYmlkbzFyV0RXdUcwOXE3dFc0ZHJicHd2YkUtR1pudFNrVnRfV2pUUEs2VXZrVUxfcm5ON1czanVXN19TNTBaTU9HcXZtQjNwbEpDTzRzZnJybXc5OVRrMUZzQ0ZhMTkzYVNPcFoyM3E1ajBTSzBPSGQ4MXZQWFpqSXVwMmw1WnZ0MTF5OGh3MXVlMXpEcUFHYXNNWTh5eHBGMXpLODZnTVlWSlJ0TEVOOUdJRmN1Zl8yWFlMODJfVG00ZmVLSDcwYmM5WWJmbW9GNkxrR2MtaVZrQ0hfLUR3QVExZVRSIiwicmNpZCI6IkhfejRXQ3VOQ1pPU3llSWlPQ0lPeDRLZlFQcHZiZDdtekNpVm5zeGNJREEiLCJmbG8iOjJ9.jEHCemBmDEk86BbOxKLqt6T5zXq1n790wGTfSwQQLJz5g1EKUO6QHWww9PRAV-EmPPmeo4o0WdnoAAEYbu8ceKyiUg_9066ymBzqPBVdypVo_aexrI8rsK6FMgzw2-zVwsotyAvV_Kd_KL61tYRbEorP-Ooe9wP7LIelzebL8FjFywZD9GwRWXNa9Tyjl0OvOiXwbzWvgUX8E5-rvmsQOYm2YPNd44VecHFbSri80QFE0P4uDPameG5XuAZr51ewovdA2kmLVNd9T0tH7_0TLyuFPD_Gl4MVEeaySpTddS0owHP3i0koQ4nOuTUMOZv_Xc1SzPCWbNf3-e-srzBS0g',
    'seeker_session': 'true',
    'reddit_chat_view': 'closed',
    'subreddit_sort': 'AcD3tRM45bAC',
    'g_state': '{"i_l":0,"i_ll":1792178971682,"i_e":{"enable_itp_optimization":24},"i_et":1792178971682,"i_b":"qkjhMM+N3nl+xCojJ9LdvvHTW3aG+lE+UaIrlHcGhhY"}',
    'session_tracker': 'gclkbgnakkfhnflllc.0.1792178972819.Z0FBQUFBQnEwbnNjcEJxR3gtU3k5OFk0d0F5SU9mc1NMeVY4V0l2dFRQVVFuRG5CQTE3TkRaMTBsYThhVDFUZlZJcVZfVXo3UHRMMks0WkptMU1vV2JxRHR5YTN2S05Eamh4TTFCbW5HV0JTVWFaS2haUUFrRXM1blJhQ2JueTNuN2g4VF9pYWdmVGM',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'ru,en;q=0.9,en-GB;q=0.8,en-US;q=0.7,ru-RU;q=0.6',
    'available-dictionary': ':m4DZoH8SVUAY7ntSfCk3ER+klA7NWrA0kZyi8XDjNuQ=:',
    'cache-control': 'max-age=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Microsoft Edge";v="155", "Chromium";v="155", "Not(A:Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'none',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': ua.random,
    # 'cookie': 'csv=2; edgebucket=EccAQ9SaD0Uu7lUl5z; loid=000000000m7meb3bj5.2.1697864792065.Z0FBQUFBQnA0OHVORWN0QnNZUjlHRmxjM3N5THRsN2ZiNURlMVdXY3ZwclNmYTVjYVVEVmtvMS1OOGI2RlpRX1FmNmJacnJnRnRqTWhjV2NUU2t4UnVzWkFsSERKUVVlVmcwdXV3X1FBTFNnaWx6eWpicWRZMHNLajNnbDFzNHNGVEpUSlJFbF9qWlc; t2_m7meb3bj5_recentclicks3=t3_1dhho5x; reddit_supported_media_codecs=video/avc%2Cvideo/vp9; eu_cookie_opted=1; ads_cookie=1; reddit_session=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpsVFdYNlFVUEloWktaRG1rR0pVd1gvdWNFK01BSjBYRE12RU1kNzVxTXQ4IiwidHlwIjoiSldUIn0.eyJzdWIiOiJ0Ml9tN21lYjNiajUiLCJleHAiOjE4MDcxMTc4NjguNjUwNTExLCJpYXQiOjE3OTE0Nzk0NjguNjUwNTExLCJqdGkiOiJua3pDaXF2VUc0ZS1paDVOMFlhQnRFa2R3Tllub3ciLCJhdCI6MSwiY2lkIjoiY29va2llIiwibGNhIjoxNjk3ODY0NzkyMDY1LCJzY3AiOiJlSndBQWdEOV8xdGRBd0FCRlFDNSIsImZsbyI6MywiYW1yIjpbInNzbyJdfQ.Iaklofr9JP-dYg4mjgdZZDT3gmDgCh8YqdJlMAmEe1HbusviHddM5YMjS0_HAzF9Vz0BOWQatAvL5R8hJ-4qkwlbBKjInC8TCNaNxRfWXPsgRl5fkUQ5ys_VBBOdqfRzGzvS7d0kAwgIIc31yt3zld5uDvgjUPG07_SH8X9bNmDO0SsV6rD-kkk_lB88eTPIm_mduliuAWrvy9mf68663r7s2zH3xjNpZEERtYB80YnFRwT2qW866GgW9dw3tOAjRHLSzsocv2Nl6kO1E5bK6fRc59uYquep6ENReT_mHtFzTZPr9Q4lPnwiuXEcklEiUZu5qa71ggXLqXeUhdTEMg; csrf_token=e3a8bed97ea3fb2bd76c5d111c3d2406; token_v2=eyJhbGciOiJSUzI1NiIsImtpZCI6IlNIQTI1NjpzS3dsMnlsV0VtMjVmcXhwTU40cWY4MXE2OWFFdWFyMnpLMUdhVGxjdWNZIiwidHlwIjoiSldUIn0.eyJpc3MiOiJodHRwczovL3d3dy5yZWRkaXQuY29tIiwic3ViIjoidXNlciIsImV4cCI6MTc5MjI2NDMxMS43Mzg3NDMsImlhdCI6MTc5MjE3NzkxMS43Mzg3NDMsImp0aSI6IkdqNDV0R0NyNTRjaENzTGlpeC1ZaVlxNmlVOEJlUSIsImNpZCI6IjBSLVdBTWh1b28tTXlRIiwibGlkIjoidDJfbTdtZWIzYmo1IiwiYWlkIjoidDJfbTdtZWIzYmo1IiwiYXQiOjEsImxjYSI6MTY5Nzg2NDc5MjA2NSwic2NwIjoiZUp4a2tWSE8zREFJaE9fQ3MwX1FxMVJWNWRoa0Z6VTJFZUNzOXZZVldaT045TDhOOEdVTWs5LVFxMklsZy1SS01GZElnQzNUQmdsMkl1LVh3cU9mUk84OGVzR0czUlFTRk1GYTZaVFRZOTB5Q1NSNGtockxHeEpReFc1a0xqYzZzT1dlSHdnSkd0ZkNmYVhIcFUxb0djYmlkbzFyV0RXdUcwOXE3dFc0ZHJicHd2YkUtR1pudFNrVnRfV2pUUEs2VXZrVUxfcm5ON1czanVXN19TNTBaTU9HcXZtQjNwbEpDTzRzZnJybXc5OVRrMUZzQ0ZhMTkzYVNPcFoyM3E1ajBTSzBPSGQ4MXZQWFpqSXVwMmw1WnZ0MTF5OGh3MXVlMXpEcUFHYXNNWTh5eHBGMXpLODZnTVlWSlJ0TEVOOUdJRmN1Zl8yWFlMODJfVG00ZmVLSDcwYmM5WWJmbW9GNkxrR2MtaVZrQ0hfLUR3QVExZVRSIiwicmNpZCI6IkhfejRXQ3VOQ1pPU3llSWlPQ0lPeDRLZlFQcHZiZDdtekNpVm5zeGNJREEiLCJmbG8iOjJ9.jEHCemBmDEk86BbOxKLqt6T5zXq1n790wGTfSwQQLJz5g1EKUO6QHWww9PRAV-EmPPmeo4o0WdnoAAEYbu8ceKyiUg_9066ymBzqPBVdypVo_aexrI8rsK6FMgzw2-zVwsotyAvV_Kd_KL61tYRbEorP-Ooe9wP7LIelzebL8FjFywZD9GwRWXNa9Tyjl0OvOiXwbzWvgUX8E5-rvmsQOYm2YPNd44VecHFbSri80QFE0P4uDPameG5XuAZr51ewovdA2kmLVNd9T0tH7_0TLyuFPD_Gl4MVEeaySpTddS0owHP3i0koQ4nOuTUMOZv_Xc1SzPCWbNf3-e-srzBS0g; seeker_session=true; reddit_chat_view=closed; subreddit_sort=AcD3tRM45bAC; g_state={"i_l":0,"i_ll":1792178971682,"i_e":{"enable_itp_optimization":24},"i_et":1792178971682,"i_b":"qkjhMM+N3nl+xCojJ9LdvvHTW3aG+lE+UaIrlHcGhhY"}; session_tracker=gclkbgnakkfhnflllc.0.1792178972819.Z0FBQUFBQnEwbnNjcEJxR3gtU3k5OFk0d0F5SU9mc1NMeVY4V0l2dFRQVVFuRG5CQTE3TkRaMTBsYThhVDFUZlZJcVZfVXo3UHRMMks0WkptMU1vV2JxRHR5YTN2S05Eamh4TTFCbW5HV0JTVWFaS2haUUFrRXM1blJhQ2JueTNuN2g4VF9pYWdmVGM',
}

import os

def parse_site(url, path, after=""):
    names = set(os.listdir(path))
    last_after = after
    count = 0
    try:
        while count < 5000:
            print('a')
            if after != "":
                response = requests.get(f"https://www.reddit.com/r/{url}/top.json?t=all&limit=100&after={after}", cookies=cookies, headers=headers)
            else:
                response = requests.get(f"https://www.reddit.com/r/{url}/top.json?t=all&limit=100", cookies=cookies, headers=headers)
            print(response.url, response.status_code)
            if response.status_code == 200:
                data = response.json()
                names = set(os.listdir(path))
                after = data["data"].get("after")
                children = data["data"].get("children", None)
                if children is None:
                    print("DONE")
                    break
                for child in children:
                    try:
                        image_url = child["data"]["url_overridden_by_dest"]
                        if not (image_url.endswith(("jpeg", "jpg", "png", "webp"))):
                            print("Неверный формат файла")
                            time.sleep(1)
                            continue
                        if image_url.split("/")[-1] in names:
                            print(f"{image_url.split("/")[-1]} уже был")
                        img_response = requests.get(image_url)
                        time.sleep(1)
                        if img_response.status_code == 200:
                            filename = image_url.split("/")[-1]
                            with open(f"{path}/{filename}", "wb") as file:
                                file.write(img_response.content)
                            print(f"Успешно: {image_url}")
                            print(after)
                            count += 1
                        else:
                            print(f"Error. Status code {img_response.status_code} for {image_url}")
                    except Exception as ex:
                        print(f"Ошибка {ex}")
                    
                print(count)
            else:
                 print(f"Error. Status code {response.status_code}")
        last_after = after
    except Exception as ex:
        raise ex
    finally:
        with open("last_after.txt", 'w', encoding="utf8") as file:
            file.write(last_after)
        with open("aa.json", 'w', encoding="utf8") as file:
            json.dump(data, file)
#Пишет ошибку Error. Status code 429 for http://i.imgur.com/DG9RFXb.jpg

parse_site("terriblepics", "low")

