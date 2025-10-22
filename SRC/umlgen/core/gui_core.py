import operator
import configparser
import tkinter.filedialog as tkfiledialog
import tkinter as tk
from typing import List
import glob
import json
import os, sys

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import umlgen.utils.utils as utils
import umlgen.utils.enums as enums
import core.gui_manager as gui

import umlgen.models.models_core as coreModels
import umlgen.models.models_gui as guiModels


_nodesGui = []
_modulesGui = []
_packagesGui = []
FONT_SIZE = 10
NODES_PADDING = 50
MODULE_PADDING = 25
MODULE_HEADER_HEIGHT = 25
TEXT_PADDING = 7
CIRCLE_RADIUS = 4.0
ARROW_RADIUS = 7.0

def clearArraysGui():
    """
    Vyčistí veškerá pole
    """
    _nodesGui.clear()
    _modulesGui.clear()
    _packagesGui.clear()

def prepare_diagram(canvas, nodesCore = [], modulesCore = [], packagesCore = [], isInitialDraw = True):
    """
    Hlavní funkce pro přípravu objektů diagramu. Vytvoří objekty tříd pro gui
    """
    global _nodesGui
    global _modulesGui
    global _packagesGui
    clearArraysGui()
    setup_nodes_gui(nodesCore = nodesCore)
    setup_modules_gui(modulesCore = modulesCore)
    setup_packages_gui(packagesCore=packagesCore)
    setup_relations_gui(nodesCore = nodesCore)
    draw_diagram(canvas=canvas, isInitialDraw=isInitialDraw)

def setup_nodes_gui(nodesCore: List[coreModels.NodeCore]):
    """
    Funkce pro vytvoření objektů entit a jejich parametrů
    """
    for node in nodesCore:
        node.gui_object = guiModels.NodeGui(name = node.name, type = node.nodetype)
        node.gui_object.pos_x = node.pos_x
        node.gui_object.pos_y = node.pos_y
        node.gui_object.height = node.height
        node.gui_object.width = node.width
        node.gui_object.min_width = node.min_width
        node.gui_object.min_height = node.min_height
        node.gui_object.module_name = node.module_name
        node.gui_object.draw_attributes = node.draw_attributes
        node.gui_object.draw_methods = node.draw_methods
        node.gui_object.visible = node.visible
        for attribute in node.attributes:
            node.gui_object.attributes.append(guiModels.TextGui(content = attribute.label, visible=attribute.visible, public=attribute.public))
        for method in node.methods:
            node.gui_object.methods.append(guiModels.TextGui(content = method.label, visible=method.visible, public=method.public))
        _nodesGui.append(node.gui_object)

def setup_relations_gui(nodesCore: List[coreModels.NodeCore]):
    """
    Funkce pro vytvoření objektů vztahů a jejich parametrů. Současně je prováže s entitami
    """
    for node in nodesCore:
        for relation in node.relations:
            for nodeGui in _nodesGui:
                if relation.target.name == nodeGui.name:
                    node.gui_object.relationships.append(guiModels.RelationshipGui(target=nodeGui, 
                                                                                       parent=node.gui_object, 
                                                                                       type=relation.type, 
                                                                                       break_x=relation.break_x, 
                                                                                       break_y=relation.break_y, 
                                                                                       straight=relation.straight,
                                                                                       visible=relation.visible,
                                                                                       parent_x_offset=relation.line_parent_x_offset,
                                                                                       parent_y_offset=relation.line_parent_y_offset,
                                                                                       target_x_offset=relation.line_target_x_offset,
                                                                                       target_y_offset=relation.line_target_y_offset,))
                    
def setup_modules_gui(modulesCore: List[coreModels.ModuleCore]):
    """
    Funkce pro vytvoření objektů modulů
    """
    for module in modulesCore:
        module.gui_object = guiModels.ModuleGui(name=module.name)
        module.gui_object.visible = module.visible
        _modulesGui.append(module.gui_object)

def setup_packages_gui(packagesCore: List[coreModels.PackageCore]):
    """
    Funkce pro vytvoření objektů balíčků a jeich vložení do pole, které slouží k práci s nimi
    """
    for package in packagesCore:
        package.gui_object = guiModels.PackageGui(name=package.name)
        package.gui_object.visible = package.visible
        for module in package.modules:
            for mod in _modulesGui:
                if mod.name == module.name:
                    package.gui_object.modules.append(mod)
                    mod.package = package.gui_object
        _packagesGui.append(package.gui_object)

