from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
import time
import pandas as pd

service = Service(executable_path="C:\Program Files\chromedriver.exe")
options = Options()
options.add_argument("--zoom-level=0.25")

driver = webdriver.Chrome(service=service, options=options)

url = "https://www.anwb.nl/auto/private-lease/anwb-private-lease/aanbod"

driver.get(url)
print(f"Accessing '{url}'")


#Accept Cookies
buttonCookies = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-27797e7b-0') and contains(@class, 'coKYvH') and contains(@class, 'sc-jdkBTo') and contains(@class, 'kdJrhK')]"))
).click()


#Delete


#Collecting list of brands
#.click see more
moreBrand = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable((By.CSS_SELECTOR, "[data-testid='filter-limitation']"))
)
driver.execute_script("arguments[0].scrollIntoView(true);", moreBrand) #scroll so the button is visible
time.sleep(1) #let the scrolling done
moreBrand.click()
#.start collecting
brands = driver.find_elements(By.XPATH, "//*[contains(@name, 'manufacturer[]')]")
brands = [brand.get_attribute("value") for brand in brands]
moreBrand.click()


#Collecting list of fueltypes
fueltypes = driver.find_elements(By.XPATH, "//*[contains(@name, 'fuelType[]')]")
fueltypes = [fueltype.get_attribute("value") for fueltype in fueltypes]


#Collecting list of bodytypes
vehicleChassis = driver.find_elements(By.XPATH, "//*[contains(@name, 'vehicleChassis[]')]")
vehicleChassis = [chassis.get_attribute("value").split()[0] for chassis in vehicleChassis]


allCars = []
carPrices = []
allVehicleChassis = []
for i, chasName in enumerate(vehicleChassis):
    #Select each vehicleChassis
    checkbox = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.ID, f"vehicleChassis-{i}-label"))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox) #scroll so the button is visible
    time.sleep(1) #let the scrolling done
    checkbox.click()
    print(f"collecting number {i+1}: {chasName}")


    #Click "see more" (load all cars)
    while True:
        try:
            buttonMore = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(@class, 'sc-ibQAlb') and contains(@class, 'cenIer') and contains(@class, 'sc-fThUAz') and contains(@class, 'fyGVSO')]"))
            )
            
            driver.execute_script("arguments[0].scrollIntoView(true);", buttonMore) #scroll so the button is visible
            time.sleep(1)
            buttonMore.click()
        except TimeoutException:
            print('done')
            break

    #Collecting cars
    carsTemp = driver.find_elements(By.CLASS_NAME, "sc-fQgSAe")
    carsTemp = [car.text for car in carsTemp]
    allCars += carsTemp

    allVehicleChassis += [f'{chasName.split()[0]}']*len(carsTemp)

    #Collecting prices
    pricesTemp = driver.find_elements(By.CLASS_NAME, "sc-Gppvi")
    pricesTemp = [price.text for price in pricesTemp]
    carPrices += pricesTemp

    #uncheck the checkbox
    driver.execute_script("arguments[0].scrollIntoView(true);", checkbox)
    time.sleep(1)
    checkbox.click()


driver.quit()


print(f'collected {len(allCars)} cars')

splitAllCars = [name.split() for name in allCars]
carManufacturer = [name[0] for name in splitAllCars]
carFuel = [fueltypes[1] if name[-1] == "Elektrisch"
                else fueltypes[2] if name[-1] == "Hybrid"
                else fueltypes[3] if name[-1] == "PHEV"
                else fueltypes[0]
                for name in splitAllCars]
carModel = [' '.join(name[1:-1]) if name[-1] in ["Elektrisch", "Hybrid", "PHEV"]
            else ' '.join(name[1:])
            for name in splitAllCars]
carPrices = [int(s.replace("€ ", "").replace(",-", "").replace(".","")) for s in carPrices]

print("Creating .csv file...")
df = pd.DataFrame({'manufacturer': carManufacturer, 'model':carModel, 'price':carPrices, 'fuel_type':carFuel, 'vehicle_chassis':allVehicleChassis})
df.to_csv('cars.csv', index=False)