"""
Write a program in Python, which:
   * Finds and fetches all images on a web page and stores the images on disk
   * Writes a file on disk, which lists the URL's of the images fetched
"""

import os
import logging
from flask import current_app
# Uncomment following lines to enable logging
# logging.basicConfig(level=logging.INFO,
#                     format='%(asctime)s - %(levelname)s - %(message)s')

from .helpers import get_filename, save_image_from_uri, install_package, \
    process_links

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse

try:
    import requests
    from requests.exceptions import InvalidSchema, InvalidURL
except ImportError:
    install_package('requests')
    import requests
    from requests.exceptions import InvalidSchema, InvalidURL

try:
    from lxml import html
except ImportError:
    install_package('lxml')
    from lxml import html


def get_image_urls_from_webpage(input_url, inc_data_uri=True):
    """
    This function finds links to all images shown on given web page and
    returns a list of urls for those images.
    Note: The urls also include data-uri(s) given in <img> tag's src attribute.
    :param input_url: Url of web page from which images links needs to be
    scrapped.
    :param inc_data_uri: Include data-uris as image resources (default=True)
    :return: list of urls (included data-uri) to images displayed on webpage.
    returns an empty list if there is an exception or no URLs are retrieved
    from webpage.
    """
    try:
        page_content = requests.get(input_url)
        html_tree = html.fromstring(page_content.text)
        # Images loaded directly
        image_urls = html_tree.xpath('//img/@src')
        logging.debug('{count} links retrieved from <img> @src'.format(
            count=len(image_urls)))
        # Images loaded in hyperlinks
        hyperlinks = html_tree.xpath('//a/@href')
        # Lazy loaded image sources.
        data_src_urls = html_tree.xpath('//img/@data-src')
        logging.debug('{count} links retrieved from <img> @data-src'.format(
            count=len(data_src_urls)))

        # Find Image links from hyperlinks
        hyperlinks_images = process_links(hyperlinks,
                                          file_extensions=current_app.config[
                                              'IMAGE_EXTENSIONS'])
        logging.debug('{count} links retrieved from images retrieved from '
                      'hyperlinks'.format(count=len(hyperlinks_images)))
        # Combine all links
        image_urls.extend(data_src_urls)
        image_urls.extend(hyperlinks_images)

        if len(image_urls) == 0:
            logging.info('No urls for Images found in requested page.')
            return []
        protocols = current_app.config['PROTOCOLS']
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
        logging.info('{count} unique links extracted for image sources from '
                     'given webpage={url}'.format(
                        count=len(set(processed_urls)), url=input_url))
        return set(processed_urls)
    except (InvalidSchema, InvalidURL) as ex:
        logging.error('Invalid URL={url} provided for scrapping images. '
                      'Error={err}'.format(url=input_url, err=ex))
        return []


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
    protocols = current_app.config['PROTOCOLS']
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
