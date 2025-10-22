import os, sys
import tkinter as tk
from typing import List
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core.gui_manager as gui_manager
import utils.enums as enums

CIRCLE_RADIUS = 4.0
MODULE_HEADER_HEIGHT = 25
TEXT_PADDING = 7


class MainFrame(tk.Frame):
    """ Je třída která implementuje Tkinter rám.
    Její konstruktor založí plátno se scrollbary.
    """

    def __init__(self, root, width, height):
        tk.Frame.__init__(self, root)
        self.canvas = tk.Canvas(self, background="white")
        self.xsb = tk.Scrollbar(self, orient="horizontal",
                                command=self.canvas.xview)
        self.ysb = tk.Scrollbar(self, orient="vertical",
                                command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.ysb.set,
                              xscrollcommand=self.xsb.set)

        # nastaveni rozmeru platna
        self.canvas.configure(scrollregion=(0, 0, 7500, 7500))

        self.xsb.grid(row=1, column=0, sticky="ew")
        self.ysb.grid(row=0, column=1, sticky="ns")
        self.canvas.grid(row=0, column=0, sticky="wens")
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.canvas.bind('<B1-Motion>', gui_manager.move_object)
        self.canvas.bind('<ButtonRelease-1>', gui_manager.release_mouse)
        self.canvas.bind("<Button-3>", gui_manager.set_right_click_menu)

        # Uzivatel se muze posouvat po canvasu zmacknutim kolecka na mysi a tazenim
        self.canvas.bind("<ButtonPress-2>", self.drag_start)
        self.canvas.bind("<B2-Motion>", self.drag_move)

    def drag_start(self, event):
        self.canvas.scan_mark(event.x, event.y)

    def drag_move(self, event):
        self.canvas.scan_dragto(event.x, event.y, gain=1)

class Drawable:
    """ Třída představující ten nejobecnější element,
    který se vyskytuje na plátně.
    """

    def __init__(self):
        self.pos_x: int = 0
        self.pos_y: int = 0
        self.label = ""
        self.canvas_object = ""

class LineGui(Drawable):
    """ Třída představující linku.
    """

    def __init__(self):
        Drawable.__init__(self)
        self.y_offset: int = 0


class TextGui(Drawable):
    """ Třída představující metody a atributy v uzlu.
    """

    def __init__(self, content, visible = True, public = True):
        Drawable.__init__(self)
        self.content = content
        self.y_offset: int = 0
        self.visible = visible
        self.public = public

    def change_position(self, canvas, x: int, y: int):
        """ Funkce pro pohyb s objektem této třídy po plátně
        """
        self.pos_x = x
        self.pos_y = y
        canvas.coords(self.canvas_object, self.pos_x, self.pos_y )

class CornerGui(Drawable):
    def __init__(self, visible = True ):
        Drawable.__init__(self)
        self.visible = visible
        self.offset = 12
        self.color = "white"
        self.outline = "black"

    def change_position(self, canvas, x: int, y: int):
        """ Funkce pro pohyb s objektem této třídy po plátně
        """
        self.pos_x = x
        self.pos_y = y
        canvas.coords(self.canvas_object, 
                      self.pos_x - self.offset, 
                      self.pos_y,
                      self.pos_x, 
                      self.pos_y,
                      self.pos_x, 
                      self.pos_y - self.offset,)
        
def update_text_visibility(canvas, node, text):
    coords_text = canvas.coords(text)
    coords_node = canvas.coords(node)
    visible = False
    if len(coords_text) > 0 and len(coords_node) > 0:
        if coords_text[1] <=coords_node[3]:
            visible = True
        if visible:
            canvas.itemconfigure(text, state=tk.NORMAL) 
        else:
            canvas.itemconfigure(text, state=tk.HIDDEN) 


class NodeGui(Drawable):
    """ Třída představující uzel, který je vykreslován na
    plátně. Ukládá si odkaz na všechno co obsahuje.
    """

    def __init__(self, name, type = 1, visible = True):
        Drawable.__init__(self)
        self.name = name
        self.type = enums.NodeType(type)
        self.attributes = []
        self.methods = []
        self.width = 150
        self.height = 40
        self.min_width = 150
        self.min_height = 40
        self.method_separator = None
        self.attributes_separator = None
        self.draw_attributes = True
        self.draw_methods = True
        self.relationships = []
        self.module_name = None
        self.corner_mover = None
        self.visible = visible

    def change_dimensions(self, canvas, x : int, y: int):
        node_header_height = 40
        x_dif = x - self.pos_x
        y_dif = y - self.pos_y
        if x_dif < 100:
            x_dif = 100
        if y_dif < node_header_height:
            y_dif = node_header_height

        self.width = x_dif
        self.height = y_dif
        canvas.coords(self.canvas_object, self.pos_x, self.pos_y, self.pos_x+self.width, self.pos_y+self.height)
        canvas.coords(self.label.canvas_object, self.pos_x + self.width / 2, self.pos_y + node_header_height / 2)
        if self.attributes_separator is not None:
            canvas.coords(self.attributes_separator.canvas_object, 
                          self.pos_x, 
                          self.pos_y + self.attributes_separator.y_offset, 
                          self.pos_x + self.width, 
                          self.pos_y + self.attributes_separator.y_offset)
        if self.method_separator is not None:
            canvas.coords(self.method_separator.canvas_object, 
                          self.pos_x, 
                          self.pos_y + self.method_separator.y_offset, 
                          self.pos_x + self.width, 
                          self.pos_y + self.method_separator.y_offset)
            update_text_visibility(canvas=canvas, node=self.canvas_object, text=self.method_separator.canvas_object)

        for attribute in self.attributes:
            attribute.change_position(canvas, self.pos_x + self.width / 2, self.pos_y + node_header_height + attribute.y_offset)
            update_text_visibility(canvas=canvas, node=self.canvas_object, text=attribute.canvas_object)
        
        for method in self.methods:
            method.change_position(canvas, self.pos_x + self.width / 2, self.pos_y + node_header_height + method.y_offset)
            update_text_visibility(canvas=canvas, node=self.canvas_object, text=method.canvas_object)
        
        self.corner_mover.change_position(canvas, self.pos_x + self.width, self.pos_y + self.height)

    def change_position(self, canvas, x: int, y: int):
        """ Pohne celým uzlem po plátně, současně i s atributamy a metodamy dané entity
        """
        node_header_height = 40
        self.pos_x = x
        self.pos_y = y
        canvas.coords(self.canvas_object, self.pos_x, self.pos_y, self.pos_x+self.width, self.pos_y+self.height)
        canvas.coords(self.label.canvas_object, self.pos_x + self.width / 2, self.pos_y + node_header_height / 2)
        if self.attributes_separator is not None:
            canvas.coords(self.attributes_separator.canvas_object, 
                          self.pos_x, 
                          self.pos_y + self.attributes_separator.y_offset, 
                          self.pos_x + self.width, 
                          self.pos_y + self.attributes_separator.y_offset)
        if self.method_separator is not None:
            canvas.coords(self.method_separator.canvas_object, 
                          self.pos_x, 
                          self.pos_y + self.method_separator.y_offset, 
                          self.pos_x + self.width, 
                          self.pos_y + self.method_separator.y_offset)

        for attribute in self.attributes:
            attribute.change_position(canvas, x + self.width / 2, y + node_header_height + attribute.y_offset)
        
        for method in self.methods:
            method.change_position(canvas, x + self.width / 2, y + node_header_height + method.y_offset)

        if self.corner_mover is not None:
            self.corner_mover.change_position(canvas, x + self.width, y + self.height)
            
