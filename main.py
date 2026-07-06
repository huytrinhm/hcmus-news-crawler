from bs4 import BeautifulSoup as bs
import requests
import re
from datetime import datetime
from urllib.parse import urljoin
from zoneinfo import ZoneInfo

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36 Edg/125.0.0.0"
}

def crawl_ctda():
    page = requests.get("https://www.ctda.hcmus.edu.vn/vi/", headers=headers)
    soup = bs(page.content, features='lxml')
    sections = soup.find_all(class_='display-posts-listing')[:4]
    section_titles = [
        'Kế hoạch học tập',
        'Giáo vụ',
        'Trợ lí sinh viên',
        'Kế toán - Tài chính'
    ]

    result = "## CTDA\n"
    for i, section in enumerate(sections):
        result += f'### {section_titles[i]}\n'

        news = [[el.contents[0].text, el.contents[0].attrs['href'], el.contents[-1].text] for el in section.find_all(class_='listing-item')]
        for n in news:
            result += f' - {n[2]}: [{n[0]}]({n[1]})\n'
        result += '\n'

    return result

def crawl_fit():
    page = requests.get("https://www.fit.hcmus.edu.vn/vn/", headers=headers)
    soup = bs(page.content, features='lxml')
    news_raw = soup.select('#dnn_ctr989_ModuleContent > table')

    result = '## FIT\n'
    for news in news_raw:
        day = news.select_one('tr:first-child > .day_month').text.strip()
        month = news.select_one('tr:last-child > .day_month').text.strip()
        year = news.select_one('.post_year').text.strip()
        title = news.select_one('a').text.strip()
        href = news.select_one('a').attrs['href']
        result += f' - {day}-{month}-{year}: [{title}](https://www.fit.hcmus.edu.vn/vn/{href})\n'

    result += '\n'

    return result

def crawl_ktdbcl():
    base_url = "https://ktdbcl.hcmus.edu.vn"
    page = requests.get(f"{base_url}/index.php", headers=headers)
    soup = bs(page.content, features="lxml")

    section_titles = [
        'THÔNG BÁO',
        'LỊCH THI',
        'KẾT QUẢ THI',
        'KẾT QUẢ PHÚC KHẢO',
    ]

    result = '## Các thông báo về Khảo thí\n'
    for section_index, section_title in enumerate(section_titles):
        header = soup.find(lambda tag: tag.name == 'h2' and tag.get_text(strip=True) == section_title)
        if not header:
            continue

        article = header.find_parent('article')
        if not article:
            continue

        if section_index > 0:
            result += '\n***\n\n'

        for link in article.find_all('a', href=True)[:5]:
            title = link.get_text(' ', strip=True)
            href = urljoin(base_url, link['href'])
            item_text = link.find_parent('li').get_text(' ', strip=True)
            date_match = re.search(r'\((\d{2}/\d{2}/\d{4})\)$', item_text)
            date = f'{date_match.group(1)}: ' if date_match else ''
            result += f' - {date}[{title}]({href})\n'

    return result

def crawl_hcmus():
    page = requests.get("https://hcmus.edu.vn/category/dao-tao/dai-hoc/thong-tin-danh-cho-sinh-vien/feed/", headers=headers)
    soup = bs(page.content, features="xml")
    items = soup.find_all('item')

    result = "## Thông tin dành cho sinh viên\n"

    for item in items:
        title = item.find('title').text
        link = item.find('link').text
        pub_date = item.find('pubDate').text
        pub_date = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S %z").strftime('%d/%m/%Y')
        result += f"- {pub_date}: [{title}]({link})\n"

    result += '\n'

    return result

if __name__ == '__main__':
    with open('NEWS.md', 'w', encoding='utf-8') as f:
        f.write('# All news\n')
        f.write(f'_Last update: **{datetime.now(tz=ZoneInfo("Asia/Ho_Chi_Minh"))}**_\n')
        f.write(crawl_ctda())
        f.write(crawl_fit())
        f.write(crawl_hcmus())
        f.write(crawl_ktdbcl())
