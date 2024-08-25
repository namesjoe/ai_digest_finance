import psycopg2
from logger import get_logger

logger = get_logger(__name__)


def pg_connection():
  conn = psycopg2.connect(
    host="localhost",
    database="postgres"
  )
  return conn


def insert_article(conn, title, description, published_date, url, final_url, text):
  """
  Вставляет статью в таблицу articles.

  Args:
    conn: Подключение к базе данных PostgreSQL.
    title (str): Заголовок статьи.
    description (str): Описание статьи.
    published_date (datetime): Дата публикации статьи.
    url (str): Исходный URL статьи.
    final_url (str): Перенаправленный URL статьи.
    text (str): Текст статьи.
  """
  try:
    with conn.cursor() as cur:
      cur.execute(
        """
        INSERT INTO news (title, description, published_date, url, final_url, text) 
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (title, published_date) DO NOTHING;  -- Игнорируем дубликаты
        """,
        (title, description, published_date, url, final_url, text)
      )
    conn.commit()
    logger.info(f"Статья '{title}' успешно добавлена.")
  except psycopg2.Error as e:
    logger.error(f"Ошибка при добавлении статьи: {e}")
    conn.rollback()

def insert_science_article(conn, doi, author, title, published_date, abstract):
  try:
    with conn.cursor() as cur:
      cur.execute(
        """
        INSERT INTO science_articles (doi, author, title, published_date, abstract) 
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (title, published_date) DO NOTHING;  -- Игнорируем дубликаты
        """,
        (doi, author, title, published_date, abstract)
      )
    conn.commit()
    logger.info(f"Статья '{title}' успешно добавлена.")
  except psycopg2.Error as e:
    logger.error(f"Ошибка при добавлении статьи: {e}")
    conn.rollback()

if __name__ == '__main__':
  conn = pg_connection()
  print(1)
  from datetime import datetime

  insert_article(conn=conn,
                 title="test_title",
                 description='test_description',
                 published_date=datetime(2022, 1, 15),
                 url="https://google.com",
                 final_url='hh.ru',
                 text="Test test test"

                 )