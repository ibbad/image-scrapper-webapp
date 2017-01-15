"""
This module implements the endpoints for web api.
"""
import os
import logging
from flask import flash, redirect, url_for, request, abort, send_file
from flask import render_template, current_app
from scrapper.procedures.scrapping_functions import \
    get_image_urls_from_webpage
from scrapper.procedures.helpers import get_filename
from scrapper.web.forms import GetURLsForm
from . import web_api, web_logger
from .web_helpers import store_urls_to_file, create_files_folder, \
    send_files_to_user, get_netloc_from_url


@web_api.route('/shutdown')
def server_shutdown():
    """
    Shutdown application server.
    :return:
    """
    if not current_app.testing:
        abort(404)
    shutdown = request.environ.get('werkzeug.server.shutdown')
    if not shutdown:
        abort(500)
    shutdown()
    return 'Shutting down...'


@web_api.route('/index.html', methods=['GET', 'POST'])
def index():
    """
    Function for handling index page. It displays a form to the user for
    submitting a URL to a webpage in string field. It then displays the list of
    url to the images when the webpage (in question) is loaded.
    :return:
    """
    form = GetURLsForm()
    if form.validate_on_submit():
        if form.url_field.data == '':
            return render_template('400.html', message='No/ Bad URL provided.')
        urls = get_image_urls_from_webpage(form.url_field.data)
        flash('{count} urls for images retrieved.'.format(count=len(urls)))

        # Create directory for storing files
        create_files_folder(current_app.config['FILES_DIR'],
                            change_to_directory=False)
        filename = get_filename(
            os.path.join(current_app.config['FILES_DIR'],
                         get_netloc_from_url(form.url_field.data) + '.txt'))
        try:
            # Store list of files for later use.
            store_urls_to_file(filename, urls)
            if form.show.data:
                logging.info(
                    'Presenting {count} links for image resources extracted '
                    'from webpage={url}'.format(count=len(urls),
                                                url=form.url_field.data))
                return render_template('show_links.html',
                                       count=len(urls),
                                       webpage=form.url_field.data,
                                       urls=urls)
            if form.download.data:
                # User wants to download all images in the page.
                zfilename = send_files_to_user(
                    url_name=get_netloc_from_url(form.url_field.data),
                    urls=urls)
                logging.info(
                    'Returning zip file={fname} containing images loaded with '
                    'webpage={url}'.format(fname=zfilename,
                                           url=form.url_field.data))
                return send_file(zfilename, as_attachment=True,
                                 attachment_filename=os.path.basename(zfilename))
        except ImportError as ex:
            web_logger.error('Unable to store image urls for webpage={url} in'
                             ' local storage. '
                             'Error={err}'.format(url=form.url_field.data,
                                                  err=ex))
            return render_template(
                '500.html',
                message='Unable to retrieve the set of images from webpage='
                        '{url}'.format(url=form.url_field.data))
    return render_template('index.html', form=form)


@web_api.route('/')
def root():
    """
    Redirect / to /index page.
    :return: .../index
    """
    return redirect(url_for('web_api.index'))
