""" Modul definující generátor. Tento modul se stará o běh
celé aplikace. Definuje metody pro hlavní nabídku a pamatuje
si stav ve kterém aplikace je.
"""

import tkinter.filedialog as tkfiledialog
import tkinter as tk
import json
import os

import umlgen.core.analyzer as analyzerModel
import umlgen.core.gui_manager as gui
import umlgen.core.gui_core as gui_core
import umlgen.models.models_core as coreModels
import umlgen.utils.utils as utils
import umlgen.utils.enums as enums

_canvas = None
_nodesCore = []
_modulesCore = []
_packagesCore = []
_cursor = "arrow"
_open_file_name = None

def change_window_name(window, name):
    """Nastaví název okna tak, aby reflektoval otevřený soubor/složku """
    global _open_file_name
    _open_file_name = None
    _open_file_name = name
    window.title('Python UML generator - ' + _open_file_name)

def clear_window_name(window):
    """ Nastaví název okna na defaultní název"""
    global _open_file_name
    _open_file_name = None
    window.title('Python UML generator')

def clearArraysCore():
    """ Vymaže veškeré data z polí """
    _nodesCore.clear()
    _modulesCore.clear()
    _packagesCore.clear()


def new_project(window):
    """ Vyčístí plátno a založí nové čisté. """
    clearArraysCore()
    clear_window_name(window = window)
    gui_core.prepare_diagram(canvas = _canvas,
                             nodesCore = _nodesCore,
                             modulesCore = _modulesCore,
                             packagesCore=_packagesCore)

def save_project():
    """ Uloží projekt do souboru json. """
    update_nodes()
    filetypes = [
        ("json file", "*.json"),
    ]
    filename = tkfiledialog.SaveAs(defaultextension='.json', filetypes=filetypes,
                                   title="Export to JSON",
                                   ).show()
    if filename:
        f = open(filename, 'w', encoding="utf-8")
        project = coreModels.Project( _nodesCore, _modulesCore, _packagesCore)
        project_json = json.dumps(project, default=lambda o: o.__dict__,
                                  indent=4)
        f.write(str(project_json))
        f.close()

def load_project(window):
    """ Načte projekt ze souboru json a vykreslí diagram. """
    file_path = tkfiledialog.askopenfilename(
        filetypes=(("json files", "*.json"),))

    file_name = os.path.basename(os.path.normpath(file_path))

    file = open(file_path, "r", encoding="utf-8")
    data = json.loads(file.read())
    file.close()
    clearArraysCore()
    try:
        project = coreModels.Project.from_json(data)
    finally:
        _nodesCore.extend(project.proj_nodes)
        _modulesCore.extend(project.proj_modules)
        _packagesCore.extend(project.proj_packages)

    change_window_name(window=window, name=file_name)
    gui_core.prepare_diagram(canvas= _canvas,
                             nodesCore = _nodesCore,
                             modulesCore = _modulesCore,
                             packagesCore=_packagesCore,
                             isInitialDraw = False)

def load_from_source_file(window):
    """ Načte soubor se zdrojovým kódem Pythonu a vykreslí diagram. """
    file_path = tkfiledialog.askopenfilename(
        filetypes=(("py files", "*.py"),))
    file = open(file_path, "r", encoding="utf-8")
    package_name = os.path.basename(os.path.normpath(os.path.dirname(file_path)))

    try:
        tree = analyzerModel.build_ast_tree(file.read())
        file.close()
        analyzer = analyzerModel.Analyzer(os.path.basename(file_path))
        analyzer.visit(tree)

    finally:
        if not _nodesCore:
            clearArraysCore()
            _nodesCore.extend(analyzer.nodes)
            _modulesCore.append(analyzer.module)
            _packagesCore.append(coreModels.PackageCore(name=package_name, modules=[]))
            _packagesCore[0].modules.append(analyzer.module)
            # get_module_boarders_coord(a.nodes)
            change_window_name(window=window, name=package_name)
            gui_core.prepare_diagram(canvas= _canvas,
                                     nodesCore = _nodesCore,
                                     modulesCore = _modulesCore,
                                     packagesCore=_packagesCore)
        else:
            clearArraysCore()
            _nodesCore.extend(analyzer.nodes)
            _modulesCore.append(analyzer.module)
            _packagesCore.append(coreModels.PackageCore(name=package_name, modules=[]))
            _packagesCore[0].modules.append(analyzer.module)
            # update_nodes()
            # update_current_diagram_nodes(a.nodes)
            # get_module_boarders_coord(a.nodes)
            change_window_name(window=window, name=package_name)
            gui_core.prepare_diagram(canvas= _canvas,
                                     nodesCore = _nodesCore,
                                     modulesCore = _modulesCore,
                                     packagesCore=_packagesCore)

def load_from_source_directory(window):
    """ Načte soubory se zdrojovým kódem Pythonu ze složky
    a vykreslí diagram. """
    directory_path = tkfiledialog.askdirectory()
    files_paths = get_python_files(directory_path)[0]
    packages_name = get_python_files(directory_path)[1]
    nodes = []
    modules = []
    packages = []
    for package in packages_name:
        packages.append(coreModels.PackageCore(name=package, modules = []))

    for file_path in files_paths:
        package_name = os.path.basename(os.path.normpath(os.path.dirname(file_path)))
        files = open(file_path, "r", encoding="utf-8")
        try:
            tree = analyzerModel.build_ast_tree(files.read())
            analyzer = analyzerModel.Analyzer(os.path.basename(file_path))
            files.close()
            analyzer.visit(tree)
        finally:
            nodes.extend(analyzer.nodes)
            modules.append(analyzer.module)
            for package in packages:
                if package.name == package_name:
                    package.modules.append(analyzer.module)

    for package in packages:
        if len(package.modules) == 0:
            packages.remove(package)

    if not _nodesCore:
        clearArraysCore()
        _nodesCore.extend(nodes)
        _modulesCore.extend(modules)
        _packagesCore.extend(packages)
        # get_module_boarders_coord(nodes)
        change_window_name(window=window, name=packages_name[0])
        gui_core.prepare_diagram(canvas= _canvas, nodesCore = _nodesCore, modulesCore = _modulesCore, packagesCore= _packagesCore)
    else:
        clearArraysCore()
        _nodesCore.extend(nodes)
        _modulesCore.extend(modules)
        _packagesCore.extend(packages)
        # update_nodes()
        # update_current_diagram_nodes(nodes)
        # get_module_boarders_coord(nodes)
        change_window_name(window=window, name=packages_name[0])
        gui_core.prepare_diagram(canvas= _canvas, nodesCore = _nodesCore, modulesCore = _modulesCore, packagesCore= _packagesCore)

def get_python_files(directory):
    """ Získa veškeré cesty k souborům a vráti je i s názvem balíčku """
    python_files = []
    packages = []
    last_folder = os.path.basename(os.path.normpath(directory))
    packages.append(last_folder)

    # projde vsechny fily a slozky v dane ceste
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.py'):
                python_files.append(os.path.join(root, file))
        for dir in dirs:
            if not dir.endswith('__'):
                packages.append(dir)

    return python_files, packages

def update_nodes():
    """Aktualizuje uzle o změny provedené v diagramu. """
    updated_nodes = []
    updated_modules = []
    updated_packages = []
    for node in gui_core._nodesGui:
        updated_node = coreModels.NodeCore(name=node.name, module_name=node.module_name, nodetype=node.type.value)
        updated_node.pos_x = node.pos_x
        updated_node.pos_y = node.pos_y
        updated_node.draw_attributes = node.draw_attributes
        updated_node.draw_methods = node.draw_methods
        updated_node.visible = node.visible
        updated_node.height = node.height
        updated_node.width = node.width
        updated_node.min_height = node.min_height
        updated_node.min_width = node.min_width

        for a in node.attributes:
            updated_node.attributes.append(coreModels.AttributeCore(label=a.label, visible=a.visible))
        for m in node.methods:
            updated_node.methods.append(coreModels.MethodCore(label=m.label, visible=m.visible))

        for relation in node.relationships:
            updated_node.relations.append(
                coreModels.NodeRelationCore(
                    type=relation.type.value,
                    break_x=relation.break_x,
                    break_y=relation.break_y,
                    target=coreModels.NodeCore(name=relation.target.name),
                    straight=relation.straight,
                    visible=relation.visible,
                    line_parent_x_offset=relation.line_parent_x_offset,
                    line_parent_y_offset=relation.line_parent_y_offset,
                    line_target_x_offset=relation.line_target_x_offset,
                    line_target_y_offset=relation.line_target_y_offset,
                )
        )
        updated_nodes.append(updated_node)

    for module in gui_core._modulesGui:
        updated_module = coreModels.ModuleCore(name=module.name, package=None)
        updated_module.visible = module.visible
        updated_module.package = module.package.name
        updated_modules.append(updated_module)

    for package in gui_core._packagesGui:
        updated_package = coreModels.PackageCore(name=package.name, modules=[])
        updated_package.visible = package.visible
        for mod in package.modules:
            updated_package.modules.append(mod.name)
        updated_packages.append(updated_package)

    clearArraysCore()
    _nodesCore.extend(updated_nodes)
    _modulesCore.extend(updated_modules)
    _packagesCore.extend(updated_packages)

