import core

def cli(arguments):
    verbose = arguments['--verbose']
    if arguments['list']:
	show_plugins()
    elif arguments['render']:
	generate_menu()
    elif arguments['enable']:
	plugin = arguments['<plugin>']
	enable(plugin)
    elif arguments['disable']:
	plugin = arguments['<plugin>']
	disable(plugin)

TFTPBOOT_DIR = "/tftpboot"
PLUGINS_DIR = TFTPBOOT_DIR + "/er/plugins"

def show_plugins():
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
	print("ERPXE menu rendered succesfully")
    except Exception, e:
	print str(e)    
	print "missing configuration file. use 'erpxe create-configuration-file' command to create one from template"
	return
    core.generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)

from difflib import SequenceMatcher

def similar(PLUGIN):
    plugins = core.get_plugins_list(PLUGINS_DIR)
    bestName = ''
    bestScore = 0
    for plugin in plugins:
	score = SequenceMatcher(None, PLUGIN.lower(), plugin['name'].lower()).ratio()
	if score > bestScore and score > .5:
	    bestScore = score
	    bestName = plugin['name']
    if bestScore > 0:
	print "maybe you meant: " + bestName + " ?"

# Enable plugin
def enable(PLUGIN):
    if not core.is_plugin_exist(PLUGINS_DIR, PLUGIN):
	print "plugin not exist"
	return similar (PLUGIN)
    core.enable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN)

# Disable plugin
def disable(PLUGIN):
    if not core.is_plugin_exist(PLUGINS_DIR, PLUGIN):
	print "plugin not exist"
	return similar (PLUGIN)
    core.disable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN)
    print "Plugin disabled"
