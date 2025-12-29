"""
Utility functions for ESP32 LED Sports Display
Shared helper functions to reduce code duplication
"""


def url_decode_params(body):
    """
    Parse and URL decode form data from HTTP POST request body

    Args:
        body: The POST request body string containing form data

    Returns:
        Dictionary of decoded parameter key-value pairs

    Example:
        >>> url_decode_params("ssid=MyNetwork&password=test%40123")
        {'ssid': 'MyNetwork', 'password': 'test@123'}
    """
    params = {}

    if not body:
        return params

    # URL decode mappings for common characters
    replacements = {
        "+": " ",
        "%40": "@",
        "%21": "!",
        "%23": "#",
        "%24": "$",
        "%25": "%",
        "%26": "&",
        "%2B": "+",
        "%2F": "/",
        "%3D": "=",
        "%3F": "?",
    }

    for param in body.split("&"):
        if "=" in param:
            key, value = param.split("=", 1)

            # Apply URL decoding
            for encoded, decoded in replacements.items():
                value = value.replace(encoded, decoded)

            params[key] = value

    return params
