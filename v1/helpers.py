"""
This package contains helper functions to be used in the project.
"""

import os
import sys
import errno
import logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s')


def _install_package(package_name):
    """
    This function install the required package using pip.
    :param package_name: python package name.
    :return: True if successfully installed, False otherwise
    """
    try:
        import pip
        """
        Check if script is not running in virtual environment, the it should
        have root privileges to install the package.
        """
        if not hasattr(sys, 'real_prefix') and os.getuid() != 0:
            print("Unable to install {pkg} because user does not have root "
                  "privileges. Permission denied.".format(pkg=package_name))
            sys.exit(errno.EPERM)
        logging.info('Installing {pkg} using pip.'.format(pkg=package_name))
        pip.main(['install', package_name])
        return True
    except ImportError:
        print('Unable to import PIP. Please install pip manually.\nExiting...')
        sys.exit(errno.ENOPKG)
    except Exception as ex:
        logging.error("Error {err} during installing {pkg} using "
                      "pip.".format(err=str(ex), pkg=package_name))
        return False


def save_from_relative_to_root(base_url, img_url):
    """
    This function downloads the image from path relative current page and
    saves it to current working directory
    :param base_url: url to parent folder of current web page.
    :param img_url: name of image file.
    :return:
    """
    from posixpath import dirname
    filename = get_filename(dirname(img_url) or 'unknown.jpg')
    f = open(filename, "wb+")
    logging.debug('Downloaded img={img_name} from url={path}'
                  ''.format(img_name=img_url, path=base_url+'/'+img_url))
    f.write(requests.request('get', base_url+'/'+img_url).content)
    logging.info('Image={img_name} downloaded from url={path} and stored '
                 'to disk'.format(img_name=img_url, path=base_url+'/'+img_url))
    f.close()


def save_image_from_link(img_url):
    """
    This functions downloads and save image stored at given url in a file
    and saves it in current working directory.
    :param img_url: url for image to be extracted.
    :return:
    """
    import logging
    import requests
    from posixpath import dirname
    if img_url[:4] != 'http':
        img_url = 'https:'+img_url
    logging.debug('Downloading image from url={url}}'.format(url=img_url))
    filename = get_filename(dirname(img_url.split('?')[0]) or 'unknown.jpg')
    f = open(filename, "wb+")
    f.write(requests.request('get', img_url).content)
    logging.info('Image={img} downloaded from url={url} and saved to '
                 'disk'.format(img=filename, url=img_url))
    f.close()


def save_image_from_uri(uri):
    """
    This functions convert base64 encoded uri to an <img> tag in HTML page
    and saves it in current working directory.
    :param uri: url for image to be extracted.
    :return:
    """
    import base64
    import logging
    import requests

    if uri[:10] != 'data:image':
        logging.uri('Invalid uri for extracting image. '
                    'uri={in_uri}'.format(in_uri=uri))
        return
    # Get file extension and encoding scheme from URI.
    extension = uri.split(';')[0].split('/')[1]
    filename = get_filename('uri-image.' + extension)
    # Get file to the disk.
    f = open(filename, 'wb+')
    f.write(base64.b64decode(str(uri.split(",")[1])))
    logging.info('Image={img} extracted using data-uri'.format(img=filename))
    f.close()


def save_image_from_relative_path(base_url, image_url):
    """
    This function downloads an image from the path relative to root path of
    the webpage and saves it to current working directory.
    :param base_url: Root path for webpage.
    :param image_url: path for image relative to root path
    :return:
    """
    import logging
    import requests
    from posixpath import dirname
    # Extract filename i.e image name.
    img_src = os.path.join(os.path.dirname(base_url), image_url)
    filename = get_filename(dirname(image_url))
    # Save file to disk.
    f = open(filename, "wb+")
    f.write(requests.request('get', img_src).content)
    logging.info('Image={img} downloaded from url={img_url} and saved to '
                 'disk'.format(img=filename, img_url=img_src))
    f.close()



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
    import logging
    counter = 1
    filename = fq_filepath.split('/')[-1]
    logging.info('Finding incremented filepath for {fp}'.format(fp=fq_filepath))
    while os.path.exists(fq_filepath):
        fq_filepath = filename.split('.')[0] \
                      + '(%s).' % counter \
                      + '.'.join(filename.split('.')[1:])
        counter += 1
    logging.info('Incremented filepath={ifp} for given existing '
                 'filepath '.format(ifp=fq_filepath))
    return fq_filepath


