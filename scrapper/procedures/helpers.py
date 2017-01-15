"""
This package contains helper functions to be used in the project.
"""

import re
import os
import sys
import logging


def install_package(package_name):
    """
    This function install the required package using pip.
    :param package_name: python package name.
    :return: True if successfully installed, False otherwise
    """
    try:
        import pip
        '''
        Check if script is not running in virtual environment, the it should
        have root privileges to install the package.
        '''
        if not hasattr(sys, 'real_prefix') and os.getuid() != 0:
            logging.warning("Unable to install {pkg} because user is not "
                            "running python in virtual environment, neither "
                            "it has root privileges".format(pkg=package_name))
            return False
        logging.info('Installing {pkg} using pip.'.format(pkg=package_name))
        pip.main(['install', package_name])
        return True
    except ImportError:
        logging.error('Unable to import PIP for installing package={'
                      'pkg}'.format(pkg=package_name))
        return False
    except Exception as ex:
        logging.error("Error {err} during installing {pkg} using "
                      "pip.".format(err=str(ex), pkg=package_name))
        return False


def process_links(hyperlinks, file_extensions=None):
    """
    This function processes a list of hyperlinks retrieved from the webpage
    and returns the list of links which refer to an image resource. The links
    are filtered by matching the file extensions of basename in that link.
    :param hyperlinks: List of hyperlinks (i.e. @href in <a>) retrieved from
    webpage
    :param file_extensions: Extensions of files we are searching for in links.
    :return: List of hyperlinks which refer to an image resource.
    """
    img_links = []
    for link in hyperlinks:
        # Look thorough all extensions if links satisfies any media resource.
        for ext in file_extensions:
            if link[-len(ext):] == ext:
                img_links.append(link)
    return img_links


def save_from_relative_to_root(base_url, img_url):
    """
    This function downloads the image from path relative current page and
    saves it to current working directory
    :param base_url: url to parent folder of current web page.
    :param img_url: name of image file.
    :return:
    """
    import requests
    from posixpath import dirname
    filename = get_filename(dirname(img_url) or 'unknown.jpg')
    try:
        f = open(filename, "wb+")
        logging.debug('Downloaded img={img_name} from url={path}'
                      ''.format(img_name=img_url, path=base_url+'/'+img_url))
        f.write(requests.request('get', base_url+'/'+img_url).content)
        logging.info('Image={img_name} downloaded from url={path} and stored '
                     'to disk'.format(img_name=img_url,
                                      path=base_url+'/'+img_url))
        f.close()
    except Exception as ex:
        logging.error("Unable to download and store images from url={url}. "
                      "Error={err}".format(url=base_url+'/'+img_url, err=ex))


def save_image_from_link(img_url):
    """
    This functions downloads and save image stored at given url in a file
    and saves it in current working directory.
    :param img_url: url for image to be extracted.
    :return:
    """
    import requests
    from posixpath import dirname
    if not img_url.startswith('http'):
        img_url = 'https:' + img_url
    logging.debug('Downloading image from url={url}}'.format(url=img_url))
    filename = get_filename(dirname(img_url.split('?')[0]) or 'unknown.jpg')
    try:
        f = open(filename, "wb+")
        f.write(requests.request('get', img_url).content)
        logging.info('Image={img} downloaded from url={url} and saved to '
                     'disk'.format(img=filename, url=img_url))
        f.close()
    except Exception as ex:
        logging.error("Unable to download and store images from url={url}. "
                      "Error={err}".format(url=img_url, err=ex))


def save_image_from_uri(uri):
    """
    This functions convert base64 encoded uri to an <img> tag in HTML page
    and saves it in current working directory.
    :param uri: url for image to be extracted.
    :return:
    """
    import base64
    if not uri.startswith('data:image'):
        logging.info('Invalid uri for extracting image uri={in_uri}'.format(
            in_uri=uri))
        return
    # Get file extension and encoding scheme from URI.
    extension = uri.split(';')[0].split('/')[1]
    filename = get_filename('uri-image.' + extension)
    # Get file to the disk.
    try:
        f = open(filename, 'wb+')
        f.write(base64.b64decode(str(uri.split(",")[1])))
        logging.info('Image={img} extracted using data-uri'
                     ''.format(img=filename))
        f.close()
    except Exception as ex:
        logging.error("Unable to download and store images from data-uri."
                      "Error={err}".format(err=ex))


def save_image_from_relative_path(base_url, image_url):
    """
    This function downloads an image from the path relative to root path of
    the webpage and saves it to current working directory.
    :param base_url: Root path for webpage.
    :param image_url: path for image relative to root path
    :return:
    """
    import requests
    from posixpath import dirname
    # Extract filename i.e image name.
    img_src = os.path.join(os.path.dirname(base_url), image_url)
    filename = get_filename(dirname(image_url))
    # Save file to disk.
    try:
        f = open(filename, "wb+")
        f.write(requests.request('get', img_src).content)
        logging.info('Image={img} downloaded from url={img_url} and saved to '
                     'disk'.format(img=filename, img_url=img_src))
        f.close()
    except Exception as ex:
        logging.error("Unable to download and store images from url={url}."
                      "Error={err}".format(url=img_src, err=ex))


def get_filename(fq_filepath):
    """
    This function adds a numerical increment to the filename in case the file
    exists already in the disk.
    :param fq_filepath: fully qualified filepath i.e.
    folder/sub_folder/filename.extension
    :return: fq_filepath (with incremented path if similar filepath already
    exists) e.g. folder/sub_folder/filename(1).extension
    """
    import os
    filename = fq_filepath.split('/')[-1]
    if os.path.exists(fq_filepath):
        counter = 1
        logging.info('Finding incremented filepath for '
                     '{fp}'.format(fp=fq_filepath))
        while os.path.exists(fq_filepath):
            # Get incremented file number
            i_fn = '.'.join(filename.split('.')[:-1])\
                   + ' (%s).' % counter\
                   + filename.split('.')[-1]
            fq_filepath = os.path.join('/'.join(fq_filepath.split('/')[:-1]),
                                       i_fn)
            counter += 1
        logging.info('Incremented filepath={ifp} for given existing '
                     'filepath'.format(ifp=fq_filepath))
    return fq_filepath