class RelationshipGui(Drawable):
    """ Třída představující vztah mezi uzly na plátně.
    """

    def __init__(self, target, 
                 parent, type, 
                 break_x = 0, 
                 break_y = 0, 
                 straight = True, 
                 visible = True, 
                 draw_type = True,
                 default_line = True,
                 parent_x_offset = 0.0,
                 parent_y_offset = 0.0,
                 target_x_offset = 0.0,
                 target_y_offset = 0.0,
                 mover_x = 0,
                 mover_y = 0):
        Drawable.__init__(self)
        self.target = target
        self.parent = parent
        self.pos_x1 = 0
        self.pos_y1 = 0
        self.pos_x2 = 0
        self.pos_y2 = 0
        self.line = None
        self.line2 = None
        self.arrowhead_parent = None
        self.arrowhead_target = None
        self.break_circle = None
        self.move_circle = None
        self.mover_x = mover_x
        self.mover_y = mover_y
        self.break_x = break_x
        self.break_y = break_y
        self.type = type
        self.straight = straight
        self.visible = visible
        self.draw_type = draw_type
        self.default_line = default_line
        self.line_parent_x_offset = parent_x_offset
        self.line_parent_y_offset = parent_y_offset
        self.line_target_x_offset = target_x_offset
        self.line_target_y_offset = target_y_offset

    def change_position(self, canvas, def_line = True):
        """ Funkce pro pohyb s objektem této třídy po plátně
        """
        if self.visible:
            if self.default_line:
                self.default_line = def_line
            if self.straight == True:
                if self.line is not None:
                    canvas.coords(self.line, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
                if self.line2 is not None:
                    canvas.coords(self.line2, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
            else:
                if self.break_x != 0 and self.break_y != 0:
                    canvas.coords(self.line, self.pos_x1, self.pos_y1, self.break_x, self.break_y, self.pos_x2, self.pos_y2)
                    if self.line2 is not None:
                        canvas.coords(self.line2, self.pos_x1, self.pos_y1, self.break_x, self.break_y, self.pos_x2, self.pos_y2)
                    if self.move_circle is not None:
                        canvas.delete(self.move_circle)
                        self.move_circle = None
                    if self.break_circle is None:
                        self.break_circle = create_circle(
                        canvas, self.break_x, self.break_y, CIRCLE_RADIUS)
                    else:
                        canvas.coords(self.break_circle, self.break_x - CIRCLE_RADIUS, self.break_y - CIRCLE_RADIUS, self.break_x + CIRCLE_RADIUS, self.break_y + CIRCLE_RADIUS)
                else:
                    canvas.coords(self.line, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
                    if self.line2 is not None:
                        canvas.coords(self.line2, self.pos_x1, self.pos_y1, self.pos_x2, self.pos_y2)
                    if self.break_circle is not None:
                        canvas.delete(self.break_circle)
                        self.break_circle = None
                    if self.move_circle is None:
                        self.move_circle = create_circle(
                        canvas, self.mover_x, self.mover_y, CIRCLE_RADIUS)
                    else:
                        canvas.coords(self.move_circle, self.mover_x - CIRCLE_RADIUS, self.mover_y - CIRCLE_RADIUS, self.mover_x + CIRCLE_RADIUS, self.mover_y + CIRCLE_RADIUS)
    
    def change_break_position(self, canvas, breakX, breakY):
        """ Funkce pro pohyb s objektem bodu zlomu po plítně a daným vztahem
        """
        if self.straight is False:
            if is_within_nodes_boundaries(relation=self, breakX=breakX, breakY=breakY):
                update_relation_break_coords(relation=self, breakX=breakX, breakY=breakY)
                self.change_position(canvas=canvas, def_line=False)

    def change_line_position(self, canvas, breakX, breakY):
        """ Funkce pro pohyb s rovnou čárou po plátně
        """
        if self.straight is False:
            if is_within_nodes_boundaries_line(relation=self, moveX=breakX, moveY=breakY):  
                update_relation_straight_coords(relation=self, breakX=breakX, breakY=breakY)
                self.change_position(canvas=canvas, def_line=False)

    def __str__(self):
        return f"break_x: {self.break_x} break_y: {self.break_y} straight: {self.straight} type: {self.type}"
    
class ModuleGui(Drawable):
    """ Trida predstavujici vykreslovani ramecku na platne"""

    def __init__(self, name, x1 = 0, x2 = 0, y1 = 0, y2 = 0, text_width = 0, visible = True):
        Drawable.__init__(self)
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.text_width = text_width
        self.rectangle = None
        self.text_rect = None
        self.text = None
        self.visible = visible
        self.package = None
    
    def change_position(self, canvas):
        """ Funkce pro pohyb s objektem této třídy po plátně
        """
        canvas.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)
        canvas.coords(self.text, self.x1 + TEXT_PADDING, self.y1 - TEXT_PADDING - 5)
        canvas.coords(self.text_rect, self.x1, self.y1 - MODULE_HEADER_HEIGHT, self.x1 + self.text_width, self.y1)

class PackageGui(Drawable):
    """ Trida predstavujici vykreslovani ramecku balicku na platne"""

    def __init__(self, name, x1 = 0, x2 = 0, y1 = 0, y2 = 0, text_width = 0, visible = True):
        Drawable.__init__(self)
        self.name = name
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.text_width = text_width
        self.rectangle = None
        self.text_rect = None
        self.text = None
        self.visible = visible
        self.modules = []
    
    def change_position(self, canvas):
        """ Funkce pro pohyb s objektem této třídy po plátně
        """
        canvas.coords(self.rectangle, self.x1, self.y1, self.x2, self.y2)
        canvas.coords(self.text, self.x1 + TEXT_PADDING, self.y1 - TEXT_PADDING - 5)
        canvas.coords(self.text_rect, self.x1, self.y1 - MODULE_HEADER_HEIGHT, self.x1 + self.text_width, self.y1)

def create_circle(canvas, x, y, r):
    """ Vykreslí kruh o polomeru r na zadaných souřadnicích
    """
    x0 = x - r
    y0 = y - r
    x1 = x + r
    y1 = y + r
    return canvas.create_oval(x0, y0, x1, y1, outline='black', fill="white", tags="break_line_pointer")

def getTargetCoordinates(target: NodeGui):
    """ Pomocná funkce pro zjištění okrajových souřadnic entity
    """
    target_x1 = target.pos_x
    target_x2 = target.pos_x + target.width
    target_y1 = target.pos_y
    target_y2 = target.pos_y + target.height
    return {"x1": int(target_x1), "y1": int(target_y1), "x2": int(target_x2), "y2": int(target_y2)}

def is_within_nodes_boundaries(relation: RelationshipGui, breakX: float, breakY: float):
    """ Pomocná funkce, která počítá, zda nové souřadnice bodu zalomení jsou stále v průsečíku stran entit
    """
    parent_coords = getTargetCoordinates(relation.parent)
    target_coords = getTargetCoordinates(relation.target)
    parent_x = int(parent_coords["x1"]) < breakX < int(
        parent_coords["x2"])
    parent_y = int(parent_coords["y1"]) < breakY < int(
        parent_coords["y2"])
    target_x = int(target_coords["x1"]) < breakX < int(
        target_coords["x2"])
    target_y = int(target_coords["y1"]) < breakY < int(
        target_coords["y2"])
    return (parent_x and target_y) or (parent_y and target_x)

def is_within_nodes_boundaries_line(relation: RelationshipGui, moveX: float, moveY: float):
    """ Pomocná funkce, která počítá, zda nové souřadnice bodu posunuti jsou stale v pruseciku obou entit
    """
    parent_coords = getTargetCoordinates(relation.parent)
    target_coords = getTargetCoordinates(relation.target)

    x1 = 0
    x2 = 0
    y1 = 0
    y2 = 0

    if int(parent_coords["x1"]) >= int(target_coords["x1"]):
        x1 = int(parent_coords["x1"])
    else:
        x1 = int(target_coords["x1"])

    if int(parent_coords["x2"]) <= int(target_coords["x2"]):
        x2 = int(parent_coords["x2"])
    else:
        x2 = int(target_coords["x2"])

    if int(parent_coords["y1"]) >= int(target_coords["y1"]):
        y1 = int(parent_coords["y1"])
    else:
        y1 = int(target_coords["y1"])
    
    if int(parent_coords["y2"]) <= int(target_coords["y2"]):
        y2 = int(parent_coords["y2"])
    else:
        y2 = int(target_coords["y2"])

    return (x1 < moveX < x2) or (y1 < moveY < y2)


def update_relation_break_coords(relation: RelationshipGui, breakX: float, breakY: float,):
    """ Funkce pro aktualizaci souřadnic vztahu na plátně a jeho bodu zalomení
    """
    relation.break_x = breakX
    relation.break_y = breakY

    parentX1 = relation.parent.pos_x
    parentX2 = relation.parent.pos_x + relation.parent.width
    parentY1 = relation.parent.pos_y
    parentY2 = relation.parent.pos_y + relation.parent.height
    targetX1 = relation.target.pos_x
    targetX2 = relation.target.pos_x + relation.target.width
    targetY1 = relation.target.pos_y
    targetY2 = relation.target.pos_y + relation.target.height
    if  parentX1 <= breakX <= parentX2:
        relation.pos_x1 = breakX
        relation.line_parent_x_offset = breakX - parentX1
    elif breakX < parentX1:
        relation.pos_x1 = parentX1
        relation.line_parent_x_offset = 0
    else:
        relation.pos_x1 = parentX2
        relation.line_parent_x_offset = relation.parent.width

    if parentY1 <= breakY <= parentY2:
        relation.pos_y1 = breakY
        relation.line_parent_y_offset = breakY - parentY1
    elif breakY < parentY1:
        relation.pos_y1 = parentY1
        relation.line_parent_y_offset = 0
    else:
        relation.pos_y1 = parentY2
        relation.line_parent_y_offset = relation.parent.height

    if  targetX1 <= breakX <= targetX2:
        relation.pos_x2 = breakX
        relation.line_target_x_offset = breakX - targetX1
    elif breakX < targetX1:
        relation.pos_x2 = targetX1
        relation.line_target_x_offset = 0
    else:
        relation.pos_x2 = targetX2
        relation.line_target_x_offset = relation.target.width

    if targetY1 <= breakY <= targetY2:
        relation.pos_y2 = breakY
        relation.line_target_y_offset = breakY - targetY1
    elif breakY < targetY1:
        relation.pos_y2 = targetY1
        relation.line_target_y_offset = 0
    else:
        relation.pos_y2 = targetY2
        relation.line_target_y_offset = relation.target.height

def update_relation_straight_coords(relation: RelationshipGui, breakX: float, breakY: float,):
    """ Funkce pro aktualizaci souřadnic vztahu na plátně a jeho bodu pro posun (pokud je čára rovná)
    """
    relation.mover_x = breakX
    relation.mover_y = breakY

    parentX1 = relation.parent.pos_x
    parentX2 = relation.parent.pos_x + relation.parent.width
    parentY1 = relation.parent.pos_y
    parentY2 = relation.parent.pos_y + relation.parent.height
    targetX1 = relation.target.pos_x
    targetX2 = relation.target.pos_x + relation.target.width
    targetY1 = relation.target.pos_y
    targetY2 = relation.target.pos_y + relation.target.height
    if  parentX1 <= breakX <= parentX2:
        relation.pos_x1 = breakX
        relation.line_parent_x_offset = breakX - parentX1


    if parentY1 <= breakY <= parentY2:
        relation.pos_y1 = breakY
        relation.line_parent_y_offset = breakY - parentY1


    if  targetX1 <= breakX <= targetX2:
        relation.pos_x2 = breakX
        relation.line_target_x_offset = breakX - targetX1

    if targetY1 <= breakY <= targetY2:
        relation.pos_y2 = breakY
        relation.line_target_y_offset = breakY - targetY1
