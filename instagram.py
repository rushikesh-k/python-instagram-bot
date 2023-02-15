import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.common.exceptions import TimeoutException
from decouple import config


# Setup a .env file in the current directory
# like
# iguser=yourusername
# igpassword=yourpsw
# ==========================================
USERNAME = config("iguser")
PASSWORD = config("igpassword")
# ==========================================

TIMEOUT = 25


def scrape():
    usr = "rushikesh.korgaonkar"
    #usr = input('[Required] - Whose followers do you want to scrape: ')

    options = webdriver.ChromeOptions()
    # options.add_argument("--headless")

    options.add_argument('--disable-extensions')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--no-sandbox')
    options.add_argument('start-maximized')
    options.add_argument('disable-infobars')
    options.add_argument('--disable-gpu')
    options.add_argument("--log-level=3")
    mobile_emulation = {
        "userAgent": "Mozilla/5.0 (Linux; Android 4.2.1; en-us; Nexus 5 Build/JOP40D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/90.0.1025.166 Mobile Safari/535.19"}
    options.add_experimental_option("mobileEmulation", mobile_emulation)

    bot = webdriver.Chrome(service=Service(
        ChromeDriverManager().install()), options=options)

    bot.get('https://www.instagram.com/accounts/login/')

    time.sleep(1)

    # Wait for the cookie policy button to be present
    wait = WebDriverWait(bot, 10)
    """ try:
        cookie_policy_button = wait.until(EC.element_to_be_clickable((By.XPATH, "/html/body/div[4]/div/div/div[3]/div[2]/button")))
        bot.execute_script("window.scrollTo(0, document.body.scrollHeight)") 
        cookie_policy_button.click()
    except TimeoutException:
        print("Cookie policy button not found on the page")

    print("[Info] - Logging in...")   """

    user_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[3]/div/label/input')))

    user_element.send_keys(USERNAME)

    print("[Info] - sent username...")

    pass_element = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[4]/div/label/input')))

    pass_element.send_keys(PASSWORD)

    login_button = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//*[@id="loginForm"]/div[1]/div[6]/button')))

    time.sleep(0.4)

    login_button.click()

    time.sleep(5)

    current_url = bot.current_url
    if current_url == "https://www.instagram.com/accounts/login/two_factor?next=%2F":
        print("Two-factor authentication is required")
        otp = input('[Required] - Enter OTP: ')

        otp_element = WebDriverWait(bot, TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH, '//div[starts-with(@id, "mount_0_0_")]/div/div/div/div[1]/div/div/div/div[1]/section/main/div[1]/div/div/div[2]/form/div[1]/div/label/input')))
        otp_element.send_keys(otp)
        otp_button = WebDriverWait(bot, TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH, '//div[starts-with(@id, "mount_0_0_")]/div/div/div/div[1]/div/div/div/div[1]/section/main/div[1]/div/div/div[2]/form/div[2]/button')))
        time.sleep(0.4)
        otp_button.click()
    else:
        print("Two-factor authentication is not required")

    bot.get('https://www.instagram.com/{}/'.format(usr))

    followersCount = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//div[starts-with(@id, "mount_0_0_")]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[2]/a/div/span')))

    followingCount = WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, '//div[starts-with(@id, "mount_0_0_")]/div/div/div/div[1]/div/div/div/div[1]/div[1]/div[2]/section/main/div/header/section/ul/li[3]/a/div/span')))

    print('[Info] - Followers: {}'.format(followersCount.text))
    print('[Info] - Following: {}'.format(followingCount.text))

    totalFollowing = int(followingCount.text)

    time.sleep(3.5)

    WebDriverWait(bot, TIMEOUT).until(
        EC.presence_of_element_located((
            By.XPATH, "//a[contains(@href, '/following')]"))).click()

    time.sleep(5)

    print('[Info] - Scraping...')

    users = set()

    for _ in range(round(totalFollowing // 20)):
        ActionChains(bot).send_keys(Keys.END).perform()
        time.sleep(3)

    following = bot.find_elements(By.XPATH,
                                  "//a[contains(@href, '/')]")

    time.sleep(5)
    # Getting url from href attribute
    skipElements = ["", "about", "blog",
                    "direct", "docs", "legal" "object_videos", "reels", "explore"]

    for i in following:
        if i.get_attribute('href'):
            if i.get_attribute('href').split("/")[3] not in skipElements:
                users.add(i.get_attribute('href').split("/")[3])
        else:
            continue

    print("[Info] - Total users: " + str(len(users)))
    time.sleep(5)   

    refresh_existing_following_users(usr)
    time.sleep(5)
    compare_and_update_following_users(users, usr)
    


def refresh_existing_following_users(usr):
    print('[Info] - refresh_existing_following_users...')
    try:
        with open("following" + "_" + usr + ".json", "r") as f:
            data = json.load(f)

        last_new_users = data["new"]
        for user in last_new_users:
            if user not in data["old"]:
                data["old"].append(user)

        data["old"] = list(dict.fromkeys(data["old"]))
        data["new"] = []
        
        #copy elements from data["unfollowed"] to data["archieved"]
        for user in data["unfollowed"]:
            if user not in data["archieved"]:
                data["archieved"].append(user)
        data["unfollowed"] = []

        with open("following" + "_" + usr + ".json", "w") as f:
            json.dump(data, f)
            f.flush()            
            print("[Info] - refresh_existing_following_users : Done")
    except FileNotFoundError:
        print("refresh_existing_following_users : No existing File found.")
        return

def compare_and_update_following_users(users, usr):
    print('[Info] - compare_and_update_following_users...')
    print('[DONE] - Your followers are being saved in following' +
          "_" + usr + '.json file!')
    try:
        with open("following" + "_" + usr + ".json", "r") as f:
            data = json.load(f)
    except FileNotFoundError:
        print("compare_and_update_following_users : No existing File found.")
        data = {"new": [], "old": [], "unfollowed": [], "archieved": []}

    old_users = data["old"]
    last_new_users = data["new"]
    new_users = []

    print("Old users: " + str(len(old_users)))
    print("New users: " + str(len(last_new_users)))

    #if user in users exists in old_users then let it be there if doesnt exists then move it to new_users
    for user in users:
        if user not in old_users:
            new_users.append(user)
    
    #if user in old_users exists in users then let it be there if doesnt exists then move it to unfollowed
    for user in old_users:
        if user not in users:
            data["old"].remove(user)
            data["unfollowed"].append(user)

    data["new"] = new_users

    #set elements in order by alphabetical order
    data["old"] = sorted(data["old"])
    data["new"] = sorted(data["new"])
    data["unfollowed"] = sorted(data["unfollowed"])
    data["archieved"] = sorted(data["archieved"])

    with open("following" + "_" + usr + ".json", "w") as f:
        json.dump(data, f)
        f.flush()
        print('[DONE] - Your followers are saved in following' +
              "_" + usr + '.json file!')

if __name__ == '__main__':
    scrape()
