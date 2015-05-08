_settings = None

class confparser():
    def parse(self):
	return 1

class settings:
    @staticmethod
    def getAdminPanelServerPort():
	if _settings is None:
	    _settings = confparser().parse()
	    return 123
	return 5858