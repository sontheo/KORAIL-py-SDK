"""Attempt all owned cleanup while preserving the operation's first failure."""


def close_resources(resources, original=None):
    first = original
    for resource in resources:
        if resource is None:
            continue
        try:
            resource.close()
        except BaseException as failure:
            if first is None:
                first = failure
            else:
                try:
                    first.add_note(f"Cleanup raised {type(failure).__name__}: {str(failure)}")
                except BaseException:
                    pass
    if original is None and first is not None:
        raise first
