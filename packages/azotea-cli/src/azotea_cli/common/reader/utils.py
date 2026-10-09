import os
import re

from azotea_cli.common.enums import ImageType


def mk_test_img_type(regexp: re.Pattern[str]):
    def wrapper(path: str):
        def test(name: str):
            matchobj = regexp.search(name.upper())
            return True if matchobj else False

        filepath = os.path.basename(path)
        dirname = os.path.basename(os.path.dirname(path))
        return test(dirname) or test(filepath)

    return wrapper

is_flat = mk_test_img_type(re.compile(r"FLAT"))
is_dark = mk_test_img_type(re.compile(r"(DARK|OSCURO)"))
is_bias = mk_test_img_type(re.compile(r"BIAS"))

def image_type_by_path(path: str) -> ImageType:
    if is_flat(path):
        result = ImageType.FLAT
    elif is_dark(path):
        result = ImageType.DARK
    elif is_bias(path):
        result = ImageType.BIAS
    else:
        result = ImageType.LIGHT
    return result

__all__ = ["image_type_by_path"]
