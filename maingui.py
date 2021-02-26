from tkinter import *
from tkinter import filedialog
from tkinter import ttk
from tkinter import messagebox 
import pandas as pd
import os
import random 
import time 
import math
import requests
import socket
from tqdm import tqdm
import threading
import datetime
import urllib.request
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import NoSuchElementException

opener = urllib.request.URLopener()
opener.addheader('User-Agent', 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.182 Safari/537.36')


def browse_button():
    global folder_path
    filename = filedialog.askdirectory()
    folder_path.set(filename)

def Get_entry():
	put_no = int(no_of_imgs_entry.get())
	query = google_search_entry.get()
	SAVE_FOLDER = show_dir_e.get()
	if put_no != "" and query != "" and SAVE_FOLDER != "":
		threading.Thread(target=Main_program, args=(put_no, query, SAVE_FOLDER)).start()
		start_program["state"] = "disabled"
		messagebox.showinfo("ALERT", "Do Not Close Program Until The Completion Task") 
	else:
		print("Enter Some Thing")
		messagebox.showinfo("ALERT", "Please Fill All Filds") 

def Main_program(put_no, query, SAVE_FOLDER):
	driver = webdriver.Chrome(r"driver/chromedriver.exe")
	print(" Opning Chrome Browser..... \n")
	driver.maximize_window()
	driver.get("https://www.google.com/imghp?hl=en&tab=wi&ogbl")
	search_bar = driver.find_element_by_name("q")
	search_bar.send_keys(query)
	search_bar.send_keys(Keys.RETURN)
	print(" Searching...\n ")
	time.sleep(3)

	i = 1
	t = 2
	total_images.set(f"PAGE SCROLLING")
	root.update_idletasks() 
	while i < t:
	    driver.execute_script("window.scrollBy(0,document.body.scrollHeight)")
	    try:
	        driver.find_element_by_xpath("/html/body/div[2]/c-wiz/div[3]/div[1]/div/div/div/div/div[5]/input").click()
	    except Exception as e:
	        pass
	    time.sleep(5)
	    collat_bar['value'] += 10
	    precent.set(f"PAGES {i}/{t}")
	    root.update_idletasks()
	    i+=1

	soup = BeautifulSoup(driver.page_source, 'html.parser')
	img_tags = soup.find_all("img", class_="rg_i")
	total_number = len(img_tags)
	print(f" In This Page {total_number} Images Found \n \n")
	print(" Image Collating \n") 

	if int(put_no) <= total_number:
	    total_number = put_no
	else:
	    total_number = total_number

	image_links = []
	driver.find_element_by_xpath('//*[@id="islrg"]/div[1]/div[1]/a[1]/div[1]/img').click()
	count = 1
	image_not_found = 0
	total_images.set(f"TOTAL IMAGES FOUND/{len(img_tags)}")
	collat_bar['value'] = 0
	root.update_idletasks()

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
		    collat_bar['value']+=(count/total_number) * 100
		    precent.set(f"{count}/TOTAL {total_number}")
		    root.update_idletasks()
		    count+=1

	with open("links"+ "/" + "download_links.txt", "w") as lf:
	    for ap in image_links:
	        lf.write("%s\n" % ap)

	print(" Links Collecting Done ")

	ERROR = 0
	LINKS = []
	COUNT = 0
	WRITE_CSV = []
	total_images.set(f"DOWNLOADING START")
	collat_bar['value'] = 0
	root.update_idletasks()
	print(" Downloading Start \n")  
	with open("links/download_links.txt", "r") as link_file:
	    for i in link_file:
	        LINKS.append(i)

	for link in LINKS:
		try:
			socket.setdefaulttimeout(10)
			filename, headers = opener.retrieve(link, SAVE_FOLDER + "/" + str(COUNT) + ".jpg")
			print(f" {COUNT} Download, {link} ")
			time.sleep(0.5)
			collat_bar['value'] += (COUNT/int(len(LINKS))) * 100
			precent.set(f"{COUNT}/{len(LINKS)}")
			root.update_idletasks()
			COUNT+=1
			save_csv = {"INDEX": COUNT, "KEYWORD":query, "LINKS": link, "ERROR": ERROR}
			WRITE_CSV.append(save_csv)
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
	try:
		os.makedirs("csv")
	except FileExistsError:
	    print(" directory already exists ")
	    pass
	df = pd.DataFrame(WRITE_CSV)
	df.to_csv("csv" + "/" + query + " " + str(COUNT) + ".csv") 
	print(f"{ERROR} Images Not Respond")
	print(f"Downloading Finish, Total {COUNT} Images Downloaded \n")
	messagebox.showinfo("DOWNLOAD", f"DOWNLOAD COMPLETE, TOTAL DOWNLOAD {COUNT}") 
	time.sleep(5)
	driver.close()


root = Tk()
root.title("Download Bulk Images From Google")

no_of_img = Label(root, text="NO OF IMAGES (no only)", font = "Calibri 11")
google_search = Label(root, text="GOOGLE KEYWORD", font = "Calibri 11")

dirs = Label(root, text="SET DOWNLOAD FOLDER", font = "Calibri 11")
dirs_entry = Button(root, text="FOLDER", command=browse_button, width=6, font = "Calibri 11", bg="#ffe899")

folder_path = StringVar()
show_dir_e = Entry(root, textvariable=folder_path, width=50, bg = '#e5e5e5', borderwidth=2, font = "Calibri 11")

no_of_imgs_entry = Entry(root, width=100, bg = '#e5e5e5', borderwidth=2, font = "Calibri 11")
google_search_entry = Entry(root, width=100, bg = '#e5e5e5', borderwidth=2, font = "Calibri 11")

start_program = Button(root, text="START PROGRAM", width=60, font = "Calibri 11", bg="#077f21", command=Get_entry)


total_images = StringVar()
collat_bar_lab = Label(root, textvariable=total_images, font = "Calibri 11")
collat_bar = ttk.Progressbar(root, orient=HORIZONTAL, length=500, mode='determinate')
precent = StringVar()
precent_show = Label(root, textvariable=precent, font = "Calibri 11")


no_of_img.grid(row=0, column=0, sticky='E')
no_of_imgs_entry.grid(row=0, column=1, padx=20, pady=20, ipady=3)

google_search.grid(row=1, column=0, sticky='E')
google_search_entry.grid(row=1, column=1, padx=20, pady=20, ipady=3)

dirs.grid(row=2, column=0,sticky='E')
dirs_entry.grid(row=2, column=1, sticky='W', padx=20)
show_dir_e.grid(row=2, column=1, sticky='W', padx=80, ipady=3)

start_program.grid(row=4, column=1, pady=20)

collat_bar_lab.grid(row=3, column=0, pady=20)
collat_bar.grid(row=3, column=1, sticky='W', padx=80)
precent_show.grid(row=3, column=2, sticky='w')


root.geometry("1000x300+500+500")
root.mainloop()