import os
import time
import cursor
import requests
from datetime import datetime
from pypresence import Presence
from flaresolverrd import get_timestamp

cursor.hide()

client_id = "" # Your discord app client ID
RPC = Presence(client_id)
RPC.connect()

DEBUG = False
API_HOST = "https://retroachievements.org"
API_URL = f"{API_HOST}/API/"
USER_AGENT = "RetroAchievementsBot/1.0"

username = "" # RetroAchievements User to track
web_api_key = "" # Your RetroAchievements API Key
target_username = username


def make_request(endpoint, params):
    headers = {"User-Agent": USER_AGENT}
    response = requests.get(endpoint, params=params, headers=headers)
    response.raise_for_status()
    return response.json()


def get_user_profile_data(username, web_api_key, target_username):
    endpoint = f"{API_URL}API_GetUserProfile.php"
    params = {"z": username, "y": web_api_key, "u": target_username}
    return make_request(endpoint, params)


def get_recently_played_games(username, web_api_key, target_username, limit=2):
    endpoint = f"{API_URL}API_GetUserRecentlyPlayedGames.php"
    params = {"z": username, "y": web_api_key, "u": target_username, "c": limit}
    return make_request(endpoint, params)


def get_game_progress(username, web_api_key, target_username, target_game_id):
    endpoint = f"{API_URL}API_GetUserProgress.php"
    params = {
        "z": username,
        "y": web_api_key,
        "u": target_username,
        "i": target_game_id,
    }
    response = make_request(endpoint, params)

    if response and str(target_game_id) in response:
        return response[str(target_game_id)]
    else:
        return None


def get_game_data(username, web_api_key, target_game_id):
    if not target_game_id:
        return None
    endpoint = f"{API_URL}API_GetGame.php"
    params = {"z": username, "y": web_api_key, "i": target_game_id}
    return make_request(endpoint, params)


def traverse_data(data):
    if not data:
        return

    if isinstance(data, list):
        for item in data:
            traverse_dict(item)
    elif isinstance(data, dict):
        traverse_dict(data)
    else:
        print("Invalid data type")


def traverse_dict(data):
    if not data:
        return

    for key, value in data.items():
        print(f"{key}: {value}")
    print()


def print_game_info(game_dict, username):
    print(f"{username} is playing {game_dict['Title']}")
    print(game_dict.get("Presence", "No rich presence message available"))
    print()
    print(f"Console: {game_dict.get('Console', 'N/A')}")
    print(f"Developed by: {game_dict.get('Developer', 'N/A')}")
    print(f"Genre: {game_dict.get('Genre', 'N/A')}")
    print(f"Release Date: {game_dict.get('ReleaseDate', 'N/A')}")
    print()


def build_rich_presence_message(
    username=username, web_api_key=web_api_key, target_username=target_username
):
    profile_data = get_user_profile_data(username, web_api_key, target_username)
    target_game_id = profile_data.get("LastGameID")
    game_progress = get_game_progress(
        username, web_api_key, target_username, target_game_id
    )

    game_data = get_game_data(username, web_api_key, target_game_id)

    achievements_earned = game_progress.get("NumAchievedHardcore", 0)
    achievements_possible = game_progress.get("NumPossibleAchievements", 0)
    achievement_progress = f"{achievements_earned}/{achievements_possible} 🏆"

    game_icon = game_data.get("ImageBoxArt")
    game_icon_url = API_HOST + game_icon if game_icon else None

    rich_presence_msg = profile_data.get(
        "RichPresenceMsg", "No rich presence message available"
    )
    presence += f" [{achievement_progress}]"

    game_dict = {
        "Title": game_data.get("Title", "Unknown game"),
        "Console": game_data.get("ConsoleName", "N/A"),
        "Developer": game_data.get("Developer", "N/A"),
        "Genre": game_data.get("Genre", "N/A"),
        "ReleaseDate": game_data.get("Released", "N/A"),
        "GameIcon": game_icon_url,
        "Presence": presence,
    }
    os.system("cls" if os.name == "nt" else "clear")
    print_game_info(game_dict, username)
    RPC.update(
        large_image=game_icon_url,
        large_text=game_dict["Title"],
        small_image="https://media.giphy.com/media/4UjV5LeD66EPruSG18/giphy.gif",
        small_text=game_dict["Console"],
        details=game_dict["Presence"],
    )

    current_time = time.time()
    current_time = datetime.fromtimestamp(current_time).strftime("%H:%M:%S %p")
    print(f"Current time: {current_time}")


def main():
    # This IS HORRIBLE
    # But retroachievements does not EXPOSE how recently you were active
    # The longest timestamp I saw WHILE active was "1 minute ago"
    # If anyone has a better solution for this whole section, pls submit PR.
  
    last_check_time = time.time()
    build_rich_presence_message()
    timestamp = get_timestamp(username)
    if timestamp:
        timestamp_str = get_timestamp().strip()
    else:
        timestamp_str = ""

    while True:
        current_time = time.time()

        if current_time - last_check_time > 30:
            timestamp_str = get_timestamp().strip()
            last_check_time = current_time

        if "seconds" in timestamp_str or timestamp_str == "1 minute ago":
            build_rich_presence_message()
            time.sleep(10)
        elif "No timestamp found" in timestamp_str:
            os.system("cls" if os.name == "nt" else "clear")
            print("Could not find timestamp.")
            RPC.clear()
            time.sleep(120)
        else:
            os.system("cls" if os.name == "nt" else "clear")
            print("Not currently playing. Waiting...")
            RPC.clear()
            time.sleep(10)


if __name__ == "__main__":
    main()
