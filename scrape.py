import requests
import ssl, smtplib, pickle, sys, os
from bs4 import BeautifulSoup
from time import sleep

sys.setrecursionlimit(100000)
URL = 'https://www.mountainproject.com/forum/103989416/for-sale-for-free-want-to-buy'


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
    
    details = ''
    for a in results.find_all('a', href=True):
        title = a.find('strong')
        if title:
            title_and_url.add((title.contents[0]))
            if len(title_and_url) > 1:
                details = 'Posted ' + title.contents[0]
                break
    return details


def send_email(receiver_email: str, msg: str):
    context = ssl.create_default_context()
    port = 465  # For SSL
    smtp_server = "smtp.gmail.com"
    sender_email = "mountain.project.python@gmail.com"  # Enter your address
    with smtplib.SMTP_SSL(smtp_server, port, context=context) as server:
        server.login(sender_email, os.environ['MY_SMTP_P'])
        server.sendmail(sender_email, receiver_email, msg.encode('utf-8'))


def get_new_matching_posts(posts: set, keywords: list, prev_posts: set) -> set:
    matching_posts = {post for post in posts if [x for x in keywords if x in post[0].lower()]}
    return matching_posts - prev_posts


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

    search_items = ['camalot', 'cams', 'c4', 'rack']
    new_matching_posts = get_new_matching_posts(
        posts=title_and_url,
        keywords=search_items,
        prev_posts=previous_posts
    )

    if len(new_matching_posts) > 0:
        message = """
        Subject: Current for sale posts that might be selling cams: \n\n"""
        for x in new_matching_posts:
            message += x[0] + '\n' + x[1] + '\n' + get_details(x[1]) + '\n'*2

        pickle_dump(previous_posts | new_matching_posts)

        send_email(receiver_email="matteobjornsson@gmail.com", msg=message)
    else:
        print('no new posts')
    sleep(300)

