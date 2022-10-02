import maya.cmds as cmds


class Blueprint_UI:
    def __init__(self):
        # Store UI elements in a dictionary
        self.UIElements = {}

        if cmds.window('blueprint_UI_window', exists=True):
            cmds.deleteUI('blueprint_UI_window')

        window_width = 400
        window_height = 598

        self.UIElements['window'] = cmds.window('blueprint_UI_window', width=window_width, height=window_height,
                                                title='Blueprint Module UI', sizeable=False)

        cmds.showWindow(self.UIElements['window'])


