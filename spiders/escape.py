# -*- coding: utf-8 -*-


def json_encode(value):
    return json.dumps(value).replace("</", "<\\/")

    