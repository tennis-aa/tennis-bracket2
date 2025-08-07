# tennis-bracket2
Bracket challenge for ATP tournaments web app

## Dependencies

The app is written in python with the flask framework using the google firestore as a database and configuration files to deploy to a google cloud app engine are also provided. To scrape results from the atp website, the python package beautifulsoup is required. To install dependencies, you can use the requirements.txt file: `pip install -r requirements.txt`. You can also install the only direct dependencies: `pip install flask bs4 firebase-admin` (this may run into issues if there are breaking changes in new versions of the packages).

## Development

`python main.py`

> Additional setup steps for the database are required.
> With gcloud, I can use the following command to allow default access to the firestore database: `gcloud auth application-default login`

## Deployment to Google Cloud App Engine

`gcloud app deploy`

> installing the google cloud cli is required