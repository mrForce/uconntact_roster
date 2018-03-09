org_id = ''
netid=''
password = ''

import time
import string
from selenium import webdriver
import requests
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.common.keys import Keys
binary=FirefoxBinary('/usr/bin/firefox')


import sys
from lxml import html
#returns a requests session
def login(netid, password):
    binary = FirefoxBinary('/usr/bin/firefox')
    browser = webdriver.Firefox(firefox_binary=binary)
    browser.get('https://netid.uconn.edu/tools/login.php')
    netid_entry = browser.find_element_by_xpath('//*[@id="username"]')
    netid_entry.send_keys(netid)
    password_entry = browser.find_element_by_xpath('//*[@id="password"]')
    password_entry.send_keys(password)
    login = browser.find_element_by_xpath('//*[@id="button"]')
    login.click()
    return browser
def get_netid(email, browser, first=True):
    
    browser.get('http://phonebook.uconn.edu/ladvanced.html')
    if first:
        browser.find_element_by_xpath('/html/body/table[1]/tbody/tr[2]/td/table/tbody/tr[2]/td[2]/table/tbody/tr/td/div[1]/p/a').click()
        browser.get('http://phonebook.uconn.edu/ladvanced.html')
    search = browser.find_element_by_xpath('/html/body/table[2]/tbody/tr[3]/td[2]/form/table/tbody/tr[4]/td[3]/input')
    search.send_keys(email)
    search.send_keys(Keys.RETURN)
    time.sleep(3)
    soup = BeautifulSoup(browser.page_source, 'html.parser')
    rows = soup.find_all('tr')
    netid_row = False
    netid_td = False
    for row in rows:
        data = row.find_all('td')        
        i = 0
        for td in data:
            divs = td.find_all('div')
            for div in divs:
                if div.text == 'NetID':
                    netid_row = True
                    for y in data[(i + 1)::]:
                        if all([z in string.ascii_lowercase or z in string.digits for z in y.text]) and len(y.text) > 4:
                            return str(y.text)
                            
                        #if len(y.text) > 3:
                        #    netid_td = y.text
                        #    break
            i += 1
    return 'None'




session =login(netid, password)
print('IMPORTANT: For various reasons, this script won\'t include officers in the organization. You\'ll need to add them manually.')
print('Also, I can\'t tell if a student is undergrad or graduate')
#if you're organization has more than 1000 members, change the take=1000 to something bigger (it needs to be bigger than the size of your organization). 
r = requests.get('https://uconntact.uconn.edu/api/discovery/organization/' + org_id + '/member?take=100a0&orderByField=account.firstName', auth=(netid, password))
#just giving a large upper bound is easier than probing the page for the # of members
response = r.json()
members = []
for member in response['items']:
    account = member['account']
    first_name = account['firstName']
    last_name = account['lastName']
    email = 'NONE'
    for k, v in account.items():
        if 'email' in k.lower() and '@uconn.edu' in v:
            email = v
            break
    members.append((first_name, last_name, email))

first=  True
for first_name, last_name, email in members:
    netid = get_netid(email, session, first)
    print('\t'.join([first_name, last_name, netid, email, 'undergrad']))
    first = False
