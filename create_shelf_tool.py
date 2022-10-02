import os

try:
    riggingToolRoot = os.environ['RIGGING_TOOL_ROOT']
except:
    print 'RIGGING_TOOL_ROOT environment variable not correctly configured'

else:
    import sys

    print riggingToolRoot
    path = riggingToolRoot + '/Modules'

    if not path in sys.path:
        sys.path.append(path)
    import System.blueprint_UI as blueprint_UI

    reload(blueprint_UI)

    UI = blueprint_UI.Blueprint_UI()