def draw_diagram(canvas, isInitialDraw):
    """
    Hlavní funkce, která má na starosti vykreslení celého diagramu
    """
    canvas.delete("all")
    draw_nodes(canvas=canvas, isInitialDraw=isInitialDraw)
    draw_relations(canvas=canvas)
    for module in _modulesGui:
        if module.visible:
            update_module_coords(module=module)
    draw_packages(canvas=canvas)

            
def draw_packages(canvas):
    """
    Funkce, která má na starosti vykreslení rámečků představující balíčky na plátně
    """
    for package in _packagesGui:
        if package.visible:
            update_package_coords(package=package)
            general_color = utils.set_module_color()
            package.rectangle = canvas.create_rectangle(package.x1, package.y1, package.x2, package.y2, outline = general_color, fill="#fff7cc")
            package.text = canvas.create_text(package.x1 + TEXT_PADDING, 
                                              package.y1 - TEXT_PADDING - 5, 
                                              text=package.name,
                                              fill=general_color,
                                              font=("Arial", FONT_SIZE), anchor=tk.W)
            bounds = canvas.bbox(package.text)
            width = bounds[2] - bounds[0] + TEXT_PADDING * 2
            package.text_width = width
            package.text_rect = canvas.create_rectangle(package.x1, 
                                                        package.y1 - MODULE_HEADER_HEIGHT, 
                                                        package.x1 + width, 
                                                        package.y1, 
                                                        outline = general_color, fill="#fff7cc")
            canvas.lower(package.rectangle)
            canvas.lower(package.text_rect)


def draw_nodes(canvas, isInitialDraw):
    """
    Funkce pro vykreslení entit na plátně, primárná funkcionalitou je výpočet odsazení mezi modulama a jejich horizontální uspořádání
    """
    # pomocné proměnné pro výpočet velikosti grafu a pozice uzlů
    index_y = 1
    pos_x = 0
    pos_y = 0

    max_width = 0
    for module in _modulesGui:
        for node in _nodesGui:
            if node.module_name == module.name:
                base_position = index_y == 1 
                index_y += 1
                draw_node(canvas=canvas, node=node)
                max_width = node.width if node.width > max_width else max_width

                if base_position:
                    pos_x += node.pos_x
                    pos_y += node.pos_y + node.height + NODES_PADDING
                if not base_position and isInitialDraw:
                    node.change_position(canvas, pos_x, pos_y)
                    pos_y += node.height + NODES_PADDING
        
        pos_x += max_width + NODES_PADDING * 2
        pos_y = 100
    
    for node in _nodesGui:
        if node.module_name is None:
            draw_node(canvas=canvas, node=node)


