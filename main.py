import os
import time 
import math
import requests
import socket
from tqdm import tqdm
import datetime
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36')


print(" Program Starting...\n Do Not Close Program And Browser Until Job Is Done \n")
print(" Create A New Directory Where Photos Download. \n")

SAVE_FOLDER = input(" Directory Name: ")
while not SAVE_FOLDER:
    print(" Create A New Directory Where Photos Download. \n")
    SAVE_FOLDER = input(" Directory Name: ")

print(" How Many Image You Download, Enter Number Only \n")
put_no = int(input(" Enter Number: "))
while not put_no or math.isnan(put_no) :
    print(" How Many Image You Download, Enter Number Only \n")
    put_no = input(int(" Enter Number: "))

try:
    os.makedirs("../" + SAVE_FOLDER)
except FileExistsError:
    print(" directory already exists ")
    pass

print(" What you want to search on google image? \n")
query = input(" Google Image Search: ")
while not query:
    print(" What you want to search on google image? \n")
    query = input(" Google Image Search: ")


driver = webdriver.Chrome(r"driver/chromedriver.exe")
print(" Opning Chrome Browser..... \n")
driver.maximize_window()
driver.get("https://www.google.com/imghp?hl=en&tab=wi&ogbl")
search_bar = driver.find_element_by_name("q")
search_bar.send_keys(query)
search_bar.send_keys(Keys.RETURN)
print(" Searching...\n ")
time.sleep(3)

i = 0
t = 10
count_page = tqdm(total=t)
while i < t:  
    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
    try:
        driver.find_element_by_xpath("/html/body/div[2]/c-wiz/div[3]/div[1]/div/div/div/div/div[5]/input").click()
    except Exception as e:
        pass
    time.sleep(5)
    i+=1
    count_page.update(1)

soup = BeautifulSoup(driver.page_source, 'html.parser')
img_tags = soup.find_all("img", class_="rg_i")
total_number = len(img_tags)

print(f" In This Page {total_number} Images Found \n \n")

print(" Image Collating \n") 

if put_no <= total_number:
    total_number = put_no
else:
    total_number = total_number

image_links = []
count_bar = tqdm(total=total_number)
driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img').click()
count = 1
image_not_found = 0

while len(image_links) <= total_number:
    try:
        element_click = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[1]/a[2]/div')
        element_click.click()
        time.sleep(2)
    except NoSuchElementException:
        print("Error somthing")
    path = driver.find_element_by_xpath('//*[@id="Sva75c"]/div/div/div[3]/div[2]/c-wiz/div/div[1]/div[1]/div/div[2]')
    image = path.find_element_by_tag_name('img')
    link = image.get_property('src')
    if ".jpg" in link or ".png" in link or ".jpeg" in link or " TIFF" in link or "PSD" in link:
	    image_links.append(link)
	    count_bar.update(1)

with open("links"+ "/" + "download_links.txt", "w") as lf:
    for ap in image_links:
        lf.write("%s\n" % ap)

print(" Links Collecting Done ")

time.sleep(5)
driver.close()
driver.quit()  


ERROR = 0
LINKS = []
COUNT = 0

print(" Downloading Start \n")  
with open("links/download_links.txt", "r") as link_file:
    for i in link_file:
        LINKS.append(i)
for link in LINKS:
    try:
        socket.setdefaulttimeout(10)
        filename, headers = opener.retrieve(link, "../" + SAVE_FOLDER + "/" + str(COUNT) + ".jpg")
        COUNT+=1
        print(f" {COUNT} Download, {link} ")
    except requests.exceptions.ConnectionError:
        ERROR+=1
    except requests.exceptions.ReadTimeout:
        ERROR+=1
    except socket.timeout:
        ERROR+=1
    except urllib.error.HTTPError as e:
        ERROR+=1
        print('HTTPError: {}'.format(e.code))
    except urllib.error.URLError as e:
        ERROR+=1
        print('URLError: {}'.format(e.reason))
    except OSError:
        ERROR+=1
        print("Os Error")

print(f"{ERROR} Images Not Respond")
print(f"Downloading Finish, Total {COUNT} Images Downloaded \n")


