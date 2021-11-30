COLOR = {
	'purple': '\033[95m',
	'blue': '\033[94m',
	'green': '\033[92m',
	'yellow': '\033[93m',
	'red': '\033[91m',
	'white': '\033[0m',
	'bold': "\033[1m",
}


def printM(msg, color='green'):
    '''
    Display a printed message in color.
    '''
    print('%s%s%s%s' % (COLOR['bold'], COLOR[color], msg, COLOR['white']))

