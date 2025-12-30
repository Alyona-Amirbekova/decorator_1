import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from fake_headers import Headers

# Импортируем наш декоратор logger
from task_2 import logger

KEYWORDS = ['дизайн', 'фото', 'web', 'python']

base_url = 'https://habr.com/ru/articles/'
headers = Headers(browser='chrome', os='win').generate()


def get_page_content(url, headers):
    response = requests.get(url, headers=headers)
    return response.text


def parse_articles(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    articles = []

    # Находим все блоки статей на странице
    article_list = soup.find_all('article', class_='tm-articles-list__item')

    for article in article_list:
        # Ищем заголовок статьи
        title_elem = article.find('h2', class_='tm-title')
        if not title_elem:
            continue

        title_link = title_elem.find('a')
        if not title_link:
            continue

        title = title_link.text.strip()
        relative_link = title_link.get('href')
        link = urljoin('https://habr.com', relative_link)  # Исправлен базовый URL

        # Ищем дату публикации
        time_elem = article.find('time')
        date = time_elem.get('datetime') if time_elem else 'Дата не найдена'

        # Ищем превью текста (например, краткое описание или начало статьи)
        preview_elem = article.find('div', class_='tm-article-snippet__lead')
        preview_text = preview_elem.get_text(strip=True) if preview_elem else ""

        snippet_elem = article.find('div', class_='tm-article-snippet__content')
        if snippet_elem:
             snippet_text = snippet_elem.get_text(strip=True)
             preview_text += " " + snippet_text.replace(title, "", 1).strip()

        # Собираем весь доступный текст для поиска
        full_preview_text = title + " " + preview_text

        articles.append({
            'date': date,
            'title': title,
            'link': link,
            'preview_text': full_preview_text.lower()  # Для поиска переводим в нижний регистр
        })

    return articles


def find_articles_with_keywords(articles, keywords):
    matching_articles = []
    lower_keywords = [kw.lower() for kw in keywords]

    for article in articles:
        if any(keyword in article['preview_text'] for keyword in lower_keywords):
            matching_articles.append(article)

    return matching_articles


def main():
    print("Начинаем выполнение main...")

    html_content = get_page_content(base_url, headers)

    if not html_content:
        print("Не удалось получить содержимое страницы. Завершение.")
        return

    all_articles = parse_articles(html_content)
    print(f"Найдено {len(all_articles)} статей на странице.")

    filtered_articles = find_articles_with_keywords(all_articles, KEYWORDS)
    print(f"Найдено {len(filtered_articles)} статей, соответствующих критериям.")

    print("\n--- Подходящие статьи ---")
    if filtered_articles:
        for article in filtered_articles:
            print(f"{article['date']} – {article['title']} – {article['link']}")
    else:
        print("Не найдено статей, соответствующих ключевым словам.")

    print("Завершение выполнения main.")


if __name__ == '__main__':
    # Оборачиваем main
    main = logger('main_parser.log')(main)
    # Оборачиваем другие функции
    get_page_content = logger('get_page_content.log')(get_page_content)
    parse_articles = logger('parse_articles.log')(parse_articles)
    find_articles_with_keywords = logger('find_articles_with_keywords.log')(find_articles_with_keywords)

    main()
