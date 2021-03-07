import textwrap
CHAR_WIDTH = 80

def wrap_message(msg):
    wrapped = "\n".join(textwrap.wrap(msg, CHAR_WIDTH,
                            break_long_words=False))

    return wrapped