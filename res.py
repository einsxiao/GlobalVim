#!/usr/bin/env python
# -*- coding: utf-8 -*-

######################################################################
INFO= {
    'Version':'3.2.2.0',
    #'ServerAddr' : "http://192.168.1.77:8573/",
    'ServerAddr' : "https://ovo.ltd/",
    'UpdateAddr' : "https://www.microsoft.com/store/apps/9PDQ9H0CVLMS ",
    'UpdateAddr' : "ms-windows-store://pdp/?productid=9PDQ9H0CVLMS ",
    'HomePage':"https://ovo.ltd/projects/globalvim-en/",
    'Email':'einsxiao@hotmail.com',
    'ImageChangePeriod': 50,
    'MacroRecordingMax': 9999,
}
DEBUG = True
if DEBUG:
    import traceback
    def DE():
        INFO['GEEKEY'].onKeyboardClear()
        print( traceback.format_exc() )
else:
    def DE():
        INFO['GEEKEY'].onKeyboardClear()
        pass
    pass

INFO['VersionSrc'] = INFO['ServerAddr']+"image_ads/app_info/"
INFO['ImageSrc'] =INFO['ServerAddr'] + "image_ads/ads_image/"
INFO['LogInitText'] = """Double click to hide this log window."""
INFO['NetVersion'] = None 
######################################################################

import wx
import wx.adv 
import wx.lib.agw.hyperlink as hyperlink
#import base64
import os
import sys
import time
import copy
import re

import PyHook3
import keyboard
import mouse
from wx.lib.embeddedimage import PyEmbeddedImage
from keyboard import _winkeyboard as os_keyboard


from functools import reduce

#from win32 import win32api
import ctypes
from ctypes import windll, c_ulong, byref, sizeof, Structure, create_string_buffer
import winshell
import win32con
import win32api
import win32gui
import binascii
import webbrowser
#import win32clipboard as win32cb

from localization import *
from locale import getdefaultlocale

from uuid import getnode
client_info = getnode()

#### coded image used in application
import image_logo
import image_mountain
import image_bridge

user32 = ctypes.WinDLL('user32', use_last_error=True)

class log:
    log_func = None
    @classmethod
    def log(cls,*args):
        cont = ' '.join( str(i) for i in args )
        cls.log_func(cont)
        pass

def toInt(numstr,defaultvalue = 0):
    try:
        return int(numstr);
    except:
        return defaultvalue
    pass

def toFloat(numstr,defaultvalue = 0):
    try:
        return float(numstr);
    except:
        return defaultvalue
    pass

def toNumber(strnum='',num=0):
    try:
        num = float(strnum)
    except Exception:
        pass
    return num

def potentialKeyOfDict(key,dic):
    for k in dic:
        if k.startswith(key): return True
    return False

INFO['APP'] = None

def warning(message,title=''):
    style = wx.OK|wx.TE_MULTILINE
    dlg = wx.MessageDialog(INFO['APP'],message,title,style = style)
    dlg.ShowModal()
    dlg.Destroy()
    self.payImage.SetFocus()
    pass


lang = Language()

lang.set_language( getdefaultlocale()[0] )
# if win32api.GetSystemDefaultLangID() == 0x804:
#     lang.set_language('zh')
# else:
#     lang.set_language('en')
#     pass

set_lang = lang.set_language
is_en = lambda: True if lang.lang_config == 'en' else False
add_lang = lang.add_lang
lt = lang.lang

def bitmapFromBase64( base64_str ):
    try:
        return wx.Bitmap( PyEmbeddedImage(base64_str).GetImage() );
    except Exception as e:
        log.log("bitmapFromBase64 wrong for:", e , base64_str[:20] )
        return wx.Bitmap( PyEmbeddedImage(image_mountain.img).GetImage() );

def boolFromStr( s ):
    if ( s == 'True' ): return True
    return False

