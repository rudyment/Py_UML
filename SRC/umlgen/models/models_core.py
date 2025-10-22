import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

import umlgen.utils.enums as enums

class Project(object):
    """ Třída která obaluje všechny uzle, tak aby
    se daly načíst pomocí JSON parseru.
    """

    def __init__(self, proj_nodes, proj_modules, proj_packages):
        self.proj_nodes = proj_nodes
        self.proj_modules = proj_modules
        self.proj_packages = proj_packages

    @classmethod
    def from_json(cls, data):
        proj_nodes = list(map(NodeCore.from_json, data["proj_nodes"]))
        proj_modules = list(map(ModuleCore.from_json, data["proj_modules"]))
        proj_packages = list(map(PackageCore.from_json, data["proj_packages"]))

        for module in proj_modules:
            for package in proj_packages:
                if module.package == package.name:
                    module.package = package

        for package in proj_packages:
            package.modules = []
            for module in proj_modules:
                if module.package == package:
                    package.modules.append(module)

        return cls(proj_nodes, proj_modules, proj_packages)

class NodeCore(object):
    """ Třída představující uzel. """

    def __init__(self, name, module_name = None, 
                 nodetype=1, 
                 pos_x=100, pos_y=100,
                 width = 150, height = 40,
                 min_width = 150, min_height = 40,
                 relations=None,
                 methods=None, attributes=None, 
                 gui_object=None, draw_attributes = True, 
                 draw_methods = True, visible = True):
        self.nodetype = enums.NodeType(nodetype)
        self.pos_x = pos_x
        self.pos_y = pos_y
        self.width = width
        self.height = height
        self.min_height = min_height
        self.min_width = min_width
        self.name = name
        self.module_name = module_name
        self.relations = relations if relations is not None else []
        self.methods = methods if methods is not None else []
        self.attributes = attributes if attributes is not None else []
        self.draw_attributes = draw_attributes
        self.draw_methods = draw_methods
        self.gui_object = gui_object if gui_object is not None else None
        self.visible = visible

    def __str__(self):
        returnString = "nodeType: % s, " " pos_x: % s, " " pos_y: % s" " name: % s \n" % (
            self.nodetype, self.pos_x, self.pos_y, self.name)
        returnString += "relations: [ \n"
        for relation in self.relations:
            returnString += "   relation: %s \n" % (relation)
        returnString += "]\n"
        returnString += "methods: [ \n"
        for method in self.methods:
            returnString += "   method: %s \n" % (method)
        returnString += "]\n"
        returnString += "attributes: [ \n"
        for attribute in self.attributes:
            returnString += "   attribute: %s \n" % (attribute)
        returnString += "]\n"
        return returnString

    @classmethod
    def from_json(cls, data):
        relations_mapped = list(map(NodeRelationCore.from_json,
                                    data["relations"]))
        attributes_mapped = list(map(AttributeCore.from_json,
                                    data["attributes"]))
        methods_mapped = list(map(AttributeCore.from_json,
                                    data["methods"]))
        data.update({"relations": relations_mapped})
        data.update({"attributes": attributes_mapped})
        data.update({"methods": methods_mapped})
        return cls(**data)
    
class NodeRelationCore(object):
    """ Třída představující vztah mezi uzly, obsahuje
    odkaz na cílový uzel.
    """

    def __init__(self, type, 
                 break_x, break_y, 
                 target, 
                 straight, 
                 visible = True, 
                 draw_type = True,
                 line_parent_x_offset = 0.0,
                 line_parent_y_offset = 0.0,
                 line_target_x_offset = 0.0,
                 line_target_y_offset = 0.0):
        self.type = enums.RelationType(type)
        self.break_x = break_x
        self.break_y = break_y
        self.target = target
        self.straight = straight
        self.visible = visible
        self.draw_type = draw_type
        self.line_parent_x_offset = line_parent_x_offset
        self.line_parent_y_offset = line_parent_y_offset
        self.line_target_x_offset = line_target_x_offset
        self.line_target_y_offset = line_target_y_offset

    def __str__(self):
        return "type: % s, " "break_x: % s, " "break_y: % s" "straight: % s" % (self.type, self.break_x, self.break_y, self.straight)

    @classmethod
    def from_json(cls, data):
        data.update({"target": NodeCore(data["target"].get("name"),
                                    data["target"].get("nodetype"))})
        return cls(**data)
    
class ModuleCore(object):
    """Trida pro ukladani parametru jednotlivych modulu"""

    def __init__(self, name, pos_x1 = 0, pos_y1 = 0, pos_x2 = 0, pos_y2 = 0, gui_object = None, visible = True, package = None):
        self.name = name
        self.pos_x1 = pos_x1
        self.pos_y1 = pos_y1
        self.pos_x2 = pos_x2
        self.pos_y2 = pos_y2
        self.gui_object = gui_object if gui_object is not None else None
        self.visible = visible
        self.package = package

    def __str__(self):
        returnString = "name: % s, " " pos_x1: % s, " " pos_y1: % s" " pos_x2: % s" " pos_y2: % s" "\n" % (
            self.name, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
        return returnString
    
    @classmethod
    def from_json(cls, data):
        return cls(**data)
    
class PackageCore(object):
    """Třída představující vykreslené balíčky na plátně"""

    def __init__(self, name, pos_x1 = 0, pos_y1 = 0, pos_x2 = 0, pos_y2 = 0, gui_object = None, visible = True, modules = []):
        self.name = name
        self.pos_x1 = pos_x1
        self.pos_y1 = pos_y1
        self.pos_x2 = pos_x2
        self.pos_y2 = pos_y2
        self.gui_object = gui_object if gui_object is not None else None
        self.visible = visible
        self.modules = modules

    def __str__(self):
        returnString = "name: % s, " " pos_x1: % s, " " pos_y1: % s" " pos_x2: % s" " pos_y2: % s" "\n" % (
            self.name, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
        return returnString
    
    @classmethod
    def from_json(cls, data):
        return cls(**data)
    
class AttributeCore(object):
    """Třída pro ukládání jednotlivých atributů tříd"""
    def __init__(self, label, visible = True, public = True):
        self.label = label
        self.visible = visible
        self.public = public

    @classmethod
    def from_json(cls, data):
        return cls(**data)
    
class MethodCore(object):
    """Třída pro ukládání jednotlivých metod tříd"""
    def __init__(self, label, visible = True, public = True):
        self.label = label
        self.visible = visible
        self.public = public

    @classmethod
    def from_json(cls, data):
        return cls(**data)
