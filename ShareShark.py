import discord, requests, json, time, os
from CodeGenerator import QRCodeGenerator
from discord.ext import commands, tasks
from env import DISCORD_BOT_TOKEN, API_URL, EXPIRES, MAX_DOWNLOADS, AUTO_DELETE

intents = discord.Intents.default()
intents.message_content = True

PREFIX = "/"
TIMEOUT = 10

QR_fill = "white"
QR_back = "blue"

bot = commands.Bot(command_prefix=PREFIX, intents=intents)

async def upload_file(file_contents):

    HEADERS = {
        'accept': 'application/json',
        'expires': EXPIRES.isoformat(),
        'maxDownloads': str(MAX_DOWNLOADS),
        'autoDelete': str(AUTO_DELETE)
    }

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
    i = 0
    while upload_not_complete:
        print(wait_animation[i % len(wait_animation)], end='\r')
        time.sleep(.1)
        i += 1
        if i == 20:
            break

    return requests.post(API_URL, headers=HEADERS, files={'file': file_contents}, timeout=TIMEOUT)

async def extract_response(json_response):
    return (json_response["id"], json_response["key"], json_response["path"], json_response["name"], json_response["link"], json_response["expires"])

@bot.event
async def on_message(message):
    # Only uploads file if the bot has been mentioned and an attachment is included
    if (f"@{bot.user.id}" in message.content) and message.attachments:
        for attachment in message.attachments:
            embed = discord.Embed(title="**ShareShark Upload**")
            embed.add_field(name="Status", value=f"Uploading your file '**{attachment.filename}**' to file.io...", inline=False)
            embed.set_author(name=message.author.display_name, icon_url=message.author.avatar.url)
            
            try:
                embed_message = await message.channel.send(embed=embed)
                file_contents = await attachment.read()
                response = await upload_file(file_contents)
                embed.remove_field(index=0)
                if (response.status_code == 200):
                    embed.add_field(name="Status", value=f"Uploading your file '**{attachment.filename}**' to file.io... ✅ **200**", inline=False)
                    embed_message = await embed_message.edit(embed=embed)
                    print("Response status: ", response.status_code, "\r")
                    json_response = json.loads(response.text)
                    print(json_response)

                    identifier, key, path, file_name, link, expires = await extract_response(json_response)
                    
                    embed.add_field(name="URL", value=f"Your file '{file_name}' available at: {link} until {expires}.", inline=False)
                    embed_message = await embed_message.edit(embed=embed)

                    generator = QRCodeGenerator()
                    qr_name = key + ".jpg"
                    qr_path = "./codes/" + qr_name
                    generator.generate_qr_code(url=link, file=qr_path, fill_color=QR_fill, back_color=QR_back)

                    print(f"The QR-code is located at: {qr_path}")
                    qr_message = await message.channel.send("", file=discord.File(qr_path))
    
                else:
                    embed.add_field(name="Status", value=f"Uploading your file '**{attachment.filename}**' to file.io... ❌ **{response.status_code}**", inline=False)
                    await embed_message.edit(embed=embed)
                    print("Response status: ", response.status_code)
                    raise Exception(f"File not delivered.. Status code: {response.status_code}")

            except Exception as exception:
                embed.add_field(name="Errors", value=str(exception), inline=False)
                await embed_message.edit(embed=embed)
                print(exception)            

    elif (PREFIX + "ACK") in message.content.upper():
        print(f"[ACK]: {message.author.display_name} confirmed that file has been received.")
        await message.channel.send(f"**ACK** received, sent by {message.author.mention}")


if __name__ == "__main__":
    bot.run(DISCORD_BOT_TOKEN)