########### keyboard basic information
RawKeyMap={
    'Escape':('esc',27,'Esc','01','00'),

    'F1':('f1',59), 'F2':('f2',60), 'F3':('f3',61), 'F4':('f4',62), 'F5':('f5',63), 'F6':('f6',64), 'F7':('f7',65), 'F8':('f8',66), 'F9':('f9',67), 'F10':('f10',68), 'F11':('f11',87), 'F12':('f12',88),

    '1':('1',49,'1  !'), '2':('2',50,'2  @'), '3':('3',51,'3  #'),
    '4':('4',52,'4  $'), '5':('5',53,'5  %'), '6':('6',54,'6  ^'),
    '7':('7',55,'7  &&'), '8':('8',56,'8  *'), '9':('9',57,'9  ('), '0':('0',48,'0  )'),

    'A':('a',65), 'B':('b',66), 'C':('c',67), 'D':('d',68), 'E':('e',69), 'F':('f',70), 'G':('g',71), 'H':('h',72), 'I':('i',73), 'J':('j',74), 'K':('k',75), 'L':('l',76), 'M':('m',77), 'N':('n',78), 'O':('o',79), 'P':('p',80), 'Q':('q',81,'REC'), 'R':('r',82), 'S':('s',83), 'T':('t',84), 'U':('u',85), 'V':('v',86,'VIM'), 'W':('w',87), 'X':('x',88), 'Y':('y',89), 'Z':('z',90),

    'Oem_3':('`',192,'`  ~','29','00'),
    'Oem_Minus':('-',189,'-  _'),
    'Oem_Plus':('=',187,'=  +'),
    'Back':('backspace',8,'Backspace'),

    'Tab':('tab',9,'Tab','0F','00'),
    'Oem_4':('[',219,"[  {"),
    'Oem_6':(']',221,"]  }"),
    'Oem_5':('\\',220,"\\  |"),

    'Capital':('caps lock',20,'CapsLock','3A','00'),
    'Oem_1':(';',186,';  :'),
    'Oem_7':("'",222,"'  \""),
    'Return':('return', 13,"Enter"),

    'Lshift':('left shift',160,"Shift",'2A','00'),
    'Oem_Comma':(',',188,',  <'),
    'Oem_Period':('.',190,'.  >'),
    'Oem_2':('/',191,'/  ?'),
    'Rshift':('right shift',161,"Shift",'36','00'),

    'Lcontrol':('left ctrl',162,'Ctrl','1D','00'),
    'Lwin':('left windows',91,'Win','5B','E0'),
    'Lmenu':('left alt',164,'Alt','38','00'),
    'Space':('space',32,'Space'),
    'Rmenu':('right alt',165,'Alt','38','E0'),
    'Rwin':('right windows',92,'Win','5C','E0'),
    'Apps':('menu',93,'Menu','5D','E0'),
    'Rcontrol':('right ctrl',163,'Ctrl','1D','E0'),

    'Insert':('insert',45,'Insert'),
    'Delete':('delete',46,'Delete'),
    'Home':('home',36,'Home'),
    'End':('end',35,'End'),
    'Prior':('page up',33,'PageUp'),
    'Next':('page down',34,'PageDown'),

    'Left':('left',37,'←'),
    'Right':('right',39,'→'),
    'Up':('up',38,'↑'),
    'Down':('down',40,'↓'),

    'Volume_Up':('volume up',175,'Volume Up'),
    'Volume_Down':('volume down',174,'Volume Down'),
    'Volume_Mute':('volume mute',173,'Volume Mute'),
    'Launch_Mail':('start mail',180,'Launch Mail'),
    'Brower_Home':('brower start and home',172,'Brower'),
    'Brower_Back':('brower back',166,'Brower Back'),
    'Brower_Forward':('brower forward',167,'Brower Forward'),
    'Launch_Media_Select':('select media',181,'Launch Media'),
    'Media_Play_Pause':('play/pause media',179,'Play/Pause'),
    'Media_Stop':('stop media',178,'Stop'),
    'Media_Prev_Track':('previous track',177,'Previous Track'),
    'Media_Next_Track':('next track',176,'Next Track'),
    'Print_Screen':('print screen',0x2C,'Print Screen'),

    '':('',0,'','',''),
}

KeyMap = {}
KeyTexts = {} #key display text, ie. left alt -> Alt
rKeyTexts = {} #key display text, ie. Alt -> left alt
KeyNameMap = {} #pyhook to keyboard, ie.  Lwin -> left windows
rKeyNameMap = {} #keyboard to pyhook, ie. left windows -> Lwin
KeyScanStrs = {} #scancode when regedit
rKeyScanStrs = {} #scancode when regedit
KeyScanCodeMap = {}
######## rewrite KeyMap and KeyNameMap
for key,value in RawKeyMap.items():
    KeyMap[ value[0] ] = value[1]
    if len(value) > 2 :
        KeyTexts[ value[0] ] = value[2]
        rKeyTexts[ value[2] ] = value[0]
    else:
        KeyTexts[ value[0] ] = key
        rKeyTexts[ key ] = value[0]
        pass
    rKeyNameMap[ key ] = value[0]
    KeyNameMap[ value[0] ] = key
    if len( value ) > 4 :
        KeyScanStrs[ value[0] ] = value[3]+value[4]
        rKeyScanStrs[ value[3]+value[4] ] =  value[0] 
        pass
    pass

# ID_right_ctrl = KeyMap['right ctrl']
# ID_left_ctrl = KeyMap['left ctrl']
# ID_left_shift = KeyMap['left shift']
# ID_right_shift = KeyMap['right shift']

