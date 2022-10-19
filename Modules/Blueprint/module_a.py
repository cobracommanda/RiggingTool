import os
import maya.cmds as cmds
import System.utils as utils

CLASS_NAME = "ModuleA"
TITLE = 'Module A'
DESCRIPTION = 'Test description for module A'
ICON = os.environ['RIGGING_TOOL_ROOT'] + '/Icons/_hand.xpm'


class ModuleA():
    def __init__(self, user_specified_name):
        self.module_name = CLASS_NAME
        self.user_specified_name = user_specified_name
        self.module_namespace = self.module_name + '__' + self.user_specified_name
        self.container_name = self.module_namespace + ":module_container"
        self.joint_info = [["root_joint", [0.0, 0.0, 0.0]], ["end_joint", [4.0, 0.0, 0.0]]]

    def install(self):
        cmds.namespace(setNamespace=":")
        cmds.namespace(add=self.module_namespace)

        self.joints_grp = cmds.group(empty=True, name=self.module_namespace + ":joints_grp")
        self.module_grp = cmds.group(self.joints_grp, name=self.module_namespace + ":module_grp")
        cmds.container(name=self.container_name, addNode=self.module_grp, ihb=True)

        cmds.select(clear=True)

        index = 0
        joints = []

        for joint in self.joint_info:
            joint_name = joint[0]
            joint_pos = joint[1]

            parent_joint = ""
            if index > 0:
                parent_joint = self.module_namespace + ":" + self.joint_info[index-1][0]
                cmds.select(parent_joint, replace=True)

            joint_name_full = cmds.joint(n=self.module_namespace + ":" + joint_name, p=joint_pos)
            joints.append(joint_name_full)
            utils.add_node_to_container(self.container_name, joint_name_full)
            cmds.container(self.container_name, edit=True, addNode=joint_name_full)

            cmds.container(self.container_name, edit=True,
                           publishAndBind=[joint_name_full + ".rotate", joint_name + "_R"])

            cmds.container(self.container_name, edit=True,
                           publishAndBind=[joint_name_full + ".rotateOrder", joint_name + "_rotateOrder"])

            if index > 0:
                cmds.joint(parent_joint, edit=True, orientJoint='xyz', sao="yup")

            index += 1

        cmds.parent(joints[0], self.joints_grp, absolute=True)

        translation_controls = []
        for joint in joints:
            translation_controls.append(self.create_translation_control_at_joint(joint))
        root_joint_point_constraint = cmds.pointConstraint(translation_controls[0], joints[0],
                                                           maintainOffset=False, name=joints[0]+"_pointConstraint")
        utils.add_node_to_container(self.container_name, root_joint_point_constraint)

        #Setup stretchy joint segments
        for index in range(len(joints) - 1):
            self.setup_stretchy_joint_segment(joints[index], joints[index + 1])

        utils.force_scene_update()

        cmds.lockNode(self.container_name, lock=True, lockUnpublished=True)

    def create_translation_control_at_joint(self, joint):
        pos_control_file = os.environ["RIGGING_TOOL_ROOT"] + "/ControlObjects/Blueprint/translation_control.ma"
        cmds.file(pos_control_file, i=True)
        container = cmds.rename("translation_control_container", joint + "_translation_control_container")
        utils.add_node_to_container(self.container_name, container)

        for node in cmds.container(container, q=True, nodeList=True):
            cmds.rename(node, joint + "_" + node, ignoreShape=True)

        control = joint + "_translation_control"

        joint_pos = cmds.xform(joint, q=True, worldSpace=True, translation=True)
        cmds.xform(control, worldSpace=True, absolute=True, translation=joint_pos)
        nice_name = utils.strip_leading_namespace(joint)[1]
        attr_name = nice_name + "_T"

        cmds.container(container, edit=True, publishAndBind=[control + ".translate", attr_name])
        cmds.container(self.container_name, edit=True, publishAndBind=[container + "." + attr_name, attr_name])

        return control

    def get_translation_control(self, joint_name):
        return joint_name + "_translation_control"

    def setup_stretchy_joint_segment(self, parent_joint, child_joint):
        parent_translation_control = self.get_translation_control(parent_joint)
        child_translation_control = self.get_translation_control(child_joint)

        pole_vector_locator = cmds.spaceLocator(n=parent_translation_control+"_poleVectorLocator")[0]
        pole_vector_locator_grp =  cmds.group(pole_vector_locator, n=pole_vector_locator+"_parentConstrainGrp")
        cmds.parent(pole_vector_locator_grp, self.module_grp, absolute=True)
        parent_constraint = cmds.parentConstraint(parent_translation_control, pole_vector_locator_grp,
                                                  maintainOffset=False)[0]
        cmds.setAttr(pole_vector_locator+".visibility", 0)

        cmds.setAttr(pole_vector_locator+".ty", -0.5)

        ik_nodes = utils.basic_stretchy_IK(parent_joint, child_joint,
                                           container=self.container_name, lock_mininum_length=False,
                                           pole_vector_object=pole_vector_locator, scale_correction_attribute=None)

        ik_handle = ik_nodes["ik_handle"]
        root_locator = ik_nodes["root_locator"]
        end_locator = ik_nodes["end_locator"]

        child_point_constraint = cmds.pointConstraint(child_translation_control, end_locator, maintainOffset=False,
                                                      n=end_locator+"_pointConstraint")[0]

        utils.add_node_to_container(self.container_name, [pole_vector_locator_grp, parent_constraint,
                                                          child_point_constraint], ihb=True)

        for node in [ik_handle, root_locator, end_locator]:
            cmds.parent(node, self.joints_grp, absolute=True)
            cmds.setAttr(node+".visibility", 0)