def draw_node(canvas, node: guiModels.NodeGui):
    """
    Primární funkce pro vykreslení konkrétní entity na plátně
    """
    width_padding = 40
    node_header_height = 40 
    text_color = utils.set_text_color()
    node_color = utils.set_node_color(node)
    draw_params = len(node.attributes) > 0 and node.draw_attributes
    draw_methods = len(node.methods) > 0 and node.draw_methods

    max_width = node.width
    max_height = node_header_height
    y_offset = 0

    max_chars = node.name
    for atr in node.attributes:
        if atr.visible:
            if len(atr.content) > len(max_chars):
                max_chars = atr.content
    for method in node.methods:
        if method.visible:
            if len(method.content) > len(max_chars):
                max_chars = method.content
    
    tmp = canvas.create_text(node.pos_x + max_width / 2, 
                            node.pos_y,
                            text = max_chars,
                            fill=text_color,
                            font=("Arial", FONT_SIZE), anchor=tk.CENTER, justify=tk.CENTER)

    bounds = canvas.bbox(tmp)
    width = bounds[2] - bounds[0] + width_padding
    max_width = width if max_width < width else max_width

    canvas.delete(tmp)

    if node.visible:
        node.label = guiModels.Drawable()
        node.label.label = node.name
        if node.visible:
            node.label.canvas_object = canvas.create_text(node.pos_x + max_width/2, 
                                                    node.pos_y + node_header_height/2, 
                                                    text="<<" + str(node.type.name).lower() + ">>" + "\n" + node.name,
                                                    fill=text_color,
                                                    font=("Arial", FONT_SIZE), anchor=tk.CENTER, justify=tk.CENTER)


        if draw_params:
            node.attributes_separator = guiModels.LineGui()
            node.attributes_separator.pos_x = node.pos_x
            node.attributes_separator.pos_y = node.pos_y + node_header_height
            node.attributes_separator.y_offset = node_header_height
            node.attributes_separator.canvas_object = canvas.create_line(node.attributes_separator.pos_x, 
                                                                    node.attributes_separator.pos_y, 
                                                                    node.attributes_separator.pos_x + max_width, 
                                                                    node.attributes_separator.pos_y, fill=text_color)
            y_offset += FONT_SIZE + TEXT_PADDING

            for attribute in node.attributes:
                if attribute.visible:
                    label = ''
                    if not attribute.public:
                        label = '- ' + attribute.content
                    else:
                        label = attribute.content
                    attribute.label = attribute.content
                    attribute.pos_x = node.pos_x + max_width / 2
                    attribute.pos_y = node.pos_y + node_header_height + y_offset
                    attribute.y_offset = y_offset
                    attribute.canvas_object = canvas.create_text(attribute.pos_x, 
                                                        attribute.pos_y,
                                                        text = label,
                                                        fill=text_color,
                                                        font=("Arial", FONT_SIZE), anchor=tk.CENTER, justify=tk.CENTER)
                    y_offset += FONT_SIZE + TEXT_PADDING
        
        if draw_methods:
            node.method_separator = guiModels.LineGui()
            node.method_separator.pos_x = node.pos_x
            node.method_separator.pos_y = node.pos_y + node_header_height + y_offset
            node.method_separator.y_offset = node_header_height + y_offset
            node.method_separator.canvas_object = canvas.create_line(node.method_separator.pos_x, 
                                                                    node.method_separator.pos_y, 
                                                                    node.method_separator.pos_x + max_width, 
                                                                    node.method_separator.pos_y, fill=text_color)
            y_offset += FONT_SIZE + TEXT_PADDING
            for method in node.methods:
                if method.visible:
                    method.label = method.content
                    label = ''
                    if not method.public:
                        label = '- ' + method.content
                    else:
                        label = method.content
                    method.pos_x = node.pos_x + max_width / 2
                    method.pos_y = node.pos_y + node_header_height + y_offset
                    method.y_offset = y_offset
                    method.canvas_object = canvas.create_text(method.pos_x, 
                                                        method.pos_y,
                                                        text = label,
                                                        fill=text_color,
                                                        font=("Arial", FONT_SIZE), anchor=tk.CENTER, justify=tk.CENTER)

                    y_offset += FONT_SIZE + TEXT_PADDING

        max_height += y_offset
        # if max_width > node.width:
        node.width = max_width
        # if max_height > node.height:
        node.height = max_height
        # if max_width < node.min_width:
        node.min_width = max_width
        # if max_height > node.min_height:
        node.min_height = max_height

        node.canvas_object = canvas.create_rectangle(node.pos_x, 
                                                    node.pos_y, 
                                                    node.pos_x + node.width, 
                                                    node.pos_y + node.height,
                                                    fill=node_color,
                                                    outline = text_color)
        node.corner_mover = guiModels.CornerGui()
        node.corner_mover.pos_x = node.pos_x + node.width
        node.corner_mover.pos_y = node.pos_y + node.height
        node.corner_mover.canvas_object = canvas.create_polygon(node.corner_mover.pos_x - node.corner_mover.offset, 
                                                   node.corner_mover.pos_y, 
                                                   node.corner_mover.pos_x, 
                                                   node.corner_mover.pos_y, 
                                                   node.corner_mover.pos_x, 
                                                   node.corner_mover.pos_y - node.corner_mover.offset, 
                                                   fill=node.corner_mover.color, outline = node.corner_mover.outline)

    canvas.lower(node.canvas_object)


def draw_relations(canvas):
    """
    Funkce pro zjištění v jakém stavu se daný vztah nachází a dle toho zvolit typ jeho vykreslení
    """
    for node in _nodesGui:
        for relation in node.relationships:
            if relation.straight:
                draw_straight_relation(canvas, relation)
            else:
                draw_break_relation(canvas, relation)
            
            

