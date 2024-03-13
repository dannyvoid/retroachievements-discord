import requests
from bs4 import BeautifulSoup


def get_html_content_with_flare_solver(url):
    flare_solver_url = "http://IP:PORT/v1" # Update this to your flaresolverrd instance
    headers = {"Content-Type": "application/json"}
    data = {"cmd": "request.get", "url": url, "maxTimeout": 60000}

    response = requests.post(flare_solver_url, headers=headers, json=data)

    if response.status_code != 200:
        raise Exception("Failed to fetch HTML content from URL")

    return response.text


def get_timestamp(username):
    url = f"https://retroachievements.org/user/{username}"
    html_content = get_html_content_with_flare_solver(url)

    soup = BeautifulSoup(html_content, "html.parser")
    target_class = '\\"smalldate'
    p_tag = soup.find("p", class_=target_class)

    if p_tag:
        content = p_tag.get_text().strip()
        timestamp = content.split(r"\n")[1].strip()
        return timestamp
    else:
        return "No timestamp found"


def main():
    timestamp = get_timestamp("dannyvoid")

    if timestamp:
        if "No timestamp found" in timestamp:
            print("No timestamp found")
        else:
            print(timestamp)


if __name__ == "__main__":
    main()
