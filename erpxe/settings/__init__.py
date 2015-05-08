# settings dictionary. created and loaded once per app run
_settings = None

class confparser():
    def parse(self):
	return { 'port': 5858 }

# should be run in top of every function in file. 
# it checks that settings has loaded from file and load/parse if not
def test():
    global _settings
    if _settings is None:
	_settings = confparser().parse()

# Get server port (for web managment panel)
def getAdminPanelServerPort():
    test()
    global _settings
    return _settings['port']