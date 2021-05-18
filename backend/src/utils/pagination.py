""" Utility funcions for API pagination query parameters"""


def default_limit_value(limit_value):
    if limit_value is None or limit_value == "" or limit_value == 0:
        return 10
    else:
        return limit_value


def default_page_value(page_value):
    if page_value is None or page_value == "" or page_value == 0:
        return 1
    else:
        return page_value