def show_attributes():
    """ zobrazí všechny skryté atributy všech entit """
    for node in gui_core._nodesGui:
        node.draw_attributes = True
        for att in node.attributes:
            att.visible = True
        gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def hide_attributes():
    """ Skryje všechny atributy všech entit """
    for node in gui_core._nodesGui:
        node.draw_attributes = False
        for att in node.attributes:
            att.visible = False
        gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def show_methods():
    """ Zobrazí všehny metody všech entit """
    for node in gui_core._nodesGui:
        node.draw_methods = True
        for method in node.attributes:
            method.visible = True
        gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def hide_methods():
    """ Skryje všechny metody všech entit """
    for node in gui_core._nodesGui:
        node.draw_methods = False
        for method in node.attributes:
            method.visible = False
        gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def show_hidden_relations():
    """ Zobrazí všechny skryté vztahy na plátně """
    for node in gui_core._nodesGui:
        for relation in node.relationships:
            relation.visible = True
    gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def show_hidden_nodes():
    """ Zobrazí všchny skryté entity na plátně """
    for node in gui_core._nodesGui:
        node.visible = True
        for relation in node.relationships:
            relation.visible = True
    for module in gui_core._modulesGui:
        module.visible = True
    for package in gui_core._packagesGui:
        package.visible = True
    gui_core.draw_diagram(canvas=_canvas, isInitialDraw=False)

