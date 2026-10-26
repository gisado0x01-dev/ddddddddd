import time
import requests

WEBHOOK_URL = "https://webhook.lewisakura.moe/api/webhooks/1564215538496970762/wRVauOta6xz_DHvMT9_4XtoX8rHw3alxtT4KELK9OJD30cWIV_eyOOgfAB55P66av9RE"

ACCOUNTS = [
    {"id": "6974yo", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "IlIlIlllIllllIILL", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "SorryForNeedYou", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "OnlyToLoveYou", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "VHPARTY", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "TheFNBU", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "6974one", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "6974two", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "6974three", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "DogIsMyEverything", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "LuauIsMyLife", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"},
    {"id": "LuauHacker", "cookie": "COOKIE_HERE", "place_id": "PLACE_ID_HERE"}
]

RBXLX_FILE_PATH = "backup_game.rbxlx"
current_account_index = 0
current_game_id = None

def send_webhook_embed(title, description, color, game_url=None):
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "footer": {"text": "자동 업로더 시스템"}
    }
    if game_url:
        embed["url"] = game_url

    data = {"embeds": [embed]}
    try:
        requests.post(WEBHOOK_URL, json=data)
    except Exception as e:
        print(f"웹훅 전송 실패: {e}")

def get_csrf_token(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    res = requests.post("https://auth.roblox.com/v2/logout", headers=headers)
    return res.headers.get("x-csrf-token")

def get_universe_id(place_id):
    res = requests.get(f"https://apis.roblox.com/universes/v1/places/{place_id}/universe")
    if res.status_code == 200:
        return res.json().get("universeId")
    return None

def is_account_banned(cookie):
    headers = {"Cookie": f".ROBLOSECURITY={cookie}"}
    res = requests.get("https://users.roblox.com/v1/users/authenticated", headers=headers)
    return res.status_code != 200

def is_game_deleted(place_id):
    if not place_id or place_id == "PLACE_ID_HERE":
        return True
    universe_id = get_universe_id(place_id)
    if not universe_id:
        return True
    res = requests.get(f"https://games.roblox.com/v1/games?universeIds={universe_id}")
    if res.status_code == 200:
        data = res.json().get("data", [])
        if len(data) > 0:
            return False
    return True

def upload_and_publish_game(account):
    cookie = account["cookie"]
    place_id = account["place_id"]
    
    csrf_token = get_csrf_token(cookie)
    if not csrf_token:
        return None

    headers = {
        "Cookie": f".ROBLOSECURITY={cookie}",
        "X-CSRF-TOKEN": csrf_token,
        "User-Agent": "Roblox/WinInet",
        "Content-Type": "application/xml"
    }

    upload_url = f"https://data.roblox.com/Data/Upload.ashx?assetid={place_id}"
    try:
        with open(RBXLX_FILE_PATH, "rb") as f:
            file_data = f.read()
    except FileNotFoundError:
        print(f"오류: {RBXLX_FILE_PATH} 파일을 찾을 수 없습니다.")
        return None

    upload_res = requests.post(upload_url, headers=headers, data=file_data)
    if upload_res.status_code != 200:
        print(f"[{account['id']}] 파일 업로드 실패 (상태 코드: {upload_res.status_code})")
        return None

    universe_id = get_universe_id(place_id)
    if universe_id:
        json_headers = {
            "Cookie": f".ROBLOSECURITY={cookie}",
            "X-CSRF-TOKEN": csrf_token,
            "Content-Type": "application/json"
        }
        
        config_url = f"https://develop.roblox.com/v2/universes/{universe_id}/configuration"
        config_data = {
            "name": "[백업] 공터",
            "description": "백업 서버입니다.",
            "isFriendsOnly": False
        }
        requests.patch(config_url, headers=json_headers, json=config_data)

        activate_url = f"https://develop.roblox.com/v1/universes/{universe_id}/activate"
        requests.post(activate_url, headers=json_headers)

    print(f"[{account['id']}] 계정에 '[백업] 공터' 업로드 및 공개 설정 완료!")
    return f"https://www.roblox.com/games/{place_id}"

def main_loop():
    global current_account_index, current_game_id
    
    print("자동 업로더 봇 가동 시작...")
    
    while True:
        if is_game_deleted(current_game_id):
            print("게임 정지 감지됨! 다음 계정으로 복구를 시도합니다.")
            
            uploaded = False
            checked_accounts = 0
            
            while checked_accounts < len(ACCOUNTS):
                acc = ACCOUNTS[current_account_index]
                current_account_index = (current_account_index + 1) % len(ACCOUNTS)
                checked_accounts += 1
                
                if not is_account_banned(acc["cookie"]):
                    new_game_url = upload_and_publish_game(acc)
                    if new_game_url:
                        current_game_id = acc["place_id"]
                        
                        send_webhook_embed(
                            title="✅ [백업] 공터 복구 완료",
                            description=f"기존 게임이 정지되어 새로운 게임으로 교체되었습니다.\n\n**[👉 여기를 눌러 게임 접속하기]({new_game_url})**",
                            color=0x00FF00
                        )
                        uploaded = True
                        break
                else:
                    print(f"[{acc['id']}] 계정은 현재 정지 상태이거나 쿠키가 만료되었습니다. 패스합니다.")
            
            if not uploaded:
                print("모든 계정이 정지되었습니다.")
                send_webhook_embed(
                    title="🚨 모든 계정 정지됨",
                    description="현재 준비된 모든 백업 계정이 정지를 먹었거나 업로드에 실패했습니다. 정지가 풀릴 때까지 기다려야 합니다.",
                    color=0xFF0000
                )
                time.sleep(1800)
                continue

        time.sleep(60)

if __name__ == "__main__":
    main_loop()