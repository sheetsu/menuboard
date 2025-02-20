import time
import sys
import requests
import asyncio
from concurrent.futures import ThreadPoolExecutor
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chromium.options import ChromiumOptions
from config.configuration import DEVICE_SETTINGS, TOKENS
from src.logger_config import logger

# URL_hdmi1 = 'https://app.smartlunch.pl/menu_board?token={}'.format(TOKENS['token_1'])
# URL_hdmi2 = 'https://app.smartlunch.pl/menu_board?token={}'.format(TOKENS['token_2'])

URL_hdmi1 = 'https://smartlunch:eDgdHy6ojWb2Ez2LDDxggiZyEupdEz4Y@staging6.smartlunch.pl/menu_board?token={}'.format(TOKENS['token_1'])
URL_hdmi2 = 'https://smartlunch:eDgdHy6ojWb2Ez2LDDxggiZyEupdEz4Y@staging6.smartlunch.pl/menu_board?token={}'.format(TOKENS['token_2'])

technical_break_filepath = 'file:///home/pi/menuboard/remote_control_service/technical_break/technical_break.html'

service = Service()
time.sleep(3)

def parse_data():
    """
    Parses two command-line arguments ('true' or 'false') into booleans for HDMI outputs,
    logs the values, and returns them as a tuple.
    """
    def str_to_bool(value):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
        else:
            raise ValueError(f'Wrong logic value: {value}')

    if len(sys.argv) != 3:
        logger.error("Usage: script.py HDMI1 HDMI2")
        sys.exit(1)

    hdmi1 = str_to_bool(sys.argv[1])
    hdmi2 = str_to_bool(sys.argv[2])

    logger.info(f"Detected HDMI outputs: HDMI1: {hdmi1}, HDMI2: {hdmi2}")

    return hdmi1, hdmi2


def browser_config(hdmi1, hdmi2):
    """
    Sets up Chrome drivers for HDMI outputs based on connectivity flags.

    Uses an inner helper to launch a driver at a given debugger address.
    For HDMI1: launches if hdmi1 is True (or hdmi2 is True when hdmi1 is False).
    For HDMI2: launches only if both hdmi1 and hdmi2 are True.
    """
    def setup_browser(debugger_address):
        try:
            browser_options = ChromiumOptions()
            browser_options.add_experimental_option("debuggerAddress", debugger_address)
            logger.info(f"Starting browser at debugger adress:{debugger_address}")
            return webdriver.Chrome(service=service, options=browser_options)
        except Exception as e:
            logger.error(f"Problem with browser at debugger address: {debugger_address}: {e}")
            return False

    driver_HDMI1 = setup_browser("localhost:8989") if (hdmi1 or (hdmi2 and not hdmi1)) else False
    if not hdmi1:
        logger.warning("HDMI1 is not connected")

    driver_HDMI2 = setup_browser("localhost:8990") if hdmi2 and hdmi1 else False
    if not hdmi2:
        logger.warning("HDMI2 is not connected")

    return driver_HDMI1, driver_HDMI2


async def async_check_url(executor, driver, url, label):
    """
    Asynchronously verifies and updates the driver's URL using an executor.

    If a URL is provided and doesn't contain 'smartlunch', it navigates to that URL.
    Otherwise, it loads a technical break page. Logs actions and errors as appropriate.
    """
    def check_url(driver, url, label):
        try:
            if url:
                if 'smartlunch' not in driver.current_url:
                    driver.get(url)
                    logger.info(f"Setting MenuBoard's URL: {url} for {label}")
            else:
                if driver.current_url != technical_break_filepath:
                    driver.get(technical_break_filepath)
                    logger.error(f"Problem occured - switching to technical break page on {label}")
                else:
                    logger.debug(f"Problem occured - {label} displays technical break page")
        except Exception as e:
            logger.error(f"Error with {label}: ", e)

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(executor, check_url, driver, url, label)


async def open_browser_page(url_1, url_2, driver_HDMI1, driver_HDMI2):
    """
    Asynchronously sets browser pages for HDMI outputs using a thread pool.
    Schedules URL checks for available drivers and awaits their completion.
    """
    executor = ThreadPoolExecutor(max_workers=2)

    tasks = []
    if driver_HDMI1:
        tasks.append(async_check_url(executor, driver_HDMI1, url_1, "HDMI1"))
    if driver_HDMI2:
        tasks.append(async_check_url(executor, driver_HDMI2, url_2, "HDMI2"))

    await asyncio.gather(*tasks)


def connect(host='https://staging6.smartlunch.pl/api/v1/terminal/heartbeat'):
    """
    Sends a heartbeat POST with the MenuBoard's serial number and returns True if the response status is 200.
    """
    try:
        url = host
        myobj = {"terminal": {"terminal_name": DEVICE_SETTINGS['Serial']}}
        smart_response = requests.post(url, json=myobj)

        response = smart_response.json()
        if 'status' in response:
            if response['status'] == 200:
                logger.debug(f"Ping succeeded with status: {response['status']}")
                return True
            else:
                logger.debug(f"Ping failed with status: {response['status']}")
                return False
        else:
            logger.debug(f"Ping failed; response: {response}")
            return False

    except Exception as e:
        logger.error("Error in connect: ", e)
        return False


def remote_control_task(driver_HDMI1, driver_HDMI2):
    """
    Continuously checks connectivity and updates browser pages.
    
    Every 20 seconds, it pings the server using connect(). If the ping succeeds,
    it updates the browsers with live URLs; if not, it loads technical break pages.
    """
    while True:
        try:
            resp = connect()
            if resp:
                logger.debug(f"Updating browser pages to: HDMI1: {URL_hdmi1}, HDMI2: {URL_hdmi2}")
                asyncio.run(open_browser_page(URL_hdmi1, URL_hdmi2, driver_HDMI1, driver_HDMI2))
            else:
                logger.debug(f"Updating browser pages to technical break pages")
                asyncio.run(open_browser_page(False, False, driver_HDMI1, driver_HDMI2))
        except Exception as e:
            logger.error("Error in remote_control_task: ", e)
        time.sleep(20)
