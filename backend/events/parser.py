import requests
from bs4 import BeautifulSoup
from datetime import datetime
from urllib.parse import urljoin
from django.utils import timezone


def parse_yandex_afisha(url, event_type):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, 'html.parser')

    events = []
    event_cards = soup.find_all('div', {'data-component': 'EventCard'})

    for card in event_cards:
        try:
            external_id = card.get('data-event-id')
            title = card.find('h2', {'data-test-id': 'eventCard.eventInfoTitle'}).get_text(strip=True)

            date_item = card.find('li', class_='DetailsItem-fq4hbj-1')
            date_str = date_item.get_text(strip=True) if date_item else ''

            date = None
            if date_str:
                try:
                    day_month, time = date_str.split(', ')
                    day, month = day_month.split()
                    month_map = {
                        'января': 1, 'февраля': 2, 'марта': 3, 'апреля': 4,
                        'мая': 5, 'июня': 6, 'июля': 7, 'августа': 8,
                        'сентября': 9, 'октября': 10, 'ноября': 11, 'декабря': 12
                    }
                    naive_date = datetime(
                        year=datetime.now().year,
                        month=month_map.get(month.lower(), 1),
                        day=int(day),
                        hour=int(time.split(':')[0]),
                        minute=int(time.split(':')[1])
                    )
                    date = timezone.make_aware(naive_date, timezone.get_current_timezone())
                except (ValueError, AttributeError) as e:
                    date = None

            venue = card.find('a', class_='PlaceLink-fq4hbj-2')
            venue = venue.get('title') if venue else ''

            price_block = card.find('span', class_='PriceBlock-njdnt8-11')
            price = price_block.get_text(strip=True).replace('\xa0', ' ') if price_block else ''

            img = card.find('img')
            image_url = img.get('src') if img else ''

            event_link = card.find('a', {'data-test-id': 'eventCard.link'})
            source_url = urljoin(url, event_link.get('href')) if event_link else ''

            events.append({
                'title': title,
                'date': date,
                'venue': venue,
                'price': price,
                'image_url': image_url,
                'event_type': event_type,
                'source_url': source_url,
                'external_id': external_id
            })

        except Exception as e:
            print(f"Ошибка при парсинге карточки: {e}")
            continue

    print(events)

    return events


def parse_event_page(url, headers):
    try:
        response = requests.get(url, headers=headers)
        soup = BeautifulSoup(response.text, 'html.parser')

        description = ''
        desc_block = soup.find('div', {'data-component': 'EventInfo_Description'})
        if desc_block:
            description = desc_block.get_text(strip=True, separator='\n')

        print(description)

        return {'description': description}
    except Exception as e:
        print(f"Ошибка при парсинге страницы события: {e}")
        return {}
