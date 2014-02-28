#!/usr/bin/env python
# -*- encoding: utf-8 -*-
# vim: set et sw=4 ts=4 sts=4 ff=unix fenc=utf8:
# Author: Jeswang<i@binux.me>
#         http://binux.me
# Created on 2014-02-16 22:24:20

import bs4
from python_stc import PythonSTC
from project_module import ProjectModule
import wx
import wx.html2 as html2

BORDER = 5

CHANGE_COLOR_TEMPLATE = """\
$(item).css({"border-color": "%s", 
 "border-width":"%s", 
 "border-style":"solid"});
"""

CHANGE_COLOR_TEMPLATE2 = """\
var selected = document.evaluate('%s', document, null, XPathResult.ANY_TYPE, null ).iterateNext();
selected.style.border="%s solid %s";
"""

SAMPLE_HANDLER = """\
#!/usr/bin/env python
# -*- encoding: utf-8 -*-

from base_handler import *

class Handler(BaseHandler):
    def run(self):
        return self.soup.find_all('a')
"""


class MainWindow(wx.Frame):
    def __init__(self, parent, title):

        wx.Frame.__init__(self, parent, title=title , size=(1200,800))
        self.SetFont(wx.Font(12, wx.FONTFAMILY_MODERN, wx.NORMAL, wx.NORMAL, False))

        panel = wx.Panel(self)

        # url 输入框
        url_box = wx.BoxSizer(wx.HORIZONTAL)

        self.url_text = wx.TextCtrl(panel, -1, "")
        url_box.Add(self.url_text, 1, flag=wx.EXPAND|wx.ALL|wx.ALIGN_LEFT|wx.CENTER, border=BORDER)

        self.go_button = wx.Button(panel, 10, u"Go")
        self.Bind(wx.EVT_BUTTON, self.OnClickGo, self.go_button)

        url_box.Add(self.go_button, 0, flag=wx.ALL|wx.ALIGN_RIGHT, border=BORDER)

        # Browser 和 Editor
        splitter = wx.SplitterWindow(panel, -1, style = wx.SP_LIVE_UPDATE)

        # Browser
        self.browser = html2.WebView.New(splitter, -1, style=wx.EXPAND|wx.ALL, size=(500,-1))
        self.Bind(html2.EVT_WEB_VIEW_LOADED, self.LoadHTMLFihish, self.browser)
        
        # Editor
        coding_panel = wx.Panel(splitter);

        self.editor  = PythonSTC(coding_panel, -1)
        self.run_button = wx.Button(coding_panel, -1, u"Run")
        self.Bind(wx.EVT_BUTTON, self.OnClickRun, self.run_button)

        coding_box = wx.BoxSizer(wx.VERTICAL)
        coding_box.Add(self.editor, 1, flag=wx.ALL|wx.EXPAND, border=BORDER)
        coding_box.Add(self.run_button, 0, flag=wx.ALL|wx.EXPAND, border=BORDER)
        
        coding_panel.SetSizer(coding_box)
        coding_panel.Layout()

        splitter.SplitVertically(self.browser, coding_panel, -450)

        box = wx.BoxSizer(wx.VERTICAL)
        box.Add(url_box, 0, wx.EXPAND|wx.TOP, 0)
        box.Add(splitter, 1, wx.EXPAND, 10)

        panel.SetSizer(box)
        panel.Layout()

        self.editor.SetText(SAMPLE_HANDLER)

        self.loadFinish = 0;
        self._history_high_light = [];

    def OnClickGo(self, event):
        url = self.url_text.GetValue()
        self.browser.LoadURL(url) 

        self.loadFinish = 0;
        self._history_high_light = []

        print('Go: ' + url);

    def LoadHTMLFihish(self, event):
        print('Finish loading.')
        self.loadFinish = 1;
        # Don't load js anymore
        # self.browser.RunScript(open('js/jquery-1.11.0.min.js').read());
        # self.browser.RunScript(open('js/jquery.xpath.js').read());

    def OnClickRun(self, event):
        print('Run: ');

        # Run code in editor
        script = self.editor.GetValue()
        if isinstance(script, unicode):
            script = script.encode('utf8')

        if self.loadFinish == 0:
            print('Still loading')
            return

        source = self.browser.GetPageSource()

        self.soup = bs4.BeautifulSoup(source)

        # 有的网页省略了 tbody 这个标签，所以粗略地判断是否是这种情况
        if self.soup.find('tbody') is None and self.soup.find('table') is not None:
            self.tbody_tag = 1

        module = ProjectModule("HelperHandler", script)
        module.rethrow()

        _class = module.get('__class__')
        assert _class is not None, "need BaseHandler in project module"
        instance = _class()._init(self.soup)
        result = instance.run()

        self.RemoveHighLight()

        if result is not None:
            for i in result:
                self.Highlight(i)

    def Highlight(self, part):
        xpath = self.GetLocation(part)
        self._history_high_light.append(xpath)

        # Old solution
        # js_string = 'var item = $(document).xpath(\"' + xpath + '\")' + CHANGE_COLOR_TEMPLATE % ('red', '1px')
        
        js_string = CHANGE_COLOR_TEMPLATE2 % (xpath, '1px', 'red')
        print(js_string)
        self.browser.RunScript(js_string);
        pass

    def RemoveHighLight(self):
        for xpath in self._history_high_light:

            # Old solution
            # js_string = 'var item = $(document).xpath(\"' + xpath + '\")' + CHANGE_COLOR_TEMPLATE % ('red', '0px')
            js_string = CHANGE_COLOR_TEMPLATE2 % (xpath, '0px', 'red')

            self.browser.RunScript(js_string);
        self._history_high_light = []
        pass

    def GetLocation(self, part):
        result = ""

        count = 1
        parents = part.parents
        for parent in parents:
            # print(parent.name + self.GetBigBrother(parent))
            if parent.name == 'table' and self.tbody_tag == 1:
                result = '/*[1]' + result

            result = '/*[' + self.GetBigBrother(parent) + ']' + result
            
            if parent.name == 'html':
                break;

        result = result + '/*[' + self.GetBigBrother(part) + ']'

        return result

    def GetBigBrother(self, part):
        result = 1;
        # print 'self ' + part.name
        while part.previous_sibling is not None:
            if isinstance(part.previous_sibling, bs4.NavigableString):
                part = part.previous_sibling
                continue
            result = result + 1
            part = part.previous_sibling
        return str(result)

if __name__ == '__main__': 
    app = wx.App() 
    dialog = MainWindow(None, "Soup Helper") 
    dialog.browser.LoadURL("http://www.v2ex.com") 
    dialog.Show() 
    app.MainLoop() 
