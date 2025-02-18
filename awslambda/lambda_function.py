from selenium.webdriver import Chrome, ChromeOptions
from screenshot_handler import ScreenshotHandler
import json
import traceback
from pprint import pprint
from server_pickler import load_methods, pickle_result
from chrome_options_handler import gen_default_chrome_options
from PIL import _imaging
from PIL import Image


def gen_chrome(chrome_options=None):
    chrome_options = chrome_options or gen_default_chrome_options()
    chrome_options.binary_location = "./bin/headless-chromium"  # required
    chrome = Chrome("./bin/chromedriver", chrome_options=chrome_options)
    return chrome


def lambda_handler(event, context):
    try:
        if event["httpMethod"] == "POST":
            # print(event["body"])
            libraries, called_name_as_method, arg, kwargs, funcs, chrome_options = load_methods(
                event["body"])
        else:
            raise Exception(f"httpMethod is {event['httpMethod']}, not 'POST'")
        try:
            for library_command in libraries:
                exec(library_command, globals())
        except Exception as e:
            raise Exception(f"{e} in lambda")
        for name, func in funcs.items():
            setattr(Chrome, name, func)
        chrome = gen_chrome(chrome_options)
        screenshothandler = ScreenshotHandler(chrome)
        # setattr(self, func.__name__, types.MethodType(method, self))
        method = getattr(chrome, called_name_as_method)
        result = method(*arg, **kwargs)
        statusCode = 200
    except Exception as e:
        statusCode = 501
        print("------server printing error start------")
        traceback.print_exc()
        print("------server printing error end------")
        result = e
    finally:
        try:
            chrome.quit()
        except Exception as e:
            pass
    result = screenshothandler.wrap_with_screenshots(result)
    return {
        'statusCode': statusCode,
        'body': pickle_result(result)
    }
