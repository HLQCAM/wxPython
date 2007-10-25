# Name:         params.py
# Purpose:      Classes for parameter introduction
# Author:       Roman Rolinsky <rolinsky@mema.ucl.ac.be>
# Created:      22.08.2001
# RCS-ID:       $Id$

'''
Visual C{Param*} classes for populating C{AtrtibutePanel} with attribute editing
blocks. 
'''

import string
import os
import wx.combo
from globals import *

WARenameDict = {'fg': 'foreground', 'bg': 'background'}

def InitParams(panel):
    '''Set pixel common size based on parent window.'''

    global Presenter
    from presenter import Presenter

    dc = wx.ClientDC(panel)
    global textH, textB
    textH = -1
    if wx.Platform == '__WXMAC__':
        textB = 3               # bigger text border needed for mac highlighting
    else:
        textB = 2
    dc.Destroy()

    # make a custom bitmap showing "..."
    bw, bh = 14, 16
    bmp = wx.EmptyBitmap(bw,bh)
    dc = wx.MemoryDC(bmp)
    
    # clear to a specific background colour
    bgcolor = wx.Colour(255,254,255)
    dc.SetBackground(wx.Brush(bgcolor))
    dc.Clear()

    # draw the label onto the bitmap
    label = "..."
    font = wx.SystemSettings.GetFont(wx.SYS_DEFAULT_GUI_FONT)
    font.SetWeight(wx.FONTWEIGHT_BOLD)
    dc.SetFont(font)
    tw,th = dc.GetTextExtent(label)
    dc.DrawText(label, (bw-tw)/2, (bw-tw)/2)
    del dc

    # now apply a mask using the bgcolor
    bmp.SetMaskColour(bgcolor)
    global bmpEdit
    bmpEdit = bmp

    # Set known encodings
    for i in range(wx.FontMapper.GetSupportedEncodingsCount()):
        ParamEncoding.values.append(wx.FontMapper.GetEncodingName(
                wx.FontMapper.GetEncoding(i)))
    ParamEncoding.values.sort()


# Class that can properly disable children
class PPanel(wx.Panel):
    '''Abstract base class creating an empty C{wx.Panel}.'''
    isCheck = False
    def __init__(self, parent, name):
        wx.Panel.__init__(self, parent, -1, name=name)
        self.freeze = False
        self.name = name
    def Enable(self, value):
        self.enabled = value
        # Something strange is going on with enable so we make sure...
        for w in self.GetChildren():
            w.Enable(value)
        #wx.Panel.Enable(self, value)
    # Common method to set modified state
    def OnChange(self, evt):
        if self.freeze: return
        Presenter.setApplied(False)
        evt.Skip()

class ParamBinaryOr(PPanel):
    '''Editing binary flag attributes defined by a string separated by '|'.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        popup = CheckListBoxComboPopup(self.values)
        self.combo = wx.combo.ComboCtrl(self, size=(220,-1))
        self.combo.SetPopupControl(popup)
        if wx.Platform == '__WXMAC__':
            sizer.Add(self.combo, 1, wx.ALL, 0)
        else:
            sizer.Add(self.combo, 1, wx.ALL, 2)
        self.SetSizerAndFit(sizer)
        self.combo.Bind(wx.EVT_TEXT, self.OnChange)
    def GetValue(self):
        return self.combo.GetValue()
    def SetValue(self, value):
        self.freeze = True
        self.combo.SetValue(value)
        self.freeze = False
    def SetValues(self):
        self.combo.InsertItems(self.values, 0)

class ParamFlag(ParamBinaryOr):
    '''Sizer flag editing.'''
    values = ['wxTOP', 'wxBOTTOM', 'wxLEFT', 'wxRIGHT', 'wxALL',
              'wxEXPAND', 'wxGROW', 'wxSHAPED', 'wxSTRETCH_NOT',
              'wxALIGN_CENTRE', 'wxALIGN_LEFT', 'wxALIGN_RIGHT',
              'wxALIGN_TOP', 'wxALIGN_BOTTOM', 
              'wxALIGN_CENTRE_VERTICAL', 'wxALIGN_CENTRE_HORIZONTAL', 
              'wxADJUST_MINSIZE', 'wxFIXED_MINSIZE'
              ]
    equal = {'wxALIGN_CENTER': 'wxALIGN_CENTRE',
             'wxALIGN_CENTER_VERTICAL': 'wxALIGN_CENTRE_VERTICAL',
             'wxALIGN_CENTER_HORIZONTAL': 'wxALIGN_CENTRE_HORIZONTAL',
             'wxUP': 'wxTOP', 'wxDOWN': 'wxBOTTOM', 'wxNORTH': 'wxTOP',
             'wxSOUTH': 'wxBOTTOM', 'wxWEST': 'wxLEFT', 'wxEAST': 'wxRIGHT'}

class ParamColour(PPanel):
    '''Color attribute editing.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.text = wx.TextCtrl(self, size=(80,textH))
        sizer.Add(self.text, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, textB)
        self.button = wx.Panel(self, size=(20, 20))
        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL | wx.LEFT, 3)
        self.SetSizer(sizer)
        self.textModified = False
        self.button.Bind(wx.EVT_PAINT, self.OnPaintButton)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
        self.button.Bind(wx.EVT_LEFT_DOWN, self.OnLeftDown)
    def GetValue(self):
        return self.text.GetValue()
    def SetValue(self, value):
        self.text.ChangeValue(value)  # update text ctrl
        self.UpdateColour(value)
    def UpdateColour(self, value):
        try:
            colour = wx.Colour(int(value[1:3], 16), int(value[3:5], 16), int(value[5:7], 16))
            self.button.SetBackgroundColour(colour)
        except:                         # ignore errors
            self.button.SetBackgroundColour(self.GetBackgroundColour())
        self.button.Refresh()
    def OnChange(self, evt):
        self.UpdateColour(evt.GetString())
        evt.Skip()
    def OnPaintButton(self, evt):
        dc = wx.PaintDC(self.button)
        dc.SetBrush(wx.TRANSPARENT_BRUSH)
        if self.IsEnabled(): dc.SetPen(wx.BLACK_PEN)
        else: dc.SetPen(wx.GREY_PEN)
        size = self.button.GetSize()
        dc.DrawRectangle(0, 0, size.width, size.height)
    def OnLeftDown(self, evt):
        data = wx.ColourData()
        data.SetColour(self.GetValue())
        dlg = wx.ColourDialog(self, data)
        if dlg.ShowModal() == wx.ID_OK:
            self.SetValue('#%02X%02X%02X' % dlg.GetColourData().GetColour().Get())
            Presenter.setApplied(False)
        dlg.Destroy()

