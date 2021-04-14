from sgselenium import SgChrome
from bs4 import BeautifulSoup as bs
from sgrequests import SgRequests
import json
import pandas as pd

def extract_json(html_string):
    json_objects = []
    count = 0

    brace_count = 0
    for element in html_string:

        if element == "{":
            brace_count = brace_count + 1
            if brace_count == 1:
                start = count

        elif element == "}":
            brace_count = brace_count - 1
            if brace_count == 0:
                end = count
                try:
                    json_objects.append(json.loads(html_string[start : end + 1]))
                    if "longitude" in json.loads(html_string[start : end + 1]).keys():
                        break

                except Exception:
                    pass
        count = count + 1

    return json_objects

def reset_sessions(data_url):

    s = SgRequests()

    driver = SgChrome(is_headless=True).driver()
    driver.get(base_url)

    incap_str = "/_Incapsula_Resource?SWJIYLWA=719d34d31c8e3a6e6fffd425f7e032f3"
    incap_url = base_url + incap_str

    s.get(incap_url)

    for request in driver.requests:

        headers = request.headers
        try:
            response = s.get(data_url, headers=headers)
            response_text = response.text

            test_html = response_text.split("div")
            if len(test_html) < 2:
                continue
            else:
                return [s, driver, headers, response_text]

        except Exception:
            continue

locator_domains = []
page_urls = []
location_names = []
street_addresses = []
citys = []
states = []
zips = []
country_codes = []
store_numbers = []
phones = []
location_types = []
latitudes = []
longitudes = []
hours_of_operations = []

base_url = "https://www.carehome.co.uk/"

new_sess = reset_sessions(base_url)

s = new_sess[0]
driver = new_sess[1]
headers = new_sess[2]
response_text = new_sess[3]

soup = bs(response_text, "html.parser")

strong_tags = soup.find("div", attrs={"class": "row", "style": "margin-bottom:30px"}).find_all("strong")
country_urls = []
location_urls = []
for strong_tag in strong_tags:
    a_tag = strong_tag.find("a")
    url = a_tag["href"]

    if "searchcountry" in url:
        country_urls.append(url)

for country_url in country_urls:
    
    response = s.get(country_url, headers=headers)
    response_text = response.text
    if len(response_text.split("div")) > 2:
        pass
    else:
        new_sess = reset_sessions(country_url)

        s = new_sess[0]
        driver = new_sess[1]
        headers = new_sess[2]
        response_text = new_sess[3]

    soup = bs(response_text, "html.parser")
    search_length = int(soup.find_all("a", attrs={"class": "page-link"})[-2].text.strip())
    
    count = 1
    while count < search_length + 1:
        search_url = country_url + "/startpage/" + str(count)
        print(search_url)
        response = s.get(search_url, headers=headers)
        response_text = response.text

        if len(response_text.split("div")) > 2:
            pass
        else:
            new_sess = reset_sessions(search_url)

            s = new_sess[0]
            driver = new_sess[1]
            headers = new_sess[2]
            response_text = new_sess[3]

        soup = bs(response_text, "html.parser")
        div_tags = soup.find_all("div", attrs={"class": "col-sm-9 col-xs-12"})
        for div_tag in div_tags:
            try:
                location_url = div_tag.find("a", attrs={"style": "font-weight:bold;font-size:28px"})["href"]
            except Exception:
                a_tags = div_tag.find_all("a")
                for a_tag in a_tags:
                    try:
                        location_url = a_tag["href"]
                    except Exception:
                        pass

            if location_url in location_urls:
                pass
            else:
                location_urls.append(location_url)
        count = count + 1

x = 0
phone_session = SgRequests()
for location_url in location_urls:
    print(x)
    print(location_url)
    response = s.get(location_url, headers=headers)
    response_text = response.text
    if len(response_text.split("div")) > 2:
        pass
    else:
        new_sess = reset_sessions(location_url)

        s = new_sess[0]
        driver = new_sess[1]
        headers = new_sess[2]
        response_text = new_sess[3]
    
    soup = bs(response_text, "html.parser")

    locator_domain = "carehome.co.uk"
    page_url = location_url
    location_name = soup.find("h1", attrs={"class": "mb-0 card-title"}).text.strip()
    
    address_parts = soup.find("meta", attrs={"property": "og:title"})["content"].split(",")
    address = address_parts[1].strip()
    city = address_parts[-2].strip()
    state_parts = address_parts[-1].split(" ")[:-2]
    state = ""
    for part in state_parts:
        state = state + part + " "
    state = state.strip().replace("County ", "")

    zipp = address_parts[-1].split(" ")[-2] + " " + address_parts[-1].split(" ")[-1]
    country_code = "UK"
    store_number = location_url.split("/")[-1]
    phone = "<INACCESSIBLE>"

    geo_json = extract_json(response_text.split("geo")[1].split("reviews")[0])[0]
    latitude = geo_json["latitude"]
    longitude = geo_json["longitude"]
    hours = "<MISSING>"

    location_type_text = soup.find("div", attrs={"class": "row profile-row"}).find_all("div", attrs={"class": "col-md-4"})[1].find("ul").text.strip().split("\n")
    if "Owner" in location_type_text[0]:
        location_type = location_type_text[-1].replace("\r", "").replace("\t", "")
    else:
        location_type = "<MISSING>"

    locator_domains.append(locator_domain)
    page_urls.append(page_url)
    location_names.append(location_name)
    street_addresses.append(address)
    citys.append(city)
    states.append(state)
    zips.append(zipp)
    country_codes.append(country_code)
    store_numbers.append(store_number)
    phones.append(phone)
    location_types.append(location_type)
    latitudes.append(latitude)
    longitudes.append(longitude)
    hours_of_operations.append(hours)

    x = x+1

df = pd.DataFrame(
    {
        "locator_domain": locator_domains,
        "page_url": page_urls,
        "location_name": location_names,
        "street_address": street_addresses,
        "city": citys,
        "state": states,
        "zip": zips,
        "store_number": store_numbers,
        "phone": phones,
        "latitude": latitudes,
        "longitude": longitudes,
        "hours_of_operation": hours_of_operations,
        "country_code": country_codes,
        "location_type": location_types,
    }
)

df = df.fillna("<MISSING>")
df = df.replace(r"^\s*$", "<MISSING>", regex=True)

df["dupecheck"] = (
    df["location_name"]
    + df["street_address"]
    + df["city"]
    + df["state"]
    + df["location_type"]
)

df = df.drop_duplicates(subset=["dupecheck"])
df = df.drop(columns=["dupecheck"])
df = df.replace(r"^\s*$", "<MISSING>", regex=True)
df = df.fillna("<MISSING>")

df.to_csv("data.csv", index=False)

