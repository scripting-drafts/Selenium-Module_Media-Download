from os import path
from seleniumwire import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options
import tools.turquoise_logger as turquoise_logger
import tools.mod_initializer as gui_enhancements
from subprocess import call

class SeleniumWireModule:
    def __init__(self):
        logg = turquoise_logger.Logger()
        gui_enhancements.run_sel()
        path_firefox_binary = 'tools/geckodriver.exe'
        path_geckodriver_log = path.abspath('resources/geckodriver.log')
        log = logg.logging()
        localhost = '127.0.0.1'
        initial_url = 'https://www.google.com'

        options = Options()
        # options.add_argument('--headless')
        options.set_preference('dom.webnotifications.enabled', False)
        options.set_preference('dom.push.enabled', False)
        options.set_preference('dom.webdriver.enabled', False)
        options.set_preference('useAutomationExtension', False)
        options.set_preference('privacy.trackingprotection.enabled', True)

        options.set_preference('browser.cache.disk.enable', False)
        options.set_preference('browser.cache.memory.enable', False)
        options.set_preference('browser.cache.offline.enable', False)
        options.set_preference('network.http.use-cache', False)

        # USER AGENT OPT
        # options.set_preference('intl.accept_languages', random.choice(localesList).lower())
        # options.set_preference('general.useragent.override', random.choice(userAgentList))

        profile_path = open('resources/profile_path', 'r').read()

        driver = webdriver.Firefox(firefox_profile=profile_path,
                                   options=options, executable_path=path_firefox_binary,
                                   service_log_path=path_geckodriver_log)
        driver.implicitly_wait(10)
        log.debug(f'Webdriver is UP')

        self.log = log
        self.localhost = localhost
        self.initial_url = initial_url
        self.driver = driver

    def get_to(self, url):
        self.driver.get(url)
        if self.driver.requests[0].response.status_code == 200:
            self.log.debug(f'Connection reached')
            title = url.split('/')[-1].strip('\n')
        else:
            self.log.debug(f'Destination not reachable')
            title = ''

        try:
            self.driver.find_element(By.CSS_SELECTOR, '.btn-primary').click()
        except Exception as e:
            self.log.error(f'error: {e}')

        self.title = title

    def get_content(self):
        for request in self.driver.requests:
            if ".m3u8" in request.url:
                self.log.debug(f'URL contains streaming: {request.url}')
                call(f'ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -i {request.url} -c copy {self.title}.mp4')

    
    def healthcheck(self):
        '''1 Returns an int if dead and None if alive  
        2 Throws a WebDriverException if dead'''
        self.log.debug('Webdriver healthcheck going on')
        try:
            assert(self.driver.service.process.poll() == None)
            self.driver.service.assert_process_still_running()
            self.log.debug('The driver appears to be OK')
            status = True
        except Exception as e:
            self.log.debug(f'The driver appears to be NOK - {e}')
            status = False
        
        return status

    def tearDown(self):
        '''Graceful shutdown and status verification'''
        self.driver.quit()
        self.log.debug('Verifying webdriver shutdown')
        status = self.healthcheck()

        if status == False:
            self.log.debug('Successful driver termination')
        else:
            self.log.error('Unsuccessful driver termination')


urls = open('urls.txt', 'r').readlines()
wm = SeleniumWireModule()

for url in urls:
    wm.get_to(url)
    wm.get_content()

wm.tearDown()