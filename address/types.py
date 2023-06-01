def strtobool(val):
    """Convert a string representation of truth to true (1) or false (0).

    True values are 'y', 'yes', 't', 'true', 'on', and '1';
    false values are anything else.
    """

    if not val:
        return 0
    val = val.lower()
    if val in ("y", "yes", "t", "true", "on", "1"):
        return 1
    else:
        return 0