def draw_straight_relation(canvas, relation: guiModels.RelationshipGui, redraw = False):
    """
    Funkce pro vykreslení vztahu na plátně jako přímky
    """
    fill_color = "black"
    if ( not relation.visible):
        fill_color = "#fff7cc"
    if relation.line is not None:
        canvas.delete(relation.line)
        relation.line = None
        
    if relation.line2 is not None:
        canvas.delete(relation.line2)
        relation.line2 = None
    
    if relation.break_circle is not None:
        canvas.delete(relation.break_circle)
        relation.break_circle = None

    if not redraw:
        calculate_relation_coords(relation=relation)
    if relation.visible:
        if relation.draw_type:
            match relation.type:
                case 1:
                    relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=fill_color , arrow=tk.LAST,
                                        arrowshape='10 10 8')
                case 2:
                    relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=fill_color, arrow=tk.LAST,
                                        arrowshape='10 5 5')
                    relation.line2 = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=fill_color, arrow=tk.FIRST,
                                        arrowshape='4 10 7')
                case 3:
                    relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=fill_color, dash=(3, 2), arrow=tk.LAST,
                                        arrowshape='3 12 10')
                case 4:
                    relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                    fill=fill_color, dash=(5, 3), arrow=tk.LAST, arrowshape='10 5 5')
                case 5:
                    relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                    fill=fill_color, dash=(3, 2), arrow=tk.LAST, arrowshape='10 10 8')
        else:
            relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=fill_color)
        
        canvas.lower(relation.line)
        if relation.line2 is not None:
            canvas.lower(relation.line2)

        for package in _packagesGui:
            if package.rectangle is not None:
                canvas.lower(package.rectangle)
            if package.text_rect is not None:
                canvas.lower(package.text_rect)

def draw_break_relation(canvas, relation: guiModels.RelationshipGui, redraw = False):
    """
    Funkce pro vykreslení vztahu na plátně jako zalomenou čáru.
    Soucasně vytvoří objekt kruhu představující bod zalomení pomocí kterého pak může uživatel vztahem posouvat
    """
    outline_color = "black"
    fill_color = "white"
    if ( not relation.visible):
        outline_color = "#fff7cc"
        fill_color = "#fff7cc"
    if relation.line is not None:
        canvas.delete(relation.line)
        relation.line = None
    if relation.line2 is not None:
        canvas.delete(relation.line2)
        relation.line2 = None

    if relation.break_circle is not None:
        canvas.delete(relation.break_circle)
        relation.break_circle = None
    if relation.move_circle is not None:
        canvas.delete(relation.move_circle)
        relation.move_circle = None

    if not redraw:
        calculate_relation_coords(relation=relation)
    if relation.visible:
        if relation.break_x == 0 or relation.break_y == 0 or relation.straight == True:
            if relation.draw_type:
                match relation.type:
                    case 1:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, arrow=tk.LAST,
                                        arrowshape='10 10 8')
                    case 2:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, arrow=tk.LAST,
                                        arrowshape='10 5 5')
                        relation.line2 = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, arrow=tk.FIRST,
                                        arrowshape='4 10 7')
                    case 3:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, dash=(3, 2), arrow=tk.LAST,
                                        arrowshape='3 12 10')
                    case 4:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, dash=(5, 3), arrow=tk.LAST, arrowshape='14 7 7')
                    case 5:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, dash=(3, 2), arrow=tk.LAST, arrowshape='10 10 8')
            else:
                relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color)
            relation.move_circle = create_circle(
                        canvas, relation.mover_x, relation.mover_y, CIRCLE_RADIUS, outline_color, fill_color)
            
        else:
            if relation.draw_type:
                match relation.type:
                    case 1:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                                fill=outline_color, arrow=tk.LAST,
                                                arrowshape='10 10 8')
                    case 2:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                                fill=outline_color, arrow=tk.LAST,
                                                arrowshape='10 5 5')
                        relation.line2 = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                                fill=outline_color, arrow=tk.FIRST,
                                                arrowshape='3 12 10')
                    case 3:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                                fill=outline_color, dash=(3, 2), arrow=tk.LAST,
                                                arrowshape='3 12 10')
                    case 4:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, dash=(5, 3), arrow=tk.LAST, arrowshape='10 5 5')
                    case 5:
                        relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                        fill=outline_color, dash=(3, 2), arrow=tk.LAST, arrowshape='10 10 8')
            else:
                relation.line = canvas.create_line(relation.pos_x1, relation.pos_y1, relation.break_x, relation.break_y, relation.pos_x2, relation.pos_y2,
                                                fill=outline_color)
            
            relation.break_circle = create_circle(
                        canvas, relation.break_x, relation.break_y, CIRCLE_RADIUS, outline_color, fill_color)
            
        canvas.lower(relation.line)
        if relation.line2 is not None:
            canvas.lower(relation.line2)

        for package in _packagesGui:
            if package.rectangle is not None:
                canvas.lower(package.rectangle)
            if package.text_rect is not None:
                canvas.lower(package.text_rect)

