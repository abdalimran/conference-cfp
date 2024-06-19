import requests
import pandas as pd
from bs4 import BeautifulSoup


def parse_core_conf_data(page, query='', by='all', source="CORE2021", sort=""):
    URL = (f"http://portal.core.edu.au/conf-ranks/"
           f"?search={query}&by={by}&source={source}&sort={sort}&page={page}")
    print(URL)
    page_data = pd.read_html(URL)
    return page_data[0]


def parse_core_for_data():
    for_code_level1 = pd.read_excel("https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-research-classification-anzsrc/2020/anzsrc2020_for.xlsx",
                                    sheet_name="Table 1",
                                    usecols=['Unnamed: 0', 'Unnamed: 1'])

    for_code_level2 = pd.read_excel("https://www.abs.gov.au/statistics/classifications/australian-and-new-zealand-standard-research-classification-anzsrc/2020/anzsrc2020_for.xlsx",
                                    sheet_name="Table 2",
                                    usecols=['Unnamed: 1', 'Unnamed: 2'])

    for_code_level1_data = (for_code_level1
                            .dropna()
                            .rename(columns={'Unnamed: 0': 'FoR_group',
                                             'Unnamed: 1': 'field_name'}))

    for_code_level1_data['field_name'] = (for_code_level1_data
                                          .field_name
                                          .str
                                          .title())

    for_code_level2_data = (for_code_level2
                            .dropna()
                            .rename(columns={'Unnamed: 1': 'FoR_code',
                                             'Unnamed: 2': 'field_name'}))

    return (for_code_level1_data, for_code_level2_data)


def parse_ggs_data():
    ggs_data = pd.read_excel("https://scie.lcc.uma.es/gii-grin-scie-rating/files/GII-GRIN-SCIE-Conference-Rating-24-ott-2021-9.17.09-Output.xlsx",
                            header=1)
    return ggs_data.drop(columns=[0])


def parse_wikicfp_programs_by_index(index):
    url = f"http://www.wikicfp.com/cfp/series?t=c&i={index}"
    r = requests.get(url)
    html_table = BeautifulSoup(r.text, features="lxml")
    data = [
        "http://www.wikicfp.com" + link.get("href")
        for link in html_table.find_all("a")
        if "/cfp/program?" in link.get("href")
    ]
    return data


def parse_wikicfp_program_events(program_url):
    r = requests.get(program_url)
    html_table = BeautifulSoup(r.text, features="lxml")
    data = [
        "http://www.wikicfp.com" + link.get("href")
        for link in html_table.find_all("a")
        if "event.showcfp?" in link.get("href")
        and "copyownerid=" in link.get("href")
        # and "2023" in link.text
    ]
    return data


def parse_wikicfp_event_detail(event_url):
    r = requests.get(event_url)
    html = BeautifulSoup(r.text, features="lxml")
    try:
        event_data = {}
        event_data = dict(
            (tr.find("th").text.strip(), tr.find("td").text.strip())
            for tr in html.find("table", attrs={"class": "gglu"}).find_all("tr")
        )

        try:
            if "Link:" in html.find("a", {"target": "_newtab"}).parent.text:
                event_data["Link"] = html.find("a", {"target": "_newtab"})["href"]
        except:
            event_data["Link"] = ""
        
        return event_data
    except:
        return None