################################################################################

# Mapping from wx constants to XML strings
fontFamiliesWx2Xml = {wx.DEFAULT: 'default', wx.DECORATIVE: 'decorative',
                wx.ROMAN: 'roman', wx.SCRIPT: 'script', wx.SWISS: 'swiss',
                wx.MODERN: 'modern'}
fontStylesWx2Xml = {wx.NORMAL: 'normal', wx.SLANT: 'slant', wx.ITALIC: 'italic'}
fontWeightsWx2Xml = {wx.NORMAL: 'normal', wx.LIGHT: 'light', wx.BOLD: 'bold'}
def ReverseMap(m):
    rm = {}
    for k,v in m.items(): rm[v] = k
    return rm
fontFamiliesXml2wx = ReverseMap(fontFamiliesWx2Xml)
fontStylesXml2wx = ReverseMap(fontStylesWx2Xml)
fontWeightsXml2wx = ReverseMap(fontWeightsWx2Xml)

# My font picker
class FontPickerCtrl(wx.Button):
    def __init__(self, parent, id=-1, font=wx.NullFont, size=wx.DefaultSize, style=0):
        wx.Button.__init__(self, parent, id)

class ParamFont(PPanel):
    '''Font attribute editing.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.button = wx.FontPickerCtrl(
            self, style=wx.FNTP_FONTDESC_AS_LABEL | wx.FNTP_USE_TEXTCTRL
            )
        self.text = self.button.GetTextCtrl()
        if wx.Platform == '__WXMAC__':
            sizer.Add(self.button, 0, wx.LEFT, -2)
        else:
            sizer.Add(self.button, 0, wx.LEFT, textB)
        self.SetSizer(sizer)
        self.Bind(wx.EVT_FONTPICKER_CHANGED, self.OnPickFont)
        self.text.Bind(wx.EVT_TEXT, self.OnText)
        self.text.Bind(wx.EVT_KILL_FOCUS, self.OnTextKillFocus)
    def OnText(self, evt):
        Presenter.setApplied(False)
        if evt.GetString():
            evt.Skip()
        else:
            self.text.ChangeValue('')
    def OnTextKillFocus(self, evt):
        if self.text.GetValue():
            evt.Skip()
    def GetValue(self):
        return self.value
    def dict2font(self, d):
        error = False
        if 'size' in d:
            try:                size = int(d['size'])
            except ValueError:  error = True; wx.LogError('Invalid size specification')
        else:
            size = g.sysFont().GetPointSize()
        if 'family' in d:
            try:                family = fontFamiliesXml2wx[d['family']]
            except KeyError:    error = True; wx.LogError('Invalid family specification')
        else:
            family = wx.DEFAULT
        if 'style' in d:
            try:                style = fontStylesXml2wx[d['style']]
            except KeyError:    error = True; wx.LogError('Invalid style specification')
        else:
            style = wx.NORMAL
        if 'weight' in d:
            try:                weight = fontWeightsXml2wx[d['weight']]
            except KeyError:    error = True; wx.LogError('Invalid weight specification')
        else:
            weight = wx.NORMAL
        try: underlined = bool(d.get('underlined', 0))
        except ValueError: error = True; wx.LogError('Invalid underlined flag specification')
        face = d.get('face','')
        enc = wx.FONTENCODING_DEFAULT
        mapper = wx.FontMapper()
        if 'encoding' in d: enc = mapper.CharsetToEncoding(d['encoding'])
        if error: wx.LogError('Invalid font specification')
        if enc == wx.FONTENCODING_DEFAULT: enc = wx.FONTENCODING_SYSTEM
        font = wx.Font(size, family, style, weight, underlined, face, enc)
        return font
        
    def SetValue(self, value):
        self.freeze = True              # disable other handlers
        if not value:
            self.text.ChangeValue('')
        else:
            self.button.SetSelectedFont(self.dict2font(value))
        self.value = value
        self.freeze = False
    def OnPickFont(self, evt):
        font = evt.GetFont()
        if font.GetEncoding() == wx.FONTENCODING_SYSTEM:
            encName = ''
        else:
            encName = wx.FontMapper.GetEncodingName(font.GetEncoding()).encode()
        value = {'size': str(font.GetPointSize()),
                 'family': fontFamiliesWx2Xml.get(font.GetFamily(), "default"),
                 'style': fontStylesWx2Xml.get(font.GetStyle(), "normal"),
                 'weight': fontWeightsWx2Xml.get(font.GetWeight(), "normal"),
                 'underlined': str(int(font.GetUnderlined())),
                 'face': font.GetFaceName().encode(),
                 'encoding': encName}
        self.SetValue(value)
        Presenter.setApplied(False)

################################################################################

# This is a replacement for SpinCtrl to make ParamUnit looking similar.
# Unfortunately there is no SpinCtrl::GetStringValue...
class ParamInt(PPanel):
    '''TextCtrl with SpinButton for integer parameters.'''
    default = 0
    range = (-2147483648, 2147483647)
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.spin = wx.SpinButton(self, style = wx.SP_VERTICAL, size=(-1,10))
        textW = 60 - self.spin.GetSize()[0]
        self.text = wx.TextCtrl(self, size=(textW,textH))
        self.spin.SetRange(*self.range)
        if wx.Platform == '__WXMAC__':
            sizer.Add(self.text, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | wx.ALL, textB)
        else:
            sizer.Add(self.text, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND | \
                          wx.LEFT | wx.TOP | wx.BOTTOM, textB)
        sizer.Add(self.spin, 0, wx.ALIGN_CENTER_VERTICAL | wx.EXPAND)
        self.SetSizer(sizer)
        self.spin.Bind(wx.EVT_SPIN_UP, self.OnSpinUp)
        self.spin.Bind(wx.EVT_SPIN_DOWN, self.OnSpinDown)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
        
    def GetValue(self):
        return self.text.GetValue()
    def SetValue(self, value):
        self.text.ChangeValue(value)
        self.SyncSpin(value)
    def SyncSpin(self, value):
        try:
            intValue = int(value)
            self.spin.SetValue(intValue)
        except:
            self.spin.SetValue(self.default)
    def OnChange(self, evt):
        self.SyncSpin(evt.GetString())
        Presenter.setApplied(False)
        evt.Skip()
    def SyncText(self, spinValue):
        if self.range[0] <= spinValue <= self.range[1]:
            self.text.ChangeValue(str(spinValue))
            Presenter.setApplied(False)
    def OnSpinUp(self, evt):
        self.SyncText(evt.GetPosition())
        evt.Skip()
    def OnSpinDown(self, evt):
        self.SyncText(evt.GetPosition())
        evt.Skip()

def MetaParamInt(**kargs):
    '''Create ParamInt class with default value.'''
    return type('ParamInt', (ParamInt,), kargs)

ParamIntNN = MetaParamInt(default=0, range=(0, 2147483647)) # non-negative
ParamIntP = MetaParamInt(default=1, range=(1, 2147483647)) # positive

# Same as ParamInt but allows dialog units (XXXd)
class ParamUnit(ParamInt):
    '''Similar to L{ParamInt}, 'd' can be appended to the value to specify
    dialog units mode.'''
    def _splitValue(self, value):
        units = ''
        if value[-1:].upper() == 'D':
            units = value[-1]
            value = value[:-1]
        return value,units
    def SyncSpin(self, value):
        try:
            value,units = self._splitValue(value)
            intValue = int(value)
            self.spin.SetValue(intValue)
        except:
            self.spin.SetValue(self.default)
    def SyncText(self, spinValue):
        if self.range[0] <= spinValue <= self.range[1]:
            value,units = self._splitValue(self.text.GetValue())
            self.text.ChangeValue(str(spinValue)+units)
            Presenter.setApplied(False)

class ParamMultilineText(PPanel):
    '''Multiline text editing.'''
    def __init__(self, parent, name, textWidth=-1):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.text = wx.TextCtrl(self, size=wx.Size(200,textH))
        sizer.Add(self.text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, textB)
        self.button = wx.BitmapButton(self, bitmap=bmpEdit, size=(-1,textH))
        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)
        self.button.Bind(wx.EVT_BUTTON, self.OnButtonEdit)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
    def GetValue(self):
        return self.text.GetValue()
    def SetValue(self, value):
        self.freeze = True              # disable other handlers
        self.text.SetValue(value)
        self.freeze = False             # disable other handlers
    def OnButtonEdit(self, evt):
        dlg = g.res.LoadDialog(self, 'DIALOG_TEXT')
        textCtrl = xrc.XRCCTRL(dlg, 'TEXT')
        textCtrl.SetValue(self.text.GetValue())
        if dlg.ShowModal() == wx.ID_OK:
            self.text.SetValue(textCtrl.GetValue())
            Presenter.setApplied(False)
        dlg.Destroy()

class ParamText(PPanel):
    '''Text attribute.'''
    textWidth = -1
    proportion = 0
    def __init__(self, parent, name, style=0, **kargs):
        PPanel.__init__(self, parent, name)
        textWidth = kargs.get('textWidth', self.textWidth)
        option = kargs.get('proportion', self.proportion)
        if textWidth == -1: option = 1
        # We use sizer even here to have the same size of text control
        sizer = wx.BoxSizer()
        self.text = wx.TextCtrl(self, size=wx.Size(textWidth,textH), style=style)
        sizer.Add(self.text, option, wx.ALIGN_CENTER_VERTICAL | wx.ALL, textB)
        self.SetSizer(sizer)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
    def GetValue(self):
        return self.text.GetValue()
    def SetValue(self, value):
        self.freeze = True              # disable other handlers
        self.text.SetValue(value)
        self.freeze = False             # disable other handlers

def MetaParamText(textWidth, proportion=0):
    '''Return a L{ParamText} class with specified width and proportion.'''
    return type('ParamText__length', (ParamText,),
                {'textWidth': textWidth, 'proportion': proportion})

ParamLongText = MetaParamText(200, 1)
ParamAccel = MetaParamText(100)
ParamHelp = MetaParamText(200, 1)
ParamPosSize = MetaParamText(80)

class ParamComment(ParamText):
    '''Comment node editing.'''
    def __init__(self, parent, name):
        ParamText.__init__(self, parent, name, 330,
                           style=wx.TE_PROCESS_ENTER)

class ContentDialog(wx.Dialog):
    '''Dialog for editing content attributes.'''
    def __init__(self, parent, value):
        # Load from resource
        pre = wx.PreDialog()
        g.res.LoadOnDialog(pre, parent, 'DIALOG_CONTENT')
        self.PostCreate(pre)
        self.list = xrc.XRCCTRL(self, 'LIST')
        # Set list items
        for v in value:
            self.list.Append(v)
        self.SetAutoLayout(True)
        self.GetSizer().Fit(self)
        # Callbacks
        self.ID_BUTTON_APPEND = xrc.XRCID('BUTTON_APPEND')
        self.ID_BUTTON_REMOVE = xrc.XRCID('BUTTON_REMOVE')
        self.ID_BUTTON_UP = xrc.XRCID('BUTTON_UP')
        self.ID_BUTTON_DOWN = xrc.XRCID('BUTTON_DOWN')
        wx.EVT_BUTTON(self, self.ID_BUTTON_UP, self.OnButtonUp)
        wx.EVT_BUTTON(self, self.ID_BUTTON_DOWN, self.OnButtonDown)
        wx.EVT_BUTTON(self, self.ID_BUTTON_APPEND, self.OnButtonAppend)
        wx.EVT_BUTTON(self, self.ID_BUTTON_REMOVE, self.OnButtonRemove)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_UP, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_DOWN, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_REMOVE, self.OnUpdateUI)
    def OnButtonUp(self, evt):
        i = self.list.GetSelection()
        str = self.list.GetString(i)
        self.list.Delete(i)
        self.list.InsertItems([str], i-1)
        self.list.SetSelection(i-1)
    def OnButtonDown(self, evt):
        i = self.list.GetSelection()
        str = self.list.GetString(i)
        self.list.Delete(i)
        self.list.InsertItems([str], i+1)
        self.list.SetSelection(i+1)
    def OnButtonAppend(self, evt):
        str = wx.GetTextFromUser('Enter new item:', 'Append', '', self)
        self.list.Append(str)
    def OnButtonRemove(self, evt):
        self.list.Delete(self.list.GetSelection())
    def OnUpdateUI(self, evt):
        if evt.GetId() == self.ID_BUTTON_REMOVE:
            evt.Enable(self.list.GetSelection() != -1)
        elif evt.GetId() == self.ID_BUTTON_UP:
            evt.Enable(self.list.GetSelection() > 0)
        elif evt.GetId() == self.ID_BUTTON_DOWN:
            evt.Enable(self.list.GetSelection() != -1 and \
                       self.list.GetSelection() < self.list.GetCount() - 1)

class ContentCheckListDialog(wx.Dialog):
    '''Dialog for editing content checklist attributes.'''
    def __init__(self, parent, value):
        pre = wx.PreDialog()
        g.res.LoadOnDialog(pre, parent, 'DIALOG_CONTENT_CHECKLIST')
        self.PostCreate(pre)
        self.list = xrc.XRCCTRL(self, 'CHECK_LIST')
        # Set list items
        i = 0
        for v,ch in value:
            self.list.Append(v)
            self.list.Check(i, ch)
            i += 1
        self.SetAutoLayout(True)
        self.GetSizer().Fit(self)
        # Callbacks
        self.ID_BUTTON_APPEND = xrc.XRCID('BUTTON_APPEND')
        self.ID_BUTTON_REMOVE = xrc.XRCID('BUTTON_REMOVE')
        self.ID_BUTTON_UP = xrc.XRCID('BUTTON_UP')
        self.ID_BUTTON_DOWN = xrc.XRCID('BUTTON_DOWN')
        wx.EVT_CHECKLISTBOX(self, self.list.GetId(), self.OnCheck)
        wx.EVT_BUTTON(self, self.ID_BUTTON_UP, self.OnButtonUp)
        wx.EVT_BUTTON(self, self.ID_BUTTON_DOWN, self.OnButtonDown)
        wx.EVT_BUTTON(self, self.ID_BUTTON_APPEND, self.OnButtonAppend)
        wx.EVT_BUTTON(self, self.ID_BUTTON_REMOVE, self.OnButtonRemove)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_UP, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_DOWN, self.OnUpdateUI)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_REMOVE, self.OnUpdateUI)
    def OnCheck(self, evt):
        # !!! Wrong wxGTK (wxMSW?) behavior: toggling selection if checking
        self.list.Deselect(evt.GetSelection())
    def OnButtonUp(self, evt):
        i = self.list.GetSelection()
        str, ch = self.list.GetString(i), self.list.IsChecked(i)
        self.list.Delete(i)
        self.list.InsertItems([str], i-1)
        self.list.Check(i-1, ch)
        self.list.SetSelection(i-1)
    def OnButtonDown(self, evt):
        i = self.list.GetSelection()
        str, ch = self.list.GetString(i), self.list.IsChecked(i)
        self.list.Delete(i)
        self.list.InsertItems([str], i+1)
        self.list.Check(i+1, ch)
        self.list.SetSelection(i+1)
    def OnButtonAppend(self, evt):
        str = wx.GetTextFromUser('Enter new item:', 'Append', '', self)
        self.list.Append(str)
    def OnButtonRemove(self, evt):
        self.list.Delete(self.list.GetSelection())
    def OnUpdateUI(self, evt):
        if evt.GetId() == self.ID_BUTTON_REMOVE:
            evt.Enable(self.list.GetSelection() != -1)
        elif evt.GetId() == self.ID_BUTTON_UP:
            evt.Enable(self.list.GetSelection() > 0)
        elif evt.GetId() == self.ID_BUTTON_DOWN:
            evt.Enable(self.list.GetSelection() != -1 and \
                       self.list.GetSelection() < self.list.GetCount() - 1)

class ParamContent(PPanel):
    '''Editing of content attribute.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.text = wx.TextCtrl(self, size=wx.Size(200,textH))
        sizer.Add(self.text, 1, wx.ALL | wx.ALIGN_CENTER_VERTICAL, textB)
        self.button = wx.BitmapButton(self, bitmap=bmpEdit, size=(-1,textH))
        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)
        self.textModified = False
        self.button.Bind(wx.EVT_BUTTON, self.OnButtonEdit)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
    def OnChange(self, evt):
        Presenter.setApplied(False)
        self.textModified = True
    def GetValue(self):
        if self.textModified:           # text has newer value
            try:
                return self.text.GetValue().split('|')
            except ValueError:
                return []
        return self.value
    def SetValue(self, value):
        if not value: value = []
        self.value = value
        repr_ = '|'.join(map(str, value))
        self.text.ChangeValue(repr_)  # update text ctrl
    def OnButtonEdit(self, evt):
        if self.textModified:           # text has newer value
            self.value = self.GetValue()
        dlg = ContentDialog(self, self.value)
        if dlg.ShowModal() == wx.ID_OK:
            value = []
            for i in range(dlg.list.GetCount()):
                value.append(dlg.list.GetString(i))
            self.SetValue(value)
            Presenter.setApplied(False)
            self.textModified = False
        dlg.Destroy()

