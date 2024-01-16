import smtplib
import os

from bs4 import BeautifulSoup
import requests


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
    showpath = f"data/{show}.show"
    if os.path.exists(showpath):
        return False
    with open(showpath, "w") as f:
        f.write("")
    return True


if __name__ == "__main__":
    s = requests.Session()
    s.headers.update({"User-Agent": "Mozilla/5.0"})
    s.get("https://lv.houseseats.com/member/")
    s.post("https://lv.houseseats.com/member/index.bv",
           data={
               "submit": "login",
               "email": os.environ["EMAIL"],
               "password": os.environ["HOUSESEATS_PASSWORD"],
               })
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
