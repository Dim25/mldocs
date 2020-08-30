#!/usr/bin/python
# encoding: utf-8
import sys

# Workflow3 supports Alfred 3's new features. The `Workflow` class
# is also compatible with Alfred 2.
from workflow import Workflow3, web


def get_tf_docs():
    data_url = 'https://raw.githubusercontent.com/lsgrep/mldocs/master/data/ml.json'
    result = web.get(data_url)
    # throw an error if request failed
    # Workflow will catch this and show it to the user
    result.raise_for_status()
    return result.json()


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
    ml_data = wf.cached_data('posts', get_tf_docs, max_age=3600 * 24 * 3)
    keywords = ml_data.keys()

    for k in args:
        keywords = [i for i in keywords if k.lower() in i.lower()]

    result = sorted(keywords, key=len)

    tf_icon = 'assets/tensorflow.icns'
    torch_icon = 'assets/pytorch.icns'

    for ml_keyword in result[:10]:
        doc_link = ml_data[ml_keyword]['url']
        doc_desc = doc_link  # default value

        # if there is a desc, we use it
        if 'desc' in ml_data[ml_keyword] and ml_data[ml_keyword]['desc']:
            doc_desc = ml_data[ml_keyword]['desc']
        icon = None

        if 'torch' in doc_link:
            icon = torch_icon
        if 'tensorflow' in doc_link:
            icon = tf_icon

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