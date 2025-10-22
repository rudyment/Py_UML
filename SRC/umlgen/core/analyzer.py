"""
Modul definující analyzátor a pomocné třídy,
které představují uzly(třídy a moduly) daného stromu.
"""

import ast
import os, sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import core.gui_manager as gui
import umlgen.models.models_core as coreModels
import umlgen.utils.enums as enums


class Analyzer(ast.NodeVisitor):
    """Třída přetěžující implementaci analyzátoru z knihovny AST.
    Slouží k analýze AST stromu.
    Pro provedení analýzy a naplnění atributů této
    třídy se volá metoda visit().
    """

    def __init__(self, filename):
        self.nodes = []
        self.filename = filename
        self.module_node = ""
        self.module = ""

    def visit_Module(self, node):
        """Metoda je volána při návštěvě uzlu
        představujícího modul. Při návštěvě naplní atribut
        classes.
        """
    
        visited_module = coreModels.NodeCore(name=str(self.filename), nodetype = enums.NodeType.MODULE, module_name=str(self.filename))
        self.module_node = visited_module
        self.module = coreModels.ModuleCore(name=str(self.filename), package=None)
        self.nodes.append(visited_module)

        for m in node.body:
            if isinstance(m, ast.FunctionDef):
                visited_module.methods.append(coreModels.MethodCore(label=m.name))
            if isinstance(m, ast.Assign):
                if hasattr(m.targets[0], "id"):
                    visited_module.attributes.append(coreModels.AttributeCore(label=str(m.targets[0].id), public = not str(m.targets[0].id).startswith('__')))
        # Získáme potomky modulu
        child_nodes = ast.iter_child_nodes(node)
        # Naplníme uzly třídami
        self.nodes.extend(self.prepare_class_nodes(child_nodes = child_nodes, module_name= str(self.filename)))

    def prepare_class_nodes(self, child_nodes, module_name):
        """Projde všechny uzly a vytvoří objekty představující
        třídy, metody, atributy a vztahy. Tyto objekty jsou pak
        zapouzdřeny ve třídě Node a vloženy do atributu classes
        """
        classes = []
        for n in child_nodes:
            # Pokud je uzel třídou pokračujeme dál.
            if isinstance(n, ast.ClassDef):
                # Založíme instanci třídy Node a zapamatujeme si jí,
                # aby bylo možné dále jí naplnit dalšími atributy.
                nodeType = enums.NodeType.CLASS
                if "nterface" in n.name:
                    nodeType = enums.NodeType.PROTOCOL
                if "bstract" in n.name:
                    nodeType = enums.NodeType.ABSTRACT
                visited_class = coreModels.NodeCore(name = n.name, nodetype = nodeType, module_name = module_name)
                sub_classes = []
                # Cyklus prochází tělo třídy a vyhledává metody a atributy.
                for statement in n.body:
                    # Pokud ma sama trida dalsi interni tridy, musime je take vytvorit
                    if isinstance(statement, ast.ClassDef):
                        sub_class = coreModels.NodeCore(name = statement.name, nodetype = enums.NodeType.CLASS, module_name = module_name)
                        sub_class.relations.append(coreModels.NodeRelationCore(
                                    enums.RelationType.CONTAINMENT, 0.0, 0.0, visited_class, False))
                        for sub_body in statement.body:
                            if isinstance(sub_body, ast.Assign):
                                for name in sub_body.targets:
                                    sub_class.attributes.append(create_attribute(name.id))
                            if isinstance(sub_body, ast.FunctionDef):
                                sub_class.methods.append(create_method(sub_body.name))
                            if hasattr(sub_body, 'body'):
                                for value in sub_body.body:
                                    if isinstance(value, ast.Assign):
                                        if isinstance(value.targets[0], ast.Attribute):
                                            if len(value.targets) == 1 and isinstance(
                                                    value.targets[0].value, ast.Name):
                                                sub_class.attributes.append(create_attribute(value.targets[0].attr))
                        sub_classes.append(sub_class)

                    # Pridame tridni attributy
                    if isinstance(statement, ast.Assign):
                        for name in statement.targets:
                            visited_class.attributes.append(create_attribute(name.id))

                    if hasattr(statement, 'body'):
                        for value in statement.body:
                            if isinstance(value, ast.Assign):
                                if isinstance(value.targets[0], ast.Attribute):
                                    if len(value.targets) == 1 and isinstance(
                                            value.targets[0].value, ast.Name):
                                        visited_class.attributes.append(create_attribute(value.targets[0].attr))
                    # Přidání metody.
                    if isinstance(statement, ast.FunctionDef):
                        visited_class.methods.append(create_method(statement.name))

                child_nodes = ast.iter_child_nodes(n)
                # Cyklus projde potomky třídy a vytvoří
                # objekty představující vztah
                for cn in child_nodes:
                    if isinstance(cn, ast.ClassDef):
                        for parent in cn.bases:
                            for node in classes:
                                if parent.id == node.name:
                                    relation_type = enums.RelationType.GENERALIZATION
                                    if node.nodetype == enums.NodeType.PROTOCOL:
                                        relation_type = enums.RelationType.PROTOCOL
                                    if node.nodetype == enums.NodeType.ABSTRACT:
                                        relation_type = enums.RelationType.ASSOCIATION
                                    for sub_node in sub_classes:
                                        if sub_node.name == cn.name:
                                            if node.nodetype == enums.NodeType.PROTOCOL:
                                                sub_node.nodetype = enums.NodeType.PROTOCOL
                                            sub_node.relations.append(coreModels.NodeRelationCore(
                                                                        relation_type, 0.0, 0.0, node, False))

                    if isinstance(cn, ast.Name):
                        if cn.id == "ABC":
                            visited_class.nodetype = enums.NodeType.ABSTRACT
                        for cp in classes:
                            if cp.name == cn.id:
                                relation_type = enums.RelationType.GENERALIZATION
                                if cp.nodetype == enums.NodeType.PROTOCOL:
                                    relation_type = enums.RelationType.PROTOCOL
                                    visited_class.nodetype = enums.NodeType.PROTOCOL
                                if cp.nodetype == enums.NodeType.ABSTRACT:
                                    visited_class.nodetype = enums.NodeType.ABSTRACT
                                visited_class.relations.append(coreModels.NodeRelationCore(
                                    relation_type, 0.0, 0.0, cp, False))
                # Nakonec přidělíme třídě vztah s jejím modulem
                visited_class.relations.append(coreModels.NodeRelationCore(
                    enums.RelationType.COMPOSITION, 0.0, 0.0, self.module_node, False))
                classes.append(visited_class)
                for node in sub_classes:
                    classes.append(node)
        return classes


def build_ast_tree(source_file):
    """ Metoda zpracuje a zkompiluje zdrojový kód do AST node
    """
    tree = ast.parse(source_file)
    return tree

def create_attribute(label):
    """ Metoda vytvori novy objekt typu atributu a vrati jej
    """
    public = True
    newLabel = str(label)

    if newLabel.startswith('__'):
        public = False
        newLabel = newLabel[2:]

    return coreModels.AttributeCore(label=newLabel, public = public)

def create_method(label):
    """ Metoda vytvori novy objekt typu metody a vrati jej
    """
    public = True
    newLabel = str(label)

    return coreModels.MethodCore(label=newLabel, public = public)
