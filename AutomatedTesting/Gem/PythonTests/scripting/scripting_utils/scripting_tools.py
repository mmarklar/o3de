"""
Copyright (c) Contributors to the Open 3D Engine Project.
For complete copyright and license terms please see the LICENSE at the root of this distribution.

SPDX-License-Identifier: Apache-2.0 OR MIT
"""

from editor_python_test_tools.utils import TestHelper as helper
from PySide2 import QtWidgets, QtTest, QtCore
from PySide2.QtCore import Qt
from editor_python_test_tools.utils import Report
import editor_python_test_tools.pyside_utils as pyside_utils
import editor_python_test_tools.hydra_editor_utils as hydra
import azlmbr.editor as editor
import azlmbr.math as math
import azlmbr.bus as bus
import azlmbr.legacy.general as general
import azlmbr.scriptcanvas as scriptcanvas
from scripting_utils.scripting_constants import (SCRIPT_CANVAS_UI, ASSET_EDITOR_UI, NODE_PALETTE_UI, NODE_PALETTE_QT,
                                                 TREE_VIEW_QT, SEARCH_FRAME_QT, SEARCH_FILTER_QT, SAVE_STRING, NAME_STRING,
                                                 SAVE_ASSET_AS, WAIT_TIME_3, NODE_INSPECTOR_TITLE_KEY, WAIT_FRAMES,
                                                 VARIABLE_MANAGER_QT, NODE_INSPECTOR_QT, NODE_INSPECTOR_UI, SCRIPT_EVENT_UI,
                                                 VARIABLE_PALETTE_QT, ADD_BUTTON_QT, VARIABLE_TYPES, EVENTS_QT, DEFAULT_SCRIPT_EVENT,
                                                 SCRIPT_EVENT_FILE_PATH, PARAMETERS_QT, VARIABLE_MANAGER_QT, NODE_INSPECTOR_QT,
                                                 NODE_INSPECTOR_UI, VARIABLE_PALETTE_QT, ADD_BUTTON_QT, VARIABLE_TYPES,
                                                 SCRIPT_CANVAS_COMPONENT_PROPERTY_PATH)

class Tests():
    new_event_created = ("New Script Event created", "Failed to create a new event")
    child_event_created = ("Child Event created", "Failed to create Child Event")
    parameter_created = ("Successfully added parameter", "Failed to add parameter")
    parameter_removed = ("Successfully removed parameter", "Failed to remove parameter")

def click_menu_option(window, option_text):
    """
    function for clicking an option from a Qt menu object. This function bypasses menu groups or categories. for example,
    if you want to click the Open option from the "File" category provide "Open" as your menu text instead of "File" then "Open".

    param window: the qt window object where the menu option is located
    param option_text: the label string used in the menu option that you want to click

    returns none
    """
    action = pyside_utils.find_child_by_pattern(window, {"text": option_text, "type": QtWidgets.QAction})
    action.trigger()

def save_script_event_file(self, file_path):
    """
    function for saving a script event file with a user defined file path. Requires asset editor qt object to be initialized
    and any required fields in the asset editor to be filled in before asset can be saved.

    param self: the script object calling this function
    param file_path: full path to the file as a string

    returns: true if the Save action is successful and the * character disappears from the asset editor label
    """
    editor.AssetEditorWidgetRequestsBus(bus.Broadcast, SAVE_ASSET_AS, file_path)
    action = pyside_utils.find_child_by_pattern(self.asset_editor_menu_bar, {"type": QtWidgets.QAction, "iconText": SAVE_STRING})
    action.trigger()
    # wait till file is saved, to validate that check the text of QLabel at the bottom of the AssetEditor,
    # if there are no unsaved changes we will not have any * in the text
    label = self.asset_editor.findChild(QtWidgets.QLabel, "textEdit")
    return helper.wait_for_condition(lambda: "*" not in label.text(), WAIT_TIME_3)


def initialize_editor_object(self):
    self.editor_main_window = pyside_utils.get_editor_main_window()


