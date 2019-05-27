import selenium
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.ui as ui
import selenium.webdriver.support.expected_conditions as EC
import os
import time
import csv
import subprocess
from sqlalchemy import create_engine,Table,Column,Integer,String,MetaData,ForeignKey
import json
import base64
import datetime
import pandas as pd 
from pandas.io import sql
from sqlalchemy import create_engine
#need to install selenium, sqlalchemy, pandas, all those can be installed by using pip



class crawler():

        #Open the start page/ Maximize windows in order to load # of sales/ Wait
        driver = webdriver.Chrome() 
        driver.get("https://stockx.com/retro-jordans/top-selling")
        driver.maximize_window()
        driver.implicitly_wait(10)
        
        #Connect to mysql database
        engine=create_engine("mysql+pymysql://root:711026@localhost:3306/test",echo=True)

        #Creater csv writer/ Lineterminator=No blink line/ Writerow as header
        now = datetime.datetime.now()
        file_name = 'StockX_' + str(now.year) + str(now.month) + str(now.day)
        sale_writer = csv.writer(open('%s.csv' %file_name, 'w+'),lineterminator='\n')
        sale_writer.writerow(['name','date','time','size','sale_price', 'color', 'style_num','series','retail_price','release_date','total_sales','highest_bid','lowest_ask','image_url'])

        #Get 120 shoes/ Click load_more
        for i in range(0,2):
                if(i>39):
                        for k in range(0,int((i+1)/40)):
                                xpath ='//*[@id="browse-wrapper"]/div[2]/div/div/div[2]/div[3]'
                                btn = driver.find_element_by_xpath(xpath)
                                btn.click()
                                time.sleep(5)
        
                #Get links/ Open the page of No.i shoes
                links=driver.find_elements_by_class_name("clickZone")
                link=links[i]
                link.click()
                time.sleep(2)

                #Get different elements
                name = driver.find_element_by_xpath('//*[@id="product-header"]/div[1]/div/h1').text
                retail_price=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[2]/div[3]/div[1]/div[3]/span').text
                retail_price=retail_price[1:]
                release_date=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[2]/div[3]/div[1]/div[4]/span').text

                #Cant get image on some page
                try:
                        image_url=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[2]/div[1]/div[1]/div[2]/div[1]/div/div[1]/img').get_attribute('src')
                except:
                        image_url=''
                num_sales=driver.find_element_by_xpath('//*[@class="gauges"]/div[1]/div[3]').text
                highest_bid=driver.find_element_by_xpath('//*[@id="ask-sell-button"]/div[1]/div').text
                highest_bid=highest_bid[1:]
                lowest_ask=driver.find_element_by_xpath('//*[@id="bid-buy-button"]/div[1]/div').text
                lowest_ask=lowest_ask[1:]
                colorway=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[2]/div[3]/div[1]/div[2]/span').text
                series=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[1]/div/div/ul/li[4]/a').text
                style_num=driver.find_element_by_xpath('//*[@id="root"]/div[1]/div[2]/div[2]/span/div[2]/div[3]/div[1]/div[1]/span').text
                print(name)
                
                #Open sales history/ Store into file_data(list)
                sale_open = driver.find_element_by_xpath('//*[@id="market-summary"]/div[2]/div/div[2]/div[3]')
                sale_open.click()
                time.sleep(3)
                file_data=[]
                for item in driver.find_elements_by_xpath('//*[@id="480"]/tbody//tr'):
                        data = item.find_elements_by_tag_name('td')
                        file_row = []
                        for ele in data: 
                                file_row.append(ele.text)
                        file_row = [name]+file_row+[colorway,style_num,series,retail_price,release_date,num_sales,highest_bid,lowest_ask,image_url] 
                        file_data.append(file_row)
                
                #Close sales history/ Back to start page
                sale_close = driver.find_element_by_xpath('//div[@class="allSales modal-lg modal-primary modal-dialog"]/div/div[1]/button')
                sale_close.click()
                sale_writer.writerows(file_data)
                driver.back()
                driver.implicitly_wait(10)
                time.sleep(2)

                #Close chrome and open again every 5 shoes = avoid login
                if(i%5==4):
                        driver.close()
                        driver = webdriver.Chrome() 
                        driver.get("https://stockx.com/retro-jordans/top-selling")
                        driver.maximize_window()#maximize in order to get # of sales
                        driver.implicitly_wait(10)
        
        #store the csv into mysql
        chunks = pd.read_csv('%s.csv'%file_name)
        chunks.to_sql('%s'%file_name,con=engine, if_exists='append')

#run
crawler_run = crawler()
