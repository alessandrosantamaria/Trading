import platform
system = platform.system()

if system == 'Windows':
    from windows import *
else:
    from linux import * 