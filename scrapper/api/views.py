"""
Function calls for rest api of image scrapper application.
"""
import os
from flask import jsonify, request, current_app
from scrapper.procedures.scrapping_functions import get_image_urls_from_webpage
from scrapper.api import r_api, api_logger
from scrapper.web.web_helpers import create_files_folder, store_urls_to_file,\
    get_netloc_from_url
from scrapper.procedures.helpers import get_filename
from .errors import bad_request, internal_server_error


@r_api.route('/get_url_list', methods=['GET'])
def get_url_list():
    """
    This function implements the endpoint for restapi for getting list of image
    urls loaded in a webpage. The url is provided as a query string (It can
    be provided as an encoded string).
    :parameter url: Url of webpage from where image resources need to be
    retrieved should be included in querystring.
    :return:
    """
    url = request.args.get('url')
    if url is None:
        api_logger.error('No url provided with restapi call to get url list '
                         'for images loaded in the page.')
        return bad_request('No url provided in query string.')
    try:
        urls = get_image_urls_from_webpage(url)
        api_logger.info('{count} urls retrieved for image sources in given '
                        'webpage={url}'.format(count=len(urls), url=url))
        # Create directory for storing files
        create_files_folder(current_app.config['FILES_DIR'],
                            change_to_directory=False)
        api_logger.debug('{dir} created for storing the file containing image '
                         'urls for webpage={url}'.format(
                            dir=current_app.config['FILES_DIR'], url=url))
        filename = get_filename(os.path.join(
            current_app.config['FILES_DIR'],
            get_netloc_from_url(url) + '.txt'))
        # Store list of files for later use.
        store_urls_to_file(filename, urls)
        api_logger.info('Urls for image resources retrieved from webpage='
                        '{url} successfully stored in '
                        'file={fname}'.format(url=url, fname=filename))
        return jsonify({
            "status": "success",
            "count": len(urls),
            "url_list": [url for url in urls]
        })
    except Exception as ex:
        api_logger.error('Unable to retrieve list of urls for image resources '
                         'from webpage url={url}. '
                         'Error {err}'.format(err=ex, url=url))
        return internal_server_error(
            message='Unable to retrieve list of urls for image resources from '
                    'webpage url={url}. Error {err}'.format(err=ex, url=url))
