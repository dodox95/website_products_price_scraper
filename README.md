Product Scraper and Updater

This script automates the process of scraping product data from a website, comparing it with existing product data, and updating the products in a WooCommerce store accordingly.
Features

    Scrapes product data from a website using Selenium.
    Compares scraped product data with existing product data.
    Updates product details in a WooCommerce store.
    Disables unlisted products in WooCommerce.
    Writes product data to CSV files for record-keeping.

Prerequisites

    Python 3.x
    Firefox browser (used by Selenium)
    Geckodriver (for Selenium to control Firefox)

Setup

    Clone the repository:

bash

git clone <repository-url>
cd <repository-directory>

    Set up a virtual environment and install the required packages:

bash

python -m venv venv
source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
pip install -r requirements.txt

    Create a .env file in the root directory and add the following configurations:

makefile

WOOCOMMERCE_URL=your_woocommerce_url
WOOCOMMERCE_CONSUMER_KEY=your_consumer_key
WOOCOMMERCE_CONSUMER_SECRET=your_consumer_secret
GERMANIAMINT_LOGIN_URL=your_login_url
GERMANIAMINT_LOGIN_EMAIL=your_email
GERMANIAMINT_LOGIN_PASSWORD=your_password

Replace the placeholders with your actual data.
Usage

Run the script:

bash

python script_name.py

The script will:

    Log in to the specified website.
    Scrape product data.
    Compare the scraped data with existing product data.
    Update the WooCommerce store with the new data.
    Write the data to CSV files (products.csv, my_products.csv, and comparison.csv).

Notes

    Ensure that the Firefox browser and Geckodriver are correctly installed and set up.
    The script runs in a loop and waits for an hour between iterations.
    Ensure that the .env file is never committed to the repository for security reasons.
