import time
import requests
from playwright.sync_api import sync_playwright

websites = {}
urlList = open("urls.txt", 'r').read().split('\n')

def print_dict(my_dict):
    print(str(my_dict).replace('{', '').replace('}', '').replace(',', '\n'))

#WEBSITE SELECTOR
for line in urlList:
    pairs = line.split(",")
    websites[pairs[0]] = pairs[1].replace(" ", '')
print_dict(websites)
site = input("Select a site to scan: \n")
url = websites.get(site)


#PAGE SPEED FINDER
with sync_playwright() as p:                #sync_playwright is playwright native object that we are establishing as p
    browser = p.chromium.launch()           #launching a chromium (chrome for bots) instance under the browser variable/object.
    page = browser.new_page()               #creating a "new tab" in chromium.
    
    with page.expect_event("load"):         #confirms the page loads
        page.goto(url)                      #then visits the URL
    
    timing = page.evaluate("() => JSON.parse(JSON.stringify(window.performance.timing))")   #grabs performance metrics directly from the browser (chromium) itself using javascript.
    load_time = timing['loadEventEnd'] - timing['navigationStart']                          #finds load time by subtracting the time between the navigation start and the load event end events.
    print(f"Load time: {load_time}ms")                                                      #formats and then prints the load time.
    
    browser.close()                         #closes the browser instance.

#WEB VITALS FINDER
#FINDS LCP, INP, CLS, FCP, TTFB, TBT by making request to Google Page Speed Insights


print(url)
params = {
    #"key"
    "url" : url,
    "strategy" : "desktop",
    "category" : [
        "performance",
        "accessibility",
        "best-practices",
        "seo"
    ]
}

req = requests.get('https://www.googleapis.com/pagespeedonline/v5/runPagespeed', params=params)
if req.status_code == 200:
    print("Status Code 200")
    raw_data = req.json()
    lcp = raw_data["lighthouseResult"]["audits"]["largest-contentful-paint"]["displayValue"]
    cls = raw_data["lighthouseResult"]["audits"]["cumulative-layout-shift"]["displayValue"]
    tbt = raw_data["lighthouseResult"]["audits"]["total-blocking-time"]["displayValue"]
    ttfb = raw_data["lighthouseResult"]["audits"]["server-response-time"]["displayValue"]
    perf_score = raw_data["lighthouseResult"]["categories"]["performance"]["score"]

    print(f"Performance Score: {perf_score * 100:.0f}")
    print(f"LCP: {lcp}")
    print(f"CLS: {cls}")
    print(f"TBT: {tbt}")
    print(f"TTFB: {ttfb}")
else:
    print(f"Failure: {req.status_code}")
