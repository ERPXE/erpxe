import core

def cli(arguments):
    verbose = arguments['--verbose']
    if arguments['list']:
	show_plugins()
    if arguments['gen-menu']:
	generate_menu()
    if arguments['enable']:
	plugin = arguments['<plugin>']
	enable(plugin)
    if arguments['disable']:
	plugin = arguments['<plugin>']
	disable(plugin)


def show_plugins():
    TFTPBOOT_DIR = "/tftpboot"
    PLUGINS_DIR = TFTPBOOT_DIR + "/er/plugins"
    plugins = core.get_plugins_list(PLUGINS_DIR)
    if plugins:
	print "Installed plugins:"
	for plugin in plugins:
	    if plugin['deactivated']:
		print plugin['name'] + " (disabled) "
	    else:
		print plugin['name']

def load_conf_file():
    # TODO Implement this
    global TFTPBOOT_DIR, PLUGINS_DIR 
    TFTPBOOT_DIR = "/tftpboot"
    PLUGINS_DIR = TFTPBOOT_DIR + "/er/plugins"
load_conf_file()

# Generate Menu files inside the TFTPBOOT folder.
def generate_menu():
    try:
	core.get_configuration()
    except Exception, e:
	print str(e)    
	print "missing configuration file. use 'erpxe create-configuration-file' command to create one from template"
	return

    core.generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)

def enable(PLUGIN):
    core.enable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN)

def disable(PLUGIN):
    core.disable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN)