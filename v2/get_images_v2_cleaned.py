"""
Script for Homework.
Task requirements.
Write a program in Python, which:
   * Finds and fetches all images on a web page and stores the images on disk
   * Writes a file on disk, which lists the URL's of the images fetched
"""
import os
import logging
from helpers import get_filename, save_image_from_uri, _install_package
from config import image_extensions, protocols

# Uncomment following lines to enable logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

try:
    # Python 3
    from urllib.request import urlopen
    from urllib.parse import urljoin, urlparse, urlsplit
except ImportError:
    # Python 2
    from urlparse import urljoin, urlparse, urlsplit

try:
    import requests
except ImportError:
    _install_package('requests')
    import requests


try:
    from lxml import html
except ImportError:
    _install_package('lxml')
    from lxml import html


def process_links(hyperlinks):
    """
    This function processes a list of hyperlinks retrieved from the webpage
    and returns the list of links which refer to an image resource. The links
    are filtered by matching the file extensions of basename in that link.
    :param hyperlinks: List of hyperlinks (i.e. @href in <a>) retrieved from
    webpage
    :return: List of hyperlinks which refer to an image resource.
    """
    img_links = []
    for link in hyperlinks:
        # Look thorough all extensions if links satisfies any media resource.
        for ext in image_extensions:
            if link[-len(ext):] == ext:
                img_links.append(link)
    return img_links


def get_image_urls_from_webpage(input_url, inc_data_uri=True):
    """
    This function finds links to all images shown on given web page and
    returns a list of urls for those images.
    Note: The urls also include data-uri(s) given in <img> tag's src attribute.
    :param input_url: Url of web page from which images links needs to be
    scrapped.
    :param inc_data_uri: Include data-uris as image resources (default=True)
    :return: list of urls (included data-uri) to images displayed on webpage.
    """
    import os

    # Retrieve the page and page structure
    page_content = requests.get(input_url)
    html_tree = html.fromstring(page_content.text)
    image_urls = html_tree.xpath('//img/@src')  # Images loaded directly
    hyperlinks = html_tree.xpath('//a/@href')   # Images loaded in hyperlinks
    data_src_urls = html_tree.xpath('//img/@data-src')  # Images loaded by JS

    # Find Image links from hyperlinks
    hyperlinks_images = process_links(hyperlinks)
    # Combine all links
    image_urls.extend(data_src_urls)
    image_urls.extend(process_links(hyperlinks_images))

    if len(image_urls) == 0:
        logging.info('No urls for Images found in requested page.')
        return -1

    parsed_url = urlparse(input_url)
    processed_urls = []
    for img_url in image_urls:
        img_url = img_url.strip()   # Remove white spaces around link
        if img_url.startswith('/'):
            processed_urls.append(parsed_url.scheme
                                  + '://'
                                  + parsed_url.netloc
                                  + '/'
                                  + img_url)
        elif img_url.startswith(protocols.get('data-uri')):
            if inc_data_uri:
                processed_urls.append(img_url)
        elif img_url.startswith(protocols.get('http')) or \
                img_url.startswith(protocols.get('https')):
            '''
            We remove query parameters (may be used for resizing etc.) from
            querying image. Uncomment following line if you need image as
            downloaded to display on page.
            '''
            # url.append(img_url)
            processed_urls.append(img_url.split('?')[0])
        else:
            processed_urls.append(os.path.join(os.path.dirname(input_url),
                                               img_url))
    # Only return unique links to avoid repetition.
    return set(processed_urls)


def download_images(image_urls, inc_data_uri=True):
    """
    This function downloads the images using urls given as input and stores
    them in current working directory.
    :param image_urls: List of urls for the images.
    :param inc_data_uri: decode images from data-uris as well (default=True).
    :return: dictionary object containing number of images downloaded
    successfully and number of images failed to download
    """
    from posixpath import basename
    failed = 0
    for img_url in image_urls:
        try:
            if img_url.startswith(protocols.get('data-uri')):
                if inc_data_uri:
                    save_image_from_uri(img_url)
            else:
                filename = get_filename(basename(img_url))
                f = open(filename, 'wb+')
                f.write(requests.request('get', img_url).content)
                f.close()
        except Exception as ex:
            logging.error('Unable to download and store image from '
                          'url={url}. Error={err}'.format(url=img_url, err=ex))
            failed += 1
            pass
    logging.info('Failed to download {count} images.'.format(count=failed))
    return {
        "success": len(image_urls) - failed,
        "fail": failed
    }


def main(argv):
    """
    Main function for handling user provided (options) parameters and
    running the function.
    :param argv: commandline arguments provided by user.
    :return:
    """
    import errno
    import getopt
    try:
        opts, args = getopt.getopt(argv, "hud: v", ["help", "url=", 'dir='])
    except getopt.GetoptError:
        print("Use -h for usage information.")
        sys.exit(errno.EINVAL)
    url = None
    dir = '/images'
    try:
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                print("Usage:\n"
                      "fsec_hw.py -h --> shows help\n"
                      "fsec_hw.py --help --> shows help\n"
                      "fsec_hw.py -u <url> -d "
                      "<directory_path_for_storing_files>\n"
                      "fsec_hw.py --url=<url> -dir="
                      "<directory_path_for_storing_files>")
                sys.exit()
            elif opt in ('-u', '--url'):
                logging.info('User input for url = {url}'.format(url=arg))
                url = arg
            elif opt in ('-d', '--dir'):
                logging.info('User input for dir = {dir}'.format(dir=arg))
                dir = arg
            else:
                print("Use -h for usage information.")
                sys.exit(errno.EINVAL)
        if url is None:
            print('Use fsec_hw.py for usage information.')
            sys.exit(errno.EINVAL)

        # Find URLs from webpage
        urls = get_image_urls_from_webpage(url)

        # Establish directory to store the downloaded images.
        parsed_url = urlparse(url)
        if not os.path.exists(dir):
            os.mkdir(dir)
        if not os.path.exists(dir+ parsed_url.netloc):
            os.mkdir(dir + parsed_url.netloc)
            logging.info('{dir} created for storing images'.format(
                dir=dir + parsed_url.netloc))
        os.chdir('images/' + parsed_url.netloc)

        # Write URLs to file
        f = open('{fn}.txt'.format(fn=parsed_url.netloc), 'w+')
        for url in urls:
            f.write(url+'\n')
        f.close()

        # Download Images
        stats = download_images(urls)
        logging.info('Successfully downloaded {succ} images and failed to '
                     'download {f} images from given website='
                     '{url}'.format(succ=stats['success'], f=stats['fail'],
                                    url=url))
        print('Successfully downloaded {succ} images and failed to '
              'download {f} images from given website={url}. \nExiting...'
              ''.format(succ=stats['success'], f=stats['fail'], url=url))
        return
    except Exception as ex:
        print("Error:{err}".format(err=ex))
        logging.error('Error:{err} while downloading images from {url}'
                      ''.format(err=ex, url=url or arg))
        return errno.EAGAIN


if __name__ == '__main__':
    import sys
    if len(sys.argv) == 1:
        print("Use -h for usage information.")
        sys.exit(0)
    main(sys.argv[1:])
