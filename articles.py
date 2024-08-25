import requests
import pandas as pd
from datetime import datetime, timedelta
from questions import queries_to_extract_source_articles
import pgres_utils
from pgres_utils import insert_science_article, pg_connection
from open_ai import analyze_articles

from logger import get_logger

logger = get_logger(__name__)

def get_news(query, from_date, to_date, api_key):
    url = f"https://newsapi.org/v2/everything?q={query}&from={from_date}&to={to_date}&sortBy=publishedAt&apiKey={api_key}"
    response = requests.get(url)
    data = response.json()
    return data['articles']


def get_openalex_articles(queries: list, from_date: str, to_date: str):
    query_str = ','.join(queries)
    url = f"https://api.openalex.org/works?filter=from_publication_date:{from_date}," \
          f"to_publication_date:{to_date}," \
          f"has_abstract:true" \
          f"&search={query_str}"

    response = requests.get(url)
    data = response.json()
    return data['results']



def get_openalex_articles(queries, from_date, to_date, max_results):
    #query_str = ','.join(queries)
    for query in queries:
        logger.info(query)
        base_url = f"https://api.openalex.org/works?filter=from_publication_date:{from_date},to_publication_date:{to_date},has_abstract:true&search={query}"
        all_articles = []
        page = 1
        per_page = 50  # Максимальное количество статей на страницу
        total_fetched = 0

        while total_fetched < max_results:
            #url = f"{base_url}&page={page}&per-page={per_page}"
            url = f"{base_url}&page={page}"
            try:
                response = requests.get(url)
            except Exception as e:
                logger.error(e)
                continue
            data = response.json()
            articles = data['results']

            if not articles:
                break  # Если статьи закончились, выходим из цикла

            all_articles.extend(articles)
            print(f'added {len(articles)} for {query}')
            total_fetched += len(articles)
            if total_fetched > max_results:
                total_fetched = 0
                continue
                #return all_articles
            page += 1

    return all_articles


# Пример использования



def inverted_index_to_abstract(inv_index):
    if inv_index is not None:
        l_inv = [(w, p) for w, pos in inv_index.items() for p in pos]
        return " ".join(map(lambda x: x[0], sorted(l_inv, key=lambda x: x[1])))

if __name__ == "__main__":
    to_date = datetime.today().strftime('%Y-%m-%d')
    from_date = (datetime.today() - timedelta(days=60)).strftime('%Y-%m-%d')
    max_results = 100

    articles = get_openalex_articles(queries_to_extract_source_articles, from_date, to_date, max_results)

    logger.info(f"Found {len(articles)} articles")
    updated_abstract_articles = []
    for art in articles:
        if isinstance(art.get('abstract_inverted_index', None), dict):
            art['abstract'] = inverted_index_to_abstract(art['abstract_inverted_index'])
            updated_abstract_articles.append(art)
        else:
            logger.info(f"no abstract in {art['id']}")

    conn = pg_connection()
    for art in updated_abstract_articles:
        try:
            doi = art.get('doi')
            author = art.get('author', {}).get('display_name')
            title = art.get('title', None)
            published_date = art.get('publication_date', None)
            abstract = art.get('abstract', None)
            if not all([title, published_date, abstract]):
                continue
            elif len(abstract) < 100:
                continue
            insert_science_article(conn=conn, doi=doi, author=author, title=title, published_date=published_date,
                                   abstract=abstract)
        except Exception as e:
            logger.error(e)
            continue


