try:
    import os
    import json
    import sys

    from selenium import webdriver
    from selenium.webdriver.common.keys import Keys
    from selenium.webdriver.common.by import By
    from selenium.webdriver.chrome.options import Options
    from selenium.webdriver.support.ui import WebDriverWait

    from abc import ABC, abstractmethod
    from time import sleep

except Exception as e:
    print("Error Modules not found : {} ".format(e))


class ChromeDriver(ABC):

    @abstractmethod
    def get_driver(self):
        """This will provide the Webdriver object """
        pass


class WebDriver(ChromeDriver):

    def __init__(self, path=None):
        self.path = path
        self.options = Options()
        self.options.add_argument('--headless')
        self.options.add_argument('--no-sandbox')
        self.options.add_argument('--start-maximized')
        self.options.add_argument('--start-fullscreen')
        self.options.add_argument('--single-process')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--window-size=1920,1080')
        self.c_service = webdriver.ChromeService(executable_path=self.path)
        self.driver_instance = self.get_driver(True)

    def get_driver(self, headless=False):
        if headless:
            driver = webdriver.Chrome(options=self.options,service=self.c_service)
            return driver
        else:
            self.option = Options()
            self.option.add_argument("--incognito")
            self.option.add_experimental_option("detach", True)
            driver = webdriver.Chrome(service=self.c_service)
            return driver


class Commands(WebDriver):

    def __init__(self, commands, path, site_id):
        self.commands = commands
        self.site_id = site_id
        WebDriver.__init__(self, path=path)

    def execute(self):
        if self.commands is None:
            message = {
                "status": 200,
                "data": {"message": "No commands to excute"},
                "error": {}
            }
        else:
            for command in self.commands:

                if command.get("command").lower() == "sleep":
                    sleep(int(command.get("time", 0)))

                if command.get("command").lower() == "click":

                    if command.get("selector").lower() == "xpath":
                        try:
                            self.driver_instance.find_element(
                                By.XPATH, command.get("path")).click()
                        except Exception as e:
                            print("error: {}".format(e))

                    if command.get("selector").lower() == "id":
                        try:
                            self.driver_instance.find_element(By.ID,
                                command.get("path")).click()
                        except Exception as e:
                            print("error: {}".format(e))

                    if command.get("selector").lower() == "css_selector":
                        try:
                            self.driver_instance.find_element(By.CSS_SELECTOR,
                                command.get("path")).click()
                        except Exception as e:
                            print("error: {}".format(e))

                if command.get("command").lower() == "type":

                    if command.get("selector").lower() == "xpath":
                        try:
                            self.driver_instance.find_element(By.XPATH,
                                command.get("path")).send_keys(command.get("search"))
                        except Exception as e:
                            print("error: {}".format(e))

                    if command.get("selector") == "id":
                        try:
                            self.driver_instance.find_element(By.ID,
                                command.get("path")).send_keys(command.get("search"))
                            # self.driver_instance.find_element(By.ID,command.get("path")).send_keys(Keys.ENTER)
                        except Exception as e:
                            print("error: {}".format(e))
                    
                    if command.get("selector") == "css_selector":
                        try:
                            self.driver_instance.find_element(By.CSS_SELECTOR,
                                                            command.get("path")).send_keys(command.get("search"))
                        except Exception as e:
                            print("error: {}".format(e))
                
                if command.get("command").lower() == "list_products":
                    try:
                        product_list = self.driver_instance.find_elements(By.CSS_SELECTOR, command.get("path"))
                    except Exception as e:
                        print("error: {}".format(e))
                    output_products = []
                    for product in product_list:
                        tmp = {}
                        tmp["title"] = tmp["price"] = ""

                        try:
                            tmp["title"] = product.find_element(
                                By.CSS_SELECTOR, command.get("title_path")).text

                        except Exception as e:
                            print("error: {}".format(e))
                        
                        try:
                            tmp["price"] = product.find_element(
                                By.CSS_SELECTOR, command.get("price_path")).text

                        except Exception as e:
                            print("error: {}".format(e))

                        output_products.append(tmp)
                        print("-------------------------")
                    
                    with open(self.site_id + '_output.json', 'w', encoding='utf-8') as f:
                        json.dump(output_products, f, ensure_ascii=False, indent=4)


    
        return True
    



class Crawler(ABC):

    @abstractmethod
    def run(self):
        """This will provide the Webdriver object """
        pass


class Scrapper(Commands, Crawler):

    def __init__(self, action, path):
        self.action = action
        Commands.__init__(
            self, path=path, commands=self.action.get("commands"), site_id=self.action.get("site_id"))

    def run(self):
        driver = self.driver_instance
        # driver.maximize_window()
        driver.get(self.action.get("url"))

        commands = self.action.get("commands")
        self.execute()


def main():
    if len(sys.argv) <= 1:
        print("SITE_ID required")
        return
    
    site_id = sys.argv[1]
    
    path = os.path.join(os.getcwd(), "chromedriver")

    with open(str(site_id) + '.json', 'r') as file:
        scrapper_commands = json.load(file)
    
    instance = Scrapper(path=path, action=scrapper_commands)
    instance = instance.run()
    


if __name__ == "__main__":
    main()