# CheckList content
class ParamContentCheckList(ParamContent):
    '''Editing of content check list attribute.'''
    def __init__(self, parent, name):
        ParamContent.__init__(self, parent, name)
    def OnButtonEdit(self, evt):
        if self.textModified:           # text has newer value
            self.value = self.GetValue()
        dlg = ContentCheckListDialog(self, self.value)
        if dlg.ShowModal() == wx.ID_OK:
            value = []
            for i in range(dlg.list.GetCount()):
                value.append((dlg.list.GetString(i), int(dlg.list.IsChecked(i))))
            self.SetValue(value)
            Presenter.setApplied(False)
            self.textModified = False
        dlg.Destroy()
    def SetValue(self, value):
        self.freeze = True
        if not value: value = []
        self.value = value
        repr_ = '|'.join(map(str,value))
        self.text.SetValue(repr_)  # update text ctrl
        self.freeze = False        

class IntListDialog(wx.Dialog):
    '''Dialog for editing integer lists.'''
    def __init__(self, parent, value):
        pre = wx.PreDialog()
        g.res.LoadOnDialog(pre, parent, 'DIALOG_INTLIST')
        self.PostCreate(pre)
        self.list = xrc.XRCCTRL(self, 'LIST')
        # Set list items
        value.sort()
        for v in value:
            self.list.Append(v)
        self.SetAutoLayout(True)
        self.GetSizer().Fit(self)
        # Callbacks
        self.spinCtrl = xrc.XRCCTRL(self, 'SPIN')
        wx.EVT_BUTTON(self, xrc.XRCID('BUTTON_ADD'), self.OnButtonAdd)
        self.ID_BUTTON_REMOVE = xrc.XRCID('BUTTON_REMOVE')
        wx.EVT_BUTTON(self, self.ID_BUTTON_REMOVE, self.OnButtonRemove)
        wx.EVT_BUTTON(self, xrc.XRCID('BUTTON_CLEAR'), self.OnButtonClear)
        wx.EVT_UPDATE_UI(self, self.ID_BUTTON_REMOVE, self.OnUpdateUI)
    def OnButtonAdd(self, evt):
        # Check that it's unique
        try:
            v = self.spinCtrl.GetValue()
            s = str(v)                  # to be sure
            i = self.list.FindString(s)
            if i == -1:                 # ignore non-unique
                # Find place to insert
                found = False
                for i in range(self.list.GetCount()):
                    if int(self.list.GetString(i)) > v:
                        found = True
                        break
                if found: self.list.InsertItems([s], i)
                else: self.list.Append(s)
        except ValueError:
            wx.LogError('List item is not an int!')
    def OnButtonRemove(self, evt):
        self.list.Delete(self.list.GetSelection())
    def OnButtonClear(self, evt):
        self.list.Clear()
    def OnUpdateUI(self, evt):
        if evt.GetId() == self.ID_BUTTON_REMOVE:
            evt.Enable(self.list.GetSelection() != -1)