def initialize_sc_editor_objects(self):
    self.sc_editor = self.editor_main_window.findChild(QtWidgets.QDockWidget, SCRIPT_CANVAS_UI)
    self.sc_editor_main_window = self.sc_editor.findChild(QtWidgets.QMainWindow)


def initialize_variable_manager_object(self):
    self.variable_manager = self.sc_editor.findChild(QtWidgets.QDockWidget, VARIABLE_MANAGER_QT)
    if not self.variable_manager.isVisible():
        self.click_menu_option(self.sc_editor, VARIABLE_MANAGER_QT)


def initialize_asset_editor_object(self):
    """
    function for initializing qt objects needed for testing around asset editor

    param self: the script object calling this function.

    returns: None
    """
    self.asset_editor = self.editor_main_window.findChild(QtWidgets.QDockWidget, ASSET_EDITOR_UI)
    self.asset_editor_widget = self.asset_editor.findChild(QtWidgets.QWidget, "AssetEditorWindowClass")
    self.asset_editor_row_container = self.asset_editor_widget.findChild(QtWidgets.QWidget, "ContainerForRows")
    self.asset_editor_menu_bar = self.asset_editor_widget.findChild(QtWidgets.QMenuBar)


def initialize_node_palette_object(self):
    """
    function for initializing qt objects needed for testing around the script canvas editor

    param self: the script object calling this function

    returns: None
    """
    self.node_palette = self.sc_editor.findChild(QtWidgets.QDockWidget, NODE_PALETTE_QT)
    self.node_tree_view = self.node_palette.findChild(QtWidgets.QTreeView, TREE_VIEW_QT)
    self.node_tree_search_frame = self.node_palette.findChild(QtWidgets.QFrame, SEARCH_FRAME_QT)
    self.node_tree_search_box = self.node_tree_search_frame.findChild(QtWidgets.QLineEdit, SEARCH_FILTER_QT)


def expand_qt_container_rows(self, object_name):
    """
    function used for expanding qt container rows with expandable children

    param self: The script object calling this function
    param object_name: qt object name as a string

    returns: none
    """
    children = self.asset_editor_row_container.findChildren(QtWidgets.QFrame, object_name)
    for child in children:
        check_box = child.findChild(QtWidgets.QCheckBox)
        if check_box and not check_box.isChecked():
            QtTest.QTest.mouseClick(check_box, QtCore.Qt.LeftButton, QtCore.Qt.NoModifier)


def open_node_palette(self):
    """
    function for checking if node palette is on and if not turn it on

    param self: the script calling this function

    returns none
    """
    if self.sc_editor.findChild(QtWidgets.QDockWidget, NODE_PALETTE_QT) is None:
        action = pyside_utils.find_child_by_pattern(self.sc_editor, {"text": NODE_PALETTE_UI, "type": QtWidgets.QAction})
        action.trigger()


def open_script_canvas():
    """
    function for opening the script canvas UI

    returns true / false result of helper function's attempt
    """
    general.open_pane(SCRIPT_CANVAS_UI)
    result = helper.wait_for_condition(lambda: general.is_pane_visible(SCRIPT_CANVAS_UI), WAIT_TIME_3)
    return result

def open_asset_editor():
    """
    function for opening the asset editor UI

    returns true/false result of helper function's attempt
    """
    general.open_pane(ASSET_EDITOR_UI)
    result = helper.wait_for_condition(lambda: general.is_pane_visible(ASSET_EDITOR_UI), WAIT_TIME_3)
    return result

def canvas_node_palette_search(self, node_name, number_of_retries):
    """
    function for searching the script canvas node palette for user defined nodes. function takes a number of retries as
    an argument in case editor/script canvas lags during test.

    param self: The script calling this function
    param node_name: the name of the node being searched for
    param number_of_retries: the number of times to search (click on the search button)

    returns: boolean value of the search attempt
    """
    self.node_tree_search_box.setText(node_name)
    helper.wait_for_condition(lambda: self.node_tree_search_box.text() == node_name, WAIT_TIME_3)
    # Try clicking ENTER in search box multiple times
    found_node = False
    for _ in range(number_of_retries):
        QtTest.QTest.keyClick(self.node_tree_search_box, QtCore.Qt.Key_Enter, QtCore.Qt.NoModifier)
        found_node = helper.wait_for_condition(
            lambda: pyside_utils.find_child_by_pattern(self.node_tree_view, {"text": node_name}) is not None, WAIT_TIME_3)
        if found_node is True:
            break
    return found_node

