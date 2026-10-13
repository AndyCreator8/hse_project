import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import requests
import time

ua = UserAgent()


response = requests.get("https://www.reddit.com/r/hardimages2/top.json?t=all&limit=100")


if response.status_code == 200:
    count = 0
    data = response.json()
    for child in data["data"]["children"]:
        image_url = child["data"].get("url_overridden_by_dest")
        try:
            img_response = requests.get(image_url, headers=headers, cookies=cookies)

            if img_response.status_code == 200:
                filename = image_url.split("/")[3]
                with open(f"images/{filename}", "wb") as file:
                    file.write(img_response.content)

                print(f"Успешно: {filename}")
                count += 1
            else:
                print(f"Пропущено (сервер вернул не картинку): {image_url}")

        except Exception as e:
            print(f"Ошибка при скачивании {image_url}: {e}")
        time.sleep(2)

    print(count)
else:
    print(f"Ошибка при запросе: {response.status_code}")