# For growable list
class ParamIntList(ParamContent):
    '''Editing integer list attribute.'''
    def __init__(self, parent, name):
        ParamContent.__init__(self, parent, name)
    def OnButtonEdit(self, evt):
        if self.textModified:           # text has newer value
            try:
                self.value = self.text.GetValue().split('|')
            except ValueError:
                self.value = []
        dlg = IntListDialog(self, self.value)
        if dlg.ShowModal() == wx.ID_OK:
            value = []
            for i in range(dlg.list.GetCount()):
                value.append(dlg.list.GetString(i))
            self.SetValue(value)
            Presenter.setApplied()
            self.textModified = False
        dlg.Destroy()

# Boxless radiobox
class RadioBox(PPanel):
    def __init__(self, parent, id, choices,
                 pos=wx.DefaultPosition, name='radiobox'):
        PPanel.__init__(self, parent, name)
        self.choices = choices
        topSizer = wx.BoxSizer()
        for i in choices:
            button = wx.RadioButton(self, -1, i, name=i)
            topSizer.Add(button, 0, wx.RIGHT, 5)
            wx.EVT_RADIOBUTTON(self, button.GetId(), self.OnRadioChoice)
        self.SetSizer(topSizer)
    def SetStringSelection(self, value):
        self.freeze = True
        for i in self.choices:
            self.FindWindowByName(i).SetValue(i == value)
        self.value = value
        self.freeze = False
    def OnRadioChoice(self, evt):
        if self.freeze: return
        if evt.GetSelection():
            self.value = evt.GetEventObject().GetName()
            Presenter.setApplied(False)
    def GetStringSelection(self):
        return self.value

# Boxless radiobox
class CheckBox(PPanel):
    isCheck = True
    def __init__(self, parent, name='checkbox'):
        PPanel.__init__(self, parent, name)
        topSizer = wx.BoxSizer()
        self.check = wx.CheckBox(self, -1, name, size=(-1,textH))
        topSizer.Add(self.check, 0, wx.TOP | wx.BOTTOM, textB)
        self.check.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.SetSizer(topSizer)
    def OnCheck(self, evt):
        Presenter.setApplied(False)
        if Presenter.panelIsDirty():
            Presenter.registerUndoEdit()
        evt.Skip()

class ParamBool(CheckBox):
    '''Editing on/off attributes.'''
    defaultString = '(default is OFF)'
    def GetValue(self):
        return ('', '1')[self.check.IsChecked()]
    def SetValue(self, value):
        self.check.SetValue(value == '1')

class ParamInverseBool(CheckBox):
    '''like L{ParamBool} but defined if unchecked'''
    defaultString = '(default is ON)'
    def GetValue(self):
        return ('0', '')[self.check.IsChecked()]
    def SetValue(self, value):
        self.check.SetValue(not value or value == '1')

class ParamOrient(RadioBox):
    '''Orientation attribute editing for sizers.'''
    values = {'horizontal': 'wxHORIZONTAL', 'vertical': 'wxVERTICAL'}
    seulav = {'wxHORIZONTAL': 'horizontal', 'wxVERTICAL': 'vertical'}
    def __init__(self, parent, name):
        RadioBox.__init__(self, parent, -1, choices=self.values.keys(), name=name)
    def GetValue(self):
        return self.values[self.GetStringSelection()]
    def SetValue(self, value):
        if not value: value = 'wxHORIZONTAL'
        self.SetStringSelection(self.seulav[value])

class ParamOrientation(RadioBox):
    '''Orientaiton attribute editing for C{wx.SplitterWindow}.'''
    values = {'horizontal': 'horizontal', 'vertical': 'vertical'}
    seulav = {'horizontal': 'horizontal', 'vertical': 'vertical'}
    def __init__(self, parent, name):
        RadioBox.__init__(self, parent, -1, choices=self.values.keys(), name=name)
    def GetValue(self):
        return self.values[self.GetStringSelection()]
    def SetValue(self, value):
        if not value: value = 'vertical'
        self.SetStringSelection(self.seulav[value])

class ParamBitmap(PPanel):
    def __init__(self, parent, name):
        pre = wx.PrePanel()
        g.res.LoadOnPanel(pre, parent, 'PANEL_BITMAP')
        self.PostCreate(pre)
        self.modified = self.freeze = False
        self.radio_std = xrc.XRCCTRL(self, 'RADIO_STD')
        self.radio_file = xrc.XRCCTRL(self, 'RADIO_FILE')
        self.combo = xrc.XRCCTRL(self, 'COMBO_STD')
        self.text = xrc.XRCCTRL(self, 'TEXT_FILE')
        self.button = xrc.XRCCTRL(self, 'BUTTON_BROWSE')
        self.textModified = False
        wx.EVT_RADIOBUTTON(self, xrc.XRCID('RADIO_STD'), self.OnRadioStd)
        wx.EVT_RADIOBUTTON(self, xrc.XRCID('RADIO_FILE'), self.OnRadioFile)
        wx.EVT_BUTTON(self, xrc.XRCID('BUTTON_BROWSE'), self.OnButtonBrowse)
        wx.EVT_COMBOBOX(self, xrc.XRCID('COMBO_STD'), self.OnCombo)
        wx.EVT_TEXT(self, xrc.XRCID('COMBO_STD'), self.OnChange)
        wx.EVT_TEXT(self, xrc.XRCID('TEXT_FILE'), self.OnChange)
    def OnRadioStd(self, evt):
        Presenter.setApplied(False)
        self.SetValue(['wxART_MISSING_IMAGE',''])
    def OnRadioFile(self, evt):
        Presenter.setApplied(False)
        self.SetValue(['',''])
    def updateRadios(self):
        if self.value[0]:
            self.radio_std.SetValue(True)
            self.radio_file.SetValue(False)
            self.text.Enable(False)
            self.button.Enable(False)
            self.combo.Enable(True)
        else:
            self.radio_std.SetValue(False)
            self.radio_file.SetValue(True)
            self.text.Enable(True)
            self.button.Enable(True)
            self.combo.Enable(False)
    def OnChange(self, evt):
        if self.freeze: return
        Presenter.setApplied(False)
        self.textModified = True
    def OnCombo(self, evt):
        if self.freeze: return
        Presenter.setApplied(False)
        self.value[0] = self.combo.GetValue()
    def GetValue(self):
        return [self.combo.GetValue(), self.text.GetValue()]
    def SetValue(self, value):
        self.freeze = True
        if not value:
            self.value = ['', '']
        else:
            self.value = value
        self.combo.SetValue(self.value[0])
        self.text.SetValue(self.value[1])  # update text ctrl
        self.updateRadios()
        self.freeze = False
    def OnButtonBrowse(self, evt):
        if self.textModified:           # text has newer value
            self.value[1] = self.text.GetValue()
        dlg = wx.FileDialog(self,
                           defaultDir = os.path.abspath(os.path.dirname(self.value[1])),
                           defaultFile = os.path.basename(self.value[1]))
        if dlg.ShowModal() == wx.ID_OK:
            # Get common part of selected path and current
            if Presenter.path:
                curpath = os.path.abspath(Presenter.path)
            else:
                curpath = os.path.join(os.getcwd(), '')
            common = os.path.commonprefix([curpath, dlg.GetPath()])
            self.SetValue(['', dlg.GetPath()[len(common):]])
            Presenter.setApplied(False)
            self.textModified = False
        dlg.Destroy()

