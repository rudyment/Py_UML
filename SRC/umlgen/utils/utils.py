import configparser
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import umlgen.utils.enums as enums


def getConfig():
    config = configparser.ConfigParser()
    # Vyhledej konfigurační soubor ve složce, kde je tento
    # nástroj spuštěn.
    # print(f'os.path.abspath = {os.path.abspath}\n'
    #       f'os.path.dirname = {os.path.dirname(
    #                            os.path.dirname(
    #                            os.path.dirname(
    #                            os.path.abspath(__file__))))}'
    #       )
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    try:
        config.read_file(open(path + r'\init.ini'))
    except:
        # Pokud není konfigurační soubor nalezen, vytvoří se nový.
        config.add_section('window-settings')
        config.set('window-settings', 'window_width', '1200')
        config.set('window-settings', 'window_height', '800')
        config.add_section('diagram-color-settings')
        config.set('diagram-color-settings', 'module_bg', '#FFF1D6')
        config.set('diagram-color-settings', 'class', '#FFDC96')
        config.set('diagram-color-settings', 'module', '#99FEFE')
        config.set('diagram-color-settings', 'abstract', '#FFCCCC')
        config.set('diagram-color-settings', 'protocol', '#66FF66')
        config.add_section('text-general-color')
        config.set('text-general-color', 'general', '#1D1D1D')
        config.set('module-general-color', 'general', '#C9C9C9')
        with open(path + r'\init.ini', 'w') as configfile:
            config.write(configfile)
    return config

def set_text_color():
    """ Nastaví barvu textu.
    """
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config.read_file(open(path + r'\init.ini'))
    text_general_color = config.get('text-general-color', 'general')
    return text_general_color

def set_module_color():
    """ Nastaví barvu pro modul.
    """
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config.read_file(open(path + r'\init.ini'))
    text_general_color = config.get('module-general-color', 'general')
    return text_general_color

def set_node_color(node):
    """ Nastaví barvu uzlů dle jejich typu.
    """
    config = configparser.ConfigParser()
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    config.read_file(open(path + r'\init.ini'))
    color = "white"
    class_color = config.get('diagram-color-settings', 'class')
    module_color = config.get('diagram-color-settings', 'module')
    abstract_color = config.get('diagram-color-settings', 'abstract')
    protocol_color = config.get('diagram-color-settings', 'protocol')
    if node.type == enums.NodeType.CLASS:
        color = class_color
    if node.type == enums.NodeType.MODULE:
        color = module_color
    if node.type == enums.NodeType.ABSTRACT:
        color = abstract_color
    if node.type == enums.NodeType.PROTOCOL:
        color = protocol_color
    return color
