"""HTML Template Loader for MicroPython"""

import constants


def load_template(filename):
    """Load HTML template from www folder"""
    try:
        with open(f"{constants.TEMPLATE_DIR}{filename}", "r") as f:
            return f.read()
    except Exception as e:
        print(f"Error loading template {filename}: {e}")
        return None


def render_template(template, **kwargs):
    """Replace template variables with values"""
    if template is None:
        return None

    result = template
    for key, value in kwargs.items():
        placeholder = "{{" + key + "}}"
        result = result.replace(placeholder, str(value))

    return result


def serve_html(html_content):
    """Wrap HTML content in HTTP response"""
    return f"""HTTP/1.1 200 OK
Content-Type: text/html

{html_content}"""