def show_about_screen():
    """ Vytvoří modální okno s textem manuálu k aplikaci """
    window = tk.Tk()
    window.title("Nápověda k aplikaci")
    window.geometry("530x850")

    content_frame = tk.Frame(window)
    content_frame.pack(fill="both", expand=True)

    canvas = tk.Canvas(content_frame)
    canvas.pack(side="left", fill="both", expand=True)

    scrollbar = tk.Scrollbar(content_frame, orient="vertical", command=canvas.yview)
    scrollbar.pack(side="right", fill="y")

    canvas.configure(yscrollcommand=scrollbar.set)
    canvas.configure(scrollregion=(0, 0, 510, 2240))


    inner_frame = tk.Frame(canvas)
    canvas.create_window((0, 0), window=inner_frame, anchor="nw")

    canvas.bind("<MouseWheel>",lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

    header_label = tk.Label(inner_frame, text="Nápověda", font=("Helvetica", 22, "bold"))
    header_label.pack(pady=(10, 0))
    create_subheader(inner_frame, "Ovládání aplikace")
    create_paragraph(inner_frame, "Ovládání", "Aplikace se primárně ovládá myší a to za využití levého tlačítka na vybrání možností a pravého tlačítka pro zobrazení kontextové nabídky daného elementu na plátně.")
    create_paragraph(inner_frame, "Posun po plátně", "uživatel se může po plátně posouvat za využití posuvníků na straně, nebo zmáčknutím prostředního tlačítka myši (kolečka).")
    create_subheader(inner_frame, "Kontextová nabídka aplikace")
    create_subheader2(inner_frame, "Nabídka Soubor:")
    create_paragraph(inner_frame, "Nový", "Smaže veškerý obsah z plátna a vytvoří nové, čisté plátno.")
    create_paragraph(inner_frame, "Načíst", "Načte uložený projekt ve formátu JSON, který je vytvořen pomocí funkce Uložit.")
    create_paragraph(inner_frame, "Uložit", "Uloží projekt do souboru ve formátu JSON.")
    create_paragraph(inner_frame, "Vytvořit UML souboru", "Vytvoří diagram ze zdrojového kódu konkrétního souboru s příponou .py.")
    create_paragraph(inner_frame, "Vytvořit UML složky", "Vytvoří diagram ze všech zdrojových kódů jazyka python dostupných ve vybrané složce a jejich podsložkách.")
    create_subheader2(inner_frame, "Nabídka Zobrazení:")
    create_paragraph(inner_frame, "Zobrazit atributy", "Zobrazí veškeré skryté atributy všech uzlů.")
    create_paragraph(inner_frame, "Zobrazit metody", "Zobrazí veškeré skryté metody všech uzlů.")
    create_paragraph(inner_frame, "Skrýt atributy", "Skryje veškeré atributy všech uzlů.")
    create_paragraph(inner_frame, "Skrýt metody", "Skryje veškeré metody všech uzlů.")
    create_paragraph(inner_frame, "Zobrazit skryté vztahy", "Zobrazí veškeré skryté vztahy uzlů na plátně.")
    create_paragraph(inner_frame, "Zobrazit skryté uzle", "Zobrazí veškeré skryté uzle na plátně.")
    create_subheader2(inner_frame, "Nabídka Nápovědy:")
    create_paragraph(inner_frame, "Nápověda k aplikaci", "Zobrazí nápovědu k funkcím aplikace")
    create_subheader(inner_frame, "Kontextová nabídka plátna")
    create_paragraph(inner_frame, "Nový uzel", "Zobrazí modální okno pro vytvoření nového uzle. Uživatel může zadat název uzle a vybrat jeho typ.")
    create_subheader(inner_frame, "Kontextová nabídka uzle")
    create_paragraph(inner_frame, "Detail", "Zobrazí modální okno s detailem uzle.")
    create_paragraph(inner_frame, "Upravit uzel", "Zobrazí modální okno pro úpravu uzle. Uživatel může změnit název uzlu a jeho typ.")
    create_paragraph(inner_frame, "Smazat uzel", "Smaže daný uzel z plátna a projektu. Taktéž odstraní jeho vztahy.")
    create_paragraph(inner_frame, "Skrýt uzel", "Skryje daný uzel na plátně. Uzel lze znovu zobrazit buď přes nabídku aplikace, nebo přes výpis uzlů modulu v kontextové nabídce daného modulu.")
    create_paragraph(inner_frame, "Skrýt atributy", "Skryje atributy daného uzlu. V případě, že má tento uzel již skryté atributy, tato nabídka se změní na zobrazení atributů.")
    create_paragraph(inner_frame, "Skrýt metody", "Skryje metody daného uzlu. V případě, že má tento uzel již skryté metody, tato nabídka se změní na zobrazení metod.")
    create_paragraph(inner_frame, "Vztahy uzle", "Zobrazí další menu s výpisem veškerých vztahů, které z tohot uzle vedou do uzle jiného. Kliknutím na daný vztah může uživatel jednoduše skrývat/zobrazovat vztahy uzle.")
    create_paragraph(inner_frame, "Uzle modulu", "Tato nabídka je dostupná jen pro uzle představující modul. Zobrazí seznam všech uzlů v modulu a uživatel může jednotlivé uzle skrývat/zobrazovat.")
    create_paragraph(inner_frame, "Spravovat uzel", "Tato nabídka zobrazí modální okno s přehledem všech attributů, metod, vztahů a pro modul i seznam uzlů v modulu. Uživatel zde může jednoduše zapínat/vypínat zobrazení daných objektů.")
    create_paragraph(inner_frame, "Nový vztah", "Po vybráním této možnosti začne dvoufázová tvorba nového vztahu. V případě, že uživatel započal tvorbu nového vztahu, pak se místo této nabízky u jiného uzle zobrazí možnost buď tvorbu ukončit, nebo vztah vytvořit.")
    create_subheader(inner_frame, "Kontextová nabídka vztahu")
    create_paragraph(inner_frame, "Změnit typ", "Představuje souhrn tří možností, kdy může uživatel jednoduše změnit typ vztahu.")
    create_paragraph(inner_frame, "Zobrazit jako přímku", "Zobrazí vybraný zalomený vztah jako přímku. Pokud je vztah již přímkou, uživatel může touto možností vztah opět zalomit.")
    create_paragraph(inner_frame, "Skrýt vztah", "Umožňuje skrýt daný vztah.")
    create_paragraph(inner_frame, "Skrýt typ vztahu", "Umožňuje uživateli skrýt typ vztahu.")
    create_paragraph(inner_frame, "Smazat vztah", "Smaže daný vztah z diagramu.")

def create_subheader(frame, title):
    # Vytvoří label pro subheader na plátně
    subheader_label = tk.Label(frame, text=title, font=("Helvetica", 15, "bold"))
    subheader_label.pack(pady=(15, 0), padx=8, )

def create_subheader2(frame, title):
    # Vytvoří label pro subheader2 na plátně
    subheader_label = tk.Label(frame, text=title, font=("Helvetica", 12, "bold"))
    subheader_label.pack(pady=(10, 0), padx=8, anchor="w")

def create_paragraph(frame, title, content):
    # Vytvoří label pro paragraf na plátně
    subheader_label = tk.Label(frame, text=title, font=("Helvetica", 10, "bold"))
    subheader_label.pack(pady=(8, 0), padx=8, anchor="w")
    paragraph_label = tk.Label(frame, text=content, font=("Helvetica", 10), wraplength=475, justify="left")
    paragraph_label.pack(pady=(0, 0), padx=8, anchor="w")

def on_app_close(window):
    # Vytvoří dialogova okna pro potvrzení, že chce uživatel skutečně zavřít aplikaci
    update_nodes()
    if not _nodesCore and not _modulesCore and not _packagesCore:
        if tk.messagebox.askokcancel("Zavřít aplikaci", "Opravdu chcete aplikaci ukončit?"):
            window.destroy()
    else:
        result = tk.messagebox.askquestion("Zavřít aplikaci", "Chcete uložit rozdělaný projekt před ukončením aplikace?")
        if result == "yes":
            save_project()
            window.destroy()
        else:
            window.destroy()

def run():
    """ Spustí aplikaci. """
    config = utils.getConfig()

    WINDOW_WIDTH = config.get('window-settings', 'window_width')
    WINDOW_HEIGHT = config.get('window-settings', 'window_height')
    global _canvas
    global _nodesCore
    global _modulesCore
    global _packagesCore
    global _cursor
    global _open_file_name

    window = gui.setup_window(WINDOW_WIDTH, WINDOW_HEIGHT)

    _canvas = gui.setup_canvas(window, WINDOW_WIDTH, WINDOW_HEIGHT)
    _cursor = "arrow"
    clearArraysCore()

    # dotaz pri uzavreni okna aplikace
    window.protocol("WM_DELETE_WINDOW", lambda win = window: on_app_close(window=win))

    # Založení hlavní nabídky.
    menu = gui.setup_menu(window)
    gui.add_command_to_menu(menu[0], "Nový", lambda win = window : new_project(win))
    gui.add_command_to_menu(menu[0], "Načíst", lambda win = window : load_project(win))
    gui.add_command_to_menu(menu[0], "Uložit", save_project)
    gui.add_command_to_menu(menu[0], "Vytvořit UML souboru",
                            lambda win = window : load_from_source_file(window=win))
    gui.add_command_to_menu(menu[0], "Vytvořit UML složky",
                            lambda win = window : load_from_source_directory(window = win))
    gui.add_command_to_menu(menu[1], "Zobrazit atributy",
                            show_attributes)
    gui.add_command_to_menu(menu[1], "Zobrazit metody",
                            show_methods)
    gui.add_command_to_menu(menu[1], "Skrýt atributy",
                            hide_attributes)
    gui.add_command_to_menu(menu[1], "Skrýt metody",
                            hide_methods)
    menu[1].add_separator()
    gui.add_command_to_menu(menu[1], "Zobrazit skryté vztahy",
                            show_hidden_relations)
    gui.add_command_to_menu(menu[1], "Zobrazit skryté uzle",
                            show_hidden_nodes)
    gui.add_command_to_menu(menu[2], "Nápověda k aplikaci",
                            show_about_screen)
    window.mainloop()  # Spuštění okna


if __name__ == '__main__':
    run()
