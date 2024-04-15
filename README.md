Scrapes lv.houseseats.com and emails myself if there are any new shows. This scraper got me free tickets to Carrie Underwood, Colin Mochrie, and more! Requires gmail with "app" password (see https://support.google.com/accounts/answer/185833?hl=en).

Environment variables required:
- EMAIL
- HOUSESEATS_PASSWORD
- GMAIL_PASSWORD
- BCC (currently only takes a single email address...)

Run once by directly running the python script, or schedule it with `docker compose up -d`
