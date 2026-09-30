"""Check Streamlit readiness; HTML, sign-in pages and sleep screens are failures."""
from urllib.request import Request, build_opener, HTTPCookieProcessor
from urllib.error import URLError
from http.cookiejar import CookieJar
import time

URL='https://courtsense-ncaa.streamlit.app/~/+/_stcore/health'


def healthy(status, body):
    return status==200 and body.strip().lower()==b'ok'


def main():
    opener = build_opener(HTTPCookieProcessor(CookieJar()))
    for attempt in range(4):
        try:
            with opener.open(Request(URL,headers={'User-Agent':'CourtSense-readiness-check/1.1'}),timeout=20) as r:
                if healthy(r.status,r.read(1024)):
                    print('Streamlit readiness endpoint is healthy. This is not a UI or model-accuracy test.')
                    return
        except (URLError,TimeoutError):
            pass
        if attempt<3:time.sleep(15)
    raise SystemExit('Readiness not confirmed: the app may be asleep, restarting, restricted, or failing. Inspect Streamlit logs; no automatic restart or data change was attempted.')


if __name__=='__main__':main()
