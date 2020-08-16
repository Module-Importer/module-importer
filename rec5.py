# -*- coding: utf-8 -*-
"""
**************************
* Module Importer 5      *
* Copyright (c) 2020 ZHR *
* All Rights Reserved.   *
* Author: Zhang Haoran   *
* Date: 2020/7/25        *
* Version: %s            *
* Python version: 3.8    *
**************************
"""

# To make the interface of this product friendly, I've tried so hard.

# definition of __version__ variable
__version__ = '5.2.0'

# imports
from wx.stc import *
from wx.lib.agw.aui import *
import builtins
import keyword
import wx
import sys
import win32api
import runpy
import traceback

# import C pickle
try:
    import cPickle as pickle  # python 2
except ImportError:
    import _pickle as pickle  # python 3

# variables with simple values
# IDs
main = sys.modules['__main__']
IDs = [
    'ID_VIEW_ATTR',
    'ID_GO_BACK',
    'ID_EVALUATE',
    'ID_IMPORT_FILE',
    'ID_IMPORT_CODE',
    'ID_SHOW_TOOLBAR',
    'ID_SHOW_SEARCH',
    'ID_FIX_DIVIDING',
    'ID_CALL',
    'ID_SET_GLOBAL',
    'ID_SET_CURRENT_AS',
    'ID_SET_SELECTED_AS',
    'ID_DELETE',
    'ID_VIEW_GLOBALS',
    'ID_SAVE_CURRENT',
    'ID_SAVE_SELECTED'
]
for i in IDs:
    setattr(main, i, wx.NewIdRef())
del main  # clear the namespace


# ID_VIEW_ATTR = wx.NewIdRef()  # View
# ID_GO_BACK = wx.NewIdRef()  # Go Back
# ID_EVALUATE = wx.NewIdRef()  # Evaluate...
# ID_IMPORT_FILE = wx.NewIdRef()  # Import.../Python File
# ID_IMPORT_CODE = wx.NewIdRef()  # Import.../Code
# ID_SHOW_TOOLBAR = wx.NewIdRef()  # Show/Tool Bar
# ID_SHOW_SEARCH = wx.NewIdRef()  # Show/Search
# ID_FIX_DIVIDING = wx.NewIdRef()  # Show/Fix Dividing
# ID_CALL = wx.NewIdRef()  # Call...
# ID_SET_GLOBAL = wx.NewIdRef()  # Variables/Set Value As...
# ID_SET_CURRENT_AS = wx.NewIdRef()  # Variables/Set Current Value As...
# ID_SET_SELECTED_AS = wx.NewIdRef()  # Variables/Set Selected Value As...
# ID_DELETE = wx.NewIdRef()  # Variables/Delete Value...
# ID_VIEW_GLOBALS = wx.NewIdRef()  # View Namespaces
# ID_SAVE_CURRENT = wx.NewIdRef()
# ID_SAVE_SELECTED = wx.NewIdRef()


# functions
def load(file):
    """Load a pickle file."""
    with open(file, 'rb') as f:
        return pickle.load(f)


def save(v, file):
    """Save as a pickle file."""
    with open(file, 'wb') as f:
        pickle.dump(v, f, True)


def create_pane_info(*noparam, **info):
    """Create an AuiPaneInfo object by using the information."""
    pinfo = AuiPaneInfo()
    for fn in noparam:
        pinfo = getattr(pinfo, fn)()
    for fn, param in info.items():
        pinfo = getattr(pinfo, fn)(param)
    return pinfo


# classes
# Make a dictionary wrapper that can wrap a dictionary as a common object.
class DictWrapper:
    """This can wrap a dictionary into a common object. The wrapped object is `self`."""

    def __init__(self, **kws):
        for kw in kws:
            try:
                setattr(self, kw, kws[kw])
            except AttributeError:
                pass


