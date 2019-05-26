#!/usr/bin/env python
# -*- coding: utf-8 -*-

from res import *
add_lang('zh',{
    '_manual':'功能手册',

    '_geekey':"GeeKey热键选择",
    '_geekey_cont':"可以点击主界面左上角GK按钮来选择任意键作为热键.",

    "_overview":"概诉",
    '_overview_cont':"""软件提供全局vim按键绑定和功能, 支持模式编辑/寄存器/宏/正则替换.
软件提供强大快捷的GeeKey热键方案, 能快速高效完成各种操作. 绑定的内容通过主面板编辑.
项目主页: """,

    "_esc":'空档状态退出',
    "_esc_cont":'Esc     -取消空档状态',

    '_oper_record':'快捷宏',
    '_oper_record_cont':"""GeeKey+q 【X】     -录制宏到按键X
GeeKey+【X】      -执行X绑定宏
GeeKey+q space 【X】      -录制宏到按键X的空档绑定
GeeKey+space 【X】      -执行X的空档绑定宏
GeeKey+q        -结束录制 """,

    '_quick_key':'快捷按键',
    '_quick_key_cont':"""GeeKey+【X】      -模拟X的绑定按键 """,

    '_quick_text/app':'快捷文本/应用',
    '_quick_text/app_cont':"""GeeKey+【X】      -发送绑定文本到当前编辑区/启动绑定应用
GeeKey+Space 【X】       -触发空档绑定文本/应用""",

    '_quick_repeat':'快速重复',
    '_quick_repeat_cont':"""GeeKey+Space 【数字N】 【X】       -操作X被重复N次""",

    '_auto_complete':'自动补全',
    '_auto_complete_cont':"""GeeKey+Space Tab      -开启/关闭自动补全功能 """,

    '_panel_quickkey':'面板呼出',
    '_panel_quickkey_cont':"""GeeKey+Space Space      -呼出/隐藏主程序面板 """,

    '_panel_vim':'vim状态切换',
    '_panel_vim_cont':"""GeeKey+v      -关闭/开启vim模式 """,
})
add_lang('en',{
    "_esc":'Quit Spacing State',
    "_esc_cont":'Esc     -quit spacing state.',

    '_geekey':"GeeKey select",
    '_geekey_cont':"HotKey can be changed by click GK button on main panel.",

    "_overview":"Overview",
    '_overview_cont':"""The application provides Vim keybindings and functions system wide with registers/macro recording/pattern substituting supported.\n
The application also provides the powerfull geekey hotkey solution which can be very quick and efficient. All bindings can be revised by application panel.
More detail instructions please visit project index: """,

    '_manual':'Manual',

    '_oper_record':'Quick Macro',
    '_oper_record_cont':"""GeeKey+q 【X】      -record macro of X
GeeKey+【X】      -execute binding macro of X
GeeKey+q space 【X】)      -record spacing binding macro of X
GeeKey+space 【X】     -execute spacing binding macro of X
GeeKey+q      -stop recording""",

    '_quick_key':'Quick Key',
    '_quick_key_cont':"""GeeKey+【X】      -simulate the binding key.""",

    '_quick_text/app':'Quick Text/Application',
    '_quick_text/app_cont':"""GeeKey+【X】      -send binding text to editing area/launch binding application
GeeKey+Space K      -trigger spacing binding text/application.""",

    '_quick_repeat':'Quick Repeat',
    '_quick_repeat_cont':"""GeeKey+Space 【N】 【X】      -operation X will be repeated N Times.""",

    '_auto_complete':'Auto Complete',
    '_auto_complete_cont':"""GeeKey+Space Tab      -turn on/off the auto-complete mode.""",

    '_panel_quickkey':'Main Panel',
    '_panel_quickkey_cont':"""GeeKey+Space Space      -show/hide the main panel.""",


    '_panel_vim':'Vim State Switch',
    '_panel_vim_cont':"""GeeKey+v      -switch vim on/off"""

})


