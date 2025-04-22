import re
import pandas as pd
import requests
from bs4 import BeautifulSoup
from pprint import pprint

base_url = "https://terraria-game.fandom.com"
main_page_url = f"{base_url}/ru/wiki/Враги"
html_main = requests.get(main_page_url).text
soup_main = BeautifulSoup(html_main, 'html')

print(soup_main)

all_headers = []

for i, header in enumerate(soup_main.find_all(['h2', 'h3'])):
    title = header.find('span', {'class': 'mw-headline'})
    if title:
        all_headers += [(header.name, title.get('id'))]

headers = []
group = ""
for i, (tag, text) in enumerate(all_headers):
    if tag == 'h2':
        group = text
    if i < len(all_headers)-1 and tag == 'h2' and all_headers[i+1][0] == 'h3':
        continue
    headers += [(group, text)]

pprint(headers)

pages = {}

for i, block in enumerate(soup_main.find_all('div', {'class':'itemlist terraria'})):
    links = block.find_all('a', href=True)
    pages[headers[i]] = []
    for j, link in enumerate(links):
        if link.text:
            pages[headers[i]] += [link['href']]

pprint(pages)


def get_int(value: str):
    if value.isdigit():
        return int(value)
    else:
        result = re.match(r"^[0-9]+", value)
        if result is not None:
            return int(result.group())
        else:
            return 0


def parse_mobe_stats(section) -> dict | None:
    stats = {}
    rows = section.find_all('div', {'class': 'pi-item pi-data pi-item-spacing pi-border-color'})
    for row in rows:
        title_wrapper = row.find('h3')
        if title_wrapper is None:
            continue
        title = title_wrapper.text.lower()
        value_wrapper = row.find('div', {'class': 'pi-data-value pi-font'})
        if value_wrapper is None:
            continue
        value = value_wrapper.text.lower()
        if title in ("здоровье", "урон", "защита", "id моба",
                     "поглощение отбрасывания",):
            stats[title] = get_int(value)
        elif title == "монеты":
            coins = {}
            coins_wrappers = value_wrapper.find_all('span', {'class': 'mw-default-size'})
            for coin_wrapper in coins_wrappers:
                value = coin_wrapper.previous_sibling.strip()
                if value.isdigit():
                    value = int(value)
                else:
                    continue
                coin_name = coin_wrapper.find('a').get('title', 'unknown').strip()
                coins[coin_name] = value

            bounty = 0
            currencies = ["Медная монета", "Серебряная монета", "Золотая монета",
                          "Платиновая монета"]
            for coin, value in coins.items():
                bounty += value * 100**currencies.index(coin)
            stats['награда'] = bounty
    return stats


def parse_stats_section(section) -> dict:
    diffs_wrapper = section.find('div', {'class': 'wds-tabs__wrapper'})
    difficulties = [d.text.strip() for d in diffs_wrapper.find_all('div', {'class': 'wds-tabs__tab-label'})]
    if difficulties != ['Обычный', 'Эксперт', 'Мастер']:
        return None
    info_wrappers = section.find_all('div', {'class': 'wds-tab__content'})
    if len(info_wrappers) != 3:
        return None

    stats = {}
    for diff, info_wrapper in zip(difficulties, info_wrappers):
        stats[diff] = parse_mobe_stats(info_wrapper)

    return stats


def parse_mobe_page(soup: BeautifulSoup, url) -> dict | None:
    block = soup.find('aside')
    if block is None:
        return None

    result = {}
    name = block.find('h2', {'class': 'pi-item pi-item-spacing pi-title pi-secondary-background'})
    if name is None:
        return None
    name = name.contents[0].strip()
    if len(name) == 0:
        print(f"\tbad name: {name}")
        return None
    result["name"] = name

    sections = block.find_all('section', {'class': 'pi-item pi-group pi-border-color'})
    for section in sections:
        diffs_wrappers = section.find_all('div', {'class': 'wds-tabs__wrapper'})
        if len(diffs_wrappers) != 0:
            result['stats'] = parse_stats_section(section)
        else:
            data_lines = section.find_all('div', {'class': 'pi-item pi-data pi-item-spacing pi-border-color'})
            for data_line in data_lines:
                value_wrapper = data_line.find('div', {'class': 'pi-data-value pi-font'})
                if value_wrapper is None:
                    continue
                value = value_wrapper.text.lower()

                h3_header = data_line.find('h3')
                if h3_header is None:
                    continue
                h3_link = h3_header.find('a')
                if h3_link is None:
                    key = h3_header.text.strip().lower()
                else:
                    key = h3_link.text.strip().lower()

                for title in ("без влияния гравитации", "проходит сквозь блоки"):
                    if title in key:
                        result[title] = True
                        break
                for title in ("id моба", "время дебаффа", "шанс дебаффа",
                              "убийств для знамени"):
                    if title in key:
                        result[title] = get_int(value)
                        break
                for title in ("время появления", "редкость"):
                    if title in key:
                        result[title] = value
                        break

    return result

data = []
print(f"Pages: {len(pages)}")
for i, ((category, title), urls) in enumerate(pages.items()):
    print(f"\tcategory {i+1}/{len(pages)}")
    for j, sub_url in enumerate(urls):
        url = f"{base_url}{sub_url}"
        page_html = requests.get(url).text
        soup_page = BeautifulSoup(page_html, 'html')
        mobe_info = parse_mobe_page(soup_page, url)
        if mobe_info is None:
            continue
        mobe_info['event_category'] = category
        mobe_info['event'] = title
        data += [mobe_info]
        print(f"\t\tmobe {j+1}/{len(urls)}")

print(f"Data length: {len(data)}")

processed_data = []
for mobe in data:
    result = {}
    for key, value in mobe.items():
        if value is None or key is None:
            continue
        if key != 'stats':
            result[key.lower()] = value.lower() if isinstance(value, str) else value
        else:
            for diff, stats in value.items():
                for stat_name, stat_value in stats.items():
                    result[f"{diff.lower()}_{stat_name.lower()}"] = stat_value

    processed_data += [result]

df = pd.DataFrame(processed_data)
df.to_csv('output.csv', index=False)