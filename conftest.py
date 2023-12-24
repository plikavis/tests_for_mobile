import allure
import pytest
import requests
from allure import step
import allure_commons._allure
from allure_commons._allure import StepContext
from appium.options.android import UiAutomator2Options
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from dotenv import load_dotenv
from requests.auth import HTTPBasicAuth
from selene import browser, support
import os


@pytest.fixture(scope='session', autouse=True)
def load_env():
    load_dotenv()


# def attach_bstack_video(session_id):
#     import requests
#     bstack_session = requests.get(
#         f'https://api.browserstack.com/app-automate/sessions/{session_id}.json',
#         auth=({login}, {password}),
#     ).json()
#     print(bstack_session)
#     video_url = bstack_session['automation_session']['video_url']
#
#     allure.attach(
#         '<html><body>'
#         '<video width="100%" height="100%" controls autoplay>'
#         f'<source src="{video_url}" type="video/mp4">'
#         '</video>'
#         '</body></html>',
#         name='video recording',
#         attachment_type=allure.attachment_type.HTML,
#     )

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

    allure.attach(
        browser.driver.get_screenshot_as_png(),
        name='screenshot',
        attachment_type=allure.attachment_type.PNG,
    )

    allure.attach(
        browser.driver.page_source,
        name='screen xml dump',
        attachment_type=allure.attachment_type.XML,
    )

    session_id = browser.driver.session_id

    with allure.step('tear down app session'):
        browser.quit()

    bstack_session = requests.get(url=f'https://api-cloud.browserstack.com/app-automate/sessions/{session_id}.json',
                                  auth=(login, password),
    ).json()
    print(bstack_session)
    video_url = bstack_session['automation_session']['video_url']

    allure.attach(
        '<html><body>'
        '<video width="100%" height="100%" controls autoplay>'
        f'<source src="{video_url}" type="video/mp4">'
        '</video>'
        '</body></html>',
        name='video recording',
        attachment_type=allure.attachment_type.HTML,
    )