def calculate_x_offset(target_x, node_x):
    return target_x - node_x

def calculate_relation_coords(relation: guiModels.RelationshipGui):
    """
    Hlavní funkce pro výpočet souřadnic vztahu v závislosti na poloze počáteční a cílové entity
    Vzhledem k tomu, že se pro entitu uchovávají součadnice levého horního rohu (x,y), je tento výpočet složitějsí,
    nicméně tento způsob uchovávání souřadnice má výhody při implementaci pohybu s objektem
    """
    position = get_nodes_position_to_each_other(parent=relation.parent, target=relation.target)
    parentPosX = relation.parent.pos_x
    parentPosY = relation.parent.pos_y
    targetPosX = relation.target.pos_x
    targetPosY = relation.target.pos_y
    parentWidth = relation.parent.width
    parentHeight = relation.parent.height
    targetWidth = relation.target.width
    targetHeight = relation.target.height
    parentX = 0
    parentY = 0
    targetX = 0
    targetY = 0

    isLineStraight = relation.straight
    breakX = 0
    breakY = 0
    moverX = 0
    moverY = 0

    match position:
        case enums.Positions.ABOVE:
            midX1 = ((parentPosX - targetPosX) / 2)
            midX2 = (((parentPosX + parentWidth) - (targetPosX + targetWidth)) / 2)
            mid = (midX1 + midX2) / 2
            parentX = parentPosX + (parentWidth / 2) - mid
            targetX = targetPosX + (targetWidth / 2) + mid
            parentY = parentPosY
            targetY = targetPosY + targetHeight
            clear_break_coords(relation=relation)
            if ((targetPosX + (targetWidth / 2) + mid) > (targetPosX + targetWidth)):
                targetX = targetPosX + targetWidth
                parentX = targetPosX + targetWidth
            if ((targetPosX + (targetWidth / 2) + mid) < (targetPosX)):
                targetX = targetPosX
                parentX = targetPosX
            if ((parentPosX + (parentWidth / 2) + mid) > (parentPosX + parentWidth)):
                parentX = parentPosX 
                targetX = parentPosX 
            if ((parentPosX + (parentWidth / 2) + mid) < (parentPosX)):
                parentX = parentPosX + parentWidth
                targetX = parentPosX + parentWidth
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset
                targetX = parentPosX + relation.line_parent_x_offset
                targetY = targetPosY + targetHeight
                if targetX > targetPosX + targetWidth:
                    targetX = targetPosX + targetWidth
                    parentX = targetX
                if targetX < targetPosX:
                    targetX = targetPosX
                    parentX = targetX

            moverX = parentX
            moverY = ((parentY - targetY) / 2) + targetY

        case enums.Positions.BELOW:
            midX1 = ((parentPosX - targetPosX) / 2)
            midX2 = (((parentPosX + parentWidth) - (targetPosX + targetWidth)) / 2)
            mid = (midX1 + midX2) / 2
            parentX = parentPosX + (parentWidth / 2) - mid
            targetX = targetPosX + (targetWidth / 2) + mid
            parentY = parentPosY + parentHeight
            targetY = targetPosY
            clear_break_coords(relation=relation)
            if ((targetPosX + (targetWidth / 2) + mid) > (targetPosX + targetWidth)):
                targetX = targetPosX + targetWidth
                parentX = targetPosX + targetWidth
            if ((targetPosX + (targetWidth / 2) + mid) < (targetPosX)):
                targetX = targetPosX
                parentX = targetPosX
            if ((parentPosX + (parentWidth / 2) + mid) > (parentPosX + parentWidth)):
                parentX = parentPosX 
                targetX = parentPosX 
            if ((parentPosX + (parentWidth / 2) + mid) < (parentPosX)):
                parentX = parentPosX + parentWidth
                targetX = parentPosX + parentWidth
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset + parentHeight
                targetX = parentPosX + relation.line_parent_x_offset
                targetY = targetPosY
                if targetX > targetPosX + targetWidth:
                    targetX = targetPosX + targetWidth
                    parentX = targetX
                if targetX < targetPosX:
                    targetX = targetPosX
                    parentX = targetX

            moverX = parentX
            moverY = ((targetY - parentY) / 2) + parentY

        case enums.Positions.LEFT:
            midY1 = ((parentPosY - targetPosY) / 2)
            midY2 = ((parentPosY + parentHeight) - (targetPosY + targetHeight)) / 2
            mid = (midY1 + midY2) / 2
            parentX = parentPosX
            targetX = targetPosX + targetWidth
            parentY = parentPosY + (parentHeight / 2) - mid
            targetY = targetPosY + (targetHeight / 2) + mid
            clear_break_coords(relation=relation)
            if ((targetPosY + (targetHeight / 2) + mid) < targetPosY):
                targetY = targetPosY
                parentY = targetPosY
            if ((targetPosY + (targetHeight / 2) + mid) > (targetPosY + targetHeight)):
                targetY = targetPosY + targetHeight
                parentY = targetPosY + targetHeight

            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX
                targetX = targetPosX + targetWidth
                parentY = parentPosY + relation.line_parent_y_offset
                targetY = parentPosY + relation.line_parent_y_offset
                if targetY < targetPosY:
                    targetY = targetPosY
                    parentY = targetY
                if targetY > targetPosY + targetHeight:
                    targetY = targetPosY + targetHeight
                    parentY = targetY

            moverX = ((parentX - targetX) / 2) + targetX
            moverY = parentY
        case enums.Positions.RIGHT:
            midY1 = ((parentPosY - targetPosY) / 2)
            midY2 = ((parentPosY + parentHeight) - (targetPosY + targetHeight)) / 2
            mid = (midY1 + midY2) / 2
            parentX = parentPosX + parentWidth
            targetX = targetPosX
            parentY = parentPosY + (parentHeight / 2) - mid
            targetY = targetPosY + (targetHeight / 2) + mid
            clear_break_coords(relation=relation)
            if ((targetPosY + (targetHeight / 2) + mid) < targetPosY):
                targetY = targetPosY
                parentY = targetPosY
            if ((targetPosY + (targetHeight / 2) + mid) > (targetPosY + targetHeight)):
                targetY = targetPosY + targetHeight
                parentY = targetPosY + targetHeight
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + parentWidth
                targetX = targetPosX 
                parentY = parentPosY + relation.line_parent_y_offset
                targetY = parentPosY + relation.line_parent_y_offset
                if targetY < targetPosY:
                    targetY = targetPosY
                    parentY = targetY
                if targetY > targetPosY + targetHeight:
                    targetY = targetPosY + targetHeight
                    parentY = targetY

            moverX = ((parentX - targetX) / 2) + targetX
            moverY = parentY
        case enums.Positions.ABOVELEFT:
            parentX = parentPosX
            targetX = targetPosX + targetWidth
            parentY = parentPosY
            targetY = targetPosY + targetHeight
            clear_mover_coords(relation=relation)
            if not isLineStraight and relation.line_parent_x_offset == 0.0 or relation.line_parent_y_offset == 0.0:
                parentX = parentPosX + parentWidth / 2
                parentY = parentPosY
                targetX = targetPosX + targetWidth
                targetY = targetPosY + targetHeight / 2
                breakX = parentX
                breakY = targetY
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset
                targetX = targetPosX + relation.line_target_x_offset
                targetY = targetPosY + relation.line_target_y_offset
                if parentPosX < relation.break_x < parentPosX + parentWidth:
                    breakX = parentPosX + relation.line_parent_x_offset
                    breakY = targetPosY + relation.line_target_y_offset
                else:
                    breakX = targetPosX + relation.line_target_x_offset
                    breakY = parentPosY + relation.line_parent_y_offset
                
        case enums.Positions.ABOVERIGHT:
            parentX = parentPosX + parentWidth
            targetX = targetPosX
            parentY = parentPosY
            targetY = targetPosY + targetHeight
            clear_mover_coords(relation=relation)
            if not isLineStraight and relation.line_parent_x_offset == 0.0 or relation.line_parent_y_offset == 0.0:
                parentX = parentPosX + parentWidth / 2
                parentY = parentPosY
                targetX = targetPosX
                targetY = targetPosY + targetHeight / 2
                breakX = parentX
                breakY = targetY
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset
                targetX = targetPosX + relation.line_target_x_offset
                targetY = targetPosY + relation.line_target_y_offset

                if parentPosX < relation.break_x < parentPosX + parentWidth:
                    breakX = parentPosX + relation.line_parent_x_offset
                    breakY = targetPosY + relation.line_target_y_offset
                else:
                    breakX = targetPosX + relation.line_target_x_offset
                    breakY = parentPosY + relation.line_parent_y_offset


        case enums.Positions.BELOWLEFT:
            parentX = parentPosX
            targetX = targetPosX + targetWidth
            parentY = parentPosY + parentHeight
            targetY = targetPosY
            clear_mover_coords(relation=relation)

            if not isLineStraight and relation.line_parent_x_offset == 0.0 or relation.line_parent_y_offset == 0.0:
                parentX = parentPosX + parentWidth / 2
                parentY = parentPosY + parentHeight
                targetX = targetPosX + targetWidth
                targetY = targetPosY + targetHeight / 2
                breakX = parentX
                breakY = targetY 
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset
                targetX = targetPosX + relation.line_target_x_offset
                targetY = targetPosY + relation.line_target_y_offset
                if parentPosX < relation.break_x < parentPosX + parentWidth:
                    breakX = parentPosX + relation.line_parent_x_offset
                    breakY = targetPosY + relation.line_target_y_offset
                else:
                    breakX = targetPosX + relation.line_target_x_offset
                    breakY = parentPosY + relation.line_parent_y_offset

                
        case enums.Positions.BELOWRIGHT:
            parentX = parentPosX + parentWidth
            targetX = targetPosX
            parentY = parentPosY + parentHeight
            targetY = targetPosY
            clear_mover_coords(relation=relation)
            if not isLineStraight and relation.line_parent_x_offset == 0.0 or relation.line_parent_y_offset == 0.0:
                parentX = parentPosX + parentWidth / 2
                parentY = parentPosY + parentHeight
                targetX = targetPosX
                targetY = targetPosY + targetHeight / 2
                breakX = parentX
                breakY = targetY
            
            if not relation.straight and relation.line_parent_x_offset != 0.0 or relation.line_parent_y_offset != 0.0:
                parentX = parentPosX + relation.line_parent_x_offset
                parentY = parentPosY + relation.line_parent_y_offset
                targetX = targetPosX + relation.line_target_x_offset
                targetY = targetPosY + relation.line_target_y_offset
                if parentPosX < relation.break_x < parentPosX + parentWidth:
                    breakX = parentPosX + relation.line_parent_x_offset
                    breakY = targetPosY + relation.line_target_y_offset
                else:
                    breakX = targetPosX + relation.line_target_x_offset
                    breakY = parentPosY + relation.line_parent_y_offset

    relation.pos_x1 = parentX
    relation.pos_y1 = parentY
    relation.pos_x2 = targetX
    relation.pos_y2 = targetY
    if not isLineStraight:
        relation.break_x = breakX
        relation.break_y = breakY
        relation.mover_x = moverX
        relation.mover_y = moverY