def get_node_palette_node_tree_qt_object (self):
    """
    function for retrieving the tree view qt object for the node palette

    params self: the script calling this function

    returns: a tree view qt object
    """
    node_palette_widget = self.sc_editor.findChild(QtWidgets.QDockWidget, NODE_PALETTE_QT)
    node_palette_node_tree = node_palette_widget.findChild(QtWidgets.QTreeView, TREE_VIEW_QT)
    return node_palette_node_tree


def get_node_palette_category_qt_object(self, category_name):
    """
    function for retrieving the qt object for a node palette category

    param self: the script calling this function
    param category_name: string for the category label you are searching node palette for

    returns: the qt object for the node palette category
    """
    node_palette_node_tree = get_node_palette_node_tree_qt_object(self)
    node_palette_category = pyside_utils.find_child_by_pattern(node_palette_node_tree, category_name)
    return node_palette_category

def get_node_inspector_node_titles(self, sc_graph_node_inspector, sc_graph):
    """
    function for retrieving the node inspector's node titles from all nodes in a script canvas graph. function takes
    a script canvas graph and node inspector qt widget.

    param self: the script calling this function
    param sc_graph_node_inspector: the sc graph node inspector qt widget
    param sc_graph: the sc graph qt widget

    returns: a list of node titles (i.e Print - Utilities/Debug). If there are duplicates of a node then the title
    will include ( X Selected) in the string.
    """
    node_inspector_scroll_area = sc_graph_node_inspector.findChild(QtWidgets.QScrollArea, "")
    # perform ctrl+a keystroke to highlight all nodes on the graph
    QtTest.QTest.keyClick(sc_graph, "a", Qt.ControlModifier, WAIT_FRAMES)
    node_inspector_backgrounds = node_inspector_scroll_area.findChildren(QtWidgets.QFrame, "Background")
    titles = []
    for background in node_inspector_backgrounds:
        background_title = background.findChild(QtWidgets.QLabel, NODE_INSPECTOR_TITLE_KEY)
        if background_title.text() is not "":
            titles.append(background_title.text())
    return titles


def get_main_sc_window_qt_object():
    """
    function for getting the sc main window qt object.

    params: none

    returns: a qt widget main window object
    """
    editor_window = pyside_utils.get_editor_main_window()
    sc_editor = editor_window.findChild(QtWidgets.QDockWidget, SCRIPT_CANVAS_UI)
    return sc_editor.findChild(QtWidgets.QMainWindow)


def create_new_sc_graph(sc_editor_main_window):
    """
    function for opening a new script canvas graph file. uses the sc editor window to trigger a new file action

    param self: the script calling this function
    param sc_editor_main_window: the qt object for the main sc_editor window

    returns: none
    """
    create_new_graph_action = pyside_utils.find_child_by_pattern(
        sc_editor_main_window, {"objectName": "action_New_Script", "type": QtWidgets.QAction}
    )
    create_new_graph_action.trigger()


def create_new_variable(self, new_variable_type):
    """
    function for creating a new SC variable through variable manager

    param self: the script objecting calling this function
    param variable_type: The variable data type to create as a string. i.e "Boolean"
    returns: none
    """

    if type(new_variable_type) is not str:
        Report.critical_result(["Invalid variable type provided", ""], False)

    valid_type = False
    for this_type in VARIABLE_TYPES:
        if new_variable_type == this_type:
            valid_type = True

    if not valid_type:
        Report.critical_result(["Invalid variable type provided", ""], False)

    add_new_variable_button = self.variable_manager.findChild(QtWidgets.QPushButton, ADD_BUTTON_QT)
    add_new_variable_button.click()  # Click on Create Variable button
    helper.wait_for_condition((
        lambda: self.variable_manager.findChild(QtWidgets.QTableView, VARIABLE_PALETTE_QT) is not None), WAIT_TIME_3)
    # Select variable type
    table_view = self.variable_manager.findChild(QtWidgets.QTableView, VARIABLE_PALETTE_QT)
    model_index = pyside_utils.find_child_by_pattern(table_view, new_variable_type)
    # Click on it to create variable
    pyside_utils.item_view_index_mouse_click(table_view, model_index)


