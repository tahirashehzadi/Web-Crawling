#! /usr/bin/python
import configparser
from bs4 import BeautifulSoup
import requests

# The selenium module
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options

from FinalizeArticle import FinalizeArticle


class NewsSources:
    parser = configparser.ConfigParser()
    parser.read("config/configuration.ini")

    def __init__(self):
        self.Sources = self.confParser( "sources" )

    def confParser(self, section):

        if not self.parser.has_section(section):
            print("No section information are available in config file for", section)
            return
        # Build dict
        tmp_dict = {}
        for option, value in self.parser.items(section):
            option = str(option)
            value = value
            tmp_dict[option] = value
        return tmp_dict

    def get(self, src):
        if src == "sources":
            return self.Sources

    def get_html(self, url):
        retry_count = 0
        error = True
        while error and retry_count < 3:
            try:
                r = requests.get(url, headers={'User-Agent': 'Mozilla/5.0'}, timeout=10)
                r.encoding = "utf-8"
                page = r.text
                page_obj = BeautifulSoup(page, "lxml")
                error = False
            except:
                error = True
                page_obj = None
                retry_count = retry_count + 1
                print("%s URL not accessible " % (src_url))

        return page_obj

if __name__ == '__main__':
    obj = NewsSources()
    Sources = obj.get("sources")
    IMAGE_DIR = "images/"

    CHROME_PATH = '/usr/bin/google-chrome'
    WINDOW_SIZE = "1920,1080"

    chrome_options = Options()
    #chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=%s" % WINDOW_SIZE)
    chrome_options.binary_location = CHROME_PATH

    driver = None
    finalize_article = FinalizeArticle()

    for src in Sources:
        print("Starting "+src)
        src_url = Sources[src]
        src_url_start = src_url.split("|")[0]
        src_url_end = src_url.split("|")[-1]
        counter = 1
        if src == "spoonflower" or src == "myfabricdesigns":
            driver = webdriver.Chrome(executable_path="ChromDriver/chromedriver", chrome_options=chrome_options)
        exit = False
        while True:
            if src == "pattern_bank":
                page_url = src_url_start + str(counter) + src_url_end
                page_obj = obj.get_html(page_url)
            elif src == "surface_pattern":
                page_url = src_url + str(counter) + "/"
                page_obj = obj.get_html(page_url)
            elif src == "spoonflower":
                page_url = src_url_start + str(counter) + src_url_end
                if driver != None:
                    driver.get(page_url)
                    WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "b-design-item")))
                    page_src = driver.page_source
                    #driver.close()
                    page_obj = BeautifulSoup(page_src, "lxml")
                else:
                    page_obj = None
            else:
                page_url = src_url_start + str(counter) + src_url_end
                if driver != None:
                    driver.get(page_url)
                    WebDriverWait(driver, 50).until(EC.visibility_of_element_located((By.CLASS_NAME, "b-design-item")))
                    page_src = driver.page_source
                    page_obj = BeautifulSoup(page_src, "lxml")
                else:
                    page_obj = None

            if page_obj != None:
                try:
                    if src == "pattern_bank":
                        pattern_no_results = page_obj.findAll("div", attrs={"class":"patterns-no-results"})[0]
                        exit = True
                    elif src == "surface_pattern":
                        title = page_obj.find("title").text
                        if "Page not found" in title:
                            exit = True
                    elif src == "spoonflower":
                        pattern_no_results = page_obj.findAll("ul", attrs={"class":"order-item-list"})[0].findAll("li")
                        if len(pattern_no_results) > 0:
                            exit = False
                        else:
                            exit = True
                except:
                    exit = False
                    pass
                if exit:
                    break
                if src == "pattern_bank":
                    div_list = page_obj.findAll("div", attrs={"class":"row design-thumbnails product-image-grid js-image-grid"})[0].findAll("div", attrs={"class":"design-col product-col col-lg-3 col-sm-4 col-xs-6"})
                elif src == "surface_pattern":
                    div_list = page_obj.findAll("div", attrs={"class":"content-grid-download__entry-image"})
                elif src == "spoonflower":
                    div_list = page_obj.findAll("ul", attrs={"class":"order-item-list"})[0].findAll("li")
                for div in div_list:
                    if src == "pattern_bank":
                        img_url = div.findAll("img", attrs={"class":"img-responsive lazyload"})[0].attrs["data-src"]
                    elif src == "surface_pattern":
                        div.div.decompose()
                        img_url = div.findAll("img")[0].attrs["src"]
                    elif src == "spoonflower":
                        img_url = div.findAll("img")[0].attrs["src"]
                    finalize_article.DownloadAndStoreImage(img_url, src)
                counter = counter + 1


    print("Process Finished...")