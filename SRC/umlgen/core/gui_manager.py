import configparser
import copy
from platform import node
import tkinter as tk
import os, sys
from tkinter import PhotoImage, ttk
from turtle import color
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import umlgen.models.models_gui as modelsGui
import umlgen.core.gui_core as gui_core
import umlgen.utils.enums as enums

_relation_base_node = None # pomocná proměnná pro uzel ze kterého je veden vztah
_node_under_mouse = None  # pomocná proměnná pro uzel který se nachází pod kurzorem
_break_under_mouse = None # pomocná proměnná pro bod zlomu, který se nachází pod kurzorem
_corner_under_mouse = None # pomocná proměnná pro roh entity, který se nachází pod kurzorem
_mover_under_mouse = None # pomocná proměnná pro roh entity, který se nachází pod kurzorem

_x_pos_offset = 0
_y_pos_offset = 0

stored_win_position = None

def setup_window(width, height):
    """ Vytvoří okno, neboli root aplikace. """
    window = tk.Tk()
    window.title('Python UML generator')
    window.geometry(str(width) + "x" + str(height) + "+10+10")
    return window

def setup_canvas(window, width, height):
    """ Připraví plátno, které bude vždy vyplňovat
     celé okno včetně scrollbaru. """
    frame = modelsGui.MainFrame(window, width, height)
    frame.pack(fill="both", expand=True)
    return frame.canvas

def setup_menu(window):
    """ Nastaví hlavní nabídku soubor a nastavení.
     Vrátí odkaz na tyto dvě nabídky pro další úpravy.
    """
    menu = tk.Menu(window)
    menu_soubor = tk.Menu(menu, tearoff=0)
    menu_edit = tk.Menu(menu, tearoff=0)
    menu_help = tk.Menu(menu, tearoff=0)
    menu.add_cascade(label="Soubor", menu=menu_soubor)
    menu.add_cascade(label="Zobrazení", menu=menu_edit)
    menu.add_cascade(label="Nápověda", menu=menu_help)
    window.config(menu=menu)
    return menu_soubor, menu_edit, menu_help

def add_command_to_menu(menu, name, func, *args):
    """ Umožňuje přidat do nabídky položky s funkcí a argumenty.
    """
    menu.add_command(label=name, command=lambda: func(*args))

def setup_button(function, canvas, text, x, y):
    """ Vytvoří tlačítko"""
    button = tk.Button(canvas,
                       command=function, text=text, bg="black", background="white", activebackground="grey", activeforeground="white", highlightthickness=0, highlightbackground="white", fg="black")

    button.place(x=x, y=y)
    return button

def release_mouse(event):
    """ Pokud je uvolněno tlačítko myši nastav
    odkaz diagramu pod kurzorem na None.
    """
    global _node_under_mouse
    global _break_under_mouse
    global _corner_under_mouse
    global _mover_under_mouse
    _node_under_mouse = None
    _break_under_mouse = None
    _corner_under_mouse = None
    _mover_under_mouse = None


