import maya.cmds as cmds

def find_all_modules(relative_directory):
    all_py_files = find_all_files(relative_directory, '.py')
    return_modules = []

    for file in all_py_files:
        if file != '__init__':
            return_modules.append(file)

    return return_modules


def find_all_files(relative_directory, file_extension):
    import os
    file_directory = os.environ['RIGGING_TOOL_ROOT'] + '/' + relative_directory + '/'
    all_files = os.listdir(file_directory)

    return_files = []

    for py_file in all_files:
        split_string = str(py_file).rpartition(file_extension)
        if not split_string[1] == '' and split_string[2] == '':
            return_files.append(split_string[0])


    return return_files


def find_highest_trailing_number(names, basename):
    import re

    highest_value = 0

    for n in names:
        if n.find(basename) == 0:
            suffix = n.partition(basename)[2]
            if re.match("^[0-9]*$", suffix):
                numerical_element = int(suffix)

                if numerical_element > highest_value:
                    highest_value = numerical_element

    return  highest_value


def strip_leading_namespace(node_name):
    if node_name.find(":") == -1:
        return None

    split_string = str(node_name).partition(":")
    return [split_string[0], split_string[2]]


def basic_stretchy_IK(root_joint, end_joint, container=None, lock_mininum_length=True, pole_vector_object=None,
                      scale_correction_attribute=None):
    contained_nodes = []
    #Create RP IK on joint chain
    ik_nodes = cmds.ikHandle(sj=root_joint, ee=end_joint, sol='ikRPsolver', n=root_joint+"_ikHandle")
    ik_nodes[1] = cmds.rename(ik_nodes[1], root_joint+"_ikEffector")
    ik_effector = ik_nodes[1]
    ik_handle = ik_nodes[0]

    cmds.setAttr(ik_handle+".visibility", 0)
    contained_nodes.extend(ik_nodes)

    #Create pole vector locator
    if pole_vector_object == None:
        pole_vector_object = cmds.spaceLocator(n=ik_handle+"_poleVectorLocator")[0]
        contained_nodes.append(pole_vector_object)

        cmds.xform(pole_vector_object, worldSpace=True, absolute=True,
                   translation=cmds.xform(root_joint, q=True, worldSpace=True, translation=True))

        cmds.xform(pole_vector_object, worldSpace=True, relative=True, translation=[0.0, 1.0, 0.0])

        cmds.setAttr(pole_vector_object+".visibility", 0)
    pole_vector_constraint = cmds.poleVectorConstraint(pole_vector_object, ik_handle)[0]
    contained_nodes.append(pole_vector_constraint)

    #Create root and end locators
    root_locator = cmds.spaceLocator(n=root_joint+"_rootPosLocator")[0]
    root_locator_point_constraint = cmds.pointConstraint(root_joint, root_locator,
                                                         maintainOffset=False, n=root_locator+"_pointConstraint")[0]


    end_locator = cmds.spaceLocator(n=end_joint+"_endPosLocator")[0]
    cmds.xform(end_locator, worldSpace=True, absolute=True,
               translation=cmds.xform(ik_handle, q=True, worldSpace=True, translation=True))

    ik_handle_point_constraint = cmds.pointConstraint(end_locator, ik_handle,
                                                     maintainOffset=False, n=ik_handle+"_pointConstraint")[0]

    contained_nodes.extend([root_locator, end_locator, root_locator_point_constraint, ik_handle_point_constraint])
    cmds.setAttr(root_locator+".visibility", 0)
    cmds.setAttr(end_locator+".visibility", 0)

    if container != None:
        cmds.container(container, edit=True, addNode=contained_nodes, ihb=True)

    return_dict = {}
    return_dict['ik_handle'] = ik_handle
    return_dict['ik_effector'] = ik_effector
    return_dict['root_locator'] = root_locator
    return_dict['end_locator'] = end_locator
    return_dict['pole_vector_object'] = pole_vector_object
    return_dict['ik_handle_point_constraint'] = ik_handle_point_constraint
    return_dict['root_locator_point_constraint'] = root_locator_point_constraint

    return return_dict

def force_scene_update():
    cmds.setToolTo("moveSuperContext")
    nodes = cmds.ls()

    for node in nodes:
        cmds.select(node, replace=True)

    cmds.select(clear=True)
    cmds.setToolTo("selectSuperContext")









