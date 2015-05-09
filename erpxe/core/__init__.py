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

def get_plugins_list(PLUGINS_DIR):
    global disable_filename
    plugins = []
    for d in os.listdir(PLUGINS_DIR):
	PLUGIN_DIR = PLUGINS_DIR + "/" + d
	PLUGIN_1_CONF = PLUGIN_DIR + "/" + d + ".menu"
	PLUGIN_CONF = PLUGIN_DIR + "/" + "plugin.xml"
	DEACTIVATED_FILE = PLUGIN_DIR + "/" + disable_filename
	if os.path.isdir(PLUGIN_DIR):
	    if os.path.isfile(PLUGIN_CONF):
		plugin = {}
		plugin['compat'] = 2
		plugin['name'] = d
		plugin['path'] = PLUGIN_DIR
		plugin['conf'] = PLUGIN_CONF
		plugins.append(plugin)
		if os.path.isfile(DEACTIVATED_FILE):
		    plugin['deactivated'] = True
		else:
		    plugin['deactivated'] = False
	    elif os.path.isfile(PLUGIN_1_CONF):
		plugin = {}
		plugin['compat'] = 1
		plugin['name'] = d
		plugin['Name'] = d
		plugin['Dir'] = plugin['name']
		plugin['ShortInfo'] = 'Depreceated ERPXE 1.x plugin. please upgrade'
		plugin['path'] = PLUGIN_DIR
		plugin['conf'] = PLUGIN_1_CONF
		plugin['menu'] = 'er/plugins/' + d + "/" + d + ".menu"
		plugins.append(plugin)
		if os.path.isfile(DEACTIVATED_FILE):
		    plugin['deactivated'] = True
		else:
		    plugin['deactivated'] = False
		plugin['Deactivated'] = plugin['deactivated']
    return plugins

def is_plugin_exist(PLUGIN):
    # TODO Implement this
    return True

def scan_xml(plugin):
    tree = ET.parse(plugin['conf'])
    root = tree.getroot()
    prefix = "{http://erpxe.com}"
    p = {}
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

def get_plugins(PLUGINS_DIR):
    plugins = get_plugins_list(PLUGINS_DIR)
    plugins_data = []
    for plugin in plugins:
	if plugin['compat']==2:
	    try:
		plugins_data.append(scan_xml(plugin))
	    except:
		pass
	elif plugin['compat']==1:
	    plugins_data.append(plugin)
    return plugins_data

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

def disable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN):
    open(getDisableFile(PLUGINS_DIR,PLUGIN), 'a').close()
    generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)

def enable_plugin(TFTPBOOT_DIR, PLUGINS_DIR, PLUGIN):
    filename = getDisableFile(PLUGINS_DIR,PLUGIN)
    if os.path.isfile(filename):
	os.remove(filename)
	print "Plugin enabled"
	generate_menu(TFTPBOOT_DIR, PLUGINS_DIR)
    else:
	print "Plugin was not disabled"
