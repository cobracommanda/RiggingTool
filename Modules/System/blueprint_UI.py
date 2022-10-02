import maya.cmds as cmds
import System.utils as utils
reload(utils)

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

        # Create main column
        self.UIElements['top_level_column'] = cmds.columnLayout(adjustableColumn=True, columnAlign='center')

        tab_height = 500
        self.UIElements['tabs'] = cmds.tabLayout(height=tab_height, innerMarginWidth=5, innerMarginHeight=5)

        tab_width = cmds.tabLayout(self.UIElements['tabs'], q=True, width=True)
        self.scroll_width = tab_width - 40

        self.initialize_module_tab(tab_height, tab_width)

        cmds.tabLayout(self.UIElements['tabs'], edit=True, tabLabelIndex=([1, "Modules"]), width=window_width)
        cmds.showWindow(self.UIElements['window'])

    def initialize_module_tab(self, tab_h, tab_w):
        scroll_height = tab_h

        self.UIElements['module_column'] = cmds.columnLayout(adj=True, rs=3)
        self.UIElements['module_frame_layout'] = cmds.frameLayout(height=scroll_height, collapsable=False,
                                                                  borderVisible=False, labelVisible=False)

        self.UIElements['modulelist_scroll'] = cmds.scrollLayout(hst=0)
        self.UIElements['modulelist_column'] = cmds.columnLayout(columnWidth=self.scroll_width, adj=True, rs=2)

        cmds.separator()

        for module in utils.find_all_modules('Modules/Blueprint'):

            self.create_module_install_button(module)
            cmds.setParent(self.UIElements['modulelist_column'])
            cmds.separator()

        cmds.setParent(self.UIElements['module_column'])
        cmds.separator()

    def create_module_install_button(self, module):
        mod = __import__('Blueprint.' + module, {}, {}, [module])
        reload(mod)

        title = mod.TITLE
        description = mod.DESCRIPTION
        icon = mod.ICON


        # print title, icon, description
        button_size = 64
        row = cmds.rowLayout(numberOfColumns=2, columnWidth=([1, button_size]), adjustableColumn=2,
                             columnAttach=([1, 'both', 0], [2, 'both', 5]))

        self.UIElements['module_button_' + module] = cmds.symbolButton(width=button_size,
                                                                       height=button_size, image=icon)



        text_column = cmds.columnLayout(columnAlign='center')
        cmds.text(align='center', width=300, label=title)
        cmds.scrollField(text=description, editable=False, wordWrap=True, width=300, height=64)
        cmds.setParent(self.UIElements['module_column'])