class TutorialDialog( wx.Dialog):

    def __init__(self,*args,**kwargs):
        self.config = None
        self.button = {}
        self.checkbox = {}
        self.combobox = {}
        self.textWidth = 150; self.contWidth = 555; self.height = 755; self.yPos = 10; self.H = 30
        self.textPanel = None
        self.contPanel = None
        self.sizer = None

        wx.Dialog.__init__(self,*args,**kwargs)
        self.SetTitle( lt('_manual') )
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.textPanel = wx.Panel(self,size=(self.textWidth,self.height) )
        self.textPanel.SetBackgroundColour( "#E5E5E5" )
        self.contPanel = wx.Panel(self,size=(self.contWidth,self.height) )
        self.bottomPanel = wx.Panel( self.contPanel, size=(self.contWidth, self.H), pos = (0, self.height - 2 * self.H ) )
        self.sizer.Add( self.textPanel )
        self.sizer.Add( self.contPanel )

        ####################
        ####################

        self.addText( lt('_overview') )
        self.addContText( lt('_overview_cont')+INFO['HomePage'], GetMap('color','function_key'), 3.5 )

        self.addText( lt('_geekey') )
        self.addContText( lt('_geekey_cont'), GetMap('color','geekey'),1.0 )

        self.addText( lt('_panel_vim') )
        self.addContText( lt('_panel_vim_cont'), GetMap('color','function_button') )

        self.addText( lt('_quick_repeat') )
        self.addContText( lt('_quick_repeat_cont'),GetMap('color','edit_button'),1.0 )

        self.addText( lt('_esc') )
        self.addContText( lt('_esc_cont'),GetMap('color','function_button'),1.0 )

        self.addText( lt('_oper_record') )
        self.addContText( lt('_oper_record_cont'), GetMap('color','macro_key'), 4.0 )
        
        self.addText( lt('_quick_key') )
        self.addContText( lt('_quick_key_cont'), GetMap('color','menu_key') )

        self.addText( lt('_quick_text/app') )
        self.addContText( lt('_quick_text/app_cont'), GetMap('color','text_key'),1.8 )

        self.addText( lt('_auto_complete') )
        self.addContText( lt('_auto_complete_cont'), GetMap('color','function_key') )

        self.addText( lt('_panel_quickkey') )
        self.addContText( lt('_panel_quickkey_cont'), GetMap('color','function_button') )
        
        # self.addText( lt('_panel_capslock') )
        # self.addContText( lt('_panel_capslock_cont'), GetMap('color','function_button') )

        ##################
        self.SetSizerAndFit( self.sizer )
        pass
    
    def contSize(self,height=1):return (self.contWidth - 3*self.H, self.H*height)
    def contPos(self): return (1.5*self.H, self.yPos)

    def addText(self,label):
        self.yPos += self.H
        text = wx.StaticText(self.textPanel,label=label, pos=(0,self.yPos), size=(self.textWidth-self.H, self.H ), style= wx.ALIGN_RIGHT )
        return text

    def addSpacer(self,height=1):
        self.yPos += self.H *height
        pass

    def addContText(self,cont,color='#BFEFFF',height=1): 
        txt = wx.TextCtrl( self.contPanel, wx.ID_ANY, cont,
                           size = self.contSize(height),
                           pos = self.contPos(),
                           style = wx.TE_RICH|wx.TE_READONLY|wx.TE_WORDWRAP|
                           wx.TE_AUTO_URL|wx.TE_MULTILINE|wx.NO_BORDER,
        )
        txt.SetBackgroundColour(color)
        txt.Bind(wx.EVT_TEXT_URL, self.OnUrlClicked)

        self.addSpacer( height - 0.4 )
        pass

    def OnUrlClicked(self,evt):
        mevt = evt.GetMouseEvent()
        if mevt.LeftDown():
            webbrowser.open( INFO['HomePage'] )
        pass

    pass