def clear_mover_coords(relation: guiModels.RelationshipGui):
    """
    Pomocná funkce, která resetuje polohu moveru a resetu offset
    """
    if relation.mover_x != 0 or relation.mover_y != 0:
        relation.mover_x = 0
        relation.mover_y = 0
        relation.line_parent_x_offset = 0.0
        relation.line_parent_y_offset = 0.0
        relation.line_target_x_offset = 0.0
        relation.line_target_y_offset = 0.0

def clear_break_coords(relation: guiModels.RelationshipGui):
    """
    Pomocná funkce, která resetuje polohu breaku a resetu offset
    """
    if relation.break_x != 0 or relation.break_y != 0:
        relation.break_x = 0
        relation.break_y = 0
        relation.line_parent_x_offset = 0.0
        relation.line_parent_y_offset = 0.0
        relation.line_target_x_offset = 0.0
        relation.line_target_y_offset = 0.0

def get_nodes_position_to_each_other(parent : guiModels.NodeGui, target : guiModels.NodeGui):
    """
    Pomocná funkce, která vrací polohu dvou entit vůči sobě na plátně
    """
    parentX1 = parent.pos_x
    parentX2 = parent.pos_x + parent.width
    parentY1 = parent.pos_y
    parentY2 = parent.pos_y + parent.height

    targetX1 = target.pos_x
    targetX2 = target.pos_x + target.width
    targetY1 = target.pos_y
    targetY2 = target.pos_y + target.height

    if (parentX1 <= targetX2 and parentX1 >= targetX1) or (parentX2 >= targetX1 and parentX2 <= targetX2) or (parentX1 <= targetX1 and parentX2 >= targetX2):
        if parentY1 > targetY2:
            return enums.Positions.ABOVE
        else:
            return enums.Positions.BELOW
    elif (parentY1 >= targetY1 and parentY1 <= targetY2) or (parentY2 >= targetY1 and parentY2 <= targetY2) or (parentY1 <= targetY1 and parentY2 >= targetY2):
        if parentX1 > targetX1:
            return enums.Positions.LEFT
        else: 
            return enums.Positions.RIGHT
    elif parentX1 > targetX2:
        if parentY1 > targetY2:
            return enums.Positions.ABOVELEFT
        else:
            return enums.Positions.BELOWLEFT
    elif parentY1 > targetY2:
        return enums.Positions.ABOVERIGHT
    else:
        return enums.Positions.BELOWRIGHT