def get_sc_editor_node_inspector(sc_editor):
    """
    function for toggling the node inspector if it's not already turned on and returning the qt widget object

    param sc_editor: the script canvas editor qt object

    returns: the node inspector qt widget object

    """
    node_inspector_widget = sc_editor.findChild(QtWidgets.QDockWidget, NODE_INSPECTOR_QT)
    if sc_editor.findChild(QtWidgets.QDockWidget, NODE_INSPECTOR_QT) is None:
        action = pyside_utils.find_child_by_pattern(sc_editor, {"text": NODE_INSPECTOR_UI, "type": QtWidgets.QAction})
        action.trigger()

    return node_inspector_widget


def create_script_event(self):
    """
    Function for creating a script event from the editor's asset editor.

    param self: the script calling this function

    returns None
    """
    action = pyside_utils.find_child_by_pattern(self.asset_editor_menu_bar, {"type": QtWidgets.QAction, "text": SCRIPT_EVENT_UI})
    action.trigger()
    result = helper.wait_for_condition(
        lambda: self.asset_editor_row_container.findChild(QtWidgets.QFrame, EVENTS_QT) is not None, WAIT_TIME_3
    )
    Report.result(Tests.new_event_created, result)

    # Add new child event
    add_event = self.asset_editor_row_container.findChild(QtWidgets.QFrame, EVENTS_QT).findChild(QtWidgets.QToolButton, "")
    add_event.click()
    result = helper.wait_for_condition(
        lambda: self.asset_editor_widget.findChild(QtWidgets.QFrame, DEFAULT_SCRIPT_EVENT) is not None, WAIT_TIME_3
    )
    Report.result(Tests.child_event_created, result)

def create_script_event_parameter(self):
    add_param = self.asset_editor_row_container.findChild(QtWidgets.QFrame, "Parameters").findChild(QtWidgets.QToolButton, "")
    add_param.click()
    result = helper.wait_for_condition(
        lambda: self.asset_editor_widget.findChild(QtWidgets.QFrame, "[0]") is not None, WAIT_TIME_3
    )
    Report.result(Tests.parameter_created, result)

def remove_script_event_parameter(self):
    remove_param = self.asset_editor_row_container.findChild(QtWidgets.QFrame, "[0]").findChild(QtWidgets.QToolButton, "")
    remove_param.click()
    result = helper.wait_for_condition(
        lambda: self.asset_editor_widget.findChild(QtWidgets.QFrame, "[0]") is None, WAIT_TIME_3
    )
    Report.result(Tests.parameter_removed, result)

def add_empty_parameter_to_script_event(self, number_of_parameters):
    """
    Function for adding a new blank parameter to a script event

    param self: the script calling this function
    param number_of_parameters: the number of empty parameters to add

    returns none
    """
    helper.wait_for_condition(
        lambda: self.asset_editor_row_container.findChild(QtWidgets.QFrame, PARAMETERS_QT) is not None, WAIT_TIME_3)
    parameters = self.asset_editor_row_container.findChild(QtWidgets.QFrame, PARAMETERS_QT)
    add_parameter = parameters.findChild(QtWidgets.QToolButton, "")

    for _ in range(number_of_parameters):
        add_parameter.click()

def get_script_event_parameter_name_text(self):
    """
    function for retrieving the name field of script event parameters

    param self: the script calling this function

    returns a container with all the parameters' editable name fields
    """
    parameter_names = self.asset_editor_row_container.findChildren(QtWidgets.QFrame, NAME_STRING)
    name_fields = []
    for parameter_name in parameter_names:
        name_fields.append(parameter_name.findChild(QtWidgets.QLineEdit))

    return name_fields

