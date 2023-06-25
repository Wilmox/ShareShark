import requests, json, time, os
from datetime import datetime, timedelta
from PIL import Image
from CodeGenerator import QRCodeGenerator
from ShareShark import send_qrcode


def upload_file():
    wait_animation = [
    "[         ]",
    "[=        ]",
    "[===      ]",
    "[====     ]",
    "[=====    ]",
    "[======   ]",
    "[=======  ]",
    "[=========]",
    "[  =======]",
    "[   ======]",
    "[    =====]",
    "[     ====]",
    "[      ===]",
    "[       ==]",
    "[        =]",
    "[         ]",
    "[         ]"
    ]
    upload_not_complete = True
    print("Uploading your file '" + FILE_NAME+ "' to " + "https://file.io" + " ...")
    
    i = 0
    while upload_not_complete:
        print(wait_animation[i % len(wait_animation)], end='\r')
        time.sleep(.1)
        i += 1
        if i == 20:
            break

    return requests.post(API_URL, headers=HEADERS, files={'file': FILE})

def extract_response(json_response):
    return (json_response["id"], json_response["key"], json_response["path"], json_response["name"], json_response["link"], json_response["expires"])


if __name__ == "__main__":

    print("~~~ Assignment 1 - Networked Application Programming ~~~")
    print("\t => Made by Simon Wilmots")

    today = datetime.now()

    API_URL = 'https://file.io/'
    FILE_NAME = 'file.txt'
    FILE = open(FILE_NAME, 'rb')
    EXPIRES =  today + timedelta(weeks=0, days=0, hours=0, minutes=10, seconds=0)
    MAX_DOWNLOADS = 1
    AUTO_DELETE = True

    HEADERS = {
        'accept': 'application/json',
        'expires': EXPIRES.isoformat(),
        'maxDownloads': str(MAX_DOWNLOADS),
        'autoDelete': str(AUTO_DELETE)
    }

    try:
        response = upload_file()
        if (response.status_code == 200):
            print("Response status: ", response.status_code, "\r")
            json_response = json.loads(response.text)

            identifier, key, path, file_name, link, expires = extract_response(json_response)

            generator = QRCodeGenerator()
            qr_path = "./codes/" + key + ".jpg"
            generator.generate_qr_code(url=link, file=qr_path, fill_color="white", back_color="blue")

            print(f"File '{file_name}' available at: {link} until {expires}.")
            print(f"The QR-code is located at: {qr_path}")
            Image.open(qr_path).show()

            send_qrcode(file=qr_path)
            
        else:
            print("Response status: ", response.status_code)
            print(response.text)
    except Exception as e:
        print(e)
