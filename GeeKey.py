#!/usr/bin/env python
# -*- coding: utf-8 -*-
import threading
import requests
import importlib
import shutil
from res import *
#from AutoComplete import *
from Configure import *
from Tutorial import *
from Vim import *


def DialogShow(header,message,geekey=None):
    dlg = wx.MessageDialog(geekey,message,header,wx.OK|wx.ICON_NONE);
    dlg.ShowModal()
    dlg.Destroy()
    pass

def GetNetVersion():
    try:
        res = requests.get( INFO['VersionSrc'] )
        net_version = res.headers['version']
        INFO['NetVersion'] = net_version
    except Exception as e:
        INFO['NetVersion'] = None
        pass
    INFO['version_processing'] = False

INFO['check_timer'] = None
def CheckUpdate(force_appear=True,geekey=None):
    #log.log('checking')
    if INFO['version_processing']:
        #log.log('wait and check again')
        if INFO['check_timer']: INFO['check_timer'].Stop()
        INFO['check_timer'] = WxCallLater(1,CheckUpdate,force_appear = force_appear, geekey=geekey)
        return 
    #log.log('compare')
    INFO['check_timer'] = None
    try: 
        current_version = INFO['Version']
        new_version = INFO['NetVersion']
        if not new_version: raise Exception('failed to get network version information')
        if current_version < new_version:
            #log.log('new version available')
            style = wx.OK|wx.CANCEL|wx.ICON_NONE
            dlg = wx.MessageDialog(geekey,lt('_new_version_detail'),lt('_new_version_available'),style = style, )
            dlg.SetSize(800,500)
            dlg.SetOKCancelLabels(lt("Update"),lt("Cancel") )
            if  dlg.ShowModal() == wx.ID_OK :
                webbrowser.open( INFO['UpdateAddr'] )
                pass
            dlg.Destroy()
            pass
        else:
            if force_appear:
                DialogShow(lt("_version_fine"),lt("_version_fine_detail"),geekey=geekey )
                pass
            pass
        pass
    except Exception as e:
        log.log(lt("Check update failed for: {0}",e))
        #geekey.Log("Check update failed for: {0}".format(e) )
        if force_appear:
            style = wx.OK|wx.CANCEL|wx.ICON_NONE
            dlg = wx.MessageDialog(geekey,lt('_network_unavailable_detail'),lt('_network_unavailable'),style = style, )
            dlg.SetSize(800,500)
            dlg.SetOKCancelLabels(lt("_to_index"),lt("Cancel") )
            if  dlg.ShowModal() == wx.ID_OK :
                webbrowser.open(  lt(INFO['HomePage']) )
                pass
            pass
        pass

    #log.log("check update finished")
    pass

class LocalTaskBarIcon( wx.adv.TaskBarIcon ):
    def __init__(self,frame):
        wx.adv.TaskBarIcon.__init__(self)
        self.frame = frame
        self.SetIcon( wx.Icon( bitmapFromBase64(image_logo.img) ), lt('_title_this') );
        self.Bind( wx.adv.EVT_TASKBAR_LEFT_DCLICK, self.OnTaskBarLeftDClick )
        self.Bind( wx.adv.EVT_TASKBAR_RIGHT_UP, self.OnRightClick )

        self.menu = wx.Menu()

        self.configure_menu =  self.menu.Append(wx.ID_ANY,lt('_configure_menu') )
        self.Bind(wx.EVT_MENU, self.frame.OnConfigure, self.configure_menu )

        self.loadfrom_menu = self.menu.Append(wx.ID_ANY, lt('_loadfrom_menu'))
        self.Bind(wx.EVT_MENU, self.frame.OnLoadFrom, self.loadfrom_menu  )

        self.saveas_menu =  self.menu.Append(wx.ID_ANY,lt('_saveas_menu'))
        self.Bind(wx.EVT_MENU, self.frame.OnSaveAs,self.saveas_menu)

        self.exit_menu = self.menu.Append(wx.ID_EXIT,lt('_exit_menu') )
        self.Bind(wx.EVT_MENU, self.frame.OnExit, self.exit_menu )

        pass

    def OnRightClick(self,evt):
        self.PopupMenu( self.menu )
        pass
        
    def OnTaskBarLeftDClick(self,evt):
        if self.frame.IsIconized():
            self.frame.Iconize(False)
            self.frame.Show(True)
            self.frame.Raise()
            pass
        else:
            self.frame.Iconize(True)
            self.frame.Show(False)
            pass
        pass
    pass

KeySize = ( 62,61 )
class GeeKeyFrame(wx.Frame):
    def __init__(self,parent,ID):
        self.initing = True
        #############################
        log.log_func = self.Log
        #############################
        self.size = (1000, 618)
        self.config = {}
        self.exe_dir = os.path.dirname( __file__ )
        self.exe_path= os.path.join( self.exe_dir,'GlobalVim.exe' )
        self.exe_data_dir = os.path.join( self.exe_dir, 'dat' )

        self.user_dir = os.path.expanduser('~')
        self.appdata_dir = os.path.join(self.user_dir,'AppData','Roaming','GlobalVim')

        self.home_dir = os.path.join( self.user_dir, 'GlobalVim' )
        self.data_dir = os.path.join(self.appdata_dir,'GlobalVim' )

        self.layout_file_name = 'default.ini'
        self.dictfile = os.path.join( self.data_dir, 'dict.dat')

        self.GeeKeyKeys = ['`','\\']
        self.geekey_mode = 'longblock'
        self.key_types = ['text','macro','edit','function']

        self.color_panels = {}
        self.buttons = {}
        self.isAdmin = False
        self.layout_list = [];
        self.layout_ButtonSize = ( 110,21 )
        self.layout_buttons = {}
        self.layout_buttons_drag = {}
        self.layout_combos = {}
        self.layout_selected = '1'
        self.key_buttons = {}  ### button for the whole key, also store those created in makeGeeKey
        self.key_combos = {}   ### combos for everything, including menukey and editkey
        self.menukey_selections = {} ## there is no specific keybutton for menu key
        self.rmenukey_selections = {}
        self.geekey_buttons = {}
        self.alt_buttons = {}
        self.geekey_alt_buttons = {}
        self.tutorial = None

        self.stateVarInit()

        #self.autoComplete = AutoComplete( parent,self,self.dictfile )
        #self.autoComplete.StateReset()
        self.vim = Vim(parent,self)
        self.image_size = 100
        self.images = [None]*self.image_size
        self.image_change_period = INFO['ImageChangePeriod']
        self.images[0] = ('xxx', bitmapFromBase64(image_mountain.img),'xxx', 0)
        self.images[1] = ('xxx', bitmapFromBase64(image_bridge.img),'xxx', 0)

        ##### UI init
        style = wx.DEFAULT_FRAME_STYLE |wx.NO_BORDER ;
        wx.Frame.__init__(self,parent,ID,lt('_title_this'),size = self.size,style = style )
        self.Centre()
        self.SetMinSize( self.size ); self.SetMaxSize( self.size )
        self.SetIcon( wx.Icon( bitmapFromBase64(image_logo.img) ) )

        self.makeMenuBar()
        self.makePanel()
        self.taskBarIcon = LocalTaskBarIcon( self )

        #####################################
        # hook keyboard events
        self.state_is_over = False
        self.hm = PyHook3.HookManager()
        self.hm.KeyDown = self.OnKeyboardEvent
        self.hm.KeyUp = self.OnKeyboardEvent
        self.hm.MouseAll = self.OnMouseEvent
        self.hm.HookMouse()
        self.UnHookAndHookKeyboard()

        ####################################
        ### init finished, start timmer and other operation
        self.timer = None
        self.paytimer = None

        #log.log('call later change image')
        self.image_index = -1
        ThreadCallLater(0.001,self.NetworkUpdateImage,0 )
        self.timer = WxCallLater(5, self.ChangeImage )
        #log.log('finish later change image')

        self.OnCheckUpdate(force_appear=False)

        #####################################
        # bindings 
        #######################################################
        ##### binding events
        self.Bind( wx.EVT_ICONIZE, self.OnIconize )
        self.Bind( wx.EVT_CLOSE, self.OnIconize )
        self.Bind( wx.EVT_PAINT, self.OnPaint ) 
        self.Bind( wx.EVT_CHAR_HOOK, self.OnKeyUP )

        self.image.Bind( wx.EVT_LEFT_DOWN, lambda evt: self.ShowLog() )
        self.image.Bind( wx.EVT_RIGHT_DOWN, self.OnImage )
        self.text.Bind( wx.EVT_LEFT_DCLICK, lambda evt: self.HideLog() )

        #####################################
        #### init configuration
        self.LoadConfig()
        self.ApplyConfig()
        

        # other start* configure
        # vim-mode
        if self.getConfig('startvim') == 'True':
            self.vim.state_switch('on')
        # auto-complete
        # if self.getConfig('startautocomplete') == 'True':
        #     self.autoComplete.SwitchState('on')

        ####
        self.initing = False

        pass

    def UnHookAndHookKeyboard(self):
        self.hm.HookKeyboard()
        pass

    def OnSave(self,event):
        """Save configuration to default.ini"""
        self.SaveConfig()
        #if self.layout_file_name != 'default.ini': self.SaveConfig(self.layout_file_name)
        pass

    def OnExit(self,event):
        """Close the frame, terminating the applications."""
        self.hm.UnhookKeyboard()
        self.hm.UnhookMouse()

        self.state_is_over = True
        self.vim.quit_visual_mode()

        self.SaveConfig()
        if self.paytimer: self.paytimer.Stop()
        if self.timer: self.timer.Stop()


        self.vim.Destroy() 

        self.taskBarIcon.Destroy()
        #self.autoComplete.Destroy()

        self.Destroy()
        pass

    def OnAbout(self,event):
        """Display an About Dialog"""
        aboutInfo = wx.adv.AboutDialogInfo()
        aboutInfo.SetName( lt("GlobalVim/GeeKey") )
        aboutInfo.SetVersion( INFO['Version'] )
        aboutInfo.SetCopyright( "(C) 2019" )
        aboutInfo.SetDescription( lt("_about_message") )
        wx.adv.AboutBox(aboutInfo);
        pass

    def OnHide(self,event):
        self.Hide()
        pass

    def startUpConfigApply(self):
        state = str2bool( self.getConfig('startup') )
        linkpath = os.path.join( winshell.startup(), 'GlobalVim'+'.lnk' );
        if state:
            if os.path.exists( linkpath ): os.remove( linkpath )
            winshell.CreateShortcut( Path = linkpath, Target = self.exe_path, Icon = (self.exe_path,0) )
            pass
        else:
            if os.path.exists( linkpath ): winshell.delete_file( linkpath )
            pass
        pass

    def OnIconize(self,event):
        self.Iconize(True)
        self.Show(False)
        pass

    def makeMenuBar(self):
        """
        A menu bar is composed of menus.
        """
        
        ##### menu bar start
        self.menuBar = wx.MenuBar()
        ##### operation
        self.settingsMenu = wx.Menu()
        self.configure_menu =  self.settingsMenu.Append(wx.ID_ANY,lt('_configure_menu') )
        self.Bind(wx.EVT_MENU, self.OnConfigure, self.configure_menu )
        self.exit_menu = self.settingsMenu.Append(wx.ID_EXIT,lt('exit_menu') )
        self.Bind(wx.EVT_MENU, self.OnExit, self.exit_menu )
        ##### layout
        self.layoutMenu = wx.Menu()
        self.loadfrom_menu = self.layoutMenu.Append(wx.ID_ANY, lt('_loadfrom_menu'))
        self.Bind(wx.EVT_MENU, self.OnLoadFrom, self.loadfrom_menu  )
        self.saveas_menu =  self.layoutMenu.Append(wx.ID_ANY,lt('_saveas_menu'))
        self.Bind(wx.EVT_MENU, self.OnSaveAs,self.saveas_menu)
        #self.save_menu =  self.layoutMenu.Append(wx.ID_ANY, lt('_save_menu'))  
        #self.Bind(wx.EVT_MENU, self.OnSave,self.save_menu)
        ##### help
        self.helpMenu = wx.Menu()
        self.tutorial_menu = self.helpMenu.Append(wx.ID_ANY,lt('_tutorial_menu') ) 
        self.Bind(wx.EVT_MENU, self.OnTutorial, self.tutorial_menu )

        self.about_menu = self.helpMenu.Append( wx.ID_ABOUT, lt('_about_menu')) 
        self.Bind(wx.EVT_MENU, self.OnAbout, self.about_menu )

        self.check_menu = self.helpMenu.Append( wx.ID_ANY, lt('_check_update') )
        self.Bind(wx.EVT_MENU, self.OnCheckUpdate, self.check_menu )

        self.index_menu = self.helpMenu.Append( wx.ID_ANY, lt('_index_menu')) 
        self.Bind(wx.EVT_MENU, self.OnIndex, self.index_menu )

        #menu bar
        self.menuBar.Append( self.settingsMenu, lt('_option_menu') )
        self.menuBar.Append( self.layoutMenu, lt('_layout_menu'))
        self.menuBar.Append( self.helpMenu, lt('_help_menu'))
        ################ menu bar end
        
        self.SetMenuBar( self.menuBar )
        
        pass
    
    def OnSaveAs(self,evt):
        with wx.FileDialog( self, lt("Save Layout"),wildcard="layout files (*.ini)|*.ini",style = wx.FD_SAVE | wx.FD_OVERWRITE_PROMPT ) as fileDialog:
            fileDialog.SetDirectory( self.home_dir )
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            pathname = fileDialog.GetPath()
            self.SaveConfig( pathname )
            pass
        pass
    
    def OnLoadFrom(self,evt):
        with wx.FileDialog( self, lt("Load Layout"),wildcard="layout files (*.ini)|*.ini|All files (*.*)|*.*",style = wx.FD_OPEN | wx.FD_FILE_MUST_EXIST | wx.FD_CHANGE_DIR) as fileDialog:
            fileDialog.SetDirectory( self.home_dir )
            if fileDialog.ShowModal() == wx.ID_CANCEL: return
            pathname = fileDialog.GetPath()
            self.LoadConfig(pathname, changeMenuKey = True )
            self.ApplyConfig()
            self.SaveConfig()
            pass
        pass
    
    def OnConfigure(self,evt):
        configDialog = ConfigDialog(self.config,self)
        if configDialog.ShowModal() == wx.ID_OK:
            self.config = configDialog.GetConfig()
            self.ApplyConfig()
            pass
        configDialog.Destroy()
        pass

    def OnLogin(self,evt): pass
    def OnLoginOut(self,evt): pass
    def OnReRun(self,evt):pass

    def OnIndex(self,evt):
        webbrowser.open( lt(INFO['HomePage']) )
        pass

    def OnTutorial(self,evt):
        #print('ontutorial called' )
        if not self.tutorial: self.tutorial = TutorialDialog(self,pos=(99,99),)
        self.tutorial.Show()
        pass

    def OnPayImage(self):
        self.payImageIndex = 3 - self.payImageIndex
        self.payImage.SetBitmap( self.payImages[ self.payImageIndex -1 ] )
        self.paytimer = WxCallLater(2.0, self.OnPayImage )
        pass

    def makePanel(self):
        ##### mainPanel
        self.mainPanel = wx.Panel(self, -1 )
        self.mainPanel.SetBackgroundColour('#FCFCFC')
        self.keyboardPanel = wx.Panel(self.mainPanel,pos=(0,0),size=(1000,411 ) )
        self.keyboardPanel.SetBackgroundColour('#4A708B')

        ##############################################################
        self.bottomPanel = wx.Panel(self.mainPanel,pos=(0,411),size=(1000,220) )
        self.bottomPanel.SetBackgroundColour('#698b69')

        #####
        ## image panel for 716x132
        bx = 3; by = -3;
        self.imagePanel = wx.Panel(self.bottomPanel, pos = (4+bx,8+by), size = (855,136),style=wx.NO_BORDER )
        self.imagePanel.SetBackgroundColour('#87CEEB')
        self.image = wx.StaticBitmap( self.imagePanel,wx.ID_ANY, bitmapFromBase64( image_mountain.img ), pos = (0,0), )

        self.text = wx.TextCtrl( self.bottomPanel, pos = (4+bx,8+by), size=(855,136),
                                 style = wx.TE_RICH|wx.TE_MULTILINE|wx.TE_BESTWRAP, )
        self.text.Hide()

        #####
        ## Layout buttons
        bx = 137; by = -3;
        self.makeLayoutButton('1', (730+bx,8+by)   )
        self.makeLayoutButton('2', (730+bx,31+by)  )
        self.makeLayoutButton('3', (730+bx,54+by)  )
        self.makeLayoutButton('4', (730+bx,77+by)  )
        self.makeLayoutButton('5', (730+bx,100+by)  )
        self.makeLayoutButton('6', (730+bx,123+by) )

        ################################
        ## payment image
        bx = -6; by = -3;
        # self.payImages = [ bitmapFromBase64(image_wechat_code.img), bitmapFromBase64(image_wechat_code_alt.img), ]
        # self.payImagePanel = wx.Panel(self.bottomPanel, pos = (847+bx,8+by), size = (140,136),style=wx.NO_BORDER )
        # self.payImage=wx.StaticBitmap(self.payImagePanel, wx.ID_ANY, self.payImages[0], );
        # self.payImage.SetToolTip( lt("_support_tooltip_wechat") )
        # self.payImageIndex = 1;
        # self.OnPayImage()
        # self.payImage.Bind( wx.EVT_LEFT_DOWN, lambda evt: self.ShowLog() )

        #######################################################
        ####
        bx = -40; by=-10; 
        width = 236; height = 18;
        for i in range(4):
            panel = wx.Panel( self.keyboardPanel, pos = ( 58+bx+i*width,86+by),  size=(width,height) )
            self.color_panels[ self.key_types[i] ] = panel
            panel.SetBackgroundColour( GetColorMap(  self.key_types[i]+'_key') )
            panel.SetToolTip( lt("_"+self.key_types[i]+"_color_info") )
            pass

        self.geekey_set_button = wx.Button(self.keyboardPanel, label= 'GK',
                                           pos =(28+100+bx,19+by),size=(47,28),style=0 )
        self.geekey_set_button.SetBackgroundColour( GetColorMap('geekey') );
        self.geekey_set_button.Bind( wx.EVT_BUTTON, self.onGeeKeySet )
        self.geekey_set_button.SetToolTip( lt("Click to select another GeeKey HotKey") )

        self.keyboard_clear_button = wx.Button(self.keyboardPanel, label= 'Clear',
                                           pos =(28+100+bx,51+by),size=(47,28),style=0 )
        self.keyboard_clear_button.SetBackgroundColour( GetColorMap('geekey') );
        self.keyboard_clear_button.Bind( wx.EVT_BUTTON, self.onKeyboardClear )
        self.keyboard_clear_button.SetToolTip( lt("Click to Clear Keyboard State") )



        self.makeGeeKeyButton('esc',(22+35+bx,18+by),(62,61),keytype='menu')
        self.makeGeeKeyButton("f1",(148+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f2",(211+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f3",(274+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f4",(337+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f5",(432+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f6",(495+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f7",(558+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f8",(621+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f9",(717+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f10",(780+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f11",(843+35+bx,18+by),keytype='function')
        self.makeGeeKeyButton("f12",(906+35+bx,18+by),keytype='function')

        by = - 15;
        self.makeGeeKeyButton('`',(22+35+bx,109+by),(62,61),keytype='text')
        self.makeGeeKeyButton("1",(120+bx,109+by),keytype='text')
        self.makeGeeKeyButton("2",(183+bx,109+by),keytype='text')
        self.makeGeeKeyButton("3",(246+bx,109+by),keytype='text')
        self.makeGeeKeyButton("4",(309+bx,109+by),keytype='text')
        self.makeGeeKeyButton("5",(372+bx,109+by),keytype='text')
        self.makeGeeKeyButton("6",(435+bx,109+by),keytype='text')
        self.makeGeeKeyButton("7",(498+bx,109+by),keytype='text')
        self.makeGeeKeyButton("8",(561+bx,109+by),keytype='text')
        self.makeGeeKeyButton("9",(624+bx,109+by),keytype='text')
        self.makeGeeKeyButton("0",(687+bx,109+by),keytype='text')
        self.makeGeeKeyButton('-',(715+35+bx,109+by),keytype='edit')
        self.makeGeeKeyButton('=',(778+35+bx,109+by),keytype='edit')
        self.makeGeeKeyButton("backspace",(841+35+bx,109+by),size=(127,61),keytype='edit')

        self.makeGeeKeyButton('tab',(22+35+bx,170+by),size=(94,61),keytype='menu')
        self.makeGeeKeyButton("q",(117+35+bx,170+by),keytype='plain')
        self.makeGeeKeyButton("w",(215+bx,170+by),keytype='macro')
        self.makeGeeKeyButton("e",(278+bx,170+by),keytype='macro')
        self.makeGeeKeyButton("r",(341+bx,170+by),keytype='macro')
        self.makeGeeKeyButton("t",(404+bx,170+by),keytype='macro')
        self.makeGeeKeyButton("y",(467+bx,170+by),keytype='macro')
        self.makeGeeKeyButton('u',(530+bx,170+by),keytype='edit')
        self.makeGeeKeyButton('i',(593+bx,170+by),keytype='edit')
        self.makeGeeKeyButton('o',(656+bx,170+by),keytype='edit')
        self.makeGeeKeyButton('p',(719+bx,170+by),keytype='edit')
        self.makeGeeKeyButton('[',(782+bx,170+by),keytype='edit')
        self.makeGeeKeyButton(']',(845+bx,170+by),keytype='edit')
        self.makeGeeKeyButton('\\',(873+35+bx,170+by),size=(95,61),keytype='edit')

        self.makeGeeKeyButton('caps lock',(22+35+bx,231+by),(108,61),keytype='menu')
        self.makeGeeKeyButton("a",(166+bx,231+by),keytype='macro')
        self.makeGeeKeyButton("s",(229+bx,231+by),keytype='macro')
        self.makeGeeKeyButton("d",(292+bx,231+by),keytype='macro')
        self.makeGeeKeyButton("f",(355+bx,231+by),keytype='macro')
        self.makeGeeKeyButton("g",(418+bx,231+by),keytype='macro')
        self.makeGeeKeyButton('h',(481+bx,231+by),keytype='edit')
        self.makeGeeKeyButton('j',(544+bx,231+by),keytype='edit')
        self.makeGeeKeyButton('k',(607+bx,231+by),keytype='edit')
        self.makeGeeKeyButton('l',(670+bx,231+by),keytype='edit')
        self.makeGeeKeyButton(';',(733+bx,231+by),keytype='edit')
        self.makeGeeKeyButton("'",(796+bx,231+by),keytype='edit')
        self.makeGeeKeyButton("return",(824+35+bx,231+by),size=(144,61),keytype='edit')
        
        self.makeGeeKeyButton("left shift",(22+35+bx,292+by),size=(140,61),keytype='menu')
        self.makeGeeKeyButton("z",(198+bx,292+by),keytype='macro' )
        self.makeGeeKeyButton("x",(261+bx,292+by),keytype='macro' )
        self.makeGeeKeyButton("c",(324+bx,292+by),keytype='macro' )
        self.makeGeeKeyButton("v",(387+bx,292+by),keytype='plain' )
        self.makeGeeKeyButton("b",(415+35+bx,292+by),keytype='macro' )
        self.makeGeeKeyButton("n",(478+35+bx,292+by),keytype='edit' )
        self.makeGeeKeyButton("m",(541+35+bx,292+by),keytype='edit' )
        self.makeGeeKeyButton(",",(604+35+bx,292+by),keytype='edit' )
        self.makeGeeKeyButton(".",(667+35+bx,292+by),keytype='edit' )
        self.makeGeeKeyButton("/",(730+35+bx,292+by),keytype='edit' )
        self.makeGeeKeyButton("right shift",(793+35+bx,292+by),size=(175,61),keytype='menu')

        ####
        self.makeGeeKeyButton('left ctrl',(22+35+bx,353+by),(93,61),keytype='menu')
        self.makeGeeKeyButton('left windows',(116+35+bx,353+by),(78,61),keytype='menu')
        self.makeGeeKeyButton('left alt',(195+35+bx,353+by),(78,61),keytype='menu')
        self.makeGeeKeyButton('space',(273+35+bx,353+by),size=(363,61),keytype='plain')
        
        self.makeGeeKeyButton('right alt',(637+35+bx,353+by),(78,61),keytype='menu')
        self.makeGeeKeyButton('right windows',(716+35+bx,353+by),(78,61),keytype='menu')
        self.makeGeeKeyButton('menu',(795+35+bx,353+by),(78,61),keytype='menu')
        self.makeGeeKeyButton('right ctrl',(874+35+bx,353+by),(94,61),keytype='menu')
        pass

    def getConfig(self,key=None,defaultValue = None ):
        if key in self.config:
            return self.config[key]
        return defaultValue

    def ApplyConfig(self):
        self.initing = True
        ### language
        set_lang( self.config['language'] )
        if self.tutorial :
            self.tutorial.Destroy()
            self.tutorial = None
            pass
        ### geekey key
        self.GeeKeyKeys = self.config['geekeykey'].split(':')
        self.geekey_mode = self.config['geekeymode']

        ### log text
        self.text.SetValue(lt(INFO['LogInitText'],) )

        ### startup
        self.startUpConfigApply()

        ### update colour
        self.keyboardPanel.SetBackgroundColour(GetColorMap('keyboard_panel') )
        self.bottomPanel.SetBackgroundColour(GetColorMap('bottom_panel') )

        ### update labels fixed:
        self.taskBarIcon.SetIcon( wx.Icon( bitmapFromBase64(image_logo.img) ), lt('_title_this') );
        self.SetTitle( lt('_title_this') )
        self.configure_menu.SetText( lt('_configure_menu') )
        self.exit_menu.SetText( lt('_exit_menu') )
        self.loadfrom_menu.SetText(lt('_loadfrom_menu'))
        self.saveas_menu.SetText(lt('_saveas_menu'))
        self.tutorial_menu.SetText(lt('_tutorial_menu') ) 
        self.about_menu.SetText( lt('_about_menu')) 
        self.check_menu.SetText( lt('_check_update')) 
        self.index_menu.SetText( lt('_index_menu')) 
        self.menuBar.SetLabelTop(0, lt('_option_menu') )
        self.menuBar.SetLabelTop(1, lt('_layout_menu'))
        self.menuBar.SetLabelTop(2, lt('_help_menu'))
        self.geekey_set_button.SetToolTip( lt("Click to select another GeeKey HotKey") )
        self.keyboard_clear_button.SetToolTip( lt("Click to Clear Keyboard State") )


        self.taskBarIcon.configure_menu.SetText( lt('_configure_menu') )
        self.taskBarIcon.loadfrom_menu.SetText( lt('_loadfrom_menu') )
        self.taskBarIcon.saveas_menu.SetText( lt('_saveas_menu') )
        self.taskBarIcon.exit_menu.SetText( lt('_exit_menu') )
        
        ### update button style 
        for key,value in GlobalMaps['keytype'].items():
            if key in self.GeeKeyKeys:
                label = GetKeyText(key) + "\n"+"GeeKey"
                self.key_buttons[key].SetLabel( label )
                self.key_buttons[key].SetBackgroundColour( GetColorMap('geekey') )
                self.key_buttons[key].SetToolTip( lt('_tip_for_geekey',lt("\nShort stoke to perform {0}",GetKeyText(key) ) if self.geekey_mode == 'longblock' else "" ) ) 
                if key in self.geekey_buttons: self.geekey_buttons[key].Show(False)
                if key+"__" in self.alt_buttons:
                    self.alt_buttons[key+"__"].Show(False)
                    self.geekey_alt_buttons[key+"__"].Show(False)
                pass
            else:
                #print(key,value)
                if key in ('','space') or value in ('menu','plain'): continue
                self.setKeyToType(key,value)
                if key[-2:] == '__': continue
                if self.key_buttons[key].GetLabel()[-6:] == 'GeeKey':
                    self.key_buttons[key].SetLabel( GetKeyText(key) )
                    self.geekey_buttons[key].Show(True)
                    self.alt_buttons[key+"__"].Show(True)
                    self.geekey_alt_buttons[key+"__"].Show(True)
                pass
            pass

        ### set tooltip for v and menukeys 
        for name in ('space','v','q'):
            self.key_buttons[name].SetToolTip( lt('_tip_for_'+name ) );

        for name in MenuKeys:
            select = GlobalMaps['menu'].get(name,name)
            label = GetKeyText(select)
            if select in self.GeeKeyKeys:
                label = label + "\n"+"GeeKey"
                self.key_buttons[name].SetBackgroundColour( GetColorMap('geekey') )
                self.key_buttons[name].SetToolTip( lt('_tip_for_geekey',lt("\nShort stoke to perform {0}",GetKeyText(select) ) if self.geekey_mode == 'longblock' else "" ) ) 
            else:
                self.key_buttons[name].SetBackgroundColour( GetColorMap(select,'menu_key') )
                self.key_buttons[name].SetToolTip( lt('_tip_for_'+select) if select in ToolTipKeys else "")
                pass
            self.key_buttons[name].SetLabel( label )

        ### update layout list
        self.getLayoutList()
        for i in range(6): 
            cuLabel = self.layout_buttons[ str(1+i) ].GetLabel()
            #log.log("label original = ",cuLabel)
            if cuLabel:
                SetMap('layout',str(1+i), cuLabel )
                continue
            layout = GetMap('layout',str(1+i) )
            #log.log("layout get from map = ",layout)
            if layout and layout in self.layout_list:
                self.layout_buttons[ str(1+i) ].SetLabel( layout )
            else:
                if i < len(self.layout_list):
                    self.layout_buttons[ str(1+i) ].SetLabel( self.layout_list[i] )
                    pass
                pass
            self.layout_buttons[ str(1+i) ].Update()
            self.layout_buttons[ str(1+i) ].Refresh()
            pass
        self.initing = False
        pass

    def LoadConfig(self,filename='default.ini',changeMenuKey=False):
        ### default configuration and avoid key error at the same time
        self.config[ 'geekeyenabled' ] = 'True'
        self.config[ 'geekeymode' ] = 'longblock'
        self.config[ 'geekeykey' ] = ':'.join(self.GeeKeyKeys)
        self.config[ 'startup' ] = 'False'
        self.config[ 'runasadmin' ]  = 'False'
        #self.config[ 'startshow' ] = 'True'
        #self.config[ 'startautocomplete' ] = 'False'
        self.config[ 'startvim' ] = 'False'
        self.config[ 'doubleclickfix' ] = 'False'
        self.config[ 'language' ] = getdefaultlocale()[0]
        self.config[ 'printkeyevent' ] = 'False'
        ### configfile settings 
        if not os.path.exists( self.data_dir ):
            shutil.copytree( self.exe_data_dir, self.data_dir )
        if not os.path.exists( self.home_dir ):
            os.mkdir( self.home_dir )
        if not os.path.exists( filename ):
            self.configFilename = os.path.join( self.home_dir, filename )
        else:
            self.configFilename = filename
            pass

        #log.log("load config from ",self.configFilename)
        try:
            if ( os.path.exists( self.configFilename ) ):
                f = open(self.configFilename, 'r', encoding='utf-8' )
                #self.configContent = f.read().decode('string-escape').decode('utf-8')
                self.configContent = f.read()
                f.close()
                #log.log('config content read:',self.configContent)
                #### parse config
                for row in self.configContent.split('||\n'):
                    items = row.split('::',1);
                    if len(items) != 2: continue
                    ### default case 
                    self.config[ items[0] ] = items[1]
                    ### case on maps do extra work
                    words = items[0].split('_map_')
                    if len( words ) == 2 and words[0] in GlobalMaps:#meny, edit, text, macro, layout
                        SetMap( words[0], words[1], items[1] )
                        continue
                    else: pass
                    pass
                else: pass
                pass
            else:
                if self.configFilename != 'default.ini':
                    # first startup, show tutorial
                    #print('first startup')
                    self.tutorial_timmer = WxCallLater(5,self.OnTutorial,None)
                    #log.log( lt("config file {0} does not exists",self.configFilename) )
                    pass
                else: pass
                pass
        except Exception as e:
            log.log( lt("Load config error for: {0} \nTry delete default.ini to fix.",e ) )
            if DEBUG: raise e
            pass

        ### get menu config from reg key of scancode map from win system
        self.isAdmin = checkIsAdmin()
        #log.log "is admin: ",self.isAdmin
        #log.log "scancode map =",getScancodeMap()
        if self.isAdmin and len( GlobalMaps['menu'] )>0 and changeMenuKey:
            ### alert that reboot to make this change function
            wx.MessageBox(lt('_reboot_to_function'),lt('_warning') )
            pass
        else: 
            GlobalMaps['menu'] = getMenuKeyMap( getScancodeMap() ) 
            pass

        ######## language should be applied at the first place for panel is initilized before applyconfig 
        set_lang( self.config['language'] )
        pass
   
    def SaveConfig(self,filename='default.ini'):
        if not filename:
            log.log("SaveConfig requires filename.")
            return

        #log.log(" GlobalMap when save = ",GlobalMaps['layout'])
        for cat in GlobalMaps:
            for key,value in GlobalMaps[cat].items():
                self.config[cat+"_map_"+key] = value
                pass
            pass

        self.configContent = ""
        for key,value in self.config.items():
            self.configContent += "%s::%s||\n"%(key, value )
        self.configFilename = os.path.join( self.home_dir, filename )
        try:
            f = open( self.configFilename, 'w', encoding = 'utf-8' )
            f.write( self.configContent )
            f.close()
        except Exception as e:
            log.log(lt("Save config error for: {0}",e ) )
            if DEBUG: raise e
            pass
        pass

    def OnPaint(self,event):
        pass

    def getLayoutList(self):
        if not os.path.exists( self.home_dir ):
            os.mkdir( self.home_dir )
            return False
        self.layout_list = []
        lists = os.listdir( self.home_dir )
        for item in lists:
            if item.lower()[-4:] == '.ini':
                self.layout_list.append( item[:-4] )
                pass
            pass
        pass

    def onLayoutButtonDrop(self,evt,name):
        self.getLayoutList()
        #log.log('get here')
        self.layout_combos[name].SetItems( self.layout_list )
        #log.log('get here')
        self.layout_combos[name].Popup()
        pass

    def onLayoutComboSelected(self,evt,name):
        self.layout_buttons[name].SetLabel( self.layout_combos[name].GetValue() )
        #log.log('setmap layout',name,self.layout_combos[name].GetValue() )
        SetMap('layout',name,self.layout_combos[name].GetValue() )
        self.onLayoutButton(evt,name)
        self.SaveConfig()
        pass

    def onLayoutButton(self,evt,name):
        layout_name = self.layout_buttons[ name ].GetLabel()
        if layout_name == '': return False
        self.layout_buttons[ self.layout_selected ].SetBackgroundColour( GetColorMap( 'layout_{0}'.format(self.layout_selected)  ) )
        self.layout_buttons[ name ].SetBackgroundColour( GetColorMap( 'layout_selected' ) )
        self.layout_buttons[ name ].Update()
        self.layout_buttons[ name ].Refresh()
        #### update the layout
        self.layout_file_name = layout_name +".layout"
        #log.log("load from ",self.layout_file_name)
        self.LoadConfig( filename = self.layout_file_name, changeMenuKey = True )
        self.ApplyConfig()
        self.layout_selected = name
        pass

    def makeLayoutButton(self,name,pos):
        self.layout_buttons[name] = wx.Button( self.bottomPanel,
                                               label = self.getConfig('layout_'+name,''),
                                               pos = (pos[0],pos[1]),
                                               size = (110-21,21),
                                               style=0|wx.BU_LEFT|wx.BORDER_NONE
        )
        self.layout_buttons[name].Bind( wx.EVT_BUTTON,lambda evt,name=name: self.onLayoutButton(evt,name) )
        self.layout_buttons[name].SetBackgroundColour( GetColorMap('layout_{0}'.format(name) ) )
        self.layout_buttons[name].Bind( wx.EVT_ENTER_WINDOW, lambda evt: self.layout_buttons[name].SetBackgroundColour("#ADD000") )
        self.layout_buttons[name].Bind( wx.EVT_LEAVE_WINDOW, lambda evt: self.layout_buttons[name].SetBackgroundColour( GetColorMap('layout_{0}'.format(name) ) ) )

        self.layout_buttons_drag[name] = wx.Button( self.bottomPanel,
                                                    label = '',
                                                    pos = (pos[0]+110-21,pos[1]),
                                                    size = (21,21),
                                                    style = wx.BORDER_NONE
        )
        op_name = str( 7-int(name) )
        self.layout_buttons_drag[name].Bind( wx.EVT_BUTTON,lambda evt,name = name: self.onLayoutButtonDrop(evt,name) )
        self.layout_buttons_drag[name].SetBackgroundColour( GetColorMap( 'layout_'+op_name ) )
        self.layout_buttons_drag[name].Bind( wx.EVT_ENTER_WINDOW, lambda evt: self.layout_buttons_drag[name].SetBackgroundColour("#AAA000") )
        self.layout_buttons_drag[name].Bind( wx.EVT_LEAVE_WINDOW, lambda evt: self.layout_buttons_drag[name].SetBackgroundColour( GetColorMap('layout_'+op_name) ) )
        
        ### get layout list of 
        #self.getLayoutList()
        self.layout_combos[name] = wx.ComboBox( self.bottomPanel,
                                                pos = pos,
                                                size=(110-21,21),
                                                choices = self.layout_list
        )
        self.layout_combos[name].Bind( wx.EVT_COMBOBOX, lambda evt,name = name: self.onLayoutComboSelected(evt,name) )
        self.layout_combos[name].Hide()
        pass

    def makeGeeKeyButton(self,name,pos,size=KeySize,keytype='plain'):
        dx = 5;
        cpos = (pos[0], pos[1]+size[1]-25)
        label = ""
        alt_name = name+"__"
        keytype =  GetMap('keytype',name) or keytype

        SetMap('keytype', name, keytype)

        if keytype in ('macro','text','edit','function'): ### geekey keys
            SetMap('keytype', alt_name, 'macro')
            ###########################
            self.key_buttons[name] = wx.Button(self.keyboardPanel, label = GetKeyText(name), pos = pos, size = size, style = 0 )
            self.key_buttons[name].Bind( wx.EVT_BUTTON, lambda evt,name=name : self.onKeyButton(evt,name) )
            self.geekey_buttons[name] = wx.Button( self.key_buttons[name], label=label, pos=(dx,3*size[1]/4-dx), size=(size[0]-dx*2,size[1]/4), style=0|wx.BORDER_NONE)
            self.geekey_buttons[name].Bind( wx.EVT_BUTTON,lambda evt,name=name:self.onGeeKeyButton(evt,name) )
            ##############
            if not name in NumberKeys:
                self.alt_buttons[alt_name ] = wx.Button( self.key_buttons[name], label=label, pos=(2+5*dx-size[1]/4,dx), size=(size[1]/4,size[1]/4), style=0|wx.BORDER_NONE)
                self.alt_buttons[alt_name ].Bind( wx.EVT_BUTTON,lambda evt,name=alt_name:self.onAltButton(evt,name) )
                self.geekey_alt_buttons[alt_name] = wx.Button( self.key_buttons[name], label=label, pos=(5*dx,dx), size=(size[0]-dx*6,size[1]/4), style=0|wx.BORDER_NONE)
                self.geekey_alt_buttons[alt_name].Bind( wx.EVT_BUTTON, lambda evt,name=alt_name:self.onGeeKeyButton(evt,name) )
            ##########################################
            self.key_combos[name] = wx.ComboBox( self.keyboardPanel,value='',pos=cpos,size=(max(100,size[0]),20),choices = EditKeysText ) 
            self.key_combos[name].Bind( wx.EVT_COMBOBOX, lambda evt,name=name:self.onGeeKeyComboSelected(evt,name) )
            self.key_combos[name].Hide()
            pass
        elif keytype == 'menu': ### menu keys
            self.key_buttons[name] = wx.Button(self.keyboardPanel, label = GetKeyText(name), pos = pos, size = size, style = 0 )
            self.key_combos[ name ] = wx.ComboBox(self.keyboardPanel,value=GetKeyText(name),pos=cpos,size=size,choices=MenuKeys )
            self.key_combos[name].Bind(wx.EVT_COMBOBOX,lambda evt,name=name: self.onMenuKeyComboSelected(evt,name) )
            self.key_combos[name].Hide()
            ############
            self.key_buttons[name].Bind(wx.EVT_BUTTON,lambda evt,name=name:self.onMenuKeyButton(evt,name) )
            ############
            self.menukey_selections[name] = name;
            self.rmenukey_selections[name] = name;
            pass
        else: ### plain keys
            self.key_buttons[name] = wx.Button( self.keyboardPanel, label = GetKeyText(name), pos = pos, size = size, style = 0 )
            self.key_buttons[name].SetBackgroundColour( GetColorMap(name,'plain_key') );
            if name == 'q':
                self.key_buttons[name].SetBackgroundColour( GetColorMap('rec') );
                pass
            if name == 'v':
                self.key_buttons[name].SetBackgroundColour( GetColorMap('vim disable') );
                self.key_buttons[name].Bind(wx.EVT_BUTTON,lambda evt:self.vim.state_switch() )
                pass
            pass
        pass

    def setKeyToType(self,name,keytype,is_alt=False ):
        if not self.initing: log.log( lt("Key {0} set to type {1}",name, keytype ) )
        try:
            SetMap('keytype',name,keytype)
            if name[-2:] == '__':
                self.alt_buttons[name].SetBackgroundColour( GetColorMap(name, keytype+'_button' ) )
                self.alt_buttons[name].Refresh()
            else:
                self.key_buttons[name].SetBackgroundColour( GetColorMap(name, keytype+'_key' ) )
                self.key_buttons[name].Refresh()
            ####
            label =  GetMap( keytype, name )
            if keytype == 'edit': label = GetKeyText( label )
            elif keytype == 'function': label =  os.path.basename( label )
            elif keytype == 'macro':
                mapvalue = label.split(':',2)
                if len(mapvalue) == 3: label = mapvalue[0] or mapvalue[2]
            ####
            if name[-2:] == '__':
                self.geekey_alt_buttons[name].SetLabel( label )
                self.geekey_alt_buttons[name].SetBackgroundColour( GetColorMap( keytype+'_button') )
                self.geekey_alt_buttons[name].Refresh()
                pass
            else:
                self.key_buttons[name].SetToolTip( label )
                self.geekey_buttons[name].SetLabel( label )
                self.geekey_buttons[name].SetBackgroundColour( GetColorMap( keytype+'_button') )
                self.geekey_buttons[name].Refresh()
                pass
            self.SaveConfig()
        except Exception as e:
            pass
        pass

    def onKeyButton(self,evt,name):
        if   GetMap('keytype',name) == 'text' : self.setKeyToType(name,'macro')
        elif GetMap('keytype',name) == 'macro': self.setKeyToType(name,'edit')
        elif GetMap('keytype',name) == 'edit' : self.setKeyToType(name,'function')
        elif GetMap('keytype',name) == 'function': self.setKeyToType(name,'text')
        pass

    def onAltButton(self,evt,name):
        if GetMap('keytype',name) == 'text' : self.setKeyToType(name,'macro')
        elif GetMap('keytype',name) == 'macro': self.setKeyToType(name,'function')
        elif GetMap('keytype',name) == 'function': self.setKeyToType(name,'text')

    def onGeeKeyButton(self,evt,name,keytype = None):
        #log.log("geekey button name=%s keytype = %s"%(name,keytype))
        if not keytype: keytype =  GetMap('keytype', name )
        if  keytype == 'edit': self.key_combos[name].Popup()
        elif keytype in ('function','macro'):
            #log.log("try GeeKeydialog")
            value = GetMap(keytype,name)
            if keytype == 'function':
                config = {
                    'name': name,
                    'value': value,
                    'type': keytype,
                    'height': 200,
                }
            else:
                value = value.split(':',2)
                config = {
                    'name': name,
                    'label': value[0] if len(value)>=3 else '',
                    'ratio': value[1] if len(value)>=3 else '',
                    'value': ':'+value[2] if len(value)>=3 else '',
                    'type': keytype,
                    'height': 300,
                }
            self.RaiseShow()
            dlg = GeeKeyDialog(config , self )
            dlg.Raise()
            if dlg.ShowModal() == wx.ID_OK:
                config = dlg.GetConfig()
                label = config['label']
                value = config['value']
                if name[-2:] == "__":
                    self.geekey_alt_buttons[name].SetLabel( label or value )
                    self.geekey_alt_buttons[name].SetToolTip( value )
                    pass
                else:
                    self.geekey_buttons[name].SetLabel( label or value)
                    self.geekey_buttons[name].SetToolTip( value )
                    pass
                if keytype == 'function':
                    SetMap( keytype, name, value)
                else:
                    SetMap( keytype, name, "{0}:{1}{2}".format(label,config['ratio'],value) ) 
                    pass

                log.log(lt('value for {0} of type {1} set to:\n{2}',name,keytype,GetMap(keytype,name)) )
            else:
                if keytype == 'macro':
                    if self.old_sequence:
                        SetMap( keytype, name, self.old_sequence )
                        self.old_sequence = ''
                pass
            dlg.Destroy()
            self.image.SetFocus()
        elif keytype in ('text'):
            style = (wx.TE_MULTILINE if keytype == 'text' else 0)|wx.OK|wx.CANCEL
            self.RaiseShow()
            dlg = wx.TextEntryDialog(self,'',lt('_'+keytype+'_to_key',name),style=style)
            #dlg.SetOKCancelLabels(lt("OK"),lt("Cancel") )
            dlg.SetValue( GetMap(keytype,name) )
            dlg.SetSize( (400,300) )
            dlg.Raise()
            if dlg.ShowModal() == wx.ID_OK:
                value = dlg.GetValue()
                if name[-2:] == '__':
                    self.geekey_alt_buttons[name].SetLabel( value )
                    self.geekey_alt_buttons[name].SetToolTip( value )
                else:
                    self.geekey_buttons[name].SetLabel( value )
                    self.geekey_buttons[name].SetToolTip( value )
                    pass
                SetMap(keytype, name, value )
                log.log(lt('value for {0} of type {1} set to:\n{2}',name,keytype,value) )
                pass
            else: pass
            dlg.Destroy()
            self.image.SetFocus()
            pass
        else:
            log.log(lt("Keytype for key {0} not set. Try delete default.ini to fix",name)) 
            pass
        if name[-2:] == '__':
            self.geekey_alt_buttons[name].Refresh()
        else:
            self.geekey_buttons[name].Refresh()
            pass
        self.SaveConfig()

        pass

    def onGeeKeyComboSelected(self,evt,name): ## only edit key will call popup and get in
        select = rKeyTexts[ self.key_combos[name].GetValue() ]
        SetMap('edit',name,select)
        self.geekey_buttons[name].SetLabel( GetKeyText(select) )
        self.geekey_buttons[name].SetToolTip( GetKeyText(select) )
        self.key_combos[name].Hide()
        self.geekey_buttons[name].Refresh()
        self.image.SetFocus()

        self.SaveConfig()
        pass

    def onMenuKeyButton(self,evt,name):
        #log.log "onMenukey",self.config['language']
        if self.isAdmin:
            self.key_combos[name].Popup()
        else:
            ### try reboot with admin, otherwise popup alert
            ret = runAsAdmin()
            if ret is True:
                self.key_combos[name].Popup()
            elif ret is None:
                #log.log 'elevating to admin previleges'
                self.OnExit(None)
                exit(0)
                sys.exit(0)
            elif ret is False:
                #log.log 'failed to elevating to admin previleges'
                style = wx.OK|wx.TE_MULTILINE
                dlg = wx.MessageDialog(self,lt('_not_run_as_admin'),lt('_warning'),style = style)
                dlg.ShowModal()
                dlg.Destroy()
                self.image.SetFocus()
                pass
            else: pass
            pass
        pass
    
    def onMenuKeyComboSelected(self,evt,name):
        self.key_combos[name].Hide()
        select = self.key_combos[name].GetValue() 
        self.key_buttons[name].SetLabel( GetKeyText(select) )
        self.image.SetFocus()
        if GetMap('menu',name) != select :
            SetMap('menu',name,select)
            mapkey = constructScancodeMap( GlobalMaps['menu'] )
            setScancodeMap( mapkey )
            style = wx.OK|wx.TE_MULTILINE
            dlg = wx.MessageDialog(self,lt('_restart_to_function'),lt('_notice'),style = style)
            dlg.ShowModal()
            dlg.Destroy()
            self.image.SetFocus()
            pass

        self.SaveConfig()
        pass

    def onGeeKeySet(self,evt):
        dlg = wx.MessageDialog(self,lt('Press Key as new GeeKey'),lt('GeeKey HotKey'),
                               wx.OK|wx.CANCEL|wx.ICON_NONE
        )
        self.state_is_geekey_selecting = True
        self.geekey_selected = []
        if dlg.ShowModal() == wx.ID_OK:
            if len(self.geekey_selected) == 0:
                log.log( lt("No GeeKey HotKey selected, remain unchanged!") )
            else:
                self.GeeKeyKeys = self.geekey_selected
                log.log( lt("GeeKey HotKey is set to {0}",self.GeeKeyKeys) )
                self.config['geekeykey'] = ':'.join(self.GeeKeyKeys)
                self.SaveConfig()
                self.ApplyConfig()
                pass
            pass
        dlg.Destroy()
        self.state_is_geekey_selecting = False
        pass

    def spaceResetState(self):
        self.state_prepare_recording = False
        self.state_is_spacing = False
        self.number_string = ''
        pass

    def stateVarInit(self):
        self.keyboard_error_code = False
        self.state_on_geekey = False
        self.state_on_geekey_revised = False
        self.state_on_ctrl = False
        self.state_on_shift = False
        self.state_on_alt = False
        self.state_on_windows = False
        self.state_on_geekey_raw = False

        self.state_is_spacing = False
        self.state_is_spacing_twice = False
        self.state_is_recording = False
        self.state_is_recorded_playing= False
        self.state_is_replay = False
        self.state_is_geekey_selecting = False

        self.state_prepare_binding = False
        self.state_prepare_space_binding = False
        self.state_prepare_recording = False

        self.is_geekey_short = True

        self.state_recording_count = 0
        self.number_string = ""
        self.recording_sequence = ['']
        self.old_sequence = ""
        self.geekey_selected = []
        self.key_mouse_sequence_key = ""
        self.recording_last_time = None

        self.last_left_up_time = 0
        self.last_right_up_time = 0

        pass
        
    def onKeyboardClear(self,evt):
        self.stateVarInit()
        
        for (key,code) in list( KeyMap.items() ):
            KeyRelease(key )
            pass
        log.log( lt('Keyboard State Cleared') )
        pass

    def Replay(self,ratio,sequence):
        #log.log('replay with ',ratio,sequence)
        return WxCallLater(0.001, self._Replay, ratio, sequence, )

    def _Replay(self,ratio,sequence):
        #log.log("replay with ratio(%s) sequence(%s)"%(ratio,sequence) )
        oper = sequence[0]
        deley = 0
        #log.log('do oper',oper)
        if len( oper ) <= 2: #compact oper for keyboard  :_x~0.1  :x~  :x  :_x
            if oper[0][0] == '_':
                key = oper[0][1:] 
                keytype = 'd'
            else:
                key = oper[0]
                keytype = 'u'
                pass
            #print('try KeySend',key,keytype)
            KeySend( key = key, keytype = keytype, scancode = ScanCode_replay )
            if len(oper) == 2 and oper[1]: delay = toFloat( oper[1] )

        elif len( oper ) >= 3:  
            #print('all mouse event',oper)
            if oper[0] == 'mma':#:mma~x~y~0.1
                pos = (int(oper[1]),int(oper[2]) )
                geeMouse.moveMouse(pos)
                if len(oper) == 4 and oper[3]: delay = toFloat( oper[3] )
                pass
            elif oper[0] == 'mmr':
                pos = geeMouse.getPosition()
                pos = (pos[0]+int(oper[1]), pos[1]+int(oper[2]) )
                geeMouse.moveMouse(pos)
                if len(oper) == 4 and oper[3]: delay = toFloat( oper[3] )
                pass
            else:
                pos = None
                if oper[1] or oper[2]: pos = (int(oper[1]),int(oper[2]) )
                #print('click or wheel at',pos)
                if  len(oper) <= 4:
                    #print('click at',pos)
                    geeMouse.buttonEvent( pos, rmouseEventTypeMap[ oper[0] ] )
                    if len(oper) == 4 and oper[3]: delay = toFloat( oper[3] )
                else:
                    geeMouse.wheelMouse( pos, int(oper[3])  )
                    #print('wheel at',pos)
                    if len(oper) == 5 and oper[4]: delay = toFloat( oper[4] )
                    pass
            pass
        else: pass
        ### send next replay key
        if len( sequence ) == 1:
            #log.log("meet replay seqeunce End")
            self.state_is_replay = False
            self.state_on_geekey = self.state_on_geekey_raw
            return False
        ### call next oper after time delay
        #print('call next:',sequence[1] )
        if ratio == 0:
            self.Replay(ratio, sequence[1:] )
        else:
            time_delay = 0.0001
            time_delay = ratio * ( delay or time_delay )
            WxCallLater( time_delay, self.Replay, ratio, sequence[1:] )
            pass
        pass

    def ProcessGeeKey(self,Key, EvtType):
        keytype = GetMap('keytype',Key)
        if keytype == 'menu': return True
        if keytype == 'edit':
            editkey = GetMap('edit', Key )
            if editkey != '':
                if not editkey in ('left shift','left ctrl','left alt','left windows'):
                    KeySend( editkey, EvtType, self.number_string) 
                else:
                    KeySend( editkey, EvtType)
                    pass
            else: pass
            self.number_string = ""
            self.state_is_spacing = False
            return False
        #############################################
        ## macro text function keys
        if EvtType == 'key down': return False
        if keytype == 'function':
            mapvalue = GetMap( keytype, Key )
            if mapvalue == "": return False
            self.number_string = ""
            if mapvalue:
                mapvalue = mapvalue.split(' ',1)
                app = mapvalue[0]
                argv = mapvalue[1] if len(mapvalue) > 1 else ''
                try:
                    win32api.ShellExecute(0,'open',app,argv,'',1)
                except  Exception as e:
                    pass
                pass
            self.number_string = ""
            self.state_is_spacing = False
            return False

        ### key down case    #for text and macro
        if keytype == 'macro':
            mapvalue = GetMap( keytype, Key )
            #print('do macro:',mapvalue )
            if mapvalue == '':
                self.number_string = ""
                self.state_is_spacing = False
                return False
            #log.log("run macro %s "%(mapvalue) )

            self.state_on_geekey = False
            self.state_is_replay = True

            if self.state_on_shift:
                self.state_on_shift = False
                geeKeyboard.coverKey('shift')
                pass
            repeat_num = geeKeyboard.repeatedNumber( self.number_string )
            self.number_string = ""
            self.state_is_spacing = False

            #print(mapvalue)
            mapvalue = mapvalue.split(':')
            name = mapvalue[0]
            ratio = toFloat(mapvalue[1],1.0)
            mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  # of form [[1,2,3],[1,2,4]]
            sequence =  list(mapvalue) * int(repeat_num)
            #print('new sequence =',sequence)

            #### run opers be sequence time
            self.Replay(ratio, sequence)
            # pass
            return False

        elif keytype == 'text':
            mapvalue = GetMap( keytype, Key )
            if mapvalue == "":
                self.number_string = ""
                self.state_is_spacing = False
                return False
            #log.log("write %s "%(mapvalue) )
            self.state_on_geekey = False
            repeat_num = geeKeyboard.repeatedNumber( self.number_string )
            self.number_string = ""
            self.state_is_spacing = False
            outtext = ''
            for i in range( repeat_num ): outtext += mapvalue
            else: pass
            #log.log("send text %s"%( outtext ) )
            geeKeyboard.textSend( outtext )
            self.state_on_geekey = self.state_on_geekey_raw
            return False
        else: pass
        ### nothing do
        self.number_string = ""
        self.state_is_spacing = False
        return False

    def startRecording(self):
        ###############################
        # start recording
        self.recording_sequence = ['']
        self.recording_last_time = 0 
        self.state_prepare_recording = False
        self.state_is_recording = True



    def OnKeyboardEvent(self,evt): 
        try:
            #### alias asignment
            EvtType = evt.MessageName
            EvtScanCode = evt.ScanCode
            if EvtScanCode == ScanCode_error:
                self.keyboard_error_code = True
                EvtScanCode == ScanCode_revised
            if evt.Key in rKeyNameMap:
                Key = rKeyNameMap[ evt.Key ]
            else:
                Key = evt.Key
                KeyMap[ Key ] = evt.KeyID
                pass

            #DealAutoComplete = lambda Key: True
            # DealAutoComplete = lambda Key: self.autoComplete.GetInput(
            #     EvtType, Key, False, self.state_on_shift, self.state_on_ctrl, self.state_on_alt
            # )
            IsKeyDown = lambda : EvtType == 'key down' or EvtType == 'key sys down'
            IsKeyUp = lambda : EvtType == 'key up' or EvtType == 'key sys up'

            if self.getConfig('printkeyevent') == 'True':
                log.log('{0}, {1}({2})  ID: {3} ScanCode: {4}'.format(EvtType,Key,evt.Key,evt.KeyID,EvtScanCode), )
                pass

            if self.state_is_geekey_selecting:
                if not IsKeyDown(): return False
                if Key in self.geekey_selected: return False
                self.geekey_selected.append(Key)
                log.log( lt("Click Ok to set new GeeKey to {0}. Otherwize Click Cancel.",self.geekey_selected) )
                return False

            if self.state_prepare_recording and not self.state_on_geekey:
                if IsKeyDown(): return False
                #print('state_prepare_recording processing')
                if Key == 'space':
                    self.state_is_spacing = True
                    #print('do space binding recording')
                    self.vim.indicator.StateReset( lt('--geekey--spacing--recording--') )
                    return False

                self.startRecording()

                if self.state_is_spacing:
                    Key = Key +'__'
                    self.vim.indicator.StateReset( lt('--geekey--spacing--recording--'),Key )
                    self.number_string = ''
                    self.state_is_spacing = False
                else:
                    self.vim.indicator.StateReset( lt('--geekey--recording--'),Key )
                    pass
                self.key_mouse_sequence_key = Key
                return False
                    
            #print(Key,EvtType)
            if self.state_is_spacing and not self.state_on_geekey and not Key in self.GeeKeyKeys:
                #print('state_is_spacing')
                if Key in NumberKeys:
                    if IsKeyUp(): return False
                    #print('spacing number',self.number_string,Key)
                    self.number_string += Key
                    self.vim.indicator.StateReset(lt('--geekey--spacing--'),self.number_string+"--" )
                    return False
                if Key == 'space' and not self.number_string:
                    if IsKeyUp(): return False
                    #print('raise panel')
                    self.number_string = ''
                    self.state_is_spacing = False
                    self.RaiseShow()
                    return False
                # if Key == 'tab' and not self.number_string:
                #     if IsKeyUp(): return False
                #     #print('switch autocomplete')
                #     self.number_string = ''
                #     self.state_is_spacing = False
                #     #self.vim.indicator.StateReset('disable')
                #     self.autoComplete.SwitchState()
                #     return False
                #print('move on to do other things,if numbering, cancel spacing')
                if self.number_string and not self.state_is_spacing_twice:
                    #print('cancel spacing for ther is number string',Key)
                    self.state_is_spacing = False
                #other situation do normal thing

            ################################################
            ### record or start recording normal keys ( not by revised or replayed
            if self.state_is_recording and not EvtScanCode == ScanCode_revised and not EvtScanCode == ScanCode_replay:
                if not self.recording_last_time: self.recording_last_time = time.time()
                res = (Key,'d' if IsKeyDown() else 'u',"%.2f"%(time.time()-self.recording_last_time), )
                self.recording_last_time = time.time()
                if ( self.state_recording_count < INFO['MacroRecordingMax'] ):
                    self.recording_sequence.append( res )
                    self.state_recording_count += 1
                    pass
                pass

            if  not Key in self.GeeKeyKeys:
                ###################################################
                #shift key state
                if Key == 'left shift' or Key == 'right shift':
                    self.state_on_shift = (True if IsKeyDown() else  False)
                    return True
                ###################################################
                #alt key state
                if ( (Key == 'left alt' or Key == 'right alt') ):
                    self.state_on_alt= (True if IsKeyDown() else  False)
                    return True
                ###################################################
                #alt key state
                if ( (Key == 'left windows' or Key == 'right windows') ):
                    self.state_on_windows = (True if IsKeyDown() else  False)
                    return True
                ###################################################
                #ctrl key state update
                if ( Key =='right ctrl' or Key == 'left ctrl' ):
                    self.state_on_ctrl = (True if IsKeyDown() else  False)
                    return True
                pass

            ##################################################
            #ignore keys generated by sendKey or sendText
            if EvtScanCode == ScanCode_revised: ### normal keys
                #print( Key,EvtType, 'revised')
                #log.log( 'Key',Key,EvtType, 'ignored because revised')
                if Key == 'esc' and 'esc' in self.GeeKeyKeys:
                    if self.state_is_spacing: self.vim.indicator.StateReset("disable")
                    self.number_string = ''
                    self.state_is_spacing = False
                    if self.vim.vim_on:
                        # record last time, double press esc in 1sec will send normal esc 
                        if not self.vim.insert_mode and not self.vim.visual_mode:
                            if IsKeyDown(): return True
                            self.vim.state_reset()
                            self.vim.indicator.StateReset()
                            return True
                        else:
                            if IsKeyDown(): return False
                            self.vim.state_reset()
                            self.vim.indicator.StateReset()
                            pass
                        return False

                    else:
                        pass
                if Key in ('backspace','delete','up','down','page up','page down'):
                    if self.vim.vim_on and not self.vim.insert_mode:
                        return self.vim.ProcessKey(Key,EvtType)
                    return True #DealAutoComplete(Key) 
                self.vim.caret.StateReset()
                return True
            elif Key == 'Packet':
                #print('packet key:', Key )
                return True

            ############################################# 
            if self.state_on_geekey and IsKeyDown(): self.is_geekey_short = False
            #############################################
            ### nomal keys without geekey
            if not self.state_on_geekey and not Key in self.GeeKeyKeys: ## 
                #print('is normal: ',)
                #######################
                ### esc to do autocomplete active cancel, and vim_mode switch
                if Key == 'esc':
                    if self.state_is_spacing: self.vim.indicator.StateReset('disable')
                    self.number_string = ''
                    self.state_is_spacing = False
                    self.vim.caret.StateReset()
                    # if self.autoComplete.PopupActive():
                    #     self.autoComplete.StateReset()

                    if self.vim.vim_on: #in every mode esc will reset completely
                        # record last time, double press esc in 1sec will send normal esc 
                        if not self.vim.insert_mode and not self.vim.visual_mode:
                            if IsKeyDown(): return True
                            #KeyStroke( 'esc' )
                            self.vim.state_reset()
                            self.vim.indicator.StateReset()
                            return True
                        else:
                            if IsKeyDown(): return False
                            self.vim.state_reset()
                            self.vim.indicator.StateReset()
                            pass
                        return False
                    return True
                ####################################################
                ### key are completely pure raw
                if self.state_is_spacing:
                    if EvtType == 'key down': return False
                    self.state_is_spacing = False
                    self.vim.indicator.StateReset("disable")
                    Key += "__"
                    return self.ProcessGeeKey( Key, EvtType)
                ### deal with repeated number
                if self.number_string: #deal with repeated number Key added to string
                    #print('numbering normal key:',Key,EvtType)
                    self.vim.indicator.StateReset("disable")
                    KeySend( Key, EvtType, self.number_string )
                    self.number_string = ""
                    self.vim.caret.StateReset()
                    return False

                #self.vim.indicator.StateReset()
                #print( Key,EvtType, 'normal')
                if IsKeyDown(): self.vim.caret.StateReset()
                if self.vim.vim_on and not self.vim.insert_mode:
                    return self.vim.ProcessKey(Key,EvtType)
                return True #DealAutoComplete(Key)
                #######################

            ###################################################
            #self.vim.caret.StateReset()
            if self.getConfig('geekeyenabled') == 'False': return True
            ###################################################
            ###################################################
            ### geekey 
            if Key in self.GeeKeyKeys:
                #always keep raw state recorded, need restore after  replay
                if EvtScanCode != ScanCode_replay:
                    self.state_on_geekey_raw = (True if IsKeyDown() else  False)

                #ignore real geekey when is replaying
                if self.state_is_replay and EvtScanCode != ScanCode_replay:
                    return False

                #update geekey state in all situations
                self.state_on_geekey = (True if IsKeyDown() else  False)

                if self.geekey_mode == 'block': return False
                ### original function turn to be by alt and upper keep unchanged class key
                if IsKeyUp():
                    if (self.state_on_shift or
                        self.state_on_alt or
                        self.state_on_ctrl or
                        self.state_on_windows or
                        self.is_geekey_short): KeyStroke( Key )
                    self.is_geekey_short = True
                    return False

                return False

            #############################################
            #### state_on_geekey is surely on only space q and v 
            ### 
            if Key == 'v':
                if IsKeyDown(): return False
                self.vim.state_switch()
                return False
            
            if Key == 'q':
                if IsKeyDown(): return False
                #print('state_prepare_recording')
                if self.state_is_recording:
                    self.endRecording()
                    return False
                else:
                    self.state_prepare_recording = True
                    self.vim.indicator.StateReset( lt('--geekey--recording--') )
                    return False

            if Key == 'space':
                if IsKeyDown(): return False
                #print('set geekey spacing')
                self.vim.indicator.StateReset( lt('--geekey--spacing--') )
                if self.state_is_spacing: self.state_is_spacing_twice = True
                else: self.state_is_spacing_twice = False
                self.state_prepare_recording = False
                self.state_is_spacing = True
                return False

            return self.ProcessGeeKey( Key, EvtType )

        except Exception as e:
            log.log("keyboard error for: {0}".format(e) )
            if DEBUG: raise e
            pass
        return False

    def OnMouseEvent(self,evt):
        try:
            if ( evt.MessageName == 'mouse move' ): return True
            #######################################
            ### redording sequence
            if self.state_is_recording:
                #log.log 'recording mouse event'
                if not self.recording_last_time: self.recording_last_time = time.time()
                res = (
                    mouseEventTypeMap[evt.MessageName], evt.Position[0], evt.Position[1],
                    "%.2f"%(time.time() - self.recording_last_time )
                ) if ( evt.MessageName != 'mouse wheel' )  else (
                    mouseEventTypeMap[evt.MessageName], evt.Position[0],evt.Position[1],
                    evt.Wheel, "%.2f"%(time.time() - self.recording_last_time)
                )
                self.recording_last_time = time.time()
                #log.log res
                self.recording_sequence.append( res )
                self.state_recording_count += 1
                if ( self.state_recording_count > INFO['MacroRecordingMax'] ):
                    self.recording_sequence == ['']
                    self.state_recording_count == 0
                pass

            #######################################
            ### mouse single click turn to double click hardware error software fix
            if self.getConfig('doubleclickfix') == 'True':
                #log.log( evt.MessageName ,time.time() )
                if evt.MessageName == 'mouse left up':
                    if time.time() - self.last_left_up_time < 0.05:
                        self.last_left_up_time = time.time()
                        return False
                    self.last_left_up_time = time.time()
                if evt.MessageName == 'mouse left down':
                    if time.time() - self.last_left_up_time < 0.05:
                        self.last_left_up_time = time.time()
                        return False
                    pass
                if evt.MessageName == 'mouse right up':
                    if time.time() - self.last_right_up_time < 0.05:
                        self.last_right_up_time = time.time()
                        return False
                    self.last_right_up_time = time.time()
                if evt.MessageName == 'mouse right down':
                    if time.time() - self.last_right_up_time < 0.05:
                        self.last_right_up_time = time.time()
                        return False
                    pass
                pass

            if evt.MessageName == 'mouse left down':
                if self.vim.visual_mode:
                    self.vim.quit_visual_mode_state()
                if self.vim.vim_on:
                    self.vim.indicator.StateReset( )
                    self.vim.caret.StateReset()
                return True

            return True
        except Exception as e:
            log.log("mouse error for: {0}".format(e) )
            if DEBUG: raise e
            pass
        return True

    def OnKeyUP(self,evt):
        if evt.GetKeyCode() == wx.WXK_ESCAPE:
            self.OnIconize(evt)
            pass
        evt.Skip()
        pass

    def endRecording(self):
        #log.log("finish recording state if is recording")
        self.state_prepare_recording = False
        self.state_is_recording = False
        if not self.vim.record:
            self.vim.indicator.StateReset( lt('--geekey--'),lt('_end_record',self.key_mouse_sequence_key) )
            pass

        ### revise cont to remove end GeeKeyKeys and key
        if len( self.recording_sequence ) < 2: 
            if not self.vim.record:
                self.RaiseShow()
                log.log( lt("End recording with no result.") )
            return False

        del self.recording_sequence[-1]
        if not self.vim.record:
            del self.recording_sequence[-1]
            while len(self.recording_sequence[-1])>=2 and self.recording_sequence[-1][0] in self.GeeKeyKeys and self.recording_sequence[-1][1] == 'd':
                del self.recording_sequence[-1]
        else:
            #del self.recording_sequence[1]
            pass

        #################
        compact = lambda ele:"{0}{1}{2}".format( ':_'if ele[1]=='d' else':',
                                                 ele[0],"~"+ele[2]if ele[2] else '') if len(ele)==3 else ':'+'~'.join(map(str,ele) )

        cont = reduce(lambda cont,ele: cont + compact(ele), self.recording_sequence )
        if self.vim.record: return cont # for vim record
        if cont != '':  # if content is empty, then do nothing

            Key = self.key_mouse_sequence_key
            self.old_sequence = GetMap('macro',Key)

            cont = ':1'+cont # name is empty
            SetMap('macro',Key, cont)
            self.RaiseShow()
            self.onGeeKeyButton(None,Key,'macro')
            pass
        else:pass #end content check
        self.SaveConfig()
        pass

    def _ChangeImage(self,direction = 1):
        while True:
            if self.image_index >= self.image_size or self.image_index >= len(self.images):
                self.image_index = 0 
                break
            if self.images[ self.image_index ]: break
            self.image_index += direction
            pass
        self.image.SetBitmap( self.images[ self.image_index ][1] )
        if self.timer: self.timer.Stop()
        self.timer = WxCallLater( max(5,self.images[self.image_index][3]), self.ChangeImage )
        pass


    def ChangeImage(self,direction = 1):
        """
        only change display image, no request to get image
        """
        self.image_index += direction
        #log.log('\n\ntry change image',self.image_index)

        self.imagePanel.Show()
        self.text.Hide()

        self._ChangeImage()

        ThreadCallLater(0.001,self.NetworkUpdateImage,self.image_index+1 )

        pass

    def OnImage(self,evt):
        """
        click image, visit url if url exists
        send click info to server
        """
        try:
            #log.log(self.images)
            #log.log(self.image_index)
            url = self.images[ self.image_index ][0]
            md5 = self.images[ self.image_index ][2]
            if url != "xxx" and url != "none" and url:
                #log.log("open url",url)
                webbrowser.open( url )
                pass
            self.ChangeImage()
            # send click info to server to record, call also use wx.CallLater, thread.Timmer
            WxCallLater(0.001,requests.post,INFO['ImageSrc'],data={"md5":md5,'i':client_info} )
        except Exception as e:
            #log.log("OnImage failed for:",e)
            pass
        pass

    def NetworkUpdateImage(self,ind):
        try:
            #log.log("get image {0} from network,current image is {1}".format(ind,self.image_index))
            local_duration = self.image_change_period
            try:
                #log.log("get local images")
                os.chdir( self.data_dir )
                #mod = importlib.import_module("image_{0}".format(ind) )
                f = open("dat_{0}.dat".format(ind) ,'r',encoding='utf-8')
                dat = f.read().split('\n' )
                local_url = dat[0]
                local_md5 = dat[1]
                local_img = dat[2]
                if len(dat) > 3: local_duration = dat[3]
                #log.log("local image get")
                pass
            except Exception as e:
                #log.log("No local image exist:",e)
                local_md5 = ""
                local_img = ""
                local_url = ""
                pass
            #log.log("check network")
            res = requests.get(INFO['ImageSrc']+"?ind={0}&md5={1}&i={2}".format(ind,local_md5,client_info) )
            ind = int(res.headers['ind'] )
            if ind != self.image_index + 1:
                #log.log("ind out of network images pool, try update 0 ind now = ",ind )
                pass
            url = res.headers['url'] 
            md5 = res.headers['md5']
            duration = int(res.headers['duration'] )
            img = res.content.decode('ascii')
            self.image_size = int( res.headers['max'] )

            if md5 == local_md5:
                #log.log("image no change. use local image, md5 =",md5,"content = ",img)
                img = local_img
            else:
                #log.log("image changed. get image {0} from network and write to file".format(ind) )
                if ind < 0: ind = 0
                while ind >= self.image_size:
                    self.images.Append(None)
                    self.image_size = len( self.images)
                    pass
                try:
                    f = open( "dat_{0}.dat".format(ind), 'w', encoding='utf-8')
                    cont = "{0}\n{1}\n{2}\n{3}\n".format(url,md5,str(img),duration)
                    f.write(cont )
                    f.close()
                    #os.system('attrib +h dat_{0}.dat'.format(ind) )
                except:
                    #log.log("save network loaded image error for:",e)
                    pass
                pass
            self.images[ind] = (url, bitmapFromBase64(img), md5, duration)
            pass
        except Exception as e:
            #print("Network get image failed")
            if local_md5:
                #print("local image exist, use it")
                self.images[ind] = ( local_url,
                                     bitmapFromBase64(local_img) ,
                                     local_md5,
                                     self.image_change_period
                )
                pass
            pass


        pass

    def OnCheckUpdate(self,evt=None,force_appear=True):
        try:
            #print('check update')
            INFO['version_processing'] = True
            ThreadCallLater(0.001,GetNetVersion)
            WxCallAfter(CheckUpdate,force_appear=force_appear, geekey=self)
        except Exception as e:
            log.log(lt("Check update failed for: {0}",e))
            if DEBUG: raise e
            pass
        pass

    def ShowLog(self,delay=30):
        self.imagePanel.Hide()
        self.text.Show()
        if self.timer: self.timer.Stop()
        self.timer = WxCallLater(delay, self.ChangeImage )
        pass

    def HideLog(self):
        self.ChangeImage()

    def Log(self,cont):
        self.ShowLog()
        ori = self.text.GetValue()
        self.text.SetValue( "> "+ cont+"\n------------------------------\n"+ori[:6666] )
        pass

    def RaiseShow(self):
        self.Iconize(False)
        self.Show(True)
        self.Raise()
        
        
    pass