class ErrorHandler:
    """An error handler is used to check if a method has an error."""

    def __init__(self, handler):
        self.handler = handler
        if isinstance(handler.__doc__, str):
            self.ft = '@STYLE: FT' in handler.__doc__
        else:
            self.ft = False

    def __call__(self, *args, **kwargs):
        try:
            self.handler(*args, **kwargs)
        except BaseException as e:
            if self.ft:
                tr = traceback.format_exception(*sys.exc_info())
                wx.MessageBox(''.join(tr), type(e).__name__)
            else:
                wx.MessageBox(e.__str__(), type(e).__name__)


# A CodeEditCtrl shows an area of code.
class CodeEditCtrl(StyledTextCtrl):
    """CodeEditCtrl(text, style, parent=None) -> wx.stc.StyledTextCtrl

    This object is one of the children of wx.stc.StyledTextCtrl. It can show us a TextCtrl but colorful."""

    fontdata = {
        'name': 'Consolas',
        'size': 10
    }
    keyw = keyword.kwlist
    funw = dir(builtins)
    funw.append('self')
    funw.append('cls')

    def __init__(self, parent=None, text='', style=STC_STYLE_DEFAULT):
        """CodeEditCtrl(text, style=STC_STYLE_DEFAULT, parent=None) -> wx.stc.StyledTextCtrl"""
        super(CodeEditCtrl, self).__init__(parent, style=style)
        self.SetupSTC()
        self.AddText(text)

    def SetupSTC(self):
        """Setup the wxSTC

        This method carries out the work of setting up the demo editor.
        It's separate so as not to clutter up the init code.
        """
        self.SetLexer(STC_LEX_PYTHON)
        self.SetKeyWords(0, ' '.join(self.keyw))  # keywords
        self.SetKeyWords(1, ' '.join(self.funw))  # built-in-function-or-methods
        self.SetProperty('fold', '1')
        self.SetProperty('tab.timmy.whinge.level', '1')  # Set left and right margins
        self.SetMargins(2, 2)
        self.SetMarginType(1, STC_MARGIN_NUMBER)
        self.SetMarginWidth(1, 40)
        self.SetIndent(4)
        self.SetIndentationGuides(True)
        self.SetBackSpaceUnIndents(True)
        self.SetTabIndents(True)
        self.SetTabWidth(4)
        self.SetUseTabs(False)
        self.SetupFont()
        self.SetViewWhiteSpace(False)
        self.SetEOLMode(STC_EOL_LF)
        self.SetViewEOL(False)
        self.SetEdgeMode(STC_EDGE_NONE)

    def SetupFont(self):
        """Setup the font."""
        self.StyleSetSpec(STC_STYLE_DEFAULT, 'fore:#000000,back:#FFFFFF,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']))
        self.StyleClearAll()
        self.StyleSetSpec(STC_P_DEFAULT, 'fore:#000000,back:#FFFFFF,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']))
        self.StyleSetSpec(STC_P_COMMENTLINE, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_NUMBER, 'fore:#7F0000,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_STRING, 'fore:#007F00,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_CHARACTER, 'fore:#007F00,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_WORD, 'fore:#00007F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_WORD2, 'fore:#7F007F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_TRIPLE, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_TRIPLEDOUBLE, 'fore:#7F7F7F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_CLASSNAME, 'fore:#007F7F,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_DEFNAME, 'fore:#007F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_DECORATOR, 'fore:#7F7F00,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_OPERATOR, 'fore:#000000,bold,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_IDENTIFIER, 'fore:#000000,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_COMMENTBLOCK, 'fore:#7F7F7F,size:%s' % self.fontdata['size'])
        self.StyleSetSpec(STC_P_STRINGEOL, 'fore:#FFFFFF,back:#000000,eol,face:%s,size:%s' % (
            self.fontdata['name'],
            self.fontdata['size']
        ))


# Code dialog
class CodeDialog(wx.Dialog):
    """It shows a dialog with a code control and two buttons."""
    size = (640, 480)
    labels = {
        'ok': '&OK',
        'cancel': '&Cancel'
    }
    value = None

    def __init__(self, parent=None):
        super(CodeDialog, self).__init__(parent, title=parent.title, size=self.size, style=wx.DEFAULT_FRAME_STYLE)
        self.code = CodeEditCtrl(self)
        self.ok = wx.Button(self, label=self.labels['ok'])
        self.ok.Bind(wx.EVT_BUTTON, ErrorHandler(self.OnSubmit))
        self.cancel = wx.Button(self, label=self.labels['cancel'])
        self.cancel.Bind(wx.EVT_BUTTON, ErrorHandler(self.OnClose))
        self.vsizer = wx.BoxSizer(wx.VERTICAL)
        self.vsizer.Add(self.code, proportion=1, flag=wx.EXPAND | wx.ALL)
        self.hsizer = wx.BoxSizer(wx.HORIZONTAL)
        self.hsizer.Add(self.ok, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.hsizer.Add(self.cancel, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.vsizer.Add(self.hsizer, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL)
        self.SetSizer(self.vsizer)

    def GetValue(self):
        """Get the current value of text."""
        return self.value

    def OnSubmit(self, event):
        """Set the value and close."""
        self.value = self.code.GetValue()
        self.Destroy()

    def OnClose(self, event):
        """Close the window/dialog."""
        self.Destroy()


class MultipleEntryDialog(wx.Dialog):
    """See easygui.multenterbox."""

    def __init__(self, parent=None, message='', title='MultipleEntryDialog', choices={}):
        super(MultipleEntryDialog, self).__init__(parent, title=title, style=wx.DEFAULT_FRAME_STYLE)
        self.value = {}
        self.msgarea = wx.StaticText(self, label=message)
        self.data = {}
        self.ver = wx.BoxSizer(wx.VERTICAL)
        self.ver.Add(self.msgarea, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        for choice in choices:
            hor = wx.BoxSizer(wx.HORIZONTAL)
            lab = wx.StaticText(self, label=choice)
            tex = wx.TextCtrl(self, value=choices[choice])
            hor.Add(lab, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
            hor.Add(tex, proportion=1, flag=wx.EXPAND | wx.ALL, border=5)
            self.ver.Add(hor, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
            self.data[lab] = tex
        hor = wx.BoxSizer(wx.HORIZONTAL)
        self.ok = wx.Button(self, label='OK')
        self.ok.Bind(wx.EVT_BUTTON, ErrorHandler(self.OnSubmit))
        self.cancel = wx.Button(self, label='Cancel')
        self.cancel.Bind(wx.EVT_BUTTON, ErrorHandler(self.OnClose))
        hor.Add(self.ok, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        hor.Add(self.cancel, proportion=0, flag=wx.EXPAND | wx.ALL, border=5)
        self.ver.AddStretchSpacer()
        self.ver.Add(hor, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=5)
        self.SetSizer(self.ver)

    def GetValue(self):
        return self.value

    def OnSubmit(self, event):
        for i in self.data:
            self.value[i.GetLabel()] = self.data[i].GetValue()
        self.Destroy()

    def OnClose(self, event):
        self.Destroy()


class SearchCtrl(wx.Panel):
    """SearchCtrl shows a list of ctrls that helps the user to search."""

    def __init__(self, parent=None):
        super(SearchCtrl, self).__init__(parent)
        self.message = wx.StaticText(self, label='Check Method:')
        self.andor = wx.Choice(self, choices=['And', 'Or'])
        self.isinc = wx.CheckBox(self, label='Include')
        self.isinc.SetValue(True)
        self.andor.SetSelection(0)
        self.sbox = wx.TextCtrl(self, style=wx.TE_MULTILINE)
        self.horizer = wx.BoxSizer(wx.HORIZONTAL)
        self.horizer.Add(self.message, proportion=0, flag=wx.ALIGN_CENTER | wx.ALL, border=2)
        self.horizer.Add(self.andor, proportion=0, flag=wx.EXPAND | wx.ALL, border=2)
        self.horizer.Add(self.isinc, proportion=0, flag=wx.EXPAND | wx.ALL, border=2)
        self.verizer = wx.BoxSizer(wx.VERTICAL)
        self.verizer.Add(self.horizer, proportion=0, flag=wx.EXPAND | wx.ALL)
        self.verizer.Add(self.sbox, proportion=1, flag=wx.EXPAND | wx.ALL)
        self.SetSizer(self.verizer)


# This is a control that shows two text controls and a listbox.
class ExplorerCtrl(wx.Panel):
    """An explorer control shows two text controls and a listbox."""

    def __init__(self, parent=None):
        super(ExplorerCtrl, self).__init__(parent, style=wx.BORDER_NONE | wx.SP_LIVE_UPDATE)
        # Plus


# The main window contains all controls.
class MainWindow(wx.Frame):
    """This class is the main class. Call to show a frame with a splitter window."""
    messages = {
        'eval': 'Please enter an evaluable representation.',
        'open': 'Open File',
        'openpf': 'Open Pickle File',
        'save-current': 'Save Current Value as a Pickle File',
        'save-select': 'Save Selected Value as a Pickle File',
        'failed-to-open': 'Failed to open. It seems like you are trying to open a non-utf8 file.',
        'back-off': 'Cannot go back any more.',
        'non-select': 'You have not yet selected an item.',
        'enter-args': 'Please enter the arguments for call.',
        'not-callable': 'The item you select is not callable.',
        'set-value': 'Please enter a representation of a value and a variable.',
        'set-current': 'Please enter a name of variable.',
        'set-selected': 'Please enter a name of variable.'
    }
    toolmsg = {
        'go-back': 'Go Back',
        'evaluate': 'Evaluate',
        'import-file': 'Import File',
        'import-code': 'Import Code'
    }
    tooltips = {
        'input': 'Type here to find you want.',
        'table': 'Click here to get information. Double-click to get the attributes of the selection.',
        'info': 'It shows information here.'
    }
    pane_settings = {
        'toolbar': 'Toolbar',
        'input': 'Search Here',
        'table': 'Attributes',
        'info': 'Information'
    }
    title = 'Module Importer %s' % __version__
    size = (640, 480)
    toolsize = (24, 24)
    glbs = DictWrapper()
    value = DictWrapper(**sys.modules)
    path = [value]
    strpath = []
    select = ''
    infostr = (
        'Name: %s\n'
        'From: %s\n'
        'Value: %s\n'
        'Type: %s\n'
        'Parent: %s\n'
        '%s'
    )

    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent, title=self.title, size=self.size)
        # menubar/menu settings
        self.menubar = wx.MenuBar()
        self.menu1 = wx.Menu()
        self.menu1.Append(wx.ID_OPEN, '&Open Pickle File...\tCtrl+O')
        self.menu1.Append(ID_SAVE_CURRENT, '&Save Current Value...\tCtrl+S')
        self.menu1.Append(ID_SAVE_SELECTED, 'S&ave Selection...\tCtrl+Shift+S')
        self.menu1.AppendSeparator()
        self.menu1.Append(ID_EVALUATE, '&Evaluate...\tCtrl+E')
        self.menu1.import_ = wx.Menu()
        self.menu1.import_.Append(ID_IMPORT_FILE, 'Python &File\tCtrl+Shift+O')
        self.menu1.import_.Append(ID_IMPORT_CODE, '&Code\tCtrl+Shift+N')
        self.menu1.AppendSubMenu(self.menu1.import_, '&Import...')
        self.menu1.AppendSeparator()
        self.menu1.Append(wx.ID_EXIT, 'E&xit\tEsc')
        self.menu2 = wx.Menu()
        self.menu2.Append(ID_VIEW_ATTR, '&View\tEnter')
        self.menu2.Append(ID_GO_BACK, '&Go Back\tLeft')
        self.menu2.AppendSeparator()
        self.menu2.Append(ID_CALL, '&Call\tCtrl+C')
        self.menu2.AppendSeparator()
        self.menu2.variables = wx.Menu()
        self.menu2.variables.Append(ID_SET_GLOBAL, '&Set Value')
        self.menu2.variables.Append(ID_SET_CURRENT_AS, 'S&et Current Value As')
        self.menu2.variables.Append(ID_SET_SELECTED_AS, 'Se&t Selected Value As')
        self.menu2.variables.AppendSeparator()
        self.menu2.variables.Append(ID_DELETE, '&Delete Value')
        self.menu2.AppendSubMenu(self.menu2.variables, 'V&ariables...')
        self.menu2.Append(ID_VIEW_GLOBALS, 'V&iew Namespaces')
        self.menu3 = wx.Menu()
        self.menu3.AppendCheckItem(ID_SHOW_TOOLBAR, '&Tool Bar')
        self.menu3.Check(ID_SHOW_TOOLBAR, True)
        self.menu3.AppendCheckItem(ID_SHOW_SEARCH, '&Search Box')
        self.menu3.Check(ID_SHOW_SEARCH, True)
        self.menu3.AppendCheckItem(ID_FIX_DIVIDING, '&Fix Separator')
        self.menu4 = wx.Menu()
        self.menu4.Append(wx.ID_HELP, '&Help\tF1')
        self.menu4.AppendSeparator()
        self.menu4.Append(wx.ID_ABOUT, '&About\tCtrl+Shift+A')
        self.menubar.Append(self.menu1, '&File')
        self.menubar.Append(self.menu2, '&Edit')
        self.menubar.Append(self.menu3, '&View')
        self.menubar.Append(self.menu4, '&Help')
        self.SetMenuBar(self.menubar)
        # toolbar settings
        self.toolbar = wx.ToolBar(self, style=wx.TB_FLAT | wx.TB_NODIVIDER)
        self.toolbar.AddTool(ID_GO_BACK, self.toolmsg['go-back'],
                             wx.ArtProvider.GetBitmap(wx.ART_GO_BACK, wx.ART_TOOLBAR, self.toolsize),
                             self.toolmsg['go-back'])
        self.toolbar.AddSeparator()
        self.toolbar.AddTool(ID_EVALUATE, self.toolmsg['evaluate'],
                             wx.ArtProvider.GetBitmap(wx.ART_REPORT_VIEW, wx.ART_TOOLBAR, self.toolsize),
                             self.toolmsg['evaluate'])
        self.toolbar.AddTool(ID_IMPORT_FILE, self.toolmsg['import-file'],
                             wx.ArtProvider.GetBitmap(wx.ART_FILE_OPEN, wx.ART_TOOLBAR, self.toolsize),
                             self.toolmsg['import-file'])
        self.toolbar.AddTool(ID_IMPORT_CODE, self.toolmsg['import-code'],
                             wx.ArtProvider.GetBitmap(wx.ART_NEW, wx.ART_TOOLBAR, self.toolsize),
                             self.toolmsg['import-code'])
        self.toolbar.Realize()
        # statusbar settings
        self.statusbar = self.CreateStatusBar()
        # control settings
        self.mgr = AuiManager(agwFlags=(
                AUI_MGR_ALLOW_FLOATING
                | AUI_MGR_ALLOW_ACTIVE_PANE
                | AUI_MGR_AERO_DOCKING_GUIDES
                | AUI_MGR_SMOOTH_DOCKING)
        )
        self.mgr.SetManagedWindow(self)
        self.menu = wx.Menu()
        self.view = self.menu.Append(ID_VIEW_ATTR, '&View')
        self.delete = self.menu.Append(ID_DELETE, '&Delete')
        self.goback = self.menu.Append(ID_GO_BACK, '&Go Back')
        self.menu.AppendSeparator()
        self.call = self.menu.Append(ID_CALL, '&Call')
        self.menu.Bind(wx.EVT_MENU, ErrorHandler(self.OnDoubleClick), self.view)
        self.menu.Bind(wx.EVT_MENU, ErrorHandler(self.OnDelete), self.delete)
        self.menu.Bind(wx.EVT_MENU, ErrorHandler(self.OnGoBack), self.goback)
        self.menu.Bind(wx.EVT_MENU, ErrorHandler(self.OnCall), self.call)
        self.MenuEnable((ID_VIEW_ATTR, ID_DELETE, ID_GO_BACK, ID_CALL), False)
        self.search = SearchCtrl(self)
        self.search.sbox.Bind(wx.EVT_TEXT, ErrorHandler(self.OnSearch))
        self.search.SetToolTip(self.tooltips['input'])
        self.table = wx.ListBox(self, choices=dir(self.value), style=wx.HSCROLL)
        self.table.Bind(wx.EVT_LISTBOX, ErrorHandler(self.OnClick))
        self.table.Bind(wx.EVT_LISTBOX_DCLICK, ErrorHandler(self.OnDoubleClick))
        self.table.Bind(wx.EVT_RIGHT_UP, ErrorHandler(self.OnRightClick))
        self.table.SetToolTip(self.tooltips['table'])
        self.info = wx.TextCtrl(self, style=wx.TE_MULTILINE | wx.TE_READONLY | wx.HSCROLL)
        self.info.SetToolTip(self.tooltips['info'])
        self.mgr.AddPane(self.toolbar, create_pane_info(
            'Top',
            'ToolbarPane',
            Name=self.pane_settings['toolbar'],
            Caption=self.pane_settings['toolbar'],
            Position=0
        ))
        self.mgr.AddPane(self.search, create_pane_info(
            'Top',
            'ToolbarPane',
            Name=self.pane_settings['input'],
            Caption=self.pane_settings['toolbar'],
            Position=1
        ))
        self.mgr.AddPane(self.table, create_pane_info(
            'Left',
            Name=self.pane_settings['table'],
            Caption=self.pane_settings['table'],
            MinimizeButton=True,
            MaximizeButton=True,
            CloseButton=False
        ))
        self.mgr.AddPane(self.info, create_pane_info(
            'Center',
            Name=self.pane_settings['info'],
            Caption=self.pane_settings['info'],
            MinimizeButton=True,
            MaximizeButton=True,
            CloseButton=False
        ))
        self.mgr.Update()
        # bind events
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnOpenPF), id=wx.ID_OPEN)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnSaveCurrent), id=ID_SAVE_CURRENT)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnSaveSelected), id=ID_SAVE_SELECTED)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnEvaluate), id=ID_EVALUATE)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnImportFile), id=ID_IMPORT_FILE)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnImportCode), id=ID_IMPORT_CODE)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnExit), id=wx.ID_EXIT)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnDoubleClick), id=ID_VIEW_ATTR)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnGoBack), id=ID_GO_BACK)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnCall), id=ID_CALL)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnSetValue), id=ID_SET_GLOBAL)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnSetCurrentAs), id=ID_SET_CURRENT_AS)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnSetSelectedAs), id=ID_SET_SELECTED_AS)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnDelete), id=ID_DELETE)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnViewNamespaces), id=ID_VIEW_GLOBALS)
        self.Bind(wx.EVT_MENU, ErrorHandler(lambda event: self.ShowControl(self.toolbar, event)), id=ID_SHOW_TOOLBAR)
        self.Bind(wx.EVT_MENU, ErrorHandler(lambda event: self.ShowControl(self.search, event)),
                  id=ID_SHOW_SEARCH)
        self.Bind(wx.EVT_MENU, ErrorHandler(lambda event: self.SetSashInvisible(event.IsChecked())),
                  id=ID_FIX_DIVIDING)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnHelp), id=wx.ID_HELP)
        self.Bind(wx.EVT_MENU, ErrorHandler(self.OnAbout), id=wx.ID_ABOUT)
        self.Bind(wx.EVT_CLOSE, ErrorHandler(self.OnExit))
        # if hasattr(sys, "frozen") and getattr(sys, "frozen") == "windows_exe":
        # self.SetIconDefault()
        self.Show()

    def SetIconDefault(self):
        """Set the icon of self."""
        name = win32api.GetModuleFileName(win32api.GetModuleHandle(None))
        icon = wx.Icon(name, wx.BITMAP_TYPE_ICO)
        self.SetIcon(icon)

    def ShowControl(self, name, event):
        """Show or not show a control."""
        pane = self.mgr.GetPane(name)
        pane.Show(event.IsChecked())
        self.mgr.Update()

    def OnOpenPF(self, event):
        """Open a pickle file."""
        dialog = wx.FileDialog(self, self.messages['openpf'])
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            value = load(file)
            self.SetValue(value)
            self.strpath.clear()
        dialog.Destroy()

    def OnSaveCurrent(self, event):
        """Save current value as a pickle file."""
        dialog = wx.FileDialog(self, self.messages['save-current'], style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            value = self.GetValue()
            save(value, file)
        dialog.Destroy()

    def OnSaveSelected(self, event):
        """Save selected value as a pickle file."""
        dialog = wx.FileDialog(self, self.messages['save-select'], style=wx.FD_SAVE)
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            value = self.GetSelectedValue()
            save(value, file)
        dialog.Destroy()

    def OnEvaluate(self, event):
        """Evaluate a evaluable representation and show the attributes of it in the box."""
        dialog = wx.TextEntryDialog(self, self.messages['eval'], self.title)
        if dialog.ShowModal() == wx.ID_OK:
            rep = dialog.GetValue()
            val = eval(rep, self.GetNamespaces())
            self.SetValue(val)
            self.strpath.clear()
        dialog.Destroy()

    def OnImportFile(self, event):
        """Import a file that is like a module."""
        dialog = wx.FileDialog(self, self.messages['open'], wildcard='*.py')
        if dialog.ShowModal() == wx.ID_OK:
            file = dialog.GetPath()
            with open(file, encoding='utf-8') as f:
                code = f.read()
            glob = runpy._run_module_code(code, mod_name=file[:file.index('.')])
            self.SetValue(DictWrapper(**glob))
            self.strpath.clear()
        dialog.Destroy()

    def OnImportCode(self, event):
        """Run a code and show attributes of it. @STYLE: FT"""
        dialog = CodeDialog(self)
        dialog.ShowModal()
        value = dialog.GetValue()
        if value:
            glob = runpy._run_code(value, self.GetNamespaces())
            self.SetValue(DictWrapper(**glob))
            self.strpath.clear()
        dialog.Destroy()

    def GetNamespaces(self):
        """Get the namespaces from the table."""
        attrs = self.table.GetItems()
        ns = {}
        for attr in attrs:
            ns[attr] = getattr(self.value, attr, None)
        for glb in dir(self.glbs):
            ns[glb] = getattr(self.glbs, glb, None)
        return ns

    def GetValue(self):
        """Get the current value."""
        return self.value

    def GetSelectedValue(self):
        """Get the current selected value."""
        val = getattr(self.value, self.select, None)
        return val

    def SetValue(self, value):
        """Set the current value of the explorer."""
        self.Settle(value)
        self.value = value
        self.path.append(self.value)
        attrs = dir(self.value)
        self.strpath.append(self.select)
        self.table.Set(attrs)

    def OnDoubleClick(self, event):
        """Double click one of the choices."""
        if self.table.GetStringSelection():
            new = getattr(self.value, self.select, None)
            self.SetValue(new)
        else:
            wx.MessageBox(self.messages['non-select'], self.title)
        self.MenuEnable((ID_VIEW_ATTR, ID_DELETE, ID_CALL), False)
        self.MenuEnable((ID_GO_BACK,), True)

    def OnDelete(self, event):
        """Delete an attribute."""
        if self.table.GetStringSelection():
            delattr(self.GetValue(), self.select)
            self.table.Delete(self.table.GetItems().index(self.select))
        else:
            wx.MessageBox(self.messages['non-select'], self.title)

    def OnClick(self, event):
        """This method is called when I clicked one of the choices."""
        self.select = self.table.GetStringSelection()
        val = getattr(self.value, self.select, None)
        self.Settle(val)
        if callable(val):
            self.MenuEnable((ID_CALL,), True)
        else:
            self.MenuEnable((ID_CALL,), False)
        self.MenuEnable((ID_VIEW_ATTR, ID_DELETE), True)

    def OnRightClick(self, event):
        """When the user clicked the right mouse, this was called."""
        # if self.table.GetStringSelection():
        #     self.call.Enable(callable(self.GetSelectedValue()))
        #     self.view.Enable(True)
        # else:
        #     self.view.Enable(False)
        # self.goback.Enable(not len(self.path) <= 1)
        self.table.PopupMenu(self.menu)

    def OnSearch(self, event):
        """Search for an attribute."""
        allhave = self.search.sbox.GetValue().split(';')
        selected = []
        # if not self.search.andor.GetSelection():
        #     and
        # for attr in dir(self.value):
        #     ade = True
        #     for k in allhave:
        #         if k.strip() not in attr:
        #             ade = False
        #     if ade == self.search.isinc.GetValue():
        #         selected.append(attr)
        # else:
        #     or
        # for attr in dir(self.value):
        #     ade = False
        #     for k in allhave:
        #         if k.strip() in attr:
        #             ade = True
        #     if ade == self.search.isinc.GetValue():
        #         selected.append(attr)
        andmode = not self.search.andor.GetSelection()
        for attr in dir(self.value):
            ade = andmode
            for k in allhave:
                if (k.strip() not in attr) == andmode:
                    ade = not andmode
            if ade == self.search.isinc.GetValue():
                selected.append(attr)
        self.table.Set(selected)

    def OnGoBack(self, event):
        """Call this and the page will be back."""
        if len(self.path) > 1:
            self.path = self.path[:-1]
            self.value = self.path[-1]
            self.strpath = self.strpath[:-1]
            attrs = dir(self.value)
            self.table.Set(attrs)
        else:
            wx.MessageBox(self.messages['back-off'], self.title)
        if len(self.path) <= 1:
            self.MenuEnable((ID_GO_BACK,), False)

    def OnCall(self, event):
        """Call the selection value if it is callable."""
        dialog = wx.TextEntryDialog(self.GetParent(), self.messages['enter-args'], self.title)
        if dialog.ShowModal() == wx.ID_OK:
            call = self.GetSelectedValue()
            if callable(call):
                pat = dialog.GetValue()
                expr = '%s(%s)' % (self.table.GetStringSelection(), pat)
                val = eval(expr, self.GetNamespaces())
                self.SetValue(val)
                self.strpath.clear()
            else:
                wx.MessageBox(self.messages['not-callable'], self.title)
        dialog.Destroy()

    def OnSetValue(self, event):
        """Set a value as a variable."""
        dialog = MultipleEntryDialog(self, self.messages['set-value'], self.title,
                                     {'Name:': '', 'Value:': 'None'})
        dialog.ShowModal()
        value = dialog.GetValue()
        if value:
            val = eval(value['Value:'], self.GetNamespaces())
            setattr(self.glbs, value['Name:'], val)
        dialog.Destroy()

    def OnSetCurrentAs(self, event):
        """Set current value as a variable."""
        dialog = wx.TextEntryDialog(self, self.messages['set-current'], self.title)
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            setattr(self.glbs, name, self.GetValue())
        dialog.Destroy()

    def OnSetSelectedAs(self, event):
        """Set selected value as a variable."""
        dialog = wx.TextEntryDialog(self, self.messages['set-selected'], self.title)
        if dialog.ShowModal() == wx.ID_OK:
            name = dialog.GetValue()
            setattr(self.glbs, name, self.GetSelectedValue())
        dialog.Destroy()

    def OnViewNamespaces(self, event):
        """View the namespaces in the box."""
        self.SetValue(self.glbs)
        self.strpath.clear()

    def MenuEnable(self, ids, tf=True):
        """Enable or not?"""
        for i in ids:
            self.menu.Enable(i, tf)

    def Settle(self, val):
        """Set the content of the information bar."""
        self.info.SetValue(
            self.infostr % (
                self.select,
                '.'.join(self.strpath) or type(self.value).__name__,
                repr(val),
                type(val).__name__,
                val.__mro__[1].__name__ if type(val) == type else '',
                val.__doc__
            )
        )

    def OnHelp(self, event):
        """Call to show a help window."""

    def OnAbout(self, event):
        """Show the copyrights and authors."""
        dialog = wx.RichMessageDialog(self, __doc__ % __version__, self.title)
        dialog.ShowModal()

    def OnExit(self, event):
        """Exit the program."""
        self.Destroy()
        app.ExitMainLoop()


if __name__ == '__main__':
    app = wx.App()
    try:
        frame = MainWindow()  # namespace
        app.MainLoop()
    except BaseException as e:
        wx.MessageBox(e.__str__(), 'Fatal Error Detected: %s' % type(e).__name__)