def GetKeyText(key):
    if key in KeyTexts: return KeyTexts[key] 
    return key

##### simulate key events with fake scancode
#user32 = windll.user32
INFO['covering'] = False
ScanCodeRevised = 222
ScanCodeReplay  = 223
ScanCodeFinal   = 224
ScanCodeError   = 0
KEYDOWN = 224|0
KEYUP = 224|2
class GeeKeyBoard:
    KEYDOWN = 224|0
    KEYUP = 224|2
    def __init__(self):
        os_keyboard.init()
        pass

    def setKeyEventDelay(self,delay):
        pass
        
    def coverKey(self):
        for (key,value) in RMS.items():
            if value:
                #print('cover',key)
                INFO['covering'] = True 
                KeyRelease(key)
                MS[key] = False

    def recoverKey(self):
        for (key,value) in RMS.items():
            if value:
                #print('recover',key)
                KeyPress(key)
                INFO['covering'] = False
                MS[key] = True
        
    def keyPress(self,key,scancode=ScanCodeRevised):
        if type(key) == str:
            user32.keybd_event(KeyMap[ key ], scancode, self.KEYDOWN, 0) 
        else:
            for k in key: user32.keybd_event(KeyMap[ k ], scancode, self.KEYDOWN, 0) 
        pass

    def keyRelease(self,key,scancode=ScanCodeRevised):
        if type(key) == str:
            user32.keybd_event(KeyMap[ key ], scancode, self.KEYUP, 0)
        else:
            for k in key: user32.keybd_event(KeyMap[ k ], scancode, self.KEYUP, 0)
        pass

    def keyStroke(self,key,scancode=ScanCodeRevised):
        if type(key) == str:
            self.keyPress(key,scancode)
            self.keyRelease(key,scancode)
        else:
            for k in key:
                self.keyPress(k,scancode)
                self.keyRelease(k,scancode)
        pass

    def repeatedNumber(self,num):
        if num == '' : return 1
        res = 1
        try: res = int(num)
        except: pass
        return res

    def keySend(self,key,keytype = 'key down',repeated = 1,scancode = ScanCodeRevised):
        try:
            repeated = self.repeatedNumber( repeated)
            keytype = self.KEYDOWN if keytype.strip() in ('d','key down','key sys down') else self.KEYUP 
            keyid = KeyMap.get(key.strip(),0)
            #print(keyid)
            if keyid == 0: return
            if keytype == self.KEYDOWN:
                for i in range( repeated -1 ):
                    user32.keybd_event(keyid, scancode, self.KEYDOWN , 0)
                    user32.keybd_event(keyid, scancode, self.KEYUP , 0)
                    pass
                pass
            user32.keybd_event(keyid, scancode, keytype , 0)
            pass
        except Exception as e:
            log.log('keySend error for:',e)
            pass
        pass

    def textSend(self,text):
        try:
            for letter in text:
                os_keyboard.type_unicode(letter)
                pass
            pass
        except Exception as e:
            log.log('textSend error for:',e)
        pass
        
    pass

##############################################################
##############################################################
### map and choices initialize
FunctionKeys = ['f1','f2','f3','f4','f5','f6','f7','f8','f9','f10','f10','f11','f12']

NumberKeys = ['0','1','2','3','4','5','6','7','8','9']

CharKeys = ['a','b','c','d','e','f','g',
            'h','i','j','k','l','m','n',
            'o','p','q',    'r','s','t',
            'u','v','w',    'x','y','z']

SymbolKeys = ['`','-','=','[',']','\\',';','\'',',','.','/',]
SpecKeys = ['`',',','.','/','\\','-','=','(',')','!','@','#','$','%','^','&','*','=']

StringKeys = NumberKeys + CharKeys + SymbolKeys

ModifierKeys = [ 'left shift', 'right shift',
                 'left ctrl', 'right ctrl',
]

MenuKeys_1 = ['tab','caps lock','menu','left windows','right windows','left alt','right alt',] + ModifierKeys

MenuKeys = [ 'esc' ] + MenuKeys_1

MenuKeysText = [ KeyTexts[v] for v in MenuKeys ]

EditKeys = [ '',
             'left','down','up','right','home','end','return',
             'page up','page down','backspace','delete','insert',
             'volume up','volume down','volume mute','start mail',
             'brower start and home','brower back','brower forward',
             'select media','play/pause media','stop media','previous track','next track',
             'print screen',
             'left shift','left ctrl','left alt','left windows', 'tab','caps lock',
]
EditKeysText = [ KeyTexts[v] for v in EditKeys ]
MS = {}
RMS = {}
for key in ModifierKeys:
    MS[key]  = False
    RMS[key] = False

GlobalMaps = {}
GlobalMaps['macro'] = {
    "t":"",
    "y":"",
    "f2":"save:0:_right ctrl:_s:s:right ctrl",
    "a":"home:0:_home:home",
    "e":"end:0:_end:end",
    ",":"head:0:_right ctrl:_home:home:right ctrl",
    ".":"tail:0:_right ctrl:_end:end:right ctrl",
    "":"",
}
GlobalMaps['edit'] = {
    '-':'volume down','=':'volume up','backspace':'volume mute',
    "h":"left","j":"down","k":"up","l":'right',
    "m":'delete',
    ",":"home",
    ".":"end", 
    '[':'page up',
    ']':'page down',
    "b":"left",
    "p":"up",
    "f":"right",
    "n":"down",

}
GlobalMaps['text'] = {
    "":"",
}
GlobalMaps['function'] = {
    '':'',
}

GlobalMaps['keytype'] = {
    'f2':'macro',
    '':'',
}

GlobalMaps['vim'] = {
    ### shift_ should ahead of ctrl_ 
    'esc':'esc',
    'space':'right',
    'backspace':'left',
    'return':'return',
    'h':'left',
    'j':'down',
    'k':'up',
    'l':'right',
    '0':'home line',
    'shift_\\':'jump bar',
    'shift_6':'home block',
    'shift_4':'end',

    "shift_'":'register',
    'shift_;':'command',
    'q':'record',
    'shift_2':'execute',

    'i':'insert',
    'shift_i':'insert begin',
    'a':'append',
    'shift_a':'append end',
    'o':'insert next line',
    'shift_o':'insert prev line',

    's':'change',
    'c__w':'change word',
    'c__e':'change word',
    'c__b':'change word back',
    'shift_s':'change line',
    'c__c':'change line',
    'c__0':'change begin',
    'c__shift_6':'change begin',
    'shift_c':'change end',
    'c__shift_4':'change end',

    #'r':'replace char', ## 
    #'shift_r':'replace mode',

    'y':'copy',
    'y__w':'copy word',
    'y__e':'copy word',
    'y__b':'copy word back',
    'y__y':'copy line',
    'shift_y':'copy line',
    'y__shift_6':'copy begin',
    'y__0':'copy begin',
    'y__shift_4':'copy end',

    'p':'paste',
    'shift_p':'paste prev', # if paste line paste on privous

    'x':'x cut',
    'shift_x':'x cut previous',

    'd':'cut', # only function in visual mode
    'd__d':'cut line',
    'd__w':'cut word',
    'd__e':'cut word',
    'd__b':'cut word back',
    'd__0':'cut begin',
    'd__shift_6':'cut begin',
    'shift_d':'cut end', # only function in visual mode
    'd__shift_4':'cut end',

    'u':'undo',
    'shift_u':'redo',
    'shift_j':'merge line', 

    'v':'visual mode',
    'shift_v':'line visual mode',
    'w':'next word',
    'e':'end word',
    'b':'prev word',
    'shift_[':'prev para',
    'shift_]':'next para',

    'g__g':'jump head',
    'shift_g':'jump tail',

    'y__g__g':'copy head',
    'y__shift_g':'copy tail',
    'd__g__g':'cut head',
    'd__shift_g':'cut tail',

    #'f2':'save',
    '/':'find',
    'shift_8':'find current',

    #'z__z':'caret center',
    #'z__t':'caret top',
    #'z__b':'caret bottom',

    'ctrl_r':'redo',
    'ctrl_f':'page down',
    'ctrl_b':'page up',

}

GlobalMaps['vim_register'] = {
    '':'', #(content) 'k':'^xxxx' for pure text or 'k':'^:0:xxxxx' for operation record
}

vim_move_count ={
    'left' : -1,
    'right':  1,
    'up'   :-40,
    'down' : 40,
    'home' :-20,
    'end'  : 20,
    'word' :  6,
    'back' : -6,
}

GlobalMaps['layout'] = {'':'',}

ToolTipKeys = {'space','q','v',}

def GetMap( cat, key):
    if not cat in GlobalMaps: return ''
    if not key in GlobalMaps[cat]: return ''
    return GlobalMaps[cat][key]

def SetMap( cat, key, value):
    if not cat in GlobalMaps: return False
    GlobalMaps[ cat ][ key ] = value
    return True
   
Color_Map ={

    'layout_1':'#d2efe8',
    'layout_2':'#d3eee7',
    'layout_3':'#aee0d4',
    'layout_4':'#90d5c4',
    'layout_5':'#76cbb7',
    'layout_6':'#59c0a7', #deepskyblue
    'layout_selected':'#87cefa',

    'geekey' : '#c0f616',
    'rec' : '#cb5bff',
    'space' : '#cfefa1',
    'tab': '#e1a1ef',

    'menu_key' : '#66cdef',

    'macro_key':'#D8BFD8',
    'macro_button':'#CD96CD',

    'text_key':'#D8BFff',
    'text_button':'#CD96ff',

    'edit_key':'#BFEFFF',
    'edit_button':'#87cefa',

    'function_key':'#9Fb6cd',
    'function_button':'#9bcd9b',

    'plain_key' : '#e1a1ef',

    'candidate_texts':'#9Fb6cd',
    'candidate_selected':'#c0ff3e',

    'vim disable':'#ff6f5d',
    'vim normal':'#ebffb3',
    'vim insert':'#b3baff',
    'vim visual':'#eab3ff',
    'vim text':'#111111',
    'keyboard_panel':'#4a708b',
    'bottom_panel':'#698b69',
    '':'',
}
GlobalMaps['color'] = Color_Map
def GetColorMap(key,default='plain_key'): return GlobalMaps['color'].get(key,GlobalMaps['color'][default] )


def regesterGeeKey(action=True):
    if action: # add regedit
        pass
    else:
        pass
    win32api.RegCloseKey(key)
    pass
        
class GeeMouse:

    def wheelMouse(self,pos=None,direction=-1):
        if pos: self.moveMouse(pos)
        mouse.wheel( direction )
        pass

    def moveMouse(self,pos):
        """move the mouse to the specified coordinates"""
        mouse.move( pos[0], pos[1] )
        pass

    def pressButton(self, pos=None, button_name="left"):
        """press a button of the mouse"""
        if pos: mouse.move(pos[0],pos[1])
        mouse.press( button_name )
        pass

    def releaseButton(self, pos=None, button_name="left"):
        """release a button of the mouse"""
        if pos:mouse.move(pos[0],pos[1])
        mouse.release( button_name )
        pass

    def buttonEvent(self, pos=None, buttonStr='left' ):
        items = buttonStr.split()[1:]
        button_name = items[0]
        if len( items ) > 1:
            button_type = items[1]
            if items[1] == 'down': self.pressButton(pos, button_name)
            else: self.releaseButton(pos, button_name)
        else:
            if button_name == 'move': self.moveMouse( pos )
            elif button_name == 'wheel': self.wheelMouse( pos )
            else: pass
            pass
        pass
        

    def click(self, pos=None, button_name= "left"):
        """Click at the specified placed"""
        if pos: self.moveMouse(pos)
        mouse.click( button_name )

    def doubleClick (self, pos=None, button_name="left"):
        """Double click at the specifed placed"""
        if pos: self.moveMouse(pos)
        mouse.click( button_name)

    def getPosition(self):
        """get mouse position"""
        return mouse.get_position()

    pass

geeKeyboard = GeeKeyBoard()
geeMouse = GeeMouse()

KeyStroke = lambda Key,scancode=ScanCodeRevised: geeKeyboard.keyStroke(Key,scancode)
KeyPress = lambda Key,scancode=ScanCodeRevised: geeKeyboard.keyPress(Key,scancode)
KeyRelease = lambda Key,scancode=ScanCodeRevised: geeKeyboard.keyRelease(Key,scancode)
KeySend = lambda key,keytype='key down',repeated=1,scancode=ScanCodeRevised: geeKeyboard.keySend(key,keytype,repeated,scancode )
SetKeyDelay = lambda delay: geeKeyboard.setKeyEventDelay(delay)
TextSend = lambda txt: geeKeyboard.textSend( txt )

reg_root = win32con.HKEY_LOCAL_MACHINE
reg_path = "SYSTEM\\CurrentControlSet\\Control\\Keyboard Layout"
reg_flags = win32con.WRITE_OWNER|win32con.KEY_WOW64_64KEY|win32con.KEY_ALL_ACCESS
reg_flags_readonly = win32con.KEY_READ

def checkIsAdmin():
    try:
        key = win32api.RegOpenKeyEx(reg_root, reg_path, 0, reg_flags)
        win32api.RegCloseKey(key)
    except Exception as e:
        #log.log("checkIsAdmin failed for %s"%(e[2]) )
        return False
    return True

def getScancodeMap():
    try:
        key = win32api.RegOpenKeyEx(reg_root, reg_path, 0, reg_flags_readonly)
        value = win32api.RegQueryValueEx(key,'Scancode Map')
        strhex = str(binascii.b2a_hex( value[0] ) )
        win32api.RegCloseKey(key)
        return strhex.upper()
    except Exception as e:
        #log.log "getScanCodeMap failed for ",e[2]
        return None
    pass

init_scancode_map_key = getScancodeMap()
#log.log('init map_key = %s'%init_scancode_map_key )

def getMenuKeyMap(mapkey):
    #log.log("get into getMenuKeyMap with mapkey = %s, lenkey = %s, sub = %s"%(mapkey,len(mapkey),mapkey[16:20]))
    if not mapkey: return {}
    if mapkey[1] == "'": mapkey = mapkey[2:]
    if not mapkey: return {}
    res = {}
    num = int( mapkey[16:18] ,16)
    #log.log("str = %s, num = %s"%(mapkey[16:18],num) )
    for i in range(num-1):
        key2 = mapkey[24+8*i:28+8*i]
        key1 = mapkey[28+8*i:32+8*i]
        #log.log("swap key item: (%s:%s)"%(key1,key2) )
        if not key1 in rKeyScanStrs or not key2 in rKeyScanStrs:
            #warning("_key_swap_caution_content","_key_swap_caution")
            #log.log("unmatch key swap item")
            continue
        res [ rKeyScanStrs[key1] ] = rKeyScanStrs[key2]
        #log.log("matched key swap item: (%s:%s)"%(rKeyScanStrs[key1],rKeyScanStrs[key2] ) )
        pass
    return res

GlobalMaps['menu'] = getMenuKeyMap(init_scancode_map_key)
#log.log('gloal menu maps = ',GlobalMaps['menu'] )

def constructScancodeMap(menukey_map):
    count = 0
    res = ''
    for key1,key2 in menukey_map.items():
        if key1 == key2: continue
        count += 1
        res+= KeyScanStrs[ key2 ] + KeyScanStrs[ key1 ]
        pass
    res =  16*'0'+ format(count+1,'#04x')[2:] + 6*'0' + res + 8*'0'
    return res
#log.log constructScancodeMap( MenuKey_Map )
#log.log getMenuKeyMap( constructScancodeMap( MenuKey_Map ) )
    
def setScancodeMap(mapkey):
    try:

        try:
            key = win32api.RegOpenKeyEx(reg_root, reg_path, 0, reg_flags)
        except Exception as e:
            #log.log("try open failed in setScancodeMap")
            try:
                key = win32api.RegCreateKeyEx(reg_root, reg_path,reg_flags)
            except Exception as e:
                #log.log("try create failed in setScancodeMap")
                return False
            pass
        regstr = binascii.unhexlify( mapkey )
        win32api.RegSetValueEx(key,'Scancode Map',0,win32con.REG_BINARY, regstr)
        win32api.RegCloseKey(key)
        return True
    except Exception as e:
        #log.log e
        return False
    pass

#setScancodeMap( constructScancodeMap( MenuKey_Map ) )
    
       

mouseEventTypeMap = {
    'mouse left down':'ld',
    'mouse left up':'lu',
    'mouse right down':'rd',
    'mouse right up':'ru',
    'mouse middle down':'md',
    'mouse middle up':'mu',
    'mouse wheel':'w',
    'mouse move':'mm',
}

rmouseEventTypeMap = dict( map( lambda ele:(ele[1],ele[0]), mouseEventTypeMap.items() ) )
#log.log rmouseEventTypeMap




def runAsAdmin(argv=None, debug=False):
    shell32 = windll.shell32
    if argv is None and shell32.IsUserAnAdmin():
        return True

    return False
    # if argv is None: argv = sys.argv
    # if hasattr(sys, '_MEIPASS'):
    #     # Support pyinstaller wrapped program.
    #     arguments = argv[1:]
    # else:
    #     arguments = argv
    #     pass
    # argument_line = u' '.join(arguments)
    # executable = sys.executable
    # ret = shell32.ShellExecuteW(None, u"runas", executable, argument_line, None, 1)
    # if int(ret) <= 32:
    #     return False
    # return None


    


class RECT(Structure):
    _fields_ = [
        ("left", c_ulong),
        ("top", c_ulong),
        ("right", c_ulong),
        ("bottom", c_ulong)];
    pass

class GUITHREADINFO(Structure):
    _fields_ = [
        ("cbSize", c_ulong),
        ("flags", c_ulong),
        ("hwndActive", c_ulong),
        ("hwndFocus", c_ulong),
        ("hwndCapture", c_ulong),
        ("hwndMenuOwner", c_ulong),
        ("hwndMoveSize", c_ulong),
        ("hwndCaret", c_ulong),
        ("rcCaret", RECT)
    ]
    pass


def get_layout():
    guiThreadInfo = GUITHREADINFO(cbSize=sizeof(GUITHREADINFO))
    user32.GetGUIThreadInfo(0, byref(guiThreadInfo))
    dwThread = user32.GetWindowThreadProcessId(guiThreadInfo.hwndCaret, 0)
    return user32.GetKeyboardLayout(dwThread)

class UpdateDialog( wx.Dialog):
    
    def __init__(self,cont,*args,**kwargs):
        self.textPanel = None
        self.contPanel = None
        self.sizer = None
        self.button = {}
        self.H = 30;
        self.W = 450; self.tH = 60; self.bH = 50;
        self.yP = 20; self.xP = 20;

        wx.Dialog.__init__(self,*args,**kwargs)
        self.SetTitle( _('_new_version_available') )
        self.sizer = wx.BoxSizer(wx.VERTICAL)

        self.textPanel = wx.Panel(self,size=(self.W, self.tH) )
        self.bottomPanel = wx.Panel( self, size=(self.W, self.bH) )
        self.bottomPanel.SetBackgroundColour( "#E5E5E5" )

        self.sizer.Add( self.textPanel )
        self.sizer.Add( self.bottomPanel )

        text = wx.StaticText( self.textPanel, label='test', pos=(self.yP, self.xP), size=(self.W-20, self.tH-20 ), style= wx.ALIGN_CENTER)

        self.button['update'] = wx.Button(self.bottomPanel, label= _("Update"),pos=(self.W/2-60,self.H/3),size=(80,self.H ) )
        self.button['cancel'] = wx.Button(self.bottomPanel, label= _("Cancel"),pos=(self.W/2+40,self.H/3),size=(80,self.H) )

        self.SetSizerAndFit( self.sizer )
        pass
    pass



def _create_round_corner_mask(size, radius, border=0):
    """
    Creates a mask that when applied to a bitmap will round the bitmap's corners.
    The radius of the round corners is determined by 'radius'.
    You can supply an optional 'border' argument to create a transparent border
    around the image.

    This is accomplished by drawing a white rounded rectangle on an empty (black)
    bitmap. When a mask is created from a bitmap, black pixels become transparent,
    and white pixels become opaque.
    """

    (w, h) = size
    maskBitmap = wx.EmptyBitmap(w, h)
    mdc = wx.MemoryDC()
    mdc.SelectObject(maskBitmap)
    mdc.SetPen(wx.TRANSPARENT_PEN)
    mdc.SetBrush(wx.WHITE_BRUSH)
    mdc.DrawRoundedRectangle(border, border, w - border*2, h - border*2, radius)
    mdc.SelectObject(wx.NullBitmap)
    return wx.Mask(maskBitmap)

def rgbToHex(r,g,b):
    return "{0:02x}{1:02x}{2:02x}".format(r,g,b)

def hexToRgb(h):
    if h[0] != '#': raise Exception('hexToRgb failed for hex string not start with #')
    if len(h)<4: raise Exception('hexToRgb failed for hex string shorter than 4bits')
    if len(h)<7: h += h[1:4]
    return tuple( int(h[i:i+2],16) for i in(1,3,5) )

def hexReverse(h):
    rgb = hexToRgb( h )
    return rgbToHex( 255-rgb[0],255-rgb[1], 255-rgb[2] )
    

import threading

class callLaterThread( threading.Thread):
    def __init__(self, func,*argv):
        threading.Thread.__init__(self)

        self.run = lambda argv=argv: func(*argv)
        pass
    pass

def ThreadCallLater(delay, func, *args, **kwargs):
    try:
        delay = max(0.001,toFloat(delay) )
        timer = threading.Timer( delay, func, args, kwargs )
        timer.start()
        return timer
    except Exception as e:
        DE()
        log.log('ThreadCallLater Failed for',e)
    return None

def WxCallLater(delay,func,*args,**kwargs):
    try:
        delay = max(1,toInt(delay*1000) )
        return wx.CallLater(delay, func, *args, **kwargs)
    except Exception as e:
        DE()
        log.log('WxCallLater Failed for',e)
    return None

def WxCallAfter(func,*args,**kwargs):
    try:
        return wx.CallAfter(func, *args, **kwargs)
    except Exception as e:
        DE()
        log.log('WxCallAfter Failed for',e)
    return None

def getCbText():
    txt = wx.TextDataObject()
    while True:
        try:
            if not wx.TheClipboard.IsOpened():
                if wx.TheClipboard.Open():
                    wx.TheClipboard.GetData( txt )
                    wx.TheClipboard.Close()
                    break
                pass
        except Exception as e:
            pass
        time.sleep(0.01)
        pass
    return txt.GetText()

def setCbText(txt):
    txt = wx.TextDataObject(txt)
    while True:
        try:
            if not wx.TheClipboard.IsOpened():
                if wx.TheClipboard.Open():
                    wx.TheClipboard.SetData( txt )
                    wx.TheClipboard.Close()
                    break
                pass
        except Exception as e:
            pass
        time.sleep(0.01)
        pass
    pass

def SetRegister(register, txt):
    if not txt: return None
    #print('set register {0}:{1}'.format(register,txt) )

    if register[:6] == 'shift_':
        if register[7:] in CharKeys:
            # ignore the first ^ or <
            txt = GetMap('vim_register',register) + txt[1:] 
            pass
        pass

    return SetMap('vim_register',register,txt )

def GetRegister(register):
    if not register: return None#do nothing
    res = GetMap('vim_register',register )
    if not res: return None
    #print(type(res),res )
    return res


mapping = {'\a': r'\a', '\b': r'\b', '\f': r'\f', '\n': r'\n',
           '\r': r'\r', '\t': r'\t', '\v': r'\v'}

def escape(astr):
    for char, escaped in mapping.items():
        astr = astr.replace(char, escaped)
    return astr

UpperKeys = { #Key uppper chr, ie. 1 -> ! 
    '`':'~',
    '1':'!','2':'@','3':'#','4':'$','5':'%','6':'^','7':'&','8':'*','9':'(','0':')',
    '-':'_','=':'+',
    '[':'{',']':'}','\\':'|',
    ';':':','\'':'"',
    ',':'<','.':'>',
}

LowerKeys = { v:k for k,v in UpperKeys.items() }

def upper(ch):
    return UpperKeys.get(ch) or ch.upper()

def lower(ch):
    return LowerKeys.get(ch) or ch.lower()

KeyDisplays = { 'space':' ', }
def display(ch):
    if ch in KeyDisplays: return KeyDisplays.get(ch)
    return ch
    
def vim_search_scope(astr):
    num = ''
    while astr and astr[-1] in NumberKeys:
        num = astr[-1]+num
        astr = astr[:-1]
        pass
    if astr and astr[-1] in ('-','+'):
        d = astr[-1]
        astr = astr[:-1]
    else:
        d = ''
        pass
    if not d and num and astr: return False
    if not d and num: return [int(num),0]
    if num == '': num = 0
    else: num = int(d+num)

    return [astr,num]

   
def keyboardCallBack(evt):
    try:
        EvtType = evt.MessageName
        EvtScanCode = evt.ScanCode
        if EvtScanCode == ScanCodeError:
            INFO['keyboard_error_code'] = True
            EvtScanCode == ScanCodeRevised
        if evt.Key in rKeyNameMap:
            Key = rKeyNameMap[ evt.Key ]
        else:
            Key = evt.Key
            KeyMap[ Key ] = evt.KeyID
            pass

        #print(Key,EvtType,EvtScanCode,INFO['covering'])

        if EvtScanCode == ScanCodeFinal:
            #print('final',Key,EvtType,'passed' )
            return True
        elif Key in RMS:
            if INFO['covering']:
                #print('covering pass')
                return True
            if EvtType in ('key down','key sys down',):
                MS[key] = True
                if EvtScanCode != ScanCodeRevised:
                    #print(Key,'pressed')
                    RMS[Key] = True
                    KeyPress(Key)
                    return False
            else:
                MS[key] = False
                if EvtScanCode != ScanCodeRevised:
                    #print(Key,'released')
                    RMS[Key] = False
                    KeyRelease(Key)
                    return False
            pass

        if  INFO['GEEKEY'].getConfig('printkeyevent') == 'True':
            log.log('{1} {0} ScanCode: {2}'.format(EvtType,Key,EvtScanCode), )
            pass

        covering = INFO['covering']
        if not INFO['GEEKEY'].vim.vim_on: covering = True
        elif INFO['GEEKEY'].vim.vim_on and INFO['GEEKEY'].vim.insert_mode:
            covering = True

        if not covering: geeKeyboard.coverKey()
        res = INFO['GEEKEY'].OnKeyboardEvent(Key,EvtType,EvtScanCode)
        if not covering: geeKeyboard.recoverKey()

        if res: return True
        return False
    except Exception as e:
        DE()
        pass
    return True

def mouseCallBack(evt):
    res = INFO['GEEKEY'].OnMouseEvent(evt)
    return res

class Listener:
    def __init__(self):
        self.hm = PyHook3.HookManager()
        self.hm.KeyDown = keyboardCallBack
        self.hm.KeyUp = keyboardCallBack
        self.hm.MouseAll = mouseCallBack

        self.timer = None
        self.hook()

    def hook(self):
        self.hm.HookMouse()
        self.hm.HookKeyboard()
        if self.timer:  self.timer.Stop()
        self.timer = WxCallLater( 5, self.hook )

    def exit(self):
        self.hm.UnhookKeyboard()
        self.hm.UnhookMouse()


