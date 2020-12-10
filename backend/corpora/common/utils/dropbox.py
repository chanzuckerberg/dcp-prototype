from urllib.parse import urlparse

import requests


<<<<<<< HEAD
class DropBoxException(Exception):
    def __init__(self, detail: str = "Invalid response from Dropbox", *args, **kwargs) -> None:
        self.detail = detail


class MissingHeaderException(DropBoxException):
    def __init__(self, detail: str = "", *args, **kwargs) -> None:
        self.detail = "Missing header from Dropbox response. " + detail


=======
>>>>>>> cleanup
def get_download_url_from_shared_link(url: str) -> str:
    """Fix a dropbox url so it's a direct download. If it's not a valid dropbox url, return None."""

    parsed_url = urlparse(url)
    if parsed_url.scheme != "https" or parsed_url.netloc != "www.dropbox.com":
        return None

    if "dl=0" in parsed_url.query:
        new_query = parsed_url.query.replace("dl=0", "dl=1")
    elif not parsed_url.query:
        new_query = "dl=1"
    elif "dl=1" in parsed_url.query:
        new_query = parsed_url.query
    else:
        new_query = parsed_url.query + "&dl=1"

    parsed_url = parsed_url._replace(query=new_query)
    return parsed_url.geturl()


def get_file_info(url: str) -> dict:
    """
    Extract information about a file from a DropBox URL.
    :param url: a DropBox URL leading to a file.
    :return: The file name and size of the file.
    """
    resp = requests.head(url, allow_redirects=True)
    resp.raise_for_status()
<<<<<<< HEAD
<<<<<<< HEAD

    def _get_key(headers, key):
        try:
            return headers[key]
        except KeyError:
            raise MissingHeaderException(f"URL({url}) failed head request. '{key}' not present in the header.")

    return {
        "size": int(_get_key(resp.headers, "content-length")),
        "name": _get_key(resp.headers, "content-disposition").split(";")[1].split("=", 1)[1][1:-1],
    }
=======
    name = resp.headers.get("content-disposition")
    name = name.split(";")[1].split("=", 1)[1][1:-1] if name else ""  # name is "" if it's not in the response.
    size = resp.headers.get("content-length", "-1")  # size == -1 if it's not in the response.
    return {"size": int(size), "name": name}
>>>>>>> Uploading with status updates
=======
    return {
        "size": int(resp.headers["content-length"]),
        "name": resp.headers["content-disposition"].split(";")[1].split("=", 1)[1][1:-1],
    }
>>>>>>> return error on files of unknown file size and type