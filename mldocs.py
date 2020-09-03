#!/usr/bin/python
# encoding: utf-8
import json
import os
import sys

# Workflow3 supports Alfred 3's new features. The `Workflow` class
# is also compatible with Alfred 2.
from workflow import Workflow3, web


def get_ml_docs():
    data_url = 'https://raw.githubusercontent.com/lsgrep/mldocs/master/data/ml.json'
    result = web.get(data_url)
    # throw an error if request failed
    # Workflow will catch this and show it to the user
    result.raise_for_status()
    return result.json()


def get_ml_docs_local():
    with open('data/ml.json') as f:
        data = json.load(f)
    return data


def get_assets():
    asset_dir = 'assets'
    icon_suffix = '.icns'
    assets = os.listdir(asset_dir)
    res = []
    for i in assets:
        i = i.lower()
        if i.endswith(icon_suffix):
            asset, _ = i.split('.')
            res.append([asset, '{}/{}'.format(asset_dir, i)])
    return res


def parse_domain(link):
    return link.split("//")[-1].split("/")[0]


def main(wf):
    # The Workflow3 instance will be passed to the function
    # you call from `Workflow3.run`.
    # Not super useful, as the `wf` object created in
    # the `if __name__ ...` clause below is global...
    #
    # Your imports go here if you want to catch import errors, which
    # is not a bad idea, or if the modules/packages are in a directory
    # added via `Workflow3(libraries=...)`
    # import somemodule
    # import anothermodule

    # Get args from Workflow3, already in normalized Unicode.
    # This is also necessary for "magic" arguments to work.
    args = wf.args

    # command_delete_cache = "workflow:delcache"
    # if len(args) > 0 and args[0].lower() == command_delete_cache:
    #     wf.clear_cache()
    #     wf.send_feedback()
    #     return

    wf.logger.debug(args)
    ml_data = wf.cached_data('keywords', get_ml_docs_local, max_age=3600 * 24 * 3)
    assets = dict(wf.cached_data('assets', get_assets, max_age=3600 * 24 * 7))
    asset_keywords = sorted(assets.keys(), key=len)

    keywords = ml_data.keys()

    for k in args:
        keywords = [i for i in keywords if k.lower() in i.lower()]

    result = sorted(keywords, key=len)

    for ml_keyword in result[:20]:
        doc_link = ml_data[ml_keyword]['url']
        doc_desc = doc_link  # default value

        # if there is a desc, we use it
        if 'desc' in ml_data[ml_keyword] and ml_data[ml_keyword]['desc']:
            doc_desc = ml_data[ml_keyword]['desc']
        icon = None

        # if the asset is available
        for k in asset_keywords:
            if k in parse_domain(doc_link):
                icon = assets[k]

        wf.add_item(title=ml_keyword,
                    subtitle=doc_desc,
                    arg=doc_link,
                    valid=True,
                    icon=icon)

    # Send output to Alfred. You can only call this once.
    # Well, you *can* call it multiple times, but subsequent calls
    # are ignored (otherwise the JSON sent to Alfred would be invalid).
    wf.send_feedback()


if __name__ == '__main__':
    # Create a global `Workflow3` object
    wf = Workflow3()
    # Call your entry function via `Workflow3.run()` to enable its
    # helper functions, like exception catching, ARGV normalization,
    # magic arguments etc.
    sys.exit(wf.run(main))
