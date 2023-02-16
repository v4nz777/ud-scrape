Coupon Scraper
==============

This is a Python script that scrapes coupon codes from Udemy and similar sites. It currently supports the following sites:

*   Real Discount ([https://app.real.discount/](https://app.real.discount/))
*   Discudemy ([https://www.discudemy.com/](https://www.discudemy.com/))
*   Udemy Freebies ([https://www.udemyfreebies.com/](https://www.udemyfreebies.com/))

Installation
------------

1.  Install Python 3.x on your machine. You can download Python from the official website ([https://www.python.org/downloads/](https://www.python.org/downloads/)).
2.  Clone the repository to your local machine.
3.  Install the required packages by running the following command in the terminal:
    
    `pip install -r requirements.txt`
    

Usage
-----

1.  Open a terminal or command prompt and navigate to the directory where the script is located.
    
2.  Run the script with the following command:
    
    
    `python app.py [provider]`
    
    Replace `[provider]` with the name of the provider you want to scrape. If you don't specify a provider, it will default to "realdiscount". Valid provider names are "realdiscount", "discudemy", and "udemyfreebies".
    
    For example, to scrape coupons from Discudemy, run the following command:
    
    
    `python app.py discudemy`
    
3.  The script will output the results to the terminal, and save a log file to the `logs` directory.
    

Troubleshooting
---------------

If you encounter any issues with the script, please check the following:

*   Make sure you have installed Python 3.x on your machine.
*   Make sure you have installed the required packages by running `pip install -r requirements.txt`.
*   If the script is not producing any output, check the log files in the `logs` directory for any errors or exceptions.
*   If you are still having issues, please open an issue on GitHub or contact the me for support.