def get_script_event_parameter_type_combobox(self):
    """
    function for retrieving the type field of script event parameters

    param self: the script calling this function

    returns a container with all the parameters' editable type combo boxes
    """
    parameter_types = self.asset_editor_row_container.findChildren(QtWidgets.QFrame, "Type")
    type_combo_boxes =[]
    for parameter_type in parameter_types:
        type_combo_boxes.append(parameter_type.findChild(QtWidgets.QComboBox))

    return type_combo_boxes


def located_expected_tracer_lines(self, section_tracer, lines):
    """
    function for parsing game mode's console output for expected test lines. requires section_tracer. duplicates lines 
    and error lines are not handled by this function
    
    param self: The script calling this function
    param section_tracer: python editor tracer object
    param lines: list of expected lines
    
    
    returns true if all the expected lines were detected in the parsed output
    """
    found_lines = [printInfo.message.strip() for printInfo in section_tracer.prints]

    expected_lines = len(lines)
    matching_lines = 0

    for line in lines:
        for found_line in found_lines:
            if line == found_line:
                print("found line: " + found_line)
                matching_lines += 1

    return matching_lines >= expected_lines

def create_entity_with_sc_component_asset(entity_name, source_file, position = math.Vector3(512.0, 512.0, 32.0)):
    """
    function for creating a new entity in the scene w/ a script canvas component. Function also adds as
    script canvas file to the script canvas component's source file property.

    param entity_name: the name you want to assign the entity
    param source_file: the path to  script canvas file to be added to the script canvas component
    param position: the translation property of the new entity's transform

    returns: the entity created by this function
    """
    sourcehandle = scriptcanvas.SourceHandleFromPath(source_file)

    entity = hydra.Entity(entity_name)
    entity.create_entity(position, ["Script Canvas"])

    script_canvas_component = entity.components[0]
    hydra.set_component_property_value(script_canvas_component, SCRIPT_CANVAS_COMPONENT_PROPERTY_PATH, sourcehandle)

    return entity

def create_entity_with_multiple_sc_component_asset(entity_name, source_files, position = math.Vector3(512.0, 512.0, 32.0)):
    """
    function for creating a new entity with multiple script canvas components and adding a source file to each.

    param entity_name: the name you want to assign the entity
    param source_files: a list of source files you want added to the script canvas components
    param position: the translation property of the new entity's transform

    returns: the entity created by this function
    """

    number_of_files = len(source_files)

    components_array =[]
    for num in range(number_of_files):
        components_array.append("Script Canvas")

    entity = hydra.Entity(entity_name)
    entity.create_entity(position, components_array)

    for num in range(number_of_files):
        script_canvas_component = entity.components[num]
        sourcehandle = scriptcanvas.SourceHandleFromPath(source_files[num])
        hydra.set_component_property_value(script_canvas_component, SCRIPT_CANVAS_COMPONENT_PROPERTY_PATH, sourcehandle)

    return entity

def change_entity_sc_asset(entity, source_file, component_index = 0):
    """
    function for changing the source file component property value of an entity. Function assumes that there is a SC
    component somewhere in the list of components

    param entity: The entity with the SC component you want to update
    param source_file: The file you want to assign to the script canvas component property
    param component_index: the index of the sc component you want to update.

    returns true if the function was able to asign the source file ot the component
    """

    source_handle = scriptcanvas.SourceHandleFromPath(source_file)
    script_canvas_component = entity.components[component_index]
    hydra.set_component_property_value(script_canvas_component, SCRIPT_CANVAS_COMPONENT_PROPERTY_PATH, source_handle)
    script_file = hydra.get_component_property_value(script_canvas_component, SCRIPT_CANVAS_COMPONENT_PROPERTY_PATH)
    result = helper.wait_for_condition(lambda: script_file is not None, WAIT_TIME_3)

    return result

