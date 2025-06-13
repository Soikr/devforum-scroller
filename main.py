#!/usr/bin/env python

# Reading cookies
import json
# Necessary libraries
import re
import sys
import time
from pathlib import Path

# Selenium libraries
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as firefoxOptions
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait

if '--continue' not in sys.argv:
    sys.exit(
        "I am not liable for any damage caused by this script, which serves to only be educational.\nIf you wish to continue, run the script with the --continue argument.")

COOKIE_FILE = 'cookies.json'
URL = "https://devforum.roblox.com/"

SCROLL_AMOUNT = 100

options = firefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
driver.implicitly_wait(10)


def scroll():
    try:
        replies = WebDriverWait(driver, 4).until(
            ec.presence_of_element_located((By.CSS_SELECTOR, '.timeline-replies'))
        )
    except TimeoutException:
        print("This post has no replies, or the page has not loaded properly.\nContinuing...")
        driver.execute_script(f'window.scrollBy(0, 500);')
        time.sleep(1)
        return

    prev_value = None
    while True:
        match = re.match(r'^(\d+)\s*/\s*(\d+)$', replies.text.strip())
        if match:
            current_value = match.group(1)
            if current_value != prev_value:
                print("Replies:", current_value, "/", match.group(2))
                prev_value = current_value
            if current_value == match.group(2):
                break
        driver.execute_script(f'window.scrollBy(0, {SCROLL_AMOUNT});')
        time.sleep(.1)


def open_posts():
    # May be different on your account, check the category number on the Devforums.
    help_and_feedback = 3
    category = help_and_feedback

    posts = [
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(1) > a:nth-child(2)"),
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(2) > a:nth-child(2)"),
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(3) > a:nth-child(2)"),
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(4) > a:nth-child(2)"),
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(5) > a:nth-child(2)"),
        (By.CSS_SELECTOR,
         f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({category}) > td:nth-child(3) > div:nth-child(6) > a:nth-child(2)")
    ]

    for method, path in posts:
        post = driver.find_element(method, path)
        print("Post:", post.text)
        post.click()
        scroll()
        driver.back()
        WebDriverWait(driver, 10).until(
            lambda d: d.execute_script('return document.readyState') == 'complete'
        )


def main():
    if not Path(COOKIE_FILE).is_file():
        raise FileNotFoundError(
            "The cookies.json file was not found. Please export your Devforum cookies (This just needs ROBLOXSECURITY) as a json file into this directory.\nYou can use the browser extension 'EditThisCookie' to export your cookies.")

    with open(COOKIE_FILE) as file:
        cookies = file.read()

        replace_table = {
            'lax': 'Lax',
            'no_restriction': 'None',
            'strict': 'Strict'
        }

        for find, replace in replace_table.items():
            cookies = cookies.replace(find, replace)

        cookies = json.loads(cookies)
        cookies = next((c for c in cookies if c.get("name") == ".ROBLOSECURITY"), None)
        if not cookies:
            raise Exception("ROBLOSECURITY cookie not found.")

    driver.get(URL)
    driver.add_cookie(cookies)

    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.CSS_SELECTOR, ".btn-icon-text"))).click()
    time.sleep(4)
    WebDriverWait(driver, 10).until(
        ec.element_to_be_clickable((By.XPATH, "//button[@type='button']"))).click()

    user = None
    try:
        user = WebDriverWait(driver, 10).until(
            ec.presence_of_element_located(
                (By.CSS_SELECTOR, "#toggle-current-user")
            ))
    except TimeoutException:
        print("Not logged in, please check your cookies.")
    print("Logged in with:", user.get_attribute("aria-label"))


print("Setting up...")
main()
print("Beginning tasks")
open_posts()
print("Tasks finished, closing browser")
driver.quit()
