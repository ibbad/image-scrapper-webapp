"""
Configuration entities for script.
"""
# Image extensions that should be looked for in the webpage.
image_extensions = ['.jpg', '.png', '.svg', '.gif', '.jpeg']

# Possible protocols for loading images.
protocols = {
    'http': 'http://',
    'https': 'https://',
    'data-uri': 'data:image/'
}
