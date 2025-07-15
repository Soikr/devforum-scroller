import os
import json
import re
import time
import logging
import click
import platform
from math import ceil
from pathlib import Path
from tqdm import tqdm

from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.firefox.service import Service as FirefoxService

URL = "https://devforum.roblox.com/"

@click.command()
@click.option('--pmin', type=click.FloatRange(0.0, 3.0), default=1, help="Minutes spent on post before scrolling.")
@click.option('--rmin', type=click.FloatRange(0.0, 3.0), default=2, help="Minutes spent per reply.")
@click.option('--rper', type=click.FloatRange(0.0, 1.0), default=1.0, help="Percentage of replies to read per post.")
@click.option('--log', is_flag=True, default=False, help="Log content to file.")
@click.option('--log-path', type=click.Path(exists=False), default='logs/devforum.log', help="Log file location.")
@click.option('--cookie-file', type=click.Path(exists=False), default='cookies.json', help="Cookie file location.")
def main(pmin, rmin, rper, log, log_path, cookie_file):
    """Logs in and scrolls through the Roblox Devforums most recent posts."""
    if log:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        logging.basicConfig(filename=log_path, level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')
    logger = logging.getLogger(__name__)

    settings = {
        'POST_DELAY': int(pmin * 60),
        'REPLIES_DELAY': int(rmin * 60),
        'PERCENT_READ': round(rper, 2),
    }

    def env(var, default=None):
        return os.environ.get(var, default)

    browser_env = env("BROWSER_PATH")
    if browser_env:
        browser_bin = (
            os.path.join(browser_env, "Applications/Firefox.app/Contents/MacOS/firefox")
            if platform.system() == "Darwin"
            else os.path.join(browser_env, "bin/firefox")
        )
    else:
        browser_bin = None
    geckodriver_path = env("BROWSERDRIVER_PATH")

    options = FirefoxOptions()
    options.add_argument("--headless")
    if browser_bin:
        options.binary_location = browser_bin

    service = FirefoxService(executable_path=geckodriver_path) if geckodriver_path else FirefoxService()
    driver = webdriver.Firefox(service=service, options=options)

    def progress_sleep(seconds, desc="Waiting"):
        with tqdm(total=seconds, desc=desc, bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt}s', unit='s', leave=False) as bar:
            for _ in range(seconds):
                time.sleep(1)
                bar.update(1)

    def scroll(post_title=None):
        try:
            replies = WebDriverWait(driver, 2).until(
                ec.presence_of_element_located((By.CSS_SELECTOR, '.timeline-replies'))
            )
        except TimeoutException:
            if post_title:
                tqdm.write(f"Post: {post_title}")
            time.sleep(settings['REPLIES_DELAY'])
            return

        match = re.match(r'^(\d+)\s*/\s*(\d+)$', replies.text.strip())
        if not match:
            return
        total = ceil(float(match.group(2)) * settings['PERCENT_READ'])
        current_value = int(match.group(1))
        prev_value = current_value

        if post_title:
            tqdm.write(f"Post: {post_title}")
        progress = tqdm(
            total=total, initial=current_value, desc="Replies", unit="reply",
            bar_format='{desc}: {percentage:3.0f}%|{bar}| {n_fmt}/{total_fmt} ', leave=True
        ) if total > 0 else None

        while True:
            match = re.match(r'^(\d+)\s*/\s*(\d+)$', replies.text.strip())
            if match:
                current_value = int(match.group(1))
                if progress and current_value > prev_value:
                    progress.update(current_value - prev_value)
                if current_value != prev_value and settings['REPLIES_DELAY'] > 0:
                    time.sleep(settings['REPLIES_DELAY'])
                prev_value = current_value
                if current_value >= total:
                    break
            driver.execute_script('window.scrollBy(0, 100);')
            time.sleep(.05)
        if progress: progress.close()
        print()

    def open_posts():
        WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, "table.category-list")))
        feedback, bugs = 3, 4
        post_selectors = [
            f"table.category-list:nth-child(1) > tbody:nth-child(2) > tr:nth-child({row}) > td:nth-child(3) > div:nth-child({div}) > a:nth-child(2)"
            for row, div in [(feedback, d) for d in range(1,7)] + [(bugs,2)]
        ]
        post_links = []
        for selector in post_selectors:
            try:
                link = driver.find_element(By.CSS_SELECTOR, selector)
                post_links.append((link.text, link.get_attribute("href")))
            except Exception as err:
                tqdm.write(f"Error collecting post link: {err}")

        for title, url in post_links:
            try:
                driver.get(url)
                if log: logger.info(f"Post: {title}")
                progress_sleep(settings['POST_DELAY'], desc="Post wait")
                scroll(post_title=title)
            except Exception as err:
                tqdm.write(f"Error opening post: {err}")

    def start():
        if not Path(cookie_file).is_file():
            msg = (f"The {cookie_file} file was not found. Export your Devforum cookies "
                   f"(needs ROBLOSECURITY) as a json file into this directory. "
                   f"Use the browser extension 'EditThisCookie' to export your cookies.")
            tqdm.write(msg)
            raise FileNotFoundError(msg)
        with open(cookie_file) as file:
            cookies = json.loads(file.read().replace('lax','Lax').replace('no_restriction','None').replace('strict','Strict'))
            cookie = next((c for c in cookies if c.get("name") == ".ROBLOSECURITY"), None)
            if not cookie:
                tqdm.write("ROBLOSECURITY cookie not found.")
                raise Exception("ROBLOSECURITY cookie not found.")

        driver.get(URL)
        try:
            driver.add_cookie(cookie)
        except Exception as err:
            tqdm.write(f"Error adding cookie: {err}")
            raise
        try:
            WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.CSS_SELECTOR, ".btn-icon-text"))).click()
            WebDriverWait(driver, 10).until(ec.element_to_be_clickable((By.XPATH, "//button[@type='button']"))).click()
        except TimeoutException:
            tqdm.write("Login buttons not found or clickable.")
            raise
        try:
            user = WebDriverWait(driver, 10).until(ec.presence_of_element_located((By.CSS_SELECTOR, "#toggle-current-user")))
            tqdm.write(f"Logged in with: {user.get_attribute('aria-label')}\n")
        except TimeoutException:
            tqdm.write("Not logged in, please check your cookies.")

    tqdm.write("DevforumAuto is getting ready...")
    try:
        start()
        open_posts()
    except Exception as e:
        tqdm.write(f"Fatal error: {e}")
    tqdm.write("Tasks finished, closing browser")
    driver.quit()

if __name__ == "__main__":
    main()
