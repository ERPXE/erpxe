import os
# xml parse
import xml.etree.ElementTree as ET
#jinja2
from jinja2 import Environment, PackageLoader
env = Environment(loader=PackageLoader('erpxe', 'tftpboot'))
# erpxe settings module
#from settings import *
import settings

disable_filename = ".disabled"

CONF = None
from configobj import ConfigObj
from validate import Validator
def get_configuration():
    return ""
    CONF_FILE = "erpxe.conf"
    if not os.path.isfile(CONF_FILE):
	raise Exception("no configuration file found in "+CONF_FILE)
    try:
        config = ConfigObj(CONF_FILE, configspec="configspec")
    except:
        raise Exception("error reading conf")
    global CONF
    val = Validator()
    test = config.validate(val)
    if test != True:
	raise Exception("error validating conf")
    CONF = config
    return config

class Plugin:
    "Represents ERPXE plugin"
    name = ''
    def __init__(self, name):
	self.name = name

def parse_xml(plugin):
    tree = ET.parse(plugin['conf'])
    root = tree.getroot()
    prefix = "{http://erpxe.com}"
    p = plugin
    p['Deactivated'] = plugin['deactivated']
    p['Dir'] = plugin['name']
    for item in root:
	if not item.text.strip('\t\n\r'):
	    raise Exception("missing data")
	tag = item.tag.replace(prefix, '')
	text = item.text.strip('\t\n\r')
	if tag == "Append":
	    SERVER_IP = "10.0.0.1"
	    text = text.replace('%ip', SERVER_IP)
    	p[tag] = text
    return p

def get_parsed_plugin(PLUGINS_DIR, PLUGIN_NAME):
    plugin = get_plugin(PLUGINS_DIR, PLUGIN_NAME)
    if plugin:
	return parse_xml(plugin)
    return plugin

def get_plugin(PLUGINS_DIR, PLUGIN_NAME):
    PLUGIN_DIR = PLUGINS_DIR  + '/' + PLUGIN_NAME
    if not os.path.isdir(PLUGIN_DIR):
	return None
    plugin = {}
    global disable_filename
    #plugin = Plugin(PLUGIN_NAME)
    PLUGIN_1_CONF = PLUGIN_DIR + "/" + PLUGIN_NAME + ".menu"
    PLUGIN_CONF = PLUGIN_DIR + "/" + "plugin.xml"
    DEACTIVATED_FILE = PLUGIN_DIR + "/" + disable_filename
    if os.path.isfile(PLUGIN_CONF):
        plugin['compat'] = 2
        plugin['name'] = PLUGIN_NAME
        plugin['path'] = PLUGIN_DIR
        plugin['conf'] = PLUGIN_CONF
        if os.path.isfile(DEACTIVATED_FILE):
            plugin['deactivated'] = True
        else:
            plugin['deactivated'] = False
    elif os.path.isfile(PLUGIN_1_CONF):
        plugin['compat'] = 1
        plugin['name'] = PLUGIN_NAME
        plugin['Name'] = PLUGIN_NAME
        plugin['Dir'] = plugin['name']
        plugin['ShortInfo'] = 'Depreceated ERPXE 1.x plugin. please upgrade'
        plugin['path'] = PLUGIN_DIR
        plugin['conf'] = PLUGIN_1_CONF
        plugin['menu'] = 'er/plugins/' + PLUGIN_NAME + "/" + PLUGIN_NAME + ".menu"
        if os.path.isfile(DEACTIVATED_FILE):
            plugin['deactivated'] = True
        else:
            plugin['deactivated'] = False
        plugin['Deactivated'] = plugin['deactivated']
    return plugin

def get_plugins_list(PLUGINS_DIR):
    plugins = []
    if os.path.isdir(PLUGINS_DIR):
	for d in os.listdir(PLUGINS_DIR):
	    plugin = get_plugin(PLUGINS_DIR, d)
	    if plugin:
		plugins.append(plugin)
    return plugins

