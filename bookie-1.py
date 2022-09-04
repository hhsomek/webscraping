from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import pandas as pd
import pickle

options = Options()
options.headless = True
options.add_argument('window-size=1920x1080') #Headless = True

web = 'https://sports.tipico.de/en/live/soccer'
path = "C:\\Users\\hhsomek\\Downloads\\selenium\\chromedriver"
#path = '/Users/.../chromedriver' #introduce the path of your chromedriver file

driver = webdriver.Chrome(path, options=options)
driver.get(web)
# driver.maximize_window() #Headless = False

#option 1
accept = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((By.XPATH, '//*[@id="_evidon-accept-button"]')))
#option 2
# time.sleep(2)
# accept = driver.find_element_by_xpath('//*[@id="_evidon-accept-button"]')
accept.click()

teams = []
x12 = []
btts = []
over_under = []
odds_events = []

# ------(use it only if necessary)------
# scroll down to the bottom to load all matches
# driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
# time.sleep(3) #implicit wait to let the page load all the matches
# ---------------------------------------

#select values from dropdown (update 1)
dropdowns = WebDriverWait(driver, 5).until(EC.presence_of_all_elements_located((By.CLASS_NAME, 'SportHeader-styles-drop-down')))

first_dropdown = Select(dropdowns[0])
second_dropdown = Select(dropdowns[1])
third_dropdown = Select(dropdowns[2])

first_dropdown.select_by_visible_text('Both Teams to Score') #update 'Both teams to score?' -> 'Both Teams to Score'
second_dropdown.select_by_visible_text('Over/Under')
third_dropdown.select_by_visible_text('3-Way')

#update 2
box = driver.find_element_by_xpath('//div[contains(@testid, "Program_UPCOMING")]')
#Looking for 'sports titles'
sport_title = box.find_element_by_class_name('SportTitle-styles-sport')

# update 3 (commented code not necesssary anymore)
# for sport in sport_title:
    # selecting only football
#     if sport.text == 'Football':
parent = sport_title.find_element_by_xpath('./..') #immediate parent node
# update 4 (+3 times .find_element_by_xpath('./..'))
grandparent = parent.find_element_by_xpath('./..').find_element_by_xpath('./..').find_element_by_xpath('./..').find_element_by_xpath('./..')
#3. empty groups
try:
    empty_groups = grandparent.find_elements_by_class_name('EventOddGroup-styles-empty-group')
    empty_events = [empty_group.find_element_by_xpath('./..') for empty_group in empty_groups[:]]
except:
    pass
#Single row event
single_row_events = grandparent.find_elements_by_class_name('EventRow-styles-event-row')
#4 remove empty events from single_row_events
try:
    empty_events
    single_row_events = [single_row_event for single_row_event in single_row_events if single_row_event not in empty_events]
except:
    pass
for match in single_row_events:
    odds_event = match.find_elements_by_class_name('EventOddGroup-styles-odd-groups')
    odds_events.append(odds_event)
    # teams
    for team in match.find_elements_by_class_name('EventTeams-styles-titles'):
        teams.append(team.text)
for odds_event in odds_events:
    for n, box in enumerate(odds_event):
        rows = box.find_elements_by_xpath('.//*')
        if n == 0:
            x12.append(rows[0].text)
        #5 over/under + goal line
        if n == 1:
            parent = box.find_element_by_xpath('./..')
            goals = parent.find_element_by_class_name('EventOddGroup-styles-fixed-param-text').text
            over_under.append(goals+'\n'+rows[0].text)
        #6 both teams to score
        if n == 2:
            btts.append(rows[0].text)

driver.quit()

#7 #unlimited columns
pd.set_option('display.max_rows', 500)
pd.set_option('display.max_columns', 500)
pd.set_option('display.width', 1000)

#Storing lists within dictionary
dict_gambling = {'Teams': teams, 'btts': btts,
                 'Over/Under': over_under, '3-way': x12}
#Presenting data in dataframe
df_tipico = pd.DataFrame.from_dict(dict_gambling)
#clean leading and trailing whitespaces
df_tipico = df_tipico.applymap(lambda x: x.strip() if isinstance(x, str) else x) #14.0\n or 14 or \n14.0

#Save data with Pickle
output = open('df_tipico', 'wb') #don't forget to change name_of_file
pickle.dump(df_tipico, output)
output.close()
print(df_tipico)