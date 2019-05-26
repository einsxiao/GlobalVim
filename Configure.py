#!/usr/bin/env python
# -*- coding: utf-8 -*-

from res import *
add_lang('en',{
    '_play_ratio':'Replay Ratio',
    '_macro_label':'Alias',
    '_operation_sequence':'Operation Sequence',

})
add_lang('zh',{
    '_operation_sequence':'操作序列',
    '_macro_label':'别名',
    '_play_ratio':'重放速率',
})

str2bool = lambda v: True if v == 'True' else False
class GeeKeyDialog( wx.Dialog ):
    def __init__(self,config,*args,**kwargs):
        self.button = {}
        self.checkbox = {}
        self.combobox = {}
        self.textctrl = {}
        self.textWidth = 150; self.contWidth = 350; self.height = 500; self.yPos = 10; self.H = 30
        self.textPanel = None
        self.contPanel = None
        self.sizer = None
        self.config = config
        #log.log('geekeydialog created with config = ',self.config)
        ############################
        if 'height' in self.config: self.height = self.config['height'] 
        wx.Dialog.__init__(self,*args,**kwargs)

        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.textPanel = wx.Panel(self,size=(self.textWidth,self.height) )
        self.textPanel.SetBackgroundColour( "#E5E5E5" )

        self.contPanel = wx.Panel(self,size=(self.contWidth,self.height) )
        self.bottomPanel = wx.Panel( self.contPanel, size=(self.contWidth, self.H), pos = (0.5*self.H, self.height - 2 * self.H ) )
        self.sizer.Add( self.textPanel )
        self.sizer.Add( self.contPanel )

        ##############################################################
        self.SetTitle( lt('_'+self.config['type']+'_to_key', self.config['name'] ) )
        ####################
        if self.config['type'] == 'function':
            self.addText( lt('_function_path') ); pos = self.contPos(); size = self.contSize()
            self.textctrl['value'] = wx.TextCtrl( self.contPanel,
                                                  pos = pos, size = size,
                                                  value = self.config['value'] )
            self.button['browse']= wx.Button( self.contPanel,
                                              pos = ( pos[0]+size[0],pos[1] ),size = ( 30,size[1] ),
                                              label = '...' )
            self.button['browse'].Bind( wx.EVT_BUTTON,self.function_OnBrowse )
            pass
        elif self.config['type'] == 'macro':

            self.addText( lt('_operation_sequence')); pos = self.contPos(); size = self.contSize(y=2*self.H)
            self.textctrl['value'] = wx.TextCtrl( self.contPanel,
                                                  pos = pos, size = size,
                                                  value = self.config['value'],
                                                  style = wx.TE_RICH|wx.TE_MULTILINE|wx.TE_BESTWRAP,
            )

            self.addSpacer(2*self.H)
            self.addText( lt('_macro_label') ); pos = self.contPos(); size = self.contSize()
            self.textctrl['label'] = wx.TextCtrl( self.contPanel,
                                                  pos = pos, size = (size[0]/2,size[1]),
                                                  value = self.config['label']
            )
         
            self.addSpacer()
            self.addText( lt('_play_ratio') ); pos = self.contPos(); size = self.contSize()
            self.textctrl['ratio'] = wx.TextCtrl( self.contPanel,
                                                  pos = pos, size = (size[0]/4,size[1]),
                                                  value = str( self.config['ratio'] ),
            )
            self.textctrl['label'].SetFocus()
            pass
        else: raise Exception("type unknown")
        
        ##################
        ### buttons
        self.button['ok'] = wx.Button(self.bottomPanel, label=lt("OK"),pos=(self.H,0),size=(80,self.H ) )
        self.button['cancel'] = wx.Button(self.bottomPanel, label=lt("Cancel"),pos=(2*self.H+80,0),size=(80,self.H) )
        self.button['ok'].Bind( wx.EVT_BUTTON,self.OnOk )
        self.button['cancel'].Bind( wx.EVT_BUTTON, self.OnCancel)
        ##################
        self.SetSizerAndFit( self.sizer )
        self.Bind( wx.EVT_CHAR_HOOK, self.OnKeyUP)
        pass
    ###################################################################################
    def OnKeyUP(self,evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnCancel(evt)
            pass
        if evt.GetKeyCode() == wx.WXK_RETURN:
            self.OnOk(evt)
            pass
        evt.Skip()
        pass
    
    def contSize(self,x=None,y=None): return (self.contWidth - 3*self.H if not x else x, self.H if not y else y)
    def contPos(self): return (1.5*self.H, self.yPos)
    def addText(self,label):
        self.yPos += self.H
        text = wx.StaticText(self.textPanel,label=label, pos=(0,self.yPos), size=(self.textWidth-self.H, self.H ), style= wx.ALIGN_RIGHT )
        return text

    def addSpacer(self,h=None):
        self.yPos += self.H if not h else h
        pass

    def addCheckBox(self,key,label):
        self.checkbox[key] = wx.CheckBox(self.contPanel,label = label,size= self.contSize(), pos = self.contPos() )
        self.checkbox[key].SetValue( str2bool( self.config[key] ) )
        pass

    def function_OnBrowse(self,evt):
        fdl = wx.FileDialog(self, lt("_choose_program"),
                            wildcard="Executables (*.exe)|*.exe|All (*.*)|*.*",
                            style=wx.FD_OPEN|wx.FD_FILE_MUST_EXIST|wx.FD_CHANGE_DIR) 
        fdl.SetDirectory( self.config['value'] )
        if fdl.ShowModal() == wx.ID_OK: 
            self.config['value' ] = fdl.GetPath()
            self.textctrl['value'].SetLabel( fdl.GetPath() )
            pass
        fdl.Destroy()
        pass
    
    def OnCancel(self,evt):
        self.EndModal( wx.ID_CANCEL )
        pass

    def OnOk(self,evt):
        for key,value in self.checkbox.items():
            self.config[key] = str( value.GetValue() )
            pass

        for key,value in self.textctrl.items():
            self.config[key] = value.GetValue()
            pass

        if self.config['type'] == 'function':
            self.config['label'] = os.path.basename( self.config['value'] )
            pass

        if self.config['type'] == 'macro':
            self.config['ratio'] = str( toFloat( self.config['ratio'],1 ) )
            pass

        self.EndModal( wx.ID_OK )
        pass

    def GetConfig(self):
        return self.config
    
    pass

class ConfigDialog( wx.Dialog):

    def __init__(self,config,*args,**kwargs):
        self.config = None
        self.button = {}
        self.checkbox = {}
        self.combobox = {}
        self.textWidth = 150;
        self.contWidth = 350;
        self.height = 500;
        self.yPos = 10;
        self.H = 30
        self.textPanel = None
        self.contPanel = None
        self.sizer = None

        self.config = config
        wx.Dialog.__init__(self,*args,**kwargs)
        self.SetTitle( lt('_configure') )
        self.sizer = wx.BoxSizer(wx.HORIZONTAL)
        self.textPanel = wx.Panel(self,size=(self.textWidth,self.height) )
        self.textPanel.SetBackgroundColour( "#E5E5E5" )
        self.contPanel = wx.Panel(self,size=(self.contWidth,self.height) )
        self.bottomPanel = wx.Panel( self.contPanel, size=(self.contWidth, self.H), pos = (0.5*self.H, self.height - 2 * self.H ) )
        self.sizer.Add( self.textPanel )
        self.sizer.Add( self.contPanel )

        ####################
        ####################
        ##########enable geekey
        self.addText( lt('Geekey Enabled') )
        self.addCheckBox('geekeyenabled',lt('Enable GeeKey HotKey system') )
        self.addSpacer()

        self.addText( lt('GeeKey Mode') )
        self.combobox['geekeymode'] = wx.ComboBox( self.contPanel,
                                                 pos = self.contPos(),
                                                 size = self.contSize(),
                                                 choices = [
                                                     lt('block'),
                                                     lt('longblock'),
                                                 ] )
        self.combobox['geekeymode'].SetValue( lt('block') if self.config['geekeymode'] in ('block','Block','阻塞') else lt('longblock') )
        self.addText( '' )

        wx.StaticText(
            self.contPanel, pos=self.contPos(), size=(self.contWidth - 3*self.H,self.H*1.5),
            label = lt("'block' mode blocks original function. While 'longblock' mode blocks only when pressed longer or in combo keys.")
        )

        self.addSpacer()
        ##########language
        self.addText( lt('_language') )
        self.combobox['language'] = wx.ComboBox( self.contPanel,
                                                 pos = self.contPos(),
                                                 size = self.contSize(),
                                                 choices = ['中文','English'] )
        self.combobox['language'].SetValue( 'English' if self.config['language'] in ('en','en_US') else '中文' )
        #self.combobox['language'].Bind( wx.EVT_COMBOBOX, self.OnLanguageSelected )
        self.addSpacer()
        ##########default cat
        self.addText( lt('_general') )
        self.addCheckBox('startup',lt('_startup') )

        # self.addText( lt('') )
        # self.addCheckBox('runasadmin',lt('_runasadmin') )

        # self.addText( lt('') )
        # self.addCheckBox('startshow',lt('_startshow') )

        self.addText( lt('') )
        self.addCheckBox('startautocomplete',lt('_start_autocomplete') )

        self.addText( lt('') )
        self.addCheckBox('startvim',lt('_startvim') )

        self.addText( lt('') )
        self.addCheckBox('doubleclickfix',lt('_doubleclickfix') )

        self.addText( lt('') )
        self.addCheckBox('printkeyevent',lt('_print_key_event') )

        self.addSpacer()

        ##########Acount
        #self.addText( lt('_account') )

        ##################
        ### buttons
        self.button['ok'] = wx.Button(self.bottomPanel, label=lt("OK"),pos=(self.H,0),size=(80,self.H ) )
        self.button['cancel'] = wx.Button(self.bottomPanel, label=lt("Cancel"),pos=(2*self.H+80,0),size=(80,self.H) )
        self.button['ok'].Bind( wx.EVT_BUTTON,self.OnOk )
        self.button['cancel'].Bind(wx.EVT_BUTTON, self.OnCancel)
        ##################
        self.SetSizerAndFit( self.sizer )
        self.Bind( wx.EVT_CHAR_HOOK, self.OnKeyUP)
        pass
    
    def contSize(self):return (self.contWidth - 3*self.H, self.H)
    def contPos(self): return (1.5*self.H, self.yPos)

    def addConText(self,cont,height):
        text = wx.StaticText(self.contPanel,label=cont, pos=self.contPos(), size=self.contSize(y=height*self.H) )
        return text

    def addText(self,label):
        self.yPos += self.H
        text = wx.StaticText(self.textPanel,label=label, pos=(0,self.yPos), size=(self.textWidth-self.H, self.H ), style= wx.ALIGN_RIGHT )
        return text

    def addSpacer(self,h=None):
        self.yPos += self.H if not h else h

    def addCheckBox(self,key,label):
        self.checkbox[key] = wx.CheckBox(self.contPanel,label = label,size= self.contSize(), pos = self.contPos() )
        self.checkbox[key].SetValue( str2bool( self.config[key] ) )
        pass

    def OnCancel(self,evt):
        self.EndModal( wx.ID_CANCEL )
        pass

    def OnOk(self,evt):
        for key,value in self.checkbox.items():
            self.config[key] = str( value.GetValue() )
            pass

        self.config['language'] = 'en' if  self.combobox['language'].GetValue() == 'English' else 'zh'
        self.config['geekeymode'] = 'block' if self.combobox['geekeymode'].GetValue() in ('block','阻塞') else 'longblock'
        self.EndModal(wx.ID_OK)
        pass

    def GetConfig(self):
        return self.config

    def OnKeyUP(self,evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE: self.OnCancel(evt)
        if evt.GetKeyCode() == wx.WXK_RETURN: self.OnOk(evt)
        evt.Skip()
        pass
    
    pass



