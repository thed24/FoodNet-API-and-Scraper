FoodNet is a Hackathon project to aggregate food review data and display it via a React front-end. This repo contains two projects which supply the front-end with data.

# FoodNet Scrapers

Python scripts that run daily via a cronjob sitting in AWS Lambda. They format the scraped data into a specific model that is then persisted via the PynamoDB ORM to a DynamoDB table.

ZomatoScraper uses a headless Chromium Lambda Layer to scrape data.

GoogleReviewScraper uses the Google Review API to poll for data.

# FoodNet API

A Python API that uses PynamoDB ORM to retrieve all the items in the DB, merge the duplicate entries and output them via a simple GET endpoint. 
