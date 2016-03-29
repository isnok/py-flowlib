
def vcs_versioning(version_info):
    """ Just use the information from the vcs, and format it nicely. """

    vcs_info = version_info['vcs_info']
    tag = version_info['latest_tag']
    distance = vcs_info['prefix_tag_distances'][tag]

    vcs_version = vcs_info['latest_tag_version']

    if distance:
        commit = version_info['latest_tag_commit'][:8]
        vcs_version += '+%s.git:%s' % (distance, commit)

    if vcs_info['dirt']:
        vcs_version += '.dirty'

    return vcs_version


def snapshot_versioning(version_info):
    """ Just use the pep440-validated tag-version and add -SNAPSHOT if git is dirty """

    version = version_info['tag_version']['version']
    if version_info['vcs_info']['dirt']:
        version += '-SNAPSHOT'

    return version


