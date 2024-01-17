import smtplib
import json
import os

from bs4 import BeautifulSoup
import requests


COOKIES_FILE = "data/cookies.json"
SHOWS_FOLDER = "data/"


def load_cookies_and_update_headers(s: requests.Session) -> None:
    """Load cookies from file and update headers"""
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    s.get("https://lv.houseseats.com/member/")
    if not os.path.exists(COOKIES_FILE):
        return
    with open(COOKIES_FILE, "r") as f:
        cookies = requests.utils.cookiejar_from_dict(json.load(f))
        s.cookies.clear()
        s.cookies.update(cookies)


def check_logged_in(s: requests.Session) -> bool:
    """Check if the user is logged in"""
    r = s.get("https://lv.houseseats.com/member/")
    return "You must login or join the house" not in r.text


def log_in_and_save_cookies(s: requests.Session) -> None:
    """Log in to the website"""
    s.post("https://lv.houseseats.com/member/index.bv",
           data={
               "submit": "login",
               "email": os.environ["EMAIL"],
               "password": os.environ["HOUSESEATS_PASSWORD"],
           })
    with open(COOKIES_FILE, "w") as f:
        f.write(json.dumps(s.cookies.get_dict()))


def send_email_with_gmail(message: str) -> None:
    """Send an email with the given message to myself"""
    server = smtplib.SMTP("smtp.gmail.com", 587)
    server.ehlo()
    server.starttls()
    server.ehlo()
    server.login(os.environ["EMAIL"], os.environ["GMAIL_PASSWORD"])
    message = (
            f"To: {os.environ['EMAIL']}\n"
            f"From: {os.environ['EMAIL']}\n"
            f"Subject: New HouseSeats Show\n\n{message}"
            ).encode("utf-8").strip()
    server.sendmail(os.environ["EMAIL"], os.environ["EMAIL"], message)
    server.close()


def upsert_show(show: str) -> bool:
    """Add a new show to the database"""
    showpath = f"{SHOWS_FOLDER}{show}.show"
    if os.path.exists(showpath):
        return False
    with open(showpath, "w") as f:
        f.write("")
    return True


def scrape_shows_and_notify(s: requests.Session) -> None:
    """Scrape the shows from House Seats and notify on new ones"""
    r = s.get(
            "https://lv.houseseats.com"
            "/member/ajax/upcoming-shows.bv?"
            "supersecret=&search=&sortField=&startMonthYear="
            "&endMonthYear=&startDate=&endDate=&start=0"
            )
    soup = BeautifulSoup(r.text, "html.parser")
    shows = soup.select("div.panel-heading p.text-center a")
    for show in shows:
        if upsert_show(show.text):
            send_email_with_gmail(f"New show on houseseats: {show.text}")


if __name__ == "__main__":
    s = requests.Session()
    load_cookies_and_update_headers(s)
    if not check_logged_in(s):
        print("Not logged in. Updating cookies")
        log_in_and_save_cookies(s)
    scrape_shows_and_notify(s)
    print("Finished scraping")
