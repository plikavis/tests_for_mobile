import allure
import pytest
from allure import step
from allure_commons._allure import StepContext
from appium.options.android import UiAutomator2Options
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from selene import browser, support
import os

import utils.allure


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


@pytest.fixture(scope='session', autouse=True)
def mobile_management():
    login = os.getenv('LOGIN')
    password = os.getenv('PASSWORD')
    app = os.getenv('APP')
    options = UiAutomator2Options().load_capabilities({
        "platformVersion": "9.0",
        "deviceName": "Google Pixel 3",

        # Set URL of the application under test
        "app": f"{app}",
        # Set other BrowserStack capabilities
        'bstack:options': {
            "projectName": "First Python project",
            "buildName": "browserstack-build-1",
            "sessionName": "BStack first_test",

            # Set your access credentials
            "userName": f"{login}",
            "accessKey": f"{password}"
        }
    })

    # browser.config.driver = webdriver.Remote("http://hub.browserstack.com/wd/hub", options=options)
    with allure.step('init app session'):
        browser.config.driver = webdriver.Remote(
            'http://hub.browserstack.com/wd/hub',
            options=options
        )

    browser.config.timeout = float(os.getenv('timeout', '10.0'))

    browser.config._wait_decorator = support._logging.wait_with(
        context=StepContext
    )
    with step('Skip onboarding'):
        browser.element((AppiumBy.ID, "org.wikipedia.alpha:id/fragment_onboarding_skip_button")).click()

    yield
    utils.allure.screenshot()
    utils.allure.page_source()

    session_id = browser.driver.session_id

    with allure.step('tear down app session'):
        browser.quit()

    utils.allure.video(login, password, session_id)

