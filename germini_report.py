import json
import google.generativeai as genai
import json
from pgres_utils import pg_connection
import pandas as pd
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
import calendar
from questions import questions, replace_items_prefix, replace_items_postfix, replacer
import os

########################################
title = "AI DIGEST"
month = "July"
year = 2024
topic = "Overview of Scientific Articles about Economy, Finance and related fields."
###########################################

month_number = list(calendar.month_name).index(month)
_, last_day = calendar.monthrange(year, month_number)
start_date = f"{year:04d}-{month_number:02d}-01"
end_date = f"{year:04d}-{month_number:02d}-{last_day:02d}"

gemini_api_key = os.environ.get('GEMINI_API_KEY')
pg_conn = pg_connection()
genai.configure(api_key=gemini_api_key)


query = f"""
SELECT title, abstract, doi
FROM science_articles 
WHERE published_date BETWEEN '{start_date}' AND '{end_date}';
"""

df = pd.read_sql(query, pg_conn)

articles = {}
for index, row in df.iterrows():
    if index >= 125:
        break
    articles[row['title'] + "|DOI:" + row['doi']] = row['abstract']

# Преобразование словаря в JSON-строку
json_data = json.dumps(articles)

model = genai.GenerativeModel('gemini-1.5-flash')
chat = model.start_chat(history=[])

# Отправка JSON в Gemini
response = chat.send_message(json_data + """ <<< It's json data with title(DOI):abstract of recent scientific articles.
 You will need to analize it all together as a whole.""")


prompt = "DO NOT PROVIDE breakdown for each topic! Analize all topics together as a whole! when you citate any article use it's Title and DOI. Be specific if you write about some finding, trend or comparison, then tell us in which articles it mentioned"


responses = {}
for q in questions:
    response_on = chat.send_message(f"{q} {prompt}")
    print(f"QUESTION: \n {q} \n:")
    responses[q] = response_on.text
    print(response_on.text)

ascii_style = ParagraphStyle(
    name='AsciiStyle',
    parent=getSampleStyleSheet()['Normal'],
    fontName='Courier',  # Или любой другой моноширинный шрифт
)

# Рисунок компьютера из символов ASCII art
pc_ascii = """
     _.--""--._
   .'          `.
  |              |
  |   O      O   | 
  |              |
  | .---------. |
  | |           | |
  | |           | |
  | '----------' |
  |              |
  ________________
    |          |
    |__________|
       |    |
    ---       ---
"""


# Create PDF report
doc = SimpleDocTemplate(f"AI_DIGEST_{month}_{year}.pdf", pagesize=letter)
styles = getSampleStyleSheet()
story = []

story.append(Paragraph(title, styles['Title']))
story.append(Paragraph(f"{month} {year}", styles['Heading1']))
story.append(Paragraph(topic, styles['Heading2']))
story.append(Spacer(1, 36))  # Add some space
story.append(Paragraph("Authors: Sedov Dmitrii, Lazarev Andrei", styles['Heading3']))
story.append(Paragraph(pc_ascii, style=ascii_style))
story.append(PageBreak())  # Force page break after the title page

#general insights
story.append(Paragraph("General Insights: ", styles['Heading3']))
formatted_response = replacer(str_value=response.text, replace_items=replace_items_prefix, prefix=True)
formatted_response_ = replacer(str_value=formatted_response, replace_items=replace_items_postfix, prefix=False)
paragraphs = formatted_response_.splitlines()
for paragraph_text in paragraphs:
    story.append(Paragraph(paragraph_text, styles['Normal']))
story.append(PageBreak())

# questions
for i, resp_q in enumerate(responses.keys()):
    story.append(Paragraph(resp_q, styles['Heading3']))
    #formatted_response = responses[resp_q].replace("** ", "** \n").replace(": ", ": \n")
    formatted_response = replacer(str_value=responses[resp_q], replace_items=replace_items_prefix, prefix=True)
    formatted_response_ = replacer(str_value=formatted_response, replace_items=replace_items_postfix, prefix=False)
    paragraphs = formatted_response_.splitlines()

    for paragraph_text in paragraphs:
        story.append(Paragraph(paragraph_text, styles['Normal']))
    #story.append(Paragraph(formatted_response, styles['Normal']))
    story.append(PageBreak())  # Force a page break after each section

story.append(Paragraph(f"Sources (Articles published during {month} of {year}):", styles['Heading3']))
for index, row in df.iterrows():
    article_title = row['title']
    article_doi = row['doi']
    story.append(Paragraph(f"Title: {article_title}; DOI: {article_doi}", styles['Normal']))

# Build the PDF
doc.build(story)
