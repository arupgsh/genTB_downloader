import bs4 as bs
from urllib.request import Request, urlopen, urlretrieve
from fake_useragent import UserAgent
from os import makedirs, path, system
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities

#user datails config file get the token from browser
proj_id = '<project id from url>'

uconf= {
    'csrf_token': '<your token>',
    'session_id': '<session id>'
}

#base path configs
dwl_base = "https://gentb.hms.harvard.edu"

#Get a random user agent for the request
useragent = UserAgent()

# preparare the selenium chrome driver options
options = webdriver.ChromeOptions()
options.add_argument('--headless')
options.add_argument('--no-sandbox')
options.add_argument('--disable-gpu')
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
options.add_argument('--single-process')
options.add_argument('--ignore-certificate-errors')
options.add_argument("--disable-session-crashed-bubble")
options.add_argument("--disable-ipv6")
options.add_argument(f'user-agent={useragent.random}')
caps = DesiredCapabilities().CHROME
caps["pageLoadStrategy"] = "eager"
driver = webdriver.Chrome(options=options, executable_path='./chromedriver')
driver.implicitly_wait(10)

#create the full url path for the file
url = 'https://gentb.hms.harvard.edu/predict/'+proj_id+'/page/output/'

#set user cookie for access to the authenticated page
# Now set the cookie. This one's valid for the entire domain
driver.get(url)

driver.add_cookie({'name' : 'csrftoken', 'value': uconf['csrf_token'],'domain' : 'gentb.hms.harvard.edu'})
driver.add_cookie({'name' : 'sessionid', 'value': uconf['session_id'], 'domain' : 'gentb.hms.harvard.edu'})

#this time selenium will get the authenticated page
driver.get(url)
soup = bs.BeautifulSoup(driver.page_source,'html.parser')

#get all sample names and files in pair
samples = zip(soup.findAll('h3', {'class':'well-label'}), soup.findAll('div',{'class': 'row'}))

#process downloading of files
for sample in samples:
    sample_name = sample[0].text
    makedirs(sample_name, exist_ok=True)
    print(f'Processing: {sample_name}')
    links = sample[1].findAll('a')
    dwl_paths = [dwl_base+l.get('href') for l in links]
    for p in dwl_paths:
        fname = path.basename(p)
        oname = sample_name+'/'+fname
        print(f"Downloading: {fname}")
        system(f'curl -o {oname} {p}') #shows progress bar while downloading
        #urlretrieve(p, sample_name+'/'+fname) #alternate download method
