# DocDrop Web Applications

## Technologies
- Python3.6+
- Django3.1+
- Celery
- RabbitMQ
- PostgreSQL
- jQuery
 

## Overview
A collection of web applications showcasing use of [Hypothesis web annotator](https://web.hypothes.is/) or in support of Hypothesis usage.

More detail on each included application below.

-------------------------

### DocDrop (main application): 
#### Features
Drag and drop a document to annotate. Annotations will persist and be available if the same document is uploaded again. Supports many common document formats including PDF, EPUB and various office formats such as spreadsheets and editors. Both Microsoft and ODF documents are generally supported. Upon upload, the user is presented with a web representation of the document for Hypothesis annotation.  

#### Technical
Documents are stored on AWS. A reference is stored in the database. Before storage to AWS, a hash is taken and if the hash exists (checking database references) the same document is not uploaded again.

Documents (most types) are converted using the Libre Office headless engine. The resulting web viewable formats are pdf or csv or epub (which are not converted as there is a dedicated epub viewer). 

A hash of the converted document (if conversion was necessary) is also taken and stored. Thus, when a user uploads an existing document (i.e hash of parent exists in database) the derivative or converted document is provided and no upload nor conversion occurs.

The LibreOffice conversion process is managed by Celery with RabbitMQ (task queues). See `tasks.py`. A reference to the completed (or failed) conversion is stored in the database upon resolution. This result is checked against by the web service to manage download of the web viewable document.
    


### YouTube Video Annotator:
#### Features
Displays YouTube videos with subtitles (if existing) and allows search and annotation of the subtitles. User can pause or jump to various points in the video by clicking on text chunks in the subtitle display. Displays error if user enters a video without subtitles. 

Not all videos have subtitles created for them and the application is dependent on YouTube for subtitle creation.

Language of the subtitles can be manipulated (if multiple language subtitles exist for the video) by passing a query string argument in the url. The argument can either be a language or comma separated list of languages (in order preference). I.E `https://docdrop.org/video/<my video id>/?lang=de` or `https://docdrop.org/video/<my video id>/?lang=en,es`. English is default if no language specified. An error will occur if subtitles are not available in the specified langauge. [ISO Language
Code Reference](https://www.andiamo.co.uk/resources/iso-language-codes/).


#### Technical
Subtitles are obtained serverside using Python [youtube-transcript-api](https://pypi.org/project/youtube-transcript-api/) and passed to the users browser when the video display template renders. 

The browser then uses the [YouTube iframe api](https://developers.google.com/youtube/iframe_api_reference) to sync and control the video as user interacts with buttons and the subtitles. Addtional JavaScript is used to provide features such as search and scrolling of the subtitles. 

The subtitles can be annotated using Hypothesis.


### PDF OCR:
#### Features
Parses text from an image pdf and overlays it, creating a pdf with selectable text which can then be annotated using Hypothesis. If a pdf already contains text, there is an option to force redo which will turn the pdf back into an image and OCR that, overwriting existing text with new appliction OCR'd text. 

#### Technical
Both the original and derivative (ocr'd) pdf are stored on AWS with references stored in the database.

As with the core DocDrop application, documents are only stored once as determined by hashes, and on subsequent uploads (of the same document), the existing derivative document is provided with no further processing or upload. 

Celery with RabbitMQ is used to manage the OCR process in task queues. The result of the process is stored in the database and consulted by the browser to show user process is complete. 

The conversion process occurs using [OCRmyPDF](https://github.com/jbarlow83/OCRmyPDF) which is shelled out with a system call to the system `ocrmypdf` command.

OCRmyPDF uses tesseract and a number of additional libraries and the results are quite good, comparable to many commercially available tools. However it is very computationally expensive, most especially the "force" (or redo) option which converts the pdf back into an image before OCR. In order to rate limit, the application creates a lock file for each conversion process and refuses additional process requests after the lock file limit count is reached. This "allowed number of ocr tasks" can be altered through
the environmental variable `MAX_SIM_OCR_PROCESSES`. Additional Celery workers calling OCR may be added to other servers or VM instances at some point in the future to support higher traffic.


### PDF Refingerprinter:
#### Features
Change a pdf's "fingerprint" which is used by Hypothesis to determine if a pdf is the same as one that is already known. This allows different sets of Hypothesis annotations to be used on the same pdf by changing the identifier.  

#### Technical
Refingerprint pdfs are not stored on AWS nor is a reference kept in the database. Intermediate and final work product are stored locally and deleted upon completion.

Celery with RabbitMQ is used to queue and manage the refingerprint process (see `tasks.py`). Also it is used to queue deletion (mentioned above). 

The refingerprint process uses [pdfrw](https://github.com/pmaupin/pdfrw) for reading and writing to the document.

The document ID is overwritten with a randomized ID and random metadata is written to the document resulting in a pdf that has a different identity when used by Hypothesis.


### Google Drive Annotator:
#### Features
(currently 10/13/21 broken)

Allows pdfs from google drive to be opened in annotation display. Appears on "open with" in Google Drive ui as option. User can annotate pdf and read annotations, including other uploads or instances of the same pdf.

#### Technical
DocDrop has evolved to support many more document types than pdf. Google changed some policies on use. There are some additional issues and considerations with the DocDrop2 format. The original approach of hacking drive app into pdf.js was not nice. All this has resulted in the drive app being broken and stranded. TODO.


## Local Setup

## Python
3.6+. A virtualenvironment is recommended to install packages but how you do it is up to you. 

### Postgresql

`sudo apt install postgresql`

`sudo su postgres`

`psql`

`create database dbname` (e.g. dbname=docdrop)

`createuser --interactive --pwprompt` to set username (e.g. dduser) and password (e.g. ddpwd)

`psql`

`create database docdrop;`

`GRANT all privileges ON DATABASE docdrop TO dduser;`

`sudo apt install python-psycopg2`

`sudo apt install libpq-dev`

`pip install -r requirements.txt`

`cp _docs/env sample/ droppdf/.env`

edit .env

 ```
 DB_NAME='droppdf'
 DB_USER='dduser'
 DB_PASSWORD='ddpwd'
 DB_HOST='localhost'
 DJANGO_SERVER='dev'
 DJANGO_DEBUG=true
 DJANGO_SECRET_KEY='secret123'
 ```

### Build Front-End

Nope!


### Run Migrations 
Create and update database tables.

`python manage.py migrate`


### Create Super User
(optional, if you want to log on to admin interface to view db data)  
`python manage.py createsuperuser`


### Run Locally

`rabbitmq-server`

`cd droppdf/`

(terminal or screen 1)
`celery -A financial_planning_app worker -l info`

(terminal or screen 2)
`python manage.py runserver`


#### Monitor Celery

`systemctl status celery`

`cat /var/log/celery/worker.log`
 

### Manage

`http://localhost:8000/admin/`



## Deployment

### TODO