def set_right_click_menu(event):
    """ Vytvoří místní nabídku dle widgetu, který se nachází
    pod myší. Pokud tam žádný není zobrazí možnost vytvoření
    nové třídy.
    """
    canvas = event.widget
    m = tk.Menu(canvas, tearoff=0)
    abs_coord_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    abs_coord_y = canvas.winfo_pointery() - canvas.winfo_rooty()
    try:
        widget_id = event.widget.find_withtag("current")
        # Na základě typu objektu pod kurzorem se rozhoduje
        # jakou místní nabídku zobrazit.
        if len(widget_id) != 0:
            clicked_widget_type = get_type_by_id(widget_id[0])
            match clicked_widget_type[1]:
                case enums.WidgetType.BREAK:
                    if clicked_widget_type[0].straight:
                        menu_straight_text = "zalomit vztah"
                    else:
                        menu_straight_text = "zobrazit jako přímku"
                    if clicked_widget_type[0].draw_type:
                        menu_type_text = "skrýt typ vztahu"
                    else:
                        menu_type_text = "zobrazit typ vztahu"
                    m.add_command(label="změnit vztah na generalizaci",
                              command=lambda: change_line_type(canvas,
                                                              clicked_widget_type[0],
                                                              1))
                    m.add_command(label="změnit vztah na kompozici",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                2))
                    m.add_command(label="změnit vztah na realizaci",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                3))
                    m.add_command(label="změnit vztah na zahrnování",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                4))
                    m.add_command(label="změnit vztah na generalizaci rozhraní",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                5))
                    m.add_separator()
                    m.add_command(label=menu_straight_text,
                                command=lambda: change_line_break(canvas,
                                                                    clicked_widget_type[0]))
                    m.add_command(label="skrýt vztah",
                                command=lambda: hide_relation(canvas,
                                                                clicked_widget_type[0]))
                    m.add_command(label=menu_type_text,
                                command=lambda: hide_relation_type(canvas,
                                                                clicked_widget_type[0]))
                    m.add_command(label="smazat vztah",
                                command=lambda: delete_relation(canvas,
                                                                clicked_widget_type[0]))
                case enums.WidgetType.LINE:
                    if clicked_widget_type[0].straight:
                        menu_straight_text = "zalomit vztah"
                    else:
                        menu_straight_text = "zobrazit jako přímku"
                    if clicked_widget_type[0].draw_type:
                        menu_type_text = "skrýt typ vztahu"
                    else:
                        menu_type_text = "zobrazit typ vztahu"
                    m.add_command(label="změnit vztah na generalizaci",
                              command=lambda: change_line_type(canvas,
                                                              clicked_widget_type[0],
                                                              1))
                    m.add_command(label="změnit vztah na kompozici",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                2))
                    m.add_command(label="změnit vztah na realizaci",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                3))
                    m.add_command(label="změnit vztah na zahrnování",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                4))
                    m.add_command(label="změnit vztah na generalizaci rozhraní",
                                command=lambda: change_line_type(canvas,
                                                                clicked_widget_type[0],
                                                                5))
                    m.add_separator()
                    m.add_command(label=menu_straight_text,
                                command=lambda: change_line_break(canvas,
                                                                    clicked_widget_type[0]))
                    m.add_command(label="skrýt vztah",
                                command=lambda: hide_relation(canvas,
                                                                clicked_widget_type[0]))
                    m.add_command(label=menu_type_text,
                                command=lambda: hide_relation_type(canvas,
                                                                clicked_widget_type[0]))
                    m.add_command(label="smazat vztah",
                                command=lambda: delete_relation(canvas,
                                                                clicked_widget_type[0]))
                case enums.WidgetType.NODE:
                    if clicked_widget_type[0].type == enums.NodeType.MODULE:
                        nodes_menu = tk.Menu(m, tearoff=False)
                        checkVarsNodes = []
                        nodeVars = []
                        for node in gui_core._nodesGui:
                            if node.module_name == clicked_widget_type[0].name and node.name != clicked_widget_type[0].name:
                                var = tk.BooleanVar()
                                var.set(node.visible)
                                checkVarsNodes.append(var)
                                nodeVars.append(node)
                                nodes_menu.add_checkbutton(label=node.name, onvalue=True, offvalue=False,variable=var, command=lambda parNode = node, parVar = var: click_node_menu_nodes(canvas=canvas, node=parNode, menu_var=parVar))

                    relations_menu = tk.Menu(m, tearoff=False)
                    checkVarsRelations = []
                    relationsVars = []
                    for relation in clicked_widget_type[0].relationships:
                        var = tk.BooleanVar()
                        var.set(relation.visible)
                        checkVarsRelations.append(var)
                        relationsVars.append(relation)
                        relations_menu.add_checkbutton(label="do " + relation.target.name, onvalue=True, offvalue=False,variable=var, command=lambda parRelation = relation, parVar = var: click_node_menu_relations(canvas=canvas, relation=parRelation, menu_var=parVar))
                    if clicked_widget_type[0].draw_attributes:
                        show_attributes_text = "skrýt atributy"
                    else:
                        show_attributes_text = "zobrazit atributy"
                    if clicked_widget_type[0].draw_methods:
                        show_methods_text = "skrýt metody"
                    else:
                        show_methods_text = "zobrazit metody"
                    m.add_command(label="detail",
                                command=lambda: show_node_detail(
                                    widget_id[0]))
                    m.add_command(label="upravit uzel",
                                command=lambda: update_node_input(canvas,
                                                                    widget_id[
                                                                        0]))
                    m.add_command(label="smazat uzel",
                                command=lambda: remove_node(canvas,
                                                            widget_id[0]))
                    m.add_command(label="skrýt uzel",
                                command=lambda: hide_node(canvas,
                                                            widget_id[0]))
                    m.add_command(label=show_attributes_text,
                                command=lambda: hide_node_attributes(canvas,
                                                            widget_id[0]))
                    m.add_command(label=show_methods_text,
                                command=lambda: hide_node_methods(canvas,
                                                            widget_id[0]))
                    m.add_separator()
                    m.add_cascade(label="vztahy uzle", menu=relations_menu)
                    if clicked_widget_type[0].type == enums.NodeType.MODULE:
                        m.add_cascade(label="uzle modulu", menu=nodes_menu)
                    m.add_command(label="spravovat uzel",
                                command=lambda: show_modal_edit_node(canvas,
                                                            widget_id[0]))
                    m.add_separator()
                    if _relation_base_node is None:
                        m.add_command(label="nový vztah",
                                    command=lambda: start_new_relation(
                                        widget_id[0]))
                    else:
                        m.add_command(label="zrušit tvorbu vztahu",
                                    command=lambda: cancel_new_relation())
                        if gui_core.get_node_by_id(
                                widget_id[0]) is not _relation_base_node:
                            m.add_command(label="vytvořit vztah",
                                        command=lambda: config_new_realation(
                                            widget_id[0], _relation_base_node, canvas))
        else:
            m.add_command(label="nový uzel",
                          command=lambda: add_node_input(canvas,
                                                         abs_coord_x,
                                                         abs_coord_y))

        m.tk_popup(event.x_root, event.y_root)
    finally:
        m.grab_release()
        m.option_clear()


def move_object(event):
    """ Funkce, která je spjatá s událostí pohybu myši. Mění polohu
    diagramu nacházejících se pod kurzorem a překresluje jejich vztahy.
    """
    canvas = event.widget
    # Zjištění souřadnic kurzoru.
    real_x = canvas.canvasx(event.x)
    real_y = canvas.canvasy(event.y)

    global _node_under_mouse
    global _break_under_mouse
    global _corner_under_mouse
    global _mover_under_mouse


    global _x_pos_offset
    global _y_pos_offset


    if _node_under_mouse is None:
        for node in gui_core._nodesGui:
            if node.visible:
                bounds_corner = canvas.bbox(node.corner_mover.canvas_object)
                if (bounds_corner[0] < real_x < bounds_corner[2]) and (
                        bounds_corner[1] < real_y < bounds_corner[3]):
                    _corner_under_mouse = node.corner_mover
                    _node_under_mouse = node
                    _x_pos_offset = real_x - bounds_corner[0]
                    _y_pos_offset = real_y - bounds_corner[1]
                else:
                    bounds = canvas.bbox(node.canvas_object)
                    if (bounds[0] < real_x < bounds[2]) and (
                            bounds[1] < real_y < bounds[3]):
                        _node_under_mouse = node
                        _x_pos_offset = real_x - bounds[0]
                        _y_pos_offset = real_y - bounds[1]

    if  _break_under_mouse is None and _mover_under_mouse is None:
        for node in gui_core._nodesGui:
            for relation in node.relationships:
                if relation.break_circle is not None:
                    bounds = canvas.bbox(relation.break_circle)
                    if (bounds[0] < real_x < bounds[2]) and (
                            bounds[1] < real_y < bounds[3]):
                        _break_under_mouse = relation
                if relation.move_circle is not None:
                    bounds = canvas.bbox(relation.move_circle)
                    if (bounds[0] < real_x < bounds[2]) and (
                            bounds[1] < real_y < bounds[3]):
                        _mover_under_mouse = relation

    if _node_under_mouse is not None and _corner_under_mouse is None:
        _node_under_mouse.change_position(canvas = canvas, x = real_x - _x_pos_offset, y = real_y - _y_pos_offset)

        for relation in _node_under_mouse.relationships:
            gui_core.calculate_relation_coords(relation=relation)
            relation.change_position(canvas = canvas)
        for node in gui_core._nodesGui:
            for relation in node.relationships:
                if relation.target == _node_under_mouse:
                    gui_core.calculate_relation_coords(relation=relation)
                    relation.change_position(canvas = canvas)

        for module in gui_core._modulesGui:
            if module.name == _node_under_mouse.module_name:
                gui_core.update_module_coords(module=module)
                gui_core.update_package_coords(package=module.package)
                module.package.change_position(canvas = canvas)

    if _node_under_mouse is not None and _corner_under_mouse is not None:
        _node_under_mouse.change_dimensions(canvas, real_x, real_y)
        for relation in _node_under_mouse.relationships:
            calculate_offsets(relation=relation)
            if relation.straight:
                gui_core.calculate_relation_coords(relation=relation)
                relation.change_position(canvas)
            else:
                gui_core.calculate_relation_coords(relation=relation)
                relation.change_position(canvas)

        for node in gui_core._nodesGui:
            for relation in node.relationships:
                calculate_offsets(relation=relation)
                if relation.straight:
                    gui_core.calculate_relation_coords(relation=relation)
                    relation.change_position(canvas)
                else:
                    gui_core.calculate_relation_coords(relation=relation)
                    relation.change_position(canvas)

        for module in gui_core._modulesGui:
            if module.name == _node_under_mouse.module_name:
                gui_core.update_module_coords(module=module)
                gui_core.update_package_coords(package=module.package)
                module.package.change_position(canvas = canvas)


    if _break_under_mouse is not None:
        _break_under_mouse.change_break_position(canvas, real_x, real_y)

    if _mover_under_mouse is not None:
        _mover_under_mouse.change_line_position(canvas, real_x, real_y)

def calculate_offsets(relation : modelsGui.RelationshipGui):
    """ Upravuje offset pro pripojeni vztahu k jednotlivym uzlum
    """
    if relation.line_parent_x_offset > relation.parent.width:
        relation.line_parent_x_offset = relation.parent.width
    if relation.line_parent_y_offset != 0:
        relation.line_parent_y_offset = relation.parent.height

    if  relation.line_target_x_offset != 0:
        relation.line_target_x_offset = relation.target.width
    if relation.line_target_y_offset > relation.target.height:
        relation.line_target_y_offset = relation.target.height



def get_type_by_id(id):
    """ Vrací textový řetězec (node,line,none), který
    představuje typ elementu.
    """
    return_val = (None, enums.WidgetType.NONE)
    for node in gui_core._nodesGui:
        if node.visible:
            if node.corner_mover is not None and node.corner_mover.canvas_object == id:
                return_val = (node.corner_mover, enums.WidgetType.CORNER)
            if node.canvas_object == id or node.label.canvas_object == id or node.method_separator == id or node.attributes_separator == id:
                return_val = (node, enums.WidgetType.NODE)
            for attribute in node.attributes:
                if attribute.canvas_object == id:
                    return_val = (node, enums.WidgetType.NODE)
            for method in node.methods:
                if method.canvas_object == id:
                    return_val = (node, enums.WidgetType.NODE)
    for node in gui_core._nodesGui:
        if node.visible:
            for relation in node.relationships:
                if relation.line == id:
                    return_val = (relation, enums.WidgetType.LINE)
                if relation.break_circle == id:
                    return_val = (relation, enums.WidgetType.BREAK)
    return return_val

def change_line_break(canvas, relation):
    """
    Funkce pro změnu typu čáry vztahu ze zalomené na přímku a obráceně.
    """
    relation.straight = not relation.straight
    relation.line_parent_x_offset = 0.0
    relation.line_parent_y_offset = 0.0
    relation.line_target_x_offset = 0.0
    relation.line_target_y_offset = 0.0
    relation.default_line = True
    if relation.straight is True:
        gui_core.draw_straight_relation(canvas=canvas, relation=relation)
    else:
        gui_core.draw_break_relation(canvas=canvas, relation=relation)

def change_line_type(canvas, relation, type):
    """
    Funkce pro změnu typu čáry vztahu ze zalomené na přímku a obráceně.
    Poté znovu překreslí diagram
    """
    relation.type = type
    if relation.straight is True:
        gui_core.draw_straight_relation(canvas=canvas, relation=relation, redraw=True)
    else:
        gui_core.draw_break_relation(canvas=canvas, relation=relation, redraw=True)

def delete_relation(canvas, relation):
    """
    Funkce pro odstranění vztahu z plátna a z listu vztahů daných entit
    Poté znovu překreslí diagram
    """
    if relation.target.name == relation.parent.module_name:
        relation.parent.module_name = None
    relation.parent.relationships.remove(relation)
    del relation
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def hide_relation(canvas, relation):
    """
    Funkce pro skrytí vztahu na plátně
    Poté znovu překreslí diagram
    """
    relation.visible = False
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def hide_relation_type(canvas, relation):
    """
    Funkce pro skrytí typu vztahu na plátně
    Poté znovu překreslí diagram
    """
    relation.draw_type = not relation.draw_type
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def hide_node_attributes(canvas, node_id):
    """
    Funkce pro skrytí všech atributů entity
    Poté znovu překreslí diagram
    """
    node = gui_core.get_node_by_id(node_id)
    node.draw_attributes = not node.draw_attributes
    for attribute in node.attributes:
        if node.draw_attributes:
            attribute.visible = True
        else:
            attribute.visible = False
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def hide_node_methods(canvas, node_id):
    """
    Funkce pro skrytí všech metod entity
    Poté znovu překreslí diagram
    """
    node = gui_core.get_node_by_id(node_id)
    node.draw_methods = not node.draw_methods
    for method in node.methods:
        if node.draw_methods:
            method.visible = True
        else:
            method.visible = False
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def show_modal_edit_node(root_canvas, node_id):
    """
    Funkce pro zobrazení modálního okna pro správu dané entity
    Nabízí uřivateli možnost spravovat zobrazení jednotlivých parametrl entity, jako jsou atributy, metody, vztahy a náležící entity
    Poté znovu překreslí diagram
    """
    def save_window_position(window):
        global stored_win_position
        x = window.winfo_x()
        y = window.winfo_y()
        stored_win_position = (x, y)
        window.destroy()

    def node_tapped(node, state):
        node.visible = state.get()
        for relation in node.relationships:
            relation.visible = not relation.visible
        gui_core.draw_diagram(canvas=root_canvas, isInitialDraw=False)

    def attribute_tapped(attribute, state):
        attribute.visible = state.get()
        gui_core.draw_diagram(canvas=root_canvas, isInitialDraw=False)

    def method_tapped(method, state):
        method.visible = state.get()
        gui_core.draw_diagram(canvas=root_canvas, isInitialDraw=False)

    def relation_tapped(relation, state):
        relation.visible = state.get()
        gui_core.draw_diagram(canvas=root_canvas, isInitialDraw=False)

    node = gui_core.get_node_by_id(node_id)
    global stored_win_position
    check_vars = []
    btns_vars = []
    win = tk.Toplevel()
    win.title("Spravovat třídu")
    if stored_win_position is None:
        win.geometry("400x500")
    else:
        x, y = stored_win_position
        win.geometry(f"400x500+{x}+{y}")

    win.protocol("WM_DELETE_WINDOW", lambda: save_window_position(win))

    canvas_frame = tk.Frame(win)
    canvas_frame.pack(fill="both", expand=True)
    canvas = tk.Canvas(canvas_frame)
    canvas.pack(side='left', fill='both', expand=True)
    scrollbar = tk.Scrollbar(canvas_frame, orient='vertical', command=canvas.yview)
    scrollbar.pack(side='right', fill='y')
    canvas.configure(yscrollcommand=scrollbar.set)
    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor='nw')


    tk.Label(inner_frame, text=node.name, font=("Helvetica", 18, "bold")).pack(pady=(10, 0))

    if (node.type == enums.NodeType.MODULE) :
        tk.Label(inner_frame, text="Třídy modulu:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        for nod in gui_core._nodesGui:
            if nod.module_name == node.name and nod != node:
                var = tk.BooleanVar()
                var.set(nod.visible)
                check_vars.append(var)
                c = tk.Checkbutton(inner_frame, text=nod.name,
                                variable=var,
                                onvalue=True,
                                offvalue=False,
                                command = lambda node = nod, state = var:node_tapped(node, state))
                c.pack(anchor='w', padx=(110, 0))
                btns_vars.append(c)

    if len(node.attributes) > 0:
        tk.Label(inner_frame, text="Atributy třídy:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))

        for att in node.attributes:
            var = tk.BooleanVar()
            var.set(att.visible)
            check_vars.append(var)
            c = tk.Checkbutton(inner_frame, text=att.label,
                            variable=var,
                            onvalue=True,
                            offvalue=False,
                            command = lambda attr = att, state = var:attribute_tapped(attr, state))
            c.pack(anchor='w', padx=(110, 0))
            btns_vars.append(c)

    if len(node.methods) > 0:
        tk.Label(inner_frame, text="Metody třídy:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        for method in node.methods:
            var = tk.BooleanVar()
            var.set(method.visible)
            check_vars.append(var)
            c = tk.Checkbutton(inner_frame, text=method.label,
                            variable=var,
                            onvalue=True,
                            offvalue=False,
                            command = lambda met = method, state = var:method_tapped(met, state))
            c.pack(anchor='w', padx=(110, 0))
            btns_vars.append(c)

    if len(node.relationships) > 0:
        tk.Label(inner_frame, text="Vztahy třídy:", font=("Helvetica", 12, "bold")).pack(pady=(10, 0))
        for relation in node.relationships:
            var = tk.BooleanVar()
            var.set(relation.visible)
            check_vars.append(var)
            c = tk.Checkbutton(inner_frame, text=relation.target.name,
                            variable=var,
                            onvalue=True,
                            offvalue=False,
                            command = lambda rel = relation, state = var:relation_tapped(rel, state))
            c.pack(anchor='w', padx=(110, 0))
            btns_vars.append(c)

    inner_frame.update_idletasks()
    canvas.configure(scrollregion=canvas.bbox('all'))



def show_node_detail(node_id):
    """ Zobrazí detail o uzlu. Vytvoří nové okno, které naplní
    rozbaleným uzlem.
    """
    win = tk.Toplevel()
    win.wm_title("Detail třídy")
    canvas = tk.Canvas(win, background="white")
    canvas.pack(fill="both", expand=True)
    node = copy.deepcopy(gui_core.get_node_by_id(node_id))
    gui_core.draw_node(canvas, node)
    node.change_position(canvas, 50, 50 )
    win.geometry(str(node.width + 100) + "x" + str(node.height + 100))

def update_node_input(canvas, node_id):
    """ Vytvoří okno pro úpravu informací o uzlu.
    """
    node_to_update = gui_core.get_node_by_id(node_id)
    win = tk.Toplevel()
    win.wm_title("Upravit třídu")
    win.geometry("300x200")

    tk.Label(win, text="Název třídy").pack()

    e = tk.Entry(win)
    e.insert(tk.END, node_to_update.name)
    e.pack()

    v = tk.StringVar()
    v.set(node_to_update.type.name)

    tk.Radiobutton(win, text="Třída", variable=v, value="CLASS").pack()
    tk.Radiobutton(win, text="Abstraktní třída", variable=v,
                   value="ABSTRACT").pack()
    tk.Radiobutton(win, text="Protokol", variable=v, value="PROTOCOL").pack()
    if node_to_update.module_name is None:
        tk.Radiobutton(win, text="Modul", variable=v, value="MODULE").pack()

    ttk.Button(win, text="Přidat",
               command=lambda: update_node(win, canvas, node_to_update,
                                              e.get(), v.get())).pack()

def update_node(win, canvas, nodes_to_update, name, node_type):
    """ Zaktualizuje uzel.
    """
    nodes_to_update.name = name
    nodeType = enums.NodeType.CLASS
    for type in enums.NodeType:
        if type.name == node_type:
            nodeType = type

    if nodes_to_update.type == enums.NodeType.MODULE:
        for module in gui_core._modulesGui:
            if module.name == nodes_to_update.name:
                gui_core._modulesGui.remove(module)
        nodes_to_update.module_name = None
        for node in gui_core._nodesGui:
            if node.module_name == nodes_to_update.name:
                node.module_name = None

    if nodeType == enums.NodeType.MODULE:
        nodes_to_update.module_name = nodes_to_update.name
        for node in gui_core._nodesGui:
            if node.module_name is None:
                for relation in node.relationships:
                    if relation.target == nodes_to_update:
                        node.module_name = nodes_to_update.name
        new_module = modelsGui.ModuleGui(nodes_to_update.name,)
        gui_core._modulesGui.append(new_module)

    nodes_to_update.type = nodeType
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)
    win.destroy()

def remove_node(canvas, node_id):
    """ Odstraní uzel z diagramu i projektu.
    """
    node_to_delete = gui_core.get_node_by_id(node_id)
    # projdeme nodky a smazeme vztahy ktere vedli do nodky co chcem smazat
    for node in gui_core._nodesGui:
        for relation in node.relationships:
            if relation.target == node_to_delete:
                node.relationships.remove(relation)

    # potrebujeme smazat i modul, pokud dna nodka byla typu modul
    if node_to_delete.type == enums.NodeType.MODULE:
        for module in gui_core._modulesGui:
            if module.name == node_to_delete.name:
                for node in gui_core._nodesGui:
                    if node.module_name == module.name:
                        node.module_name = None
                gui_core._modulesGui.remove(module)

    gui_core._nodesGui.remove(node_to_delete)
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def start_new_relation(node_id):
    """ Zahájí tvorbu nového vztahu mezi uzly.
    """
    global _relation_base_node
    _relation_base_node = gui_core.get_node_by_id(node_id)

def cancel_new_relation():
    """ Ukončí tvorbu nového vztahu mezi uzly.
    """
    global _relation_base_node
    _relation_base_node = None

def config_new_realation(target_node_id, parent_node, canvas):
    """ Umozni uzivateli nakonfigurovat novy vztah """
    win = tk.Toplevel()
    win.wm_title("Konfigurace vztahu")
    win.geometry("200x200")
    v = tk.IntVar(master=win, value=1)
    v.set(value=1)
    tk.Radiobutton(win, text="Generalizace", variable=v,
                   value=1).pack(pady=(10, 0))
    tk.Radiobutton(win, text="Compozice", variable=v,
                   value=2).pack()
    tk.Radiobutton(win, text="Asociace", variable=v,
                   value=3).pack()
    tk.Radiobutton(win, text="Zahrnuje", variable=v,
                   value=4).pack()
    tk.Radiobutton(win, text="Generalizace rozhraní", variable=v,
                   value=5).pack()

    ttk.Button(win, text="Přidat vztah",
               command=lambda: add_new_relation(target_node_id, parent_node, canvas, win, v.get())).pack()


def add_new_relation(target_node_id, parent_node, canvas, win, node_type):
    """ Dokončí tvorby nového vztahu mezi uzly. Vykreslí
    čáru mezi nimi.
    """
    global _relation_base_node
    nodeType = enums.NodeType.CLASS
    for type in enums.NodeType:
        if type.value == node_type:
            nodeType = type
    target_node = gui_core.get_node_by_id(target_node_id)
    new_relation = modelsGui.RelationshipGui(target_node, parent_node, nodeType)
    _relation_base_node.relationships.append(new_relation)
    if target_node.type == enums.NodeType.MODULE:
        _relation_base_node.module_name = target_node.name
    _relation_base_node = None
    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)
    win.destroy()

def add_node_input(canvas, x, y):
    """ Vytvoří okno pro zadání informací o nové vytvářeném uzlu.
    """
    win = tk.Toplevel()
    win.wm_title("Přidat třídu")
    win.geometry("300x200")

    tk.Label(win, text="Název třídy").pack()

    e = tk.Entry(win)
    e.pack()

    v = tk.StringVar()
    v.set("CLASS")

    tk.Radiobutton(win, text="Třída", variable=v, value="CLASS").pack()
    tk.Radiobutton(win, text="Abstraktní třída", variable=v,
                   value="ABSTRACT").pack()
    tk.Radiobutton(win, text="Modul", variable=v, value="MODULE").pack()
    tk.Radiobutton(win, text="Protokol", variable=v, value="PROTOCOL").pack()

    ttk.Button(win, text="Přidat",
               command=lambda: add_node(e.get(), win, canvas,
                                        v.get(), x, y)).pack()


def add_node(name, win, canvas, node_type, x, y):
    """ Přidá nový uzel do diagramu.
    """
    if name == "":
        name = "empty"
    nodeType = enums.NodeType.CLASS
    for type in enums.NodeType:
        if type.name == node_type:
            nodeType = type
    node = modelsGui.NodeGui(name,type=nodeType)
    node.pos_x = x
    node.pos_y = y
    gui_core._nodesGui.append(node)
    # pokud se jedna o modul, pridame dalsi modul
    if node.type == enums.NodeType.MODULE:
        node.module_name = name
        module = modelsGui.ModuleGui(name)
        gui_core._modulesGui.append(module)

    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)
    win.destroy()

def hide_node(canvas, node_id):
    """
    Funkce pro skrytí dané entity na plátně
    Poté znovu překreslí diagram
    """
    node = gui_core.get_node_by_id(node_id)
    node.visible = False

    if node.type == enums.NodeType.MODULE:
        for relation in node.relationships:
            relation.visible = False
        for nodeGui in gui_core._nodesGui:
            if nodeGui.module_name == node.name:
                nodeGui.visible = False
                for relation in nodeGui.relationships:
                    relation.visible = False
        for module in gui_core._modulesGui:
            if module.name == node.name:
                module.visible = False
    else:
        for relation in node.relationships:
            relation.visible = False
        for nodeGui in gui_core._nodesGui:
            for relation in nodeGui.relationships:
                if relation.target == node:
                    relation.visible = False

    for package in gui_core._packagesGui:
        isVisible = False
        for module in package.modules:
            if module.visible is True:
                isVisible = True
        if isVisible is False:
            package.visible = False
        else:
            package.visible = True


    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def click_node_menu_nodes(canvas, node, menu_var):
    """
    Funkce pro skrytí dané entity a jejích vztahů na plátně na základě jejího výběru ze submenu dané entity
    Poté znovu překreslí diagram
    """
    node.visible = not node.visible
    menu_var.set(node.visible)
    for relation in node.relationships:
            relation.visible = not relation.visible
    for nodeGui in gui_core._nodesGui:
        for relation in nodeGui.relationships:
            if relation.target == node:
                relation.visible = not relation.visible

    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)

def click_node_menu_relations(canvas, relation, menu_var):
    """
    Funkce pro skrytí daného vztahu na plátně na základě jejího výběru ze submenu dané entity
    Poté znovu překreslí diagram
    """
    relation.visible = not relation.visible
    menu_var.set(relation.visible)

    gui_core.draw_diagram(canvas=canvas, isInitialDraw=False)
