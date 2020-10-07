# from selenium.webdriver.common.keys import Keys
import click
from os import getcwd
import splinter
from selenium.webdriver.common.keys import Keys
from time import sleep



@click.command()
@click.argument('class_name')
@click.argument('assignment_name')
@click.argument('username')
@click.argument('password')
def get(class_name, assignment_name, username, password):
    prof = {
        'browser.helperApps.neverAsk.saveToDisk': 'application/zip',
        'browser.download.lastDir': getcwd()
    }

    b = splinter.Browser(profile_preferences=prof)
    b.visit('https://bblearn.nau.edu')
    b.find_by_id('agree_button').click()
    b.find_by_id('cas-login-btn').click()
    b.find_by_id('username').first.fill(username)
    b.find_by_id('password').first.fill(password)
    b.find_by_name('submit').first.click()

    b.find_by_tag('body').first.type('focus')
    ae = b.driver.switch_to_active_element()
    class_xpath = f"//h4[contains(text(), '{class_name}')]"
    while b.is_element_not_present_by_xpath(class_xpath):
        ae.send_keys(Keys.ARROW_DOWN)
        sleep(0.1)
    b.links.find_by_partial_text(class_name).click()

    while b.is_element_not_present_by_tag('iframe'):
        sleep(0.1)

    with b.get_iframe('classic-learn-iframe') as iframe:
        grade_center_xpath = f"//a[contains(text(), 'Grade Center')]"
        if not iframe.is_element_visible_by_xpath(grade_center_xpath):
            iframe.find_by_id('menuPuller').click()
        iframe.links.find_by_text('Grade Center').click()
        iframe.links.find_by_text('Full Grade Center').click()
        (iframe.find_by_text(assignment_name).first
         .find_by_xpath('../..//a').first.click())
        iframe.find_by_text('Assignment File Download').click()
        iframe.find_by_id('listContainer_selectAll').click()
        iframe.find_by_id('bottom_Submit').click()
        iframe.links.find_by_partial_text('Download').click()

    b.quit()
