import requests
import ssl, pickle, sys
from bs4 import BeautifulSoup
from time import sleep

sys.setrecursionlimit(100000)


def pickle_dump(to_write) -> None:
    """
    Write posts to file
    """
    pickle_file = open('posts.p', 'wb')
    pickle.dump(to_write, pickle_file)
    pickle_file.close()


def get_details(url: str) -> str:
    page = requests.get(url)
    soup = BeautifulSoup(page.content, 'html.parser')
    results = soup.find(id='forum-table')
    title_and_url = set()
    #
    for a in results.find_all('a', href=True):
        title = a.find('strong')
        if title:
            title_and_url.add((title.contents[0]))
            if len(title_and_url) > 1:
                details ='Posted ' + title.contents[0]
                break

    return details

port = 465  # For SSL
smtp_server = "smtp.gmail.com"
sender_email = "mountain.project.python@gmail.com"  # Enter your address
receiver_email = "matteobjornsson@gmail.com"  # Enter receiver address
p = input("Type your password and press enter: ")
URL = 'https://www.mountainproject.com/forum/103989416/for-sale-for-free-want-to-buy'

while True:
    try:
        read_file = open('posts.p', 'rb')
        previous_posts = pickle.load(read_file)
        read_file.close()
    except FileNotFoundError:
        previous_posts = set()
        print("No post object available to read in")

    page = requests.get(URL)
    soup = BeautifulSoup(page.content, 'html.parser')

    results = soup.find(id='forum-table')
    title_and_url = set()

    for a in results.find_all('a', href=True):
        title = a.find('strong')
        if title:
            title_and_url.add((title.contents[0], a['href']))

    search_items = ['cam', 'cams', 'camalot', 'x4', 'c3', 'c4']

    posts_with_cams = {post for post in title_and_url if [x for x in search_items if x in post[0].lower()]}
    new_posts_with_cams = posts_with_cams - previous_posts
    if len(new_posts_with_cams) > 0:

        message = """\
        Subject: Current for sale posts that might be selling cams: \n\n"""
        for x in new_posts_with_cams:
            message += x[0] + '\n' + x[1] + '\n' + get_details(x[1]) + '\n'*2

        print(message)
        print(new_posts_with_cams)
        pickle_dump(previous_posts|new_posts_with_cams)
        context = ssl.create_default_context()
        # with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        #     server.login(sender_email, p)
        #     server.sendmail(sender_email, receiver_email, message)
    else:
        print('no new posts')
    sleep(60)
