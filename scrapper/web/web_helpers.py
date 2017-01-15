"""
This file contains helper functions to be used in implementing the endpoints
for web api.
"""
import os
import shutil
import zipfile
from flask import current_app, send_from_directory
from . import web_logger
from ..procedures.scrapping_functions import download_images

try:
    # Python 3
    from urllib.parse import urlparse
except ImportError:
    # Python 2
    from urlparse import urlparse


def get_netloc_from_url(url):
    """
    This function returns the net location for url by parsing it.
    :param url: web page url
    :return:
    """
    try:
        return urlparse(url).netloc
    except Exception as ex:
        web_logger.error('Error {err} while parsing {url}'.format(err=ex,
                                                                  url=url))
        return None


def store_urls_to_file(filename, urls=None):
    """
    This function writes list of urls to a given file.
    :param filename: File where urls need to be stored.
    :param urls: List of urls to be written to file.
    :return: Number of urls written to list.
    """
    if urls is None or filename is None:
        web_logger.warning('Please provide valid URL set to be written to a '
                           'valid file. Provided urls={urls}, \nfile='
                           '{file}'.format(urls=urls, file=filename))
        return 0
    success = 0
    try:
        f = open(filename, 'w+')
        for url in urls:
            f.write(url+'\n')
            success += 1
        f.close()
    except Exception as ex:
        web_logger.error('Unable to store image urls to file={file}.'
                         'Error={err}'.format(file=filename, err=ex))
        pass
    return success


def create_files_folder(path, change_to_directory=True):
    """
    This function creates the directories on the given path if they don't exist.
    :param path: Path for directory creation
    :param change_to_directory: Flag indicating whether program should switch
    to given directory as working directory. (default=True)
    :return:
    """
    try:
        if not os.path.exists(path):
            os.makedirs(path)
            web_logger.info('{dir} created for storing images'.format(
                dir=path))
        if change_to_directory:
            os.chdir(path)
        return True
    except OSError as os_ex:
        web_logger.error('Cannot create requested directory={dir} to store '
                         'files. Error={err}'.format(dir=path, err=os_ex))
        return False
    except Exception as ex:
        web_logger.error(
            'Error={err} while creating default directory for storing files '
            'i.e.dir={dir}'.format(err=ex, dir=current_app.config['FILES_DIR']))
        return False


def send_files_to_user(url_name=None, urls=None):
    """
    This function downloads the images given in the list of urls, stores them
    in temporary folder and generates a zip file containing all those
    downloaded images. This zip file can then be returned to the requesting
    user.
    :param url_name: name of website from which the image resources links are
    scrapped.
    :param urls: list of urls to image resources.
    :return:
    """
    # Establish directory to store the downloaded images.
    tmp_files_dir = current_app.config['TEMP_SUBFOLDER']

    # Create the folder for storing the images.
    if not create_files_folder(tmp_files_dir+url_name):
        web_logger.error('Unable to create folder at={dir} for storing '
                         'content.'.format(dir=tmp_files_dir+url_name))
        return None

    # Store file with list of URLs to the repo
    store_urls_to_file(url_name + '.txt', urls=urls)
    web_logger.info('Successfully stored list of {count}image urls to file='
                    '{filename}'.format(count=len(urls),
                                        filename=url_name+'.txt'))
    # Download Images
    stats = download_images(urls)
    web_logger.info('Successfully downloaded {succ} images and failed to '
                    'download {f} images from given website='
                    '{url}'.format(succ=stats['success'], f=stats['fail'],
                                   url=url_name))

    # Zip the downloaded images
    zip_filename = os.path.dirname(os.getcwd()) + '/' + url_name + '.zip'
    if zip_directory_to_file(zip_filename, path=os.getcwd()):
        os.chdir(os.path.dirname(os.getcwd()))
        shutil.rmtree(url_name, ignore_errors=True)
        os.chdir(current_app.config['APP_WD'])
        return zip_filename
    # Remove temporary files
    os.chdir(os.path.dirname(os.getcwd()))
    shutil.rmtree(url_name, ignore_errors=True)
    os.chdir(current_app.config['APP_WD'])
    return None


def zip_directory_to_file(filename, path):
    """
    This function zips the conetnts of a directory to a file.
    :param filename: Name of Zip file.
    :param path: path
    :return:
    """
    try:
        zipf = zipfile.ZipFile(filename, 'w', zipfile.ZIP_DEFLATED)
        for root, dirs, files in os.walk(path):
            for file in files:
                web_logger.debug("archiving file {f}".format(f=file))
                zipf.write(file, os.path.relpath(file, root))
        zipf.close()
        web_logger.info('Contents of {dir} zipped successfully to '
                        '{fname}'.format(dir=path, fname=filename))
        return True
    except Exception as ex:
        web_logger.error('Cannot zip contents of dir={dir} to filename='
                         '{fname}. Error={err}'.format(dir=path,
                                                       fname=filename,
                                                       err=ex))
        return None