class ParamImage(PPanel):
    '''Image selector.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.text = wx.TextCtrl(self, size=wx.Size(200,textH))
        sizer.Add(self.text, 0, wx.ALL | wx.ALIGN_CENTER_VERTICAL, textB)
        self.button = wx.Button(self, -1, 'Browse...')
        sizer.Add(self.button, 0, wx.ALIGN_CENTER_VERTICAL)
        self.SetSizer(sizer)
        self.button.Bind(wx.EVT_BUTTON, self.OnButtonBrowse)
        self.text.Bind(wx.EVT_TEXT, self.OnChange)
    def OnChange(self, evt):
        Presenter.setApplied(False)
    def GetValue(self):
        return self.text.GetValue()
    def SetValue(self, value):
        self.text.SetValue(value)
    def OnButtonBrowse(self, evt):
        value = self.text.GetValue()
        dlg = wx.FileDialog(self,
                           defaultDir = os.path.abspath(os.path.dirname(value)),
                           defaultFile = os.path.basename(value))
        if dlg.ShowModal() == wx.ID_OK:
            # Get common part of selected path and current
            if Presenter.path:
                curpath = os.path.abspath(Presenter.path)
            else:
                curpath = os.path.join(os.getcwd(), '')
            common = os.path.commonprefix([curpath, dlg.GetPath()])
            self.SetValue(dlg.GetPath()[len(common):])
            Presenter.setApplied(False)
            self.textModified = False
        dlg.Destroy()

class ParamCombo(PPanel):
    values = []
    '''Combo box.'''
    def __init__(self, parent, name):
        PPanel.__init__(self, parent, name)
        sizer = wx.BoxSizer()
        self.combo = wx.ComboBox(self, size=(220,-1))
        if wx.Platform == '__WXMAC__':
            sizer.Add(self.combo, 0, wx.ALL, 0)
        else:
            sizer.Add(self.combo, 0, wx.ALL, 2)
        self.SetSizerAndFit(sizer)
        self.combo.Bind(wx.EVT_TEXT, self.OnChange)
        self.SetValues()
    def GetValue(self):
        return self.combo.GetValue()
    def SetValue(self, value):
        self.freeze = True
        self.combo.SetValue(value)
        self.freeze = False
    def SetValues(self):
        for v in self.values:
            self.combo.Append(v)

class ParamEncoding(ParamCombo):
    '''Editing encoding attribute of the XML root node.'''
    pass

paramDict = {
    # sizer params
    'flag': ParamFlag, 'orient': ParamOrient, 'option': ParamInt,
    'cellpos': ParamPosSize, 'cellspan': ParamPosSize,
    'border': ParamUnit, 'borders': ParamUnit,
    'cols': ParamIntP, 'rows': ParamIntP,
    'vgap': ParamUnit, 'hgap': ParamUnit,
    # common window params
    'pos': ParamPosSize, 'size': ParamPosSize,
    'checkable': ParamBool, 'checked': ParamBool, 'radio': ParamBool,
    'accel': ParamAccel, 'help': ParamHelp, 'centered': ParamBool,
    'label': ParamMultilineText, 'title': ParamLongText, 'value': ParamLongText,
    'content': ParamContent, 'selection': ParamIntNN,
    'min': ParamInt, 'max': ParamInt,
    # window attributes
    'fg': ParamColour, 'bg': ParamColour, 'font': ParamFont,
    'enabled': ParamInverseBool, 'focused': ParamBool, 'hidden': ParamBool,
    'tooltip': ParamLongText, 
    # other
    'bitmap': ParamBitmap, 'icon': ParamBitmap,
    'comment': ParamComment
    }
'''Default classes for standard attributes.'''

class StylePanel(wx.Panel):
    '''Style panel.'''
    def __init__(self, parent, styles, genericStyles=[]):
        wx.Panel.__init__(self, parent, -1)
        self.SetFont(g.smallerFont())
        self.node = None
        self.controls = []
        topSizer = wx.BoxSizer(wx.HORIZONTAL)
        if genericStyles:
            # Generic styles
            sizer = wx.GridSizer(len(genericStyles), 1, 1, 5)
            label = wx.StaticText(self, label='Generic')
            label.SetFont(g.labelFont())
            sizer.Add(label, 0, wx.LEFT, 20)
            for s in genericStyles:
                if s[:2] == 'wx': label = s[2:]
                else:             label = s
                control = wx.CheckBox(self, label=label)
                sizer.Add(control)
                self.controls.append((s, control))
            topSizer.Add(sizer)
        if styles:
            # Specific styles
            sizer = wx.GridSizer(len(styles), 1, 1, 5)
            if genericStyles:
                label = wx.StaticText(self, label='Specific')
                label.SetFont(g.labelFont())
                sizer.Add(label, 0, wx.LEFT, 20)
            for s in styles:
                if s[:2] == 'wx': label = s[2:]
                else:             label = s
                control = wx.CheckBox(self, label=label)
                sizer.Add(control)
                self.controls.append((s, control))
            topSizer.Add(sizer)
        self.Bind(wx.EVT_CHECKBOX, self.OnCheck)
        self.SetSizerAndFit(topSizer)

    def GetValues(self):
        checked = []
        for s,check in self.controls:
            if check.IsChecked(): checked.append(s)
        return [('style', '|'.join(checked))]

    def SetValues(self, values):
        styles = values[0][1].split('|')
        for s,check in self.controls:
            check.SetValue(s in styles)

    def OnCheck(self, evt):
        Presenter.setApplied(False)

#############################################################################

class CheckListBoxComboPopup(wx.CheckListBox, wx.combo.ComboPopup):
        
    def __init__(self, values):
        self.values = values
        self.PostCreate(wx.PreCheckListBox())
        wx.combo.ComboPopup.__init__(self)
        
    def Create(self, parent):
        wx.CheckListBox.Create(self, parent)
        self.InsertItems(self.values, 0)
        return True

    def GetControl(self):
        return self

    def OnPopup(self):
        combo = self.GetCombo()
        value = map(string.strip, combo.GetValue().split('|'))
        if value == ['']: value = []
        self.ignored = []
        for i in value:
            try:
                self.Check(self.values.index(i))
            except ValueError:
                # Try to find equal
                if self.equal.has_key(i):
                    self.Check(self.values.index(self.equal[i]))
                else:
                    logger.warning('unknown flag: %s: ignored.', i)
                    self.ignored.append(i)

        wx.combo.ComboPopup.OnPopup(self)

    def OnDismiss(self):
        combo = self.GetCombo()
        value = []
        for i in range(self.GetCount()):
            if self.IsChecked(i):
                value.append(self.values[i])
        # Add ignored flags
        value.extend(self.ignored)
        strValue = '|'.join(value)
        if combo.GetValue() != strValue:
            combo.SetValue(strValue)
            Presenter.setApplied(False)

        wx.combo.ComboPopup.OnDismiss(self)
