import bs4 as bs
from urllib.request import Request, urlopen
import pandas as pd
import os
import re
import sys
import time
website = 'https://www.thecarconnection.com'
template = 'https://images.hgmsites.net/'
custom_header = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                  'AppleWebKit/537.36 (KHTML, like Gecko) '
                  'Chrome/126.0.6478.61 Safari/537.36'
}


def fetch(page, addition=''):
    return bs.BeautifulSoup(urlopen(Request(page + addition,
                            headers=custom_header)).read(), 'lxml')


def all_makes():
    all_makes_list = []
    make_selections = fetch(website, "/new-cars").find("div", {"class": "rowContent"})
    for option in make_selections.find_all("a"):
        all_makes_list.append(option['href'])
    return all_makes_list


def make_menu(listed):
    make_menu_list = []
    for make in listed:
        time.sleep(1)
        for div in fetch(website, make).find_all("div", {"class": "makeModelListContainer"}):
            make_menu_list.append(div.find_all("a")[0]['href'])
    return make_menu_list


def model_menu(listed):
    model_menu_list = []
    # example_make = "/cars/acura_rdx"
    for make in listed:
        soup = fetch(website, make)
        for div in soup.find_all("a", {"class": "btn avail-now first-item"}):
            model_menu_list.append(div['href'])
        for div in soup.find_all("a", {"class": "btn 1"})[:8]:
            model_menu_list.append(div['href'])
    model_menu_list = [i.replace('overview', 'specifications') for i in model_menu_list]
    return model_menu_list


def specs_and_pics(listed):
    picture_tab = [i.replace('specifications', 'photos') for i in listed]
    specifications_table = pd.DataFrame()
    for row, pic in zip(listed, picture_tab):
        soup = fetch(website, row)
        specifications_df = pd.DataFrame(columns=[soup.find_all("title")[0].text[:-15]])

        try:
            specifications_df.loc['Make', :] = soup.find_all('a', {'id': 'a_bc_1'})[0].text.strip()
            specifications_df.loc['Model', :] = soup.find_all('a', {'id': 'a_bc_2'})[0].text.strip()
            specifications_df.loc['Year', :] = soup.find_all('a', {'id': 'a_bc_3'})[0].text.strip()
            specifications_df.loc['MSRP', :] = soup.find_all('span', {'class': 'msrp'})[0].text
        except:
            print('Problem with {}.'.format(website + row))

        for div in soup.find_all("div", {"class": "specs-set-item"}):
            row_name = div.find_all("span")[0].text
            row_value = div.find_all("span")[1].text
            specifications_df.loc[row_name] = row_value

        fetch_pics_url = str(fetch(website, pic))

        try:
            for ix, photo in enumerate(re.findall('sml.+?_s.jpg', fetch_pics_url)[:150], 1):
                specifications_df.loc[f'Picture {ix}', :] = photo.replace('\\', '')
            specifications_table = pd.concat([specifications_table, specifications_df], axis=1, sort=False)
        except:
            print('Error with {}.'.format(template + photo))
    return specifications_table


def run(directory):
    os.chdir(directory)
    a = all_makes()
    b = make_menu(a)
    c = model_menu(b)
    pd.DataFrame(c).to_csv('c.csv', header=None)
    d = pd.read_csv('c.csv', index_col=0, header=None).values.ravel()
    e = specs_and_pics(d)
    e.to_csv('specs-and-pics.csv')


if __name__ == '__main__':
    car_makes = all_makes()
    for make in car_makes:
        print(make)
    print("Debugging code")
    makes_menu = make_menu(car_makes)
    for make in makes_menu:
        print(make, flush=True)


    print("Finished making requests")



    # if not os.path.isdir(sys.argv[1]):
    #     os.mkdir(sys.argv[1])

    # print('%s started running.' % os.path.basename(__file__))
    # run(sys.argv[1])
    # print('%s finished running.' % os.path.basename(__file__))