def get_plugins(PLUGINS_DIR):
    plugins = get_plugins_list(PLUGINS_DIR)
    plugins_data = []
    for plugin in plugins:
	if plugin['compat']==2:
	    try:
		plugins_data.append(parse_xml(plugin))
	    except:
		pass
	elif plugin['compat']==1:
	    plugins_data.append(plugin)
    return plugins_data


def compile_template(templatename, plugins_data):
    template = env.get_template(templatename)
    menustr = template.render(
	plugins = plugins_data,
	enable_quicklaunch = True,
	enable_timeout = True,
	config = {
	    # boot from the hard drive by default and show the PXE menu only if you hold down Ctrl-Alt.
	    'boot_from_hd': False,
	    # If set to  0, display the boot prompt only if the Shift or Alt key is pressed, or Caps Lock or Scroll lock is set
	    # (this is the default). If set to 1, always display the boot prompt.
	    'press_alt': False,
	    # If ALLOWOPTIONS is 0, the user is not allowed to specify any arguments on the kernel command line. 
	    # The only options recognized are those specified in an APPEND statement. The default is 1.
	    'disable_kernel_edit': False,
	    # If set to 1, ignore the Shift/Alt/Caps Lock/Scroll Lock escapes. 
	    # Use this (together with PROMPT 0) to force the default boot selection.
	    'enable_locks': False
	},
	password = {
	    'master': '12345'
	},
	path = {
	    'roms': 'boot/isolinux',
	    'skins': 'er/skins',
	    'skin': 'er/skins/basic',
	    'doc': 'doc',
	    'fdoc': 'pxelinux.cfg',
	    'default': 'pxelinux.cfg',
	    'plugins': 'er/plugins'
        }
    )

    MINIFY = True
    if MINIFY:
	menustr = os.linesep.join([s for s in menustr.splitlines() if s.strip('\t\n\r')])
	menustr = os.linesep.join([s for s in menustr.splitlines() if not s.strip('\t\n\r').startswith('#')])
    return menustr

def save_file(menustr, TFTPBOOT_DIR, target):
    with open(TFTPBOOT_DIR + target, "w") as menufile:
	menufile.write(menustr)
def get_plugins_alphabetically(PLUGINS_DIR):
    plugins = get_plugins(PLUGINS_DIR)
    return sorted(plugins, key=lambda k: k['Name'])

# Generate Menu files inside the TFTPBOOT folder.
def generate_menu(TFTPBOOT_DIR, PLUGINS_DIR):
    plugins_data = get_plugins_alphabetically(PLUGINS_DIR)
    save_file(compile_template('default.tmpl', plugins_data), TFTPBOOT_DIR, "/pxelinux.cfg/default")
    save_file(compile_template('mainmenu/mainmenu.tmpl', plugins_data), TFTPBOOT_DIR, "/pxelinux.cfg/mainmenu")

def getDisableFile(PLUGINS_DIR, PLUGIN):
    global disable_filename
    return PLUGINS_DIR+"/"+PLUGIN+"/" + disable_filename

def is_plugin_exist(PLUGINS_DIR, PLUGIN):
    plugin_dir = PLUGINS_DIR + "/" + PLUGIN
    return os.path.isdir(plugin_dir)

class PluginNotExistException(Exception):
    pass

def disable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN):
    """Disable plugin will create the .disabled file in the plugin dir"""
    # TODO check that PLUGINS_DIR exist
    # check that PLUGIN exist inside PLUGINS_DIR
    if not is_plugin_exist(PLUGINS_DIR, PLUGIN):
	raise PluginNotExistException(PLUGIN)
    # create the DisableFile
    open(getDisableFile(PLUGINS_DIR,PLUGIN), 'a').close()
    # regenreate menu
    generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)

def enable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN):
    filename = getDisableFile(PLUGINS_DIR,PLUGIN)
    if os.path.isfile(filename):
	os.remove(filename)
	print "Plugin enabled"
	generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)
    else:
	print "Plugin was not disabled"