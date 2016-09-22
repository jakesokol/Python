# -*- coding: utf-8 -*-
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
import unittest, time, re

class Checkout(unittest.TestCase):
    def setUp(self):
        self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(30)
        self.base_url = "https://uat.nexternal.com/"
        self.verificationErrors = []
        self.accept_next_alert = True
    
    def test_checkout(self):
        driver = self.driver
        driver.get(self.base_url + "fairway/all-products-call.aspx")
        driver.find_element_by_id("cat3").click()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lvTileProducts_ctrl2_ctl02_tpTileProduct_imgThumbnail").click()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_pdtProduct_atcTabbed_btnAddToCart").click()
        driver.find_element_by_id("btnCheckOutBottom").click()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lfBtoC_emlLogin_txtEmail").clear()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lfBtoC_emlLogin_txtEmail").send_keys("test@test.qa")
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lfBtoC_pwdLogin_rtbPassword_txtRestricted").clear()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lfBtoC_pwdLogin_rtbPassword_txtRestricted").send_keys("test")
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_lfBtoC_btnCustomerLogin").click()
        driver.find_element_by_id("ctl00_ctl00_cphMain_cphMain_dbSubmit_btnSubmit").click()
        driver.find_element_by_id("ctl00_cphMain_dbOrderSubmit_btnSubmit").click()
        order = driver.find_element_by_css_selector("p.nextOrderConfirmationText > b").text
        myorder = str(order)
        print 'Order ' + str(order)
        for i in range(60):
            try:
                if "Your Demo Order has Been Placed" == driver.find_element_by_css_selector("h1").text: break
            except: pass
            time.sleep(1)
        else: self.fail("time out")
        driver.get(self.base_url + "fairway/ordermgmt/orders.aspx")
        driver.find_element_by_id("ctl00_cphMain_rtbUserName_txtRestricted").click()
        driver.find_element_by_id("ctl00_cphMain_rtbUserName_txtRestricted").clear()
        driver.find_element_by_id("ctl00_cphMain_rtbUserName_txtRestricted").send_keys("jsokol")
        driver.find_element_by_id("ctl00_cphMain_rtbPassword_txtRestricted").clear()
        driver.find_element_by_id("ctl00_cphMain_rtbPassword_txtRestricted").send_keys("notmyrealpassword")
        driver.find_element_by_id("ctl00_cphMain_lbLogin").click()
        try: self.assertEqual(str(order), driver.find_element_by_link_text(str(order)).text)
        except AssertionError as e: self.verificationErrors.append(str(e))
        print('Verified Order ' + str(order) + ' in OMS')
        time.sleep(1)
    
    def is_element_present(self, how, what):
        try: self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e: return False
        return True
    
    def is_alert_present(self):
        try: self.driver.switch_to_alert()
        except NoAlertPresentException as e: return False
        return True
    
    def close_alert_and_get_its_text(self):
        try:
            alert = self.driver.switch_to_alert()
            alert_text = alert.text
            if self.accept_next_alert:
                alert.accept()
            else:
                alert.dismiss()
            return alert_text
        finally: self.accept_next_alert = True
    
    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)

if __name__ == "__main__":
    print " "
    print "Test Started"
    unittest.main()
