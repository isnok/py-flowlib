"""
    This file was generated by flowtool-versioning.
    Homepage: https://github.com/isnok/py-flowlib
"""

VERSION_INFO = {'vcs_info': {'commit': 'c0728d793508ed971fd5503c7a8f64a3f0fbe80a',
              'dirt': '',
              'latest_tag': 'flowtool-versioning-0.7.43',
              'latest_tag_commit': 'c0728d793508ed971fd5503c7a8f64a3f0fbe80a',
              'latest_tag_version': '0.7.43',
              'prefix': 'flowtool-versioning-',
              'prefix_tag_distances': {'flowtool-versioning-0.7.40': 44,
                                       'flowtool-versioning-0.7.41': 9,
                                       'flowtool-versioning-0.7.42': 2,
                                       'flowtool-versioning-0.7.43': 0},
              'tag_version': {'normalized': '0.7.43',
                              'release': (0, 7, 43),
                              'version': '0.7.43'}},
 'version': '0.7.43'}

def get_version():
    global VERSION_INFO
    return VERSION_INFO.get('version', '$Format:%d %H$')
