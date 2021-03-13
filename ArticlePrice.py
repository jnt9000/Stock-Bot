import selenium
import datetime
import pickle
import yaml
import os
from datetime import datetime
from selenium import webdriver
from pandas_datareader import data
from pandas_datareader._utils import RemoteDataError

class SeekingAlpha:
    def __init__(self, link):
        self.driver_path = self.get_driver_path()
        self.driver = webdriver.Chrome(self.driver_path)
        
        try:

            self.load_cookies()

            self.driver.get(link)

            start_date = end_date = str(self.get_date_object().date())

            stock = self.get_ticker()

            self.get_data(stock, start_date, end_date)

        finally: 

            self.driver.quit()

    def get_driver_path(self):
        """Gets the path from the params.yaml file"""
        with open('params.yaml') as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        return data["chrome_driver_path"]
    
    def load_cookies(self):
        """Loads cookies from the pickle cookies file. Browser needs to exist already"""
        print("Logging in to Seeking Alpha.")
        self.driver.get("https://seekingalpha.com/")
        cookies = pickle.load(open(os.path.expanduser("~/Desktop/Development/Stock-Bot/cookies.p"), "rb"))
        for cookie in cookies:
            self.driver.add_cookie(cookie)
        self.driver.get("https://seekingalpha.com/")
        print("Logged in.")

    def save_cookies(self):
        """Saves the current cookies. Use this after you log in for the first time."""
        self.driver.get("https://seekingalpha.com/")
        pickle.dump( self.driver.get_cookies() , open(os.path.expanduser("~/Desktop/Development/Stock-Bot/cookies.p"),"wb"))

    def get_date_object(self):
        """Finds date in html and converts to texts, creates a date time object from that text."""   
        date_obj = self.driver.find_element_by_xpath("""//*[@id="root"]/div[1]/div/main/div[2]/div[2]/div/div/section[1]/div/div/div[2]/span[1]""")
        date_string = date_obj.text
        date_string = " ".join(date_string.replace(".","").split(" ")[0:3])
        date_object = datetime.strptime(date_string, "%b %d, %Y")
        return date_object

    def get_ticker(self):
        """Finds ticker in html and converts to text, then makes it lowercase"""
        ticker_obj = self.driver.find_element_by_xpath("""//*[@id="root"]/div[1]/div/main/div[2]/div[2]/div/div/section[1]/div/div/div[3]/div/div/div[1]/ul/li/span""")
        stock = ticker_obj.text.split(":")[1].replace(")","").lower()
        return stock

    def get_data(self, ticker, start_date, end_date):
        """Prints stock information from api"""
        try:
            self.stock_data = data.DataReader(ticker,'yahoo',start_date,end_date)
            self.stock_data["%"] = 100*(self.stock_data["High"]-self.stock_data["Open"])/self.stock_data["Open"]
            print(self.stock_data[["High","Open","%"]])
        except RemoteDataError:
            print('No data found for {t}'.format(t=ticker))
        
if __name__ == "__main__":

    link = input("What is the link?")
    
    SeekingAlpha(link)
