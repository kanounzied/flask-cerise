import getpass
import csv

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PATH = "C:\Program Files (x86)\chromedriver.exe"
driver = webdriver.Chrome(PATH)
url = 'https://www.linkedin.com/login/fr?fromSignIn=true&trk=guest_homepage-basic_nav-header-signin'
driver.get(url)

search = driver.find_elements_by_class_name("mercado-text_input--round")

email = input('enter your email: ')
search[0].send_keys(email)
pwd = getpass.getpass("Type your password : ")
search[1].send_keys(pwd)
search[1].send_keys(Keys.RETURN)

try:
    element = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "input_verification_pin"))
    )
    print('if this message appears check your mail and type the code')
    code = input('code: ')
    element.send_keys(code)
    element.send_keys(Keys.RETURN)
except:
    print('mamchetech')

contacts = list([])
with open('Connections.csv') as csvDataFile:
    csvReader = csv.reader(csvDataFile)
    for row in csvReader:
        contacts.append({
            'firstName': row[0],
            'lastName': row[1]
        })
print(contacts)
contacts.remove({'firstName': 'First Name', 'lastName': 'Last Name'})
# print(contacts)
with open('emails.csv', mode='a', encoding="utf-8", newline='') as csv_file:  # enregistrement du dict dans emails.csv
    fieldnames = ['firstName', 'lastName', 'email']
    writer = csv.DictWriter(csv_file, fieldnames=fieldnames, delimiter=',')
    writer.writeheader()
    for contact in contacts:  # parcour sur les contacts
        firstName = contact['firstName']
        lastName = contact['lastName']
        firstName.replace(" ", "%20")
        lastName.replace(" ", "%20")
        driver.get('https://www.linkedin.com/search/results/people/?facetNetwork=%5B%22F%22%5D&firstName='+ firstName +'&lastName='+ lastName +'&origin=FACETED_SEARCH')
        classe = 'search-result__image-wrapper'
        href = driver.find_element_by_css_selector(".search-result__image-wrapper a").get_attribute('href')
        coordonnees = href + "detail/contact-info/"
        driver.get(coordonnees)
        email = driver.find_element_by_css_selector('.ci-email a').text
        print(email)
        contact['email'] = email
        writer.writerow(contact)
    csv_file.close()
driver.quit()