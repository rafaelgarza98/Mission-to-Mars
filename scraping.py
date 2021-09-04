#Import Splinter, Beautiful Soup and pandas
from splinter import Browser
from bs4 import BeautifulSoup as soup
from webdriver_manager.chrome import ChromeDriverManager
import pandas as pd
import datetime as dt

def scrape_all():
    #Set up splinter
    executable_path = {'executable_path': ChromeDriverManager().install()}
    browser = Browser('chrome', **executable_path, headless=True)
    news_title, news_paragraph = mars_news(browser)
    #Run all scraping funncs and store results in dict
    data = {
            'news_title': news_title,
            'news_paragraph': news_paragraph,
            'featured_image': featured_image(browser),
            'facts': mars_facts(),
            'last_modified': dt.datetime.now(),
            'hemispheres': mars_hemispheres(browser)
    }
    #end webdriver_manager and return data
    browser.quit()
    return data

def mars_news(browser):

    #Visit mars nasa news site
    url = 'https://redplanetscience.com'
    browser.visit(url)
    #'Optional' delay for loading page
    browser.is_element_present_by_css('div.list_text', wait_time =1)

    #conver browser html to soup obj and quit browser
    html = browser.html
    news_soup = soup(html, 'html.parser')

    #add try/except for error handling
    try:
        slide_elem = news_soup.select_one('div.list_text')

        slide_elem.find('div', class_='content_title')

        #use parent element to find first 'a' tag and save as 'news_title'
        news_title = slide_elem.find('div', class_='content_title').get_text()
    #    news_title

        #use parent elem to find paragraph txt
        news_p = slide_elem.find('div', class_='article_teaser_body').get_text()
    #    news_p
    except AttributeError:
        return None, None

    return news_title, news_p

# ### Featured Images

def featured_image(browser):

    #Visit url
    url = 'https://spaceimages-mars.com'
    browser.visit(url)

    #find and click full img button
    full_img_elem = browser.find_by_tag('button')[1]
    full_img_elem.click()

    #parse resultinig html w/ soup
    html = browser.html
    img_soup = soup(html, 'html.parser')

    #add try/except
    #find the relative img url
    try:
        img_url_rel = img_soup.find('img', class_='fancybox-image').get('src')
#    img_url_rel
    except AttributeError:
        return None

    #use base url to create absolute URL
    img_url = f'https://spaceimages-mars.com/{img_url_rel}'
#    img_url

    return img_url

# ## Mars Facts

def mars_facts():
    try:
        df = pd.read_html('https://galaxyfacts-mars.com')[0]
    except BaseException:
        return None

    #assign cols and set index of df
    df.columns = ['description', 'Mars', 'Earth']
    df.set_index('description', inplace=True)

    #convert df to html add bootstrap
    return df.to_html(classes=['table-striped'])

def mars_hemispheres(browser):

    url = 'https://marshemispheres.com/'
    browser.visit(url)
    #Create a list to hold the images and titles.
    hemisphere_image_urls = []
    #for loop for 4 hemispheres
    for i in range (0, 4):
        #create empty dictionary to hold the url and title for each hemisphere
        img_link_and_title = {}
        #visit the home url
        browser.visit(url)

        #try/catch for error handling
        try:
            #fint the link for each individual hemisphere (all enclosed on h3 tag)
            img_info = browser.find_by_tag('h3')[i]
            #goes to the info on each hemisphere
            img_info.click()
            #create soup object
            html = browser.html
            img_soup = soup(html, 'html.parser')
            #extract the title of the hemisphere (enclosed in h2 tag)
            img_title = img_soup.find('h2').text
            #extract the url for the image from the 'sample' link
            img_link = img_soup.find('div', class_='downloads').a['href']
            #create the full url for the image
            img_link_full = f'{url}{img_link}'
            #add the link and title to the dict
            img_link_and_title['img_url'] = img_link_full
            img_link_and_title['title'] = img_title
        except BaseException:
            img_link_and_title['img_url'] = None
            img_link_and_title['title'] = None

        #add the dict to the list
        hemisphere_image_urls.append(img_link_and_title)

    return hemisphere_image_urls

if __name__ == '__main__':
    #if running as script, print scraped data
    print(scrape_all())