def color(colour, text):
    return f'\033[{colour}m{text}\033[0m'


def white(text):
    return color(29, text)


def black(text):
    return color(30, text)


def red(text):
    return color(31, text)


def green(text):
    return color(32, text)


def yellow(text):
    return color(33, text)


def blue(text):
    return color(34, text)


def pink(text):
    return color(35, text)


def cyan(text):
    return color(36, text)


def gray(text):
    return color(37, text)


def blackBg(text):
    return color(40, text)


def redBg(text):
    return color(41, text)


def greenBg(text):
    return color(42, text)


def yellowBg(text):
    return color(43, text)


def blueBg(text):
    return color(44, text)


def pinkBg(text):
    return color(45, text)


def cyanBg(text):
    return color(46, text)


def grayBg(text):
    return color(47, text)
