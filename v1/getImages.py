"""
Script for Homework.
Task requirements.
Write a program in Python, which:
   * Finds and fetches all images on a web page and stores the images on disk
   * Writes a file on disk, which lists the URL's of the images fetched
"""
import errno
import sys
import os
import getopt
from posixpath import basename
import logging

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')

# Manually defined error number for Import Error
ERRNO_IMPORT_ERROR = 254

try:
    # Python 3
    from urllib.request import urlopen
except ImportError:
    # Python 2
    from urllib2 import urlopen

try:
    # Python 3
    from urllib.parse import urlparse, urlsplit
except ImportError:
    # Python 2
    from urllib2 import urlparse
    from urlparse import urlparse, urlsplit

try:
    from bs4 import BeautifulSoup
except ImportError:
    print('BeautifulSoup not found. Installing BeautifulSoup4...')
    try:
        from helpers import _install_package
        if not _install_package('bs4'):
            logging.debug("Unable to install bs4 using "
                          "helpers._install_package")
            sys.exit(errno.EPERM)
        from bs4 import BeautifulSoup
    except ImportError:
        print('Error: helper modules not found. ')
        sys.exit(ERRNO_IMPORT_ERROR)


def get_images(input_url):
    # Establish directory to store the downloaded images.
    parsed_url = urlparse(input_url)
    dirname = basename(parsed_url.path)
    if not os.path.exists('images'):
        os.mkdir('images')
    if not os.path.exists('images/'+dirname):
        os.mkdir('images/'+dirname)
        logging.info('{dir} created for storing images'.format(
            dir='images/' + dirname))
    os.chdir('images/'+dirname)
    logging.debug('{dir} chosen as current working directory for storing '
                  'images'.format(dir='images/' + dirname))
    b_soup = BeautifulSoup(urlopen(input_url).read().decode('utf-8'),
                           "html.parser")
    with open('content.txt', 'w+') as f:
        f.write(urlopen(input_url).read())
        f.close()
    img_tags = b_soup.find_all('img', {'alt': True, 'src': True})

    url_file = open(input_url.split('/')[-1] + '.txt', 'w+')
    success = 0
    for img_tag in img_tags:
        try:
            img_src = img_tag["src"]
            # Resolve images sources from relative paths.
            if img_src[:2] == '..':
                logging.info('converting relative path={rpath} to absolute '
                             'path'.format(rpath=img_src))
                img_src = os.path.join(os.path.dirname(input_url), img_src)
            logging.info("Downloading image from {img_path}.".format(
                img_path=img_src))
            img_data = urlopen(img_src).read()

            try:
                cwd = os.path.dirname(os.path.abspath(__file__))
            except NameError:
                cwd = os.getcwd()
            img_name = basename(urlsplit(img_src)[2])
            filename = cwd + '/' + img_name
            if os.path.exists(filename):
                file_counter = 1
                while os.path.exists(filename):
                    filename = img_name.split('.')[0] \
                               + '(%s).' % file_counter \
                               + '.'.join(img_name.split('.')[1:])
                    file_counter += 1
            logging.info('Storing image {fname}'.format(fname=filename))
            f = open(filename, "wb+")
            f.write(img_data)
            f.close()
            # Write image source url in the file.
            url_file.write(img_src+'\n')
            success += 1
            logging.info('Successfully downloaded and stored {img_name}'.
                         format(img_name=filename.split('/')[-1]))
        except Exception as ex:
            logging.error('Error in downloading and storing {img_src}. '
                          'Error={err}'.format(img_src=img_src,
                                               err=ex))
            pass
    logging.info('{succ} images downloaded successfully out of total {total} '
                 'images in webpage={url}'.format(succ=success,
                                                  total=len(img_tags),
                                                  url=input_url))
    url_file.close()


def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu: v", ["help", "url="])
    except getopt.GetoptError:
        print("Use -h for usage information.")
        sys.exit(errno.EINVAL)
    try:
        url = None
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print("Usage:\n"
                      "fsec_hw.py -h --> shows help\n"
                      "fsec_hw.py --help --> shows help\n"
                      "fsec_hw.py -u <url>\n"
                      "fsec_hw.py --url=<url>")
                sys.exit()
            elif opt in ('-u', '--url'):
                logging.info('User input for url = {url}'.format(url=arg))
                url = arg
            else:
                print("Use -h for usage information.")
                sys.exit(errno.EINVAL)
        if url is None:
            print('Use fsec_hw.py for usage information.')
            sys.exit(errno.EINVAL)
        get_images(url)
        print("Exiting...")
        sys.exit(0)
    except Exception as ex:
        print("Error:{err}".format(err=ex))
        sys.exit(errno.EAGAIN)

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("Use -h for usage information.")
    main(sys.argv[1:])
