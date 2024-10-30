# ai_digest_finance
## Description
Project for creation PDF Summary with **Monthly review** about what studies and scientific articles came last month and quick overview what they have in common and what trends do they research

It generates fully automated PDF FILE with sections

* General Insights
* Key findings
* Main themes or trends emerging from these articles
* Commonalities or connections
* Future directions 
* Sources Articles list

Example: **AI_DIGEST_July_2024.pdf**

We use OpenALex https://openalex.org free database of scientific articles as our main source of data via their API 
We also use Gemini Pro model with its vast context window to qustion it with out questions (with prompts)

_______________

## Architecture and Scripts Description
<img src="./Untitled Diagram.drawio-2.svg">

**./questions.py**

`queries_to_extract_source_articles`: list of queries to extract articles from Openalex Database

`questions`: List of questions we ask Gemini Pro model to make sections in result PDF document
__________________________________________

**./articles.py**

Here we extract articles from OpenALex and store it in Postgres DB table

`CREATE TABLE public.science_articles (
	id serial4 NOT NULL,
	doi varchar(255) NULL,
	author text NULL,
	title text NULL,
	published_date date NULL,
	abstract text NULL,
	CONSTRAINT science_articles_doi_key UNIQUE (doi),
	CONSTRAINT science_articles_pkey PRIMARY KEY (id),
	CONSTRAINT science_articles_title_published_date_key UNIQUE (title, published_date)
);`

*If You gather data about multiples fields of study (FOS), there is need to adjust schema to have FOS field to identify right which articles should be used for the report*
__________________________________________

**./gemini_report.py**

Here we extract articles from Postges DB we gathered articles into using following variables

`title = "AI DIGEST"` -- Title of the document

`month = "July"` -- Month which be used to extract articles

`year = 2024` -- year which be used to extract articles

`topic = "Overview of Scientific Articles about Economy, Finance and related fields."` -- Description of the PDF document


Then we  use API key for **GEMINI PRO MODEL** with its outstanding context window over 1 million tokens and transfer extracted articles to the model, after that we asking questions (**questions variable**) to makes sections it our PDF Document later
ANd after getting answers from Gemini we conduct PDF document

__________________________________________

**./pgres_utils.py**

utils to create connection and insert\extract data

__________________________________________
**./AI_DIGEST_July_2024.pdf**

Example of the condicted document






  