def create_circle(canvas, x, y, r, color = "black", fill = "white"):
    """ Vykreslí kruh o polomeru r na zadaných souřadnicích
    """
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline=color, fill=fill, tags="break_line_pointer")

def update_module_coords(module: guiModels.ModuleGui):
    """
    Pomocná funkce pro aktualizaci součadnic modulu
    """
    x1 = module.x1
    x2 = module.x2
    y1 = module.y1
    y2 = module.y2

    firstNode = True

    for node in _nodesGui:
        if node.visible:
            if node.module_name == module.name:
                if firstNode:
                    x1 = node.pos_x
                    x2 = node.pos_x + node.width
                    y1 = node.pos_y
                    y2 = node.pos_y + node.height
                if node.pos_x - MODULE_PADDING < x1:
                    x1 = node.pos_x - MODULE_PADDING
                if node.pos_x + node.width + MODULE_PADDING > x2:
                    x2 = node.pos_x + node.width + MODULE_PADDING
                if node.pos_y - MODULE_PADDING < y1:
                    y1 = node.pos_y - MODULE_PADDING
                if node.pos_y + node.height + MODULE_PADDING > y2:
                    y2 = node.pos_y + node.height + MODULE_PADDING
                firstNode = False
    
    module.x1 = x1
    module.x2 = x2
    module.y1 = y1
    module.y2 = y2

def update_package_coords(package: guiModels.PackageGui):
    """
    Pomocná funkce pro aktualizaci součadnic balíčku
    """
    x1 = package.x1
    x2 = package.x2
    y1 = package.y1
    y2 = package.y2
    firstModule = True

    for module in package.modules:
        if module.visible:
            if firstModule:
                x1 = module.x1
                x2 = module.x2
                y1 = module.y1
                y2 = module.y2
            if module.x1 < x1:
                x1 = module.x1
            if module.x2 > x2:
                x2 = module.x2
            if module.y1 < y1:
                y1 = module.y1
            if module.y2 > y2:
                y2 = module.y2
            firstModule = False

    package.x1 = x1
    package.x2 = x2
    package.y1 = y1
    package.y2 = y2

def get_node_by_id(id):
    """ Vrátí objekt představující uzel, na základě
    jeho ID na plátně.
    """
    for node in _nodesGui:
        if node.canvas_object == id or node.label.canvas_object == id: 
            return node
        for attribute in node.attributes:
            if attribute.canvas_object == id:
                return node
        for method in node.methods:
            if method.canvas_object == id:
                return node


def get_relation_by_id(id):
    """ Vrátí objekt představující vztah, na základě
    jeho ID na plátně.
    """
    for node in _nodesGui:
        for relation in node.relationships:
            if relation.line == id:
                return relation, node
