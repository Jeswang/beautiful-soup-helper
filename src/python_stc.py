#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Jeswang<wangyi724@gmail.com>
#         http://blog.jeswang.org
# Created on 2014-02-28 22:40:21

from wx import *
from wx.stc import *
import re
import string
import keyword

class PythonSTC(StyledTextCtrl):
    def __init__(self, parent, ID):
        StyledTextCtrl.__init__(self, parent, ID, style=wx.EXPAND|wx.ALL, size=(400,-1))

        self.CmdKeyAssign(ord('B'), STC_SCMOD_CTRL, STC_CMD_ZOOMIN)
        self.CmdKeyAssign(ord('N'), STC_SCMOD_CTRL, STC_CMD_ZOOMOUT)
 
        self.SetLexer(STC_LEX_PYTHON)
        self.SetKeyWords(0, string.join(keyword.kwlist))

        self.SetTabWidth(4)
        self.SetBackSpaceUnIndents(1)

        self.SetUseTabs(False)
        self.SetProperty("fold", "1")
        self.SetProperty("tab.timmy.whinge.level", "1")
        self.SetMargins(0,20)

        self.SetViewWhiteSpace(True)

        self.SetEdgeMode(STC_EDGE_BACKGROUND)
        self.SetEdgeColumn(78)

        # Setup a margin to hold fold markers
        self.SetMarginType(2, STC_MARGIN_SYMBOL)
        self.SetMarginMask(2, STC_MASK_FOLDERS)
        self.SetMarginSensitive(2, True)
        self.SetMarginWidth(2, 15)
        self.MarkerDefine(STC_MARKNUM_FOLDER, STC_MARK_ARROW, "navy", "navy")
        self.MarkerDefine(STC_MARKNUM_FOLDEROPEN, STC_MARK_ARROWDOWN, "navy", "navy")

        EVT_STC_UPDATEUI(self,    ID, self.OnUpdateUI)
        EVT_STC_MARGINCLICK(self, ID, self.OnMarginClick)

        self.StyleClearAll()

        coding_font = wx.Font(16, wx.DEFAULT, wx.NORMAL, wx.NORMAL, underline=False, faceName="Consolas", encoding=wx.FONTENCODING_DEFAULT)

        self.StyleSetFont(STC_STYLE_DEFAULT, coding_font)
        self.StyleSetFont(STC_STYLE_LINENUMBER, coding_font)
        self.StyleSetFont(STC_STYLE_CONTROLCHAR, coding_font)
        self.StyleSetFont(STC_STYLE_BRACELIGHT, coding_font)
        self.StyleSetFont(STC_STYLE_BRACEBAD, coding_font)
    
        self.StyleSetFont(STC_P_DEFAULT, coding_font)
        self.StyleSetFont(STC_P_COMMENTLINE, coding_font)
        self.StyleSetFont(STC_P_NUMBER, coding_font)
        self.StyleSetFont(STC_P_CHARACTER, coding_font)
        self.StyleSetFont(STC_P_STRING, coding_font)
        self.StyleSetFont(STC_P_WORD, coding_font)
        self.StyleSetFont(STC_P_TRIPLE, coding_font)
        self.StyleSetFont(STC_P_TRIPLEDOUBLE, coding_font)
        self.StyleSetFont(STC_P_CLASSNAME, coding_font)
        self.StyleSetFont(STC_P_DEFNAME, coding_font)
        self.StyleSetFont(STC_P_OPERATOR, coding_font)
        self.StyleSetFont(STC_P_COMMENTBLOCK, coding_font)
        self.StyleSetFont(STC_P_STRINGEOL, coding_font)
        self.StyleSetFont(STC_P_IDENTIFIER, coding_font)#,fore:#FF00FF")

        self.StyleSetSpec(STC_STYLE_LINENUMBER,  "back:#C0C0C0")
        self.StyleSetSpec(STC_STYLE_BRACELIGHT,  "fore:#FFFFFF,back:#0000FF,bold")
        self.StyleSetSpec(STC_STYLE_BRACEBAD,    "fore:#000000,back:#FF0000,bold")
        
        # Python styles
        # White space        
        self.StyleSetSpec(STC_P_DEFAULT, "fore:#808080")
        # Comment
        self.StyleSetSpec(STC_P_COMMENTLINE, "fore:#007F00")
        # Number
        self.StyleSetSpec(STC_P_NUMBER, "fore:#007F7F")
        # String
        self.StyleSetSpec(STC_P_STRING, "fore:#7F007F,italic")
        # Single quoted string
        self.StyleSetSpec(STC_P_CHARACTER, "fore:#7F007F,italic")
        # Keyword
        self.StyleSetSpec(STC_P_WORD, "fore:#00007F,bold")
        # Triple quotes
        self.StyleSetSpec(STC_P_TRIPLE, "fore:#7F0000")
        # Triple double quotes
        self.StyleSetSpec(STC_P_TRIPLEDOUBLE, "fore:#7F0000")
        # Class name definition
        self.StyleSetSpec(STC_P_CLASSNAME, "fore:#0000FF,bold,underline")
        # Function or method name definition
        self.StyleSetSpec(STC_P_DEFNAME, "fore:#007F7F,bold")
        # Operators
        self.StyleSetSpec(STC_P_OPERATOR, "bold")
        # Identifiers
        # self.StyleSetSpec(STC_P_IDENTIFIER, "bold")#,fore:#FF00FF")
        # Comment-blocks
        self.StyleSetSpec(STC_P_COMMENTBLOCK, "fore:#7F7F7F")
        # End of line where string is not closed
        self.StyleSetSpec(STC_P_STRINGEOL, "fore:#000000,back:#E0C0E0,eolfilled")

        self.SetCaretForeground("BLUE")

        EVT_KEY_UP(self, self.OnKeyPressed)


    def OnKeyPressed(self, event):
        key = event.KeyCode
        if key == 32 and event.ControlDown():
            pos = self.GetCurrentPos()
            # Tips
            if event.ShiftDown():
                self.CallTipSetBackground("yellow")
                self.CallTipShow(pos, 'param1, param2')
            # Code completion
            else:
                self.AutoCompSetIgnoreCase(True)
                self.AutoCompShow(0, string.join(keyword.kwlist))
                self.AutoCompSelect('br')
        else:
            event.Skip()

        if key == wx.WXK_RETURN:
          n = self.GetCurrentLine()
          if n==0:
            pass
          else:
            pline = self.GetLine(n-1)
            p = re.compile("\[.*for\s.*]")
            res = p.search(pline)
            if res == None:
                p = re.compile("def\s|for\s|if\s|else:|else\s|while\s")
                res = p.search(pline)
                self.autoindent( res )
            else:
                pass
        else:
            event.Skip()


    def autoindent(self, res):
      indent=""
      n=0
      l = self.GetLine(self.GetCurrentLine())
      col = self.GetColumn(self.GetCurrentPos())
      if col!=0 and l[col]!=u" ":
          return
      
      if res == None:
          l = self.GetCurrentLine()
          pline = self.GetLine(l-1)
          p = re.compile("[\S\r\n]")
          res = p.search(pline)
          if res != None:
            n = res.start()
      else:
        n = res.start()+self.GetTabWidth()
      indent=""
      for i in range(n):
          indent += " "
      self.InsertText(self.GetCurrentPos(),indent)
      self.GotoPos(self.GetCurrentPos()+n)


    def OnUpdateUI(self, evt):
        # check for matching braces
        braceAtCaret = -1
        braceOpposite = -1
        charBefore = None
        caretPos = self.GetCurrentPos()
        if caretPos > 0:
            charBefore = self.GetCharAt(caretPos - 1)
            styleBefore = self.GetStyleAt(caretPos - 1)

        # check before
        if charBefore and chr(charBefore) in "[]{}()" and styleBefore == STC_P_OPERATOR:
            braceAtCaret = caretPos - 1

        # check after
        if braceAtCaret < 0:
            charAfter = self.GetCharAt(caretPos)
            styleAfter = self.GetStyleAt(caretPos)
            if charAfter and chr(charAfter) in "[]{}()" and styleAfter == STC_P_OPERATOR:
                braceAtCaret = caretPos

        if braceAtCaret >= 0:
            braceOpposite = self.BraceMatch(braceAtCaret)

        if braceAtCaret != -1  and braceOpposite == -1:
            self.BraceBadLight(braceAtCaret)
        else:
            self.BraceHighlight(braceAtCaret, braceOpposite)

    def OnMarginClick(self, evt):
        # fold and unfold as needed
        if evt.GetMargin() == 2:
            if evt.GetShift() and evt.GetControl():
                self.FoldAll()
            else:
                lineClicked = self.LineFromPosition(evt.GetPosition())
                if self.GetFoldLevel(lineClicked) & STC_FOLDLEVELHEADERFLAG:
                    if evt.GetShift():
                        self.SetFoldExpanded(lineClicked, True)
                        self.Expand(lineClicked, True, True, 1)
                    elif evt.GetControl():
                        if self.GetFoldExpanded(lineClicked):
                            self.SetFoldExpanded(lineClicked, False)
                            self.Expand(lineClicked, False, True, 0)
                        else:
                            self.SetFoldExpanded(lineClicked, True)
                            self.Expand(lineClicked, True, True, 100)
                    else:
                        self.ToggleFold(lineClicked)


    def FoldAll(self):
        lineCount = self.GetLineCount()
        expanding = True

        # find out if we are folding or unfolding
        for lineNum in range(lineCount):
            if self.GetFoldLevel(lineNum) & STC_FOLDLEVELHEADERFLAG:
                expanding = not self.GetFoldExpanded(lineNum)
                break;

        lineNum = 0
        while lineNum < lineCount:
            level = self.GetFoldLevel(lineNum)
            if level & STC_FOLDLEVELHEADERFLAG and \
               (level & STC_FOLDLEVELNUMBERMASK) == STC_FOLDLEVELBASE:

                if expanding:
                    self.SetFoldExpanded(lineNum, True)
                    lineNum = self.Expand(lineNum, True)
                    lineNum = lineNum - 1
                else:
                    lastChild = self.GetLastChild(lineNum, -1)
                    self.SetFoldExpanded(lineNum, False)
                    if lastChild > lineNum:
                        self.HideLines(lineNum+1, lastChild)

            lineNum = lineNum + 1



    def Expand(self, line, doExpand, force=False, visLevels=0, level=-1):
        lastChild = self.GetLastChild(line, level)
        line = line + 1
        while line <= lastChild:
            if force:
                if visLevels > 0:
                    self.ShowLines(line, line)
                else:
                    self.HideLines(line, line)
            else:
                if doExpand:
                    self.ShowLines(line, line)

            if level == -1:
                level = self.GetFoldLevel(line)

            if level & STC_FOLDLEVELHEADERFLAG:
                if force:
                    if visLevels > 1:
                        self.SetFoldExpanded(line, True)
                    else:
                        self.SetFoldExpanded(line, False)
                    line = self.Expand(line, doExpand, force, visLevels-1)

                else:
                    if doExpand and self.GetFoldExpanded(line):
                        line = self.Expand(line, True, force, visLevels-1)
                    else:
                        line = self.Expand(line, False, force, visLevels-1)
            else:
                line = line + 1;

        return line
