#!/usr/bin/env python
# -*- coding: utf-8 -*-
from res import *


class VimCaret(wx.Frame):
    def __init__(self,parent,mainFrame,vim):
        self.geekey = mainFrame
        self.vim = vim

        self.normal_size = (8,1)
        self.small_size = (3,2)
        wx.Frame.__init__(self,parent,wx.NewId(),"Caret",
                          size = self.normal_size,
                          style=wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_BORDER|
                          wx.FRAME_TOOL_WINDOW
        )
        self.SetBackgroundColour('#000000')
        self.Move((-200,-200))
        self.text = wx.StaticText(self, pos=(0,0), size = self.normal_size, )
        self.text.SetBackgroundColour('#000000')

        self.ui = GUITHREADINFO(cbSize=sizeof(GUITHREADINFO) )
        self.popup_hw =  self.GetTopWindow()
        pass

    def GetTopWindow(self):
        user32.GetGUIThreadInfo(0, byref(self.ui) )
        return self.ui.hwndFocus
 
    def GetCaretPosition(self):
        try:
            fhwnd =  win32gui.GetFocus()
            user32.GetGUIThreadInfo(None, byref(self.ui) ) # None/0 for foreground thread
            if self.ui.hwndFocus != self.popup_hw: self.hw = self.ui.hwndFocus
            return win32gui.ClientToScreen(self.ui.hwndFocus,
                                           (self.ui.rcCaret.left, self.ui.rcCaret.top )
            ) 
        except Exception as e:
            return (-10,-10)


    def StateReset(self):
        if not self.vim.vim_on: return
        if self.geekey.state_is_over: return 
        WxCallLater(0.001,self._StateReset)
        pass

    def _StateReset(self):
        #log.log('caret state reset')
        if self.geekey.state_is_over: return 
        if self.vim.vim_on:
            if self.vim.insert_mode:
                self.SetSize(self.small_size)
            else:
                self.SetSize(self.normal_size)
                pass
            self.Move( self.GetCaretPosition() )
            self.Show( True )
        else:
            self.Show( False )
            pass
        pass
    pass


class VimStateIndicator(wx.Frame):
    def __init__(self,parent,mainFrame,vim):
        self.geekey = mainFrame
        self.vim = vim
        self.size = (0,0)
        self.timer = None

        wx.Frame.__init__(self,parent,wx.NewId(),"Indicator",
                          size = self.size,
                          style=wx.STAY_ON_TOP|wx.FRAME_NO_TASKBAR|wx.NO_BORDER|
                          wx.FRAME_TOOL_WINDOW
        )
        self.Move((-200,-200) )

        ###
        font = wx.Font(10, wx.ROMAN, wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_LIGHT,)
        self.panel = wx.Panel(self,-1,pos=(0,0),size=(2000,2000) )

        self.text = wx.StaticText(self.panel, pos=(0,0), style = wx.ALIGN_LEFT)
        self.text.SetFont(font)
        self.text.SetForegroundColour( GetColorMap('vim text') ) ####

        self.text_input = wx.TextCtrl(self.panel, pos=(0,0),style = wx.NO_BORDER,)
        self.text_input.SetFont(font)
        self.text_input.SetForegroundColour( GetColorMap('vim text') ) ####

        self.text_hide = wx.StaticText(self.panel, pos=(-5000,-5000), style = wx.ALIGN_LEFT)
        self.text_hide.SetFont(font)

        self.text_tmp = wx.TextCtrl(self.panel, pos=(-8888,-8888),
                                    style = wx.NO_BORDER|wx.TE_RICH2|wx.TE_MULTILINE,
        )

        ###
        self.ui = GUITHREADINFO(cbSize=sizeof(GUITHREADINFO) )
        self.sys_rect = (0, 0, win32api.GetSystemMetrics(0),  win32api.GetSystemMetrics(1)-50 )
        ###
        self.text.SetLabel( lt("--vim enabled--")),

        self.last_pos = (0,0)
        self.last_win = self.GetTopWindow()

        self.text_input.Bind(wx.EVT_TEXT, self.OnChange )
        pass

    def GetCbData(self):
        self.last_win = self.GetTopWindow()
        self.Raise()
        self.text_input.SetFocus()
        #print( self.FindFocus(), self.text_input )
        #KeyPress('left ctrl')
        old_mode = self.vim.insert_mode
        self.vim.insert_mode = True
        KeyStroke('v')
        KeyStroke('v')
        KeyStroke('v')
        KeyStroke('v')
        KeyStroke('v')
        self.vim.insert_mode = old_mode 
        #KeyRelease('left ctrl')
        win32gui.SetForegroundWindow( self.last_win )
        #print( self.FindFocus(), self.text_input )
        txt = self.text_input.GetValue()
        #print('text_input = ',txt )
        return txt

    def GetText(self):
        return self.text_input.GetValue()

    def ConfSize(self):
        self.label_size = self.text.GetSize()
        self.text_hide.SetLabel( self.text.GetLabel() +self.GetText() )
        self.size = self.text_hide.GetSize()
        self.size = (self.size[0]+20,self.size[1] )
        self.text_input.SetPosition( (self.label_size[0],0) )
        self.text_input.SetSize( (self.size[0] - self.label_size[0],self.label_size[1]) )

        self.SetSize( self.size )
        return


    def OnChange(self,evt):
        self.ConfSize()

    def GetTopWindow(self):
        user32.GetGUIThreadInfo(0, byref(self.ui) )
        return self.ui.hwndFocus
 
    def GetPosition(self):
        if self.vim.commanding and self.last_pos: return self.last_pos
        if self.FindFocus() == self.text_input and self.last_pos: return self.last_pos
        topwin = self.GetTopWindow()
        self.last_win = topwin
        try:
            rect = win32gui.GetWindowRect( topwin )
        except Exception as e:
            rect = self.sys_rect 
            pass
        if rect[3] > self.sys_rect[3]: pos = ( int(rect[2]/2+rect[0]/2), self.sys_rect[3] +5 - self.size[1] )
        else: pos  = ( int(rect[2]/2+rect[0]/2), rect[3] + 5 - self.size[1] )
        self.last_pos = pos
        return pos
    

    def __set(self,label,text,color_name = None):
        self.text.SetLabel( "  "+label+"  ")
        self.text_input.ChangeValue( text )
        self.ConfSize()

        if color_name:
            color = GetColorMap(color_name)
            self.geekey.key_buttons['v'].SetBackgroundColour( color )

            self.text.SetBackgroundColour( color )
            self.text_input.SetBackgroundColour( color )
            self.panel.SetBackgroundColour( color )
            pass
        pass

    def StateReset(self,label='', text="", label_extra=''):
        #print('StateReset called label={0} text={1}'.format(label,text) )
        if self.FindFocus() == self.text_input: win32gui.SetForegroundWindow(self.last_win)
        if self.geekey.state_is_over: return 
        WxCallLater(0.001,self._StateReset,label,text,label_extra)
        #print('StateReset finished' )
        pass
        
    def _StateReset(self,label,text,label_extra):
        #print('statereset called label={0} text={1}'.format(label,text) )
        if self.vim.vim_on:
            mode = ""
            if self.vim.visual_mode:  mode = 'visual'
            elif self.vim.insert_mode: mode = 'insert'
            else: mode = 'normal'

            if label == "" or label == 'disable':
                label = '--' + lt(mode) + '--'
                if self.vim.number: label = label + self.vim.number + "--"
                if self.vim.record: label = label + lt("recording ")+self.vim.record+"--"
                if self.vim.register: label = label + "\""+self.vim.register+"--"
                if label_extra: label = label + label_extra+"--"
                if self.vim.commanding:
                    if self.vim.expression: label = '='
                    else: label = ':'
                pass

            self.__set( label ,text, 'vim '+mode )

            self.Move( self.GetPosition() )
            self.Show( True )
        else:
            if label == 'disable':
                if self.timer: self.timer.Stop()
                self.Show(False )
                return
            if label or text:
                self.__set( label,text, 'vim insert' )
            else :
                self.__set( "--"+lt('vim disabled')+"--","",'vim disable' )
                pass
            self.Move( self.GetPosition() )
            self.Show( True )
            if not self.geekey.state_is_recording:
                if self.timer: self.timer.Stop()
                self.timer = WxCallLater(5,self.Show,False)
            pass
    pass


class Vim:
    def __init__(self,parent, mainFrame):
        self.geekey = mainFrame
        self.vim_on = False
        self.visual_mode = False
        self.insert_mode = False
        self.visual_move = 0
        self.unprocessed_char = ""
        self.number = ""
        self.registering = False
        self.register = ""
        self.esc_time = 0
        self.line_cut = False
        self.big_cut = False
        self.commanding = False
        self.command = ''
        self.expression = False
        self.recording = False
        self.record = ''
        self.executing = False
        self.execute = ''
        self.commands = ['']
        self.expressions = ['']
        self.command_index = 0 
        self.expression_index = 0

        self.caret = VimCaret(parent, self.geekey, self)
        self.indicator = VimStateIndicator(parent, self.geekey, self)

        pass

    def Destroy(self):
        if self.caret: self.caret.Destroy()
        if self.indicator: self.indicator.Destroy()
        pass

    pass

    def quit_visual_mode_state(self):
        KeyRelease('left shift')
        self.visual_mode = False

    def quit_visual_mode_move(self):
        if self.visual_move < 0: 
            KeyStroke('left')
        else:
            KeyStroke('right')
            pass
        self.visual_move = 0

    def quit_visual_mode(self,force=False):
        if force or self.visual_mode :
            #log.log('quit visual mode', self.visual_move)
            self.quit_visual_mode_state()
            self.quit_visual_mode_move()
            pass
        pass

    def quit_insert_mode(self):
        self.insert_mode = False
        pass

    def mini_state_reset(self):
        pass

    def state_reset(self):
        self.quit_visual_mode()
        self.quit_insert_mode()
        self.unprocessed_char = ''
        self.number = ''
        #self.vim_on = True
        self.registering = False
        self.register = ''
        self.commanding = False
        self.command = ''
        self.expression = False
        # self.recording = False
        # self.record = ''
        self.play_ratio = 0
        self.geekey.autoComplete.StateReset()
        self.indicator.StateReset()
        self.caret.StateReset()
        pass

    def state_switch(self,state=None):
        #state = None, 'on', 'off'
        self.geekey.number_string = ''
        self.insert_mode = False
        self.quit_visual_mode()
        self.state_reset()

        if state == 'on' or state == 'True':
            self.vim_on = True
        elif state == 'off' or state == 'False':
            self.vim_on = False 
        else:
            self.vim_on = not self.vim_on

        if self.vim_on:
            ### to make shift cover and recover work properly
            geeKeyboard.coverKey('shift')
            geeKeyboard.recoverKey('shift')
            ###
        else:
            self.recording = False
            self.record = ''

        self.geekey.Log(lt('enable vim mode') if self.vim_on else lt('exit vim mode') )

        self.indicator.StateReset()

        return False

    # big cut should be '0' '1' '0' for big copy '1' for big delete
    def _setRegister(self,bigcut,linecut):
        txt = getCbText()
        #txt = self.indicator.GetCbData()
        if linecut: txt = '^' + txt
        if not self.register:
            if bigcut == '0':
                self.register = '0'
            elif bigcut == '1':
                self.register = '1'
                # move 
                for i in range(9,1,-1):
                    SetRegister(str(i), GetRegister(str(i-1) ) )
                    pass
                pass
            else:
                self.register = '-'
                pass
            pass
        SetRegister(self.register, txt )
        self.line_cut = linecut
        self.register = ''
        self.indicator.StateReset()

    def setRegister(self,bigcut,linecut):
        WxCallLater(0.1, self._setRegister, bigcut, linecut )

    def getRegister(self):
        if not self.register: return True #do nothing
        if self.register != '"': 
            res = GetRegister(self.register) 
            #print('get register {0}:{1}'.format(self.register,res) )
            if not res:
                self.indicator.StateReset( lt('nothing in register {0}',self.register)  ) 
                return False
            if res[0] == '^':
                setCbText( res[1:] )
                self.line_cut = True
            else:
                setCbText( res )
                self.line_cut = False
                pass
            pass
        self.register = ''
        self.indicator.StateReset()
        return True

    def registeringGet(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_' + Key 
        self.register = Key
        self.registering = False
        if Key == '=':
            self.commanding = True
            self.expression = True
            self.indicator.StateReset("=")
            if self.expressions[0]: self.expressions = [''] + self.expressions
            pass
        else:
            self.indicator.StateReset()
            pass
        return False
            
    def recordingGet(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_'+Key
        self.record = Key
        self.recording = False #state to get register key for store recording
        self.indicator.StateReset()

        self.geekey.startRecording()

        return False

    def executingDo(self,Key):
        if self.geekey.state_on_shift:Key = 'shift_'+Key
        self.execute = Key
        self.executing = False
        self.indicator.StateReset(lt('executing {0}',Key) )
        cont = GetRegister(Key) 
        print('cont =',cont)
        if not cont: return False
        mapvalue = cont.split(':') # :0:_x~0.1:x~0.2
        if len(mapvalue)>=3:
            try:
                ratio = toFloat(mapvalue[1],-1)
                if ratio < 0: return False
                mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                oper_number = lambda : 1 if self.number  == '' else int(self.number)
                sequence =  list(mapvalue) * oper_number()
                self.number = ''
                self.geekey.Replay(ratio, sequence)
            except Exception as e:
                self.geekey.Log("try execute register {0} failed for: {1}".format(Key,e) )
                self.indicator.StateReset( lt('executing {0} failed',Key) )
                if DEBUG: raise e
        return False
                
    def ProcessKey(self,Key,EvtType):
        # esc not included
        if ( Key in MenuKeys_1 ): 
            self.quit_visual_mode()
            self.indicator.StateReset()
            return True

        if self.commanding:
            self.indicator.Raise()
            self.indicator.text_input.SetFocus()

            if self.visual_mode: KeyRelease('left shift')

            if Key in ('delete','backspace',):
                if EvtType == 'key up': return True
                if self.indicator.GetText() == '':
                    self.command = ""
                    self.commanding = False
                    self.expression = False
                    self.indicator.StateReset()
                    return False
                return True
            if Key in ('up','down','page up','page down'):
                if EvtType == 'key up': return False
                if self.expression:
                    if Key in ('up','page up'):
                        if self.expression_index<len(self.expressions)-1:self.expression_index+=1 
                    else:
                        if self.expression_index>0: self.expression_index -=1 
                        pass
                    self.command = self.expressions[self.expression_index]
                    self.indicator.text_input.SetValue(self.command)
                    return False
                else:
                    if Key in ('up','page up'):
                        if self.command_index<len(self.commands)-1:self.command_index+=1 
                    else:
                        if self.command_index>0: self.command_index -=1 
                        pass
                    self.command = self.commands[self.command_index]
                    self.indicator.text_input.SetValue(self.command)
                    return False

            elif Key == 'return': #single in ('xxxx') will lead to var in 'xxx'
                if EvtType == 'key up': return False
                #print('the final return ')
                if self.visual_mode: KeyPress('left shift')
                if self.indicator.FindFocus() == self.indicator.text_input:
                    win32gui.SetForegroundWindow(self.indicator.last_win )
                if self.expression:
                    try:
                        self.expressions[0] = self.indicator.GetText()
                        self.command = self.expressions[0]
                        res = str( eval( self.command) )
                        # save result to "=
                        SetRegister('=',res)
                    except Exception as e:
                        res = lt('evaluation failed for: {0}',e) 
                        self.registering = False
                        self.register = ''
                        pass
                    self.commanding = False
                    self.command = ''
                    self.expression = False
                    #print('try set res=',res)
                    self.indicator.StateReset('',res)
                    pass
                else:
                    self.commands[0] = self.indicator.GetText()
                    self.command = self.commands[0]
                    #print('execute command',self.command)
                    WxCallLater(0.1,self.ProcessCommand, self.command )
                    self.commanding = False
                    self.command = ''
                    self.expression = False
                    pass
                return False
            # append to command
            return True

        if ( Key in ('home','end','page up','page down','left','right','up','down','delete','backspace','return') ):
            return True
        
        ### always ignore key up for none input keys
        if EvtType == 'key up':
            if Key in FunctionKeys or self.geekey.state_on_ctrl or self.geekey.state_on_alt or self.geekey.state_on_windows:
                return True
            return False

        ### registering and recording
            
        ### record number to do repeat
        if not self.geekey.state_on_shift and not self.geekey.state_on_ctrl and Key in NumberKeys and not (self.number == '' and Key == '0'):
            if self.registering: self.registeringGet(Key)
            elif self.recording: self.recordingGet(Key)
            elif self.executing: self.executingDo(Key)
            else:
                self.number += Key
                self.registering = False
                self.recording = False
                self.indicator.StateReset()
                pass
            return False

        if self.registering: return self.registeringGet(Key) 
        elif self.recording: return self.recordingGet(Key)
        elif self.executing: return self.executingDo(Key)

        SendKey = lambda key,repeated=1: KeySend(key,EvtType,repeated)
        ckey = Key
        if self.geekey.state_on_shift: ckey = 'shift_' + ckey
        if self.geekey.state_on_ctrl: ckey = 'ctrl_' + ckey
        if self.geekey.state_on_alt: ckey = 'alt_' + ckey

        char_processed = True
        double_key = False
        keep_number = False

        if self.unprocessed_char:
            ckey = self.unprocessed_char + "__" + ckey 
            self.unprocessed_char = ""
            double_key = True

        oper = GetMap('vim',ckey)

        #log.log('Key = {2}, ckey = {0}, oper = {1}'.format(ckey,oper,Key) )

        move =  vim_move_count.get(oper,0)
        if self.visual_mode: self.visual_move += move

        ### record first char this turn for double chars cmd like dd, gg, et.al
        if not self.visual_mode: geeKeyboard.coverKey('shift')

        oper_number = lambda : 1 if self.number  == '' else int(self.number)

        ###########################################
        ##### vim oper start 
        ###########################################

        if oper in ('left','right','up','down','home','end','page up','page down'):
            #log.log('simulte',oper)
            for i in range(oper_number() ):
                KeyStroke( oper )
                pass
            pass
        ############################################################ 
        # instant return oper which keep self.number values
        elif oper == 'register':
            self.registering = True
            self.register = ''
            self.indicator.StateReset(label_extra="\"")
            keep_number = True
        elif oper == 'execute':
            self.execute = ''
            self.executing = True
            self.indicator.StateReset(label_extra="@")
            keep_number = True
        elif oper == 'command':
            self.commanding = True
            if self.commands[0]: self.commands = [''] + self.commands
            self.indicator.StateReset(":")
        elif oper == 'record':
            print('record command',self.record,self.recording)
            if self.record: # is recording state, try stop recording
                print('stop recording')
                res = self.geekey.endRecording()
                print( 'vim recording res =',self.record,res )
                if res:
                    res = ":0{0}".format(res)
                    SetRegister(self.record, res, )   
                    pass
                
                self.indicator.StateReset( lt("recording {0} end",self.record) )
                self.record = ''
            else:
                #print('prepare recording')
                self.recording = True
                self.indicator.StateReset(label_extra="q")
                pass
            pass
        ############################################################ 
        elif oper == 'home line':
            KeyStroke( 'home' )
            KeyStroke( 'home' )

        elif oper == 'home block':
            KeyStroke( 'home' )

        elif oper == 'next word':
            #log.log('simulate word')
            KeyPress( 'left ctrl' )
            for i in range(oper_number() ):
                KeyStroke( 'right' )
                pass
            KeyRelease( 'left ctrl' )

        elif oper == 'end word':
            #log.log('simulate word')
            if not self.visual_mode:
                KeyPress( 'left shift' )

            KeyPress( 'left ctrl' )
            for i in range(oper_number() ):
                KeyStroke( 'right' )
                pass
            KeyRelease( 'left ctrl' )

            if not self.visual_mode:
                KeyRelease( 'left shift' )
                KeyStroke( 'right' )

        elif oper == 'prev word':
            #log.log('simulate back')
            KeyPress( 'left ctrl' )
            for i in range(oper_number() ):
                KeyStroke( 'left' )
                pass
            KeyRelease( 'left ctrl')

        elif oper == 'prev para':
            KeyPress( 'left ctrl' )
            for i in range(oper_number() ):
                KeyStroke( 'up' )
                pass
            KeyRelease( 'left ctrl' )

        elif oper == 'next para':
            KeyPress( 'left ctrl' )
            for i in range(oper_number() ):
                KeyStroke( 'down' )
                pass
            KeyRelease( 'left ctrl' )

        elif oper == 'insert':
            if not self.visual_mode:
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 

        elif oper == 'insert begin':
            if not self.visual_mode:
                KeyStroke( 'home' )
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 

        elif oper == 'append':
            if not self.visual_mode:
                #KeyStroke( 'right' )
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False 

        elif oper == 'append end':
            if not self.visual_mode:
                KeyStroke( 'end' )
                self.insert_mode = True
                self.indicator.StateReset()
            else:
                char_processed = False

        elif oper == 'insert prev line':
            if not self.visual_mode:
                self.insert_mode = True
                KeyStroke('home')
                KeyStroke('return')
                KeyStroke('up')
                self.indicator.StateReset()
            else:
                char_processed = False 
            pass

        elif oper == 'insert next line':
            if not self.visual_mode:
                self.insert_mode = True
                KeyStroke('end')
                KeyStroke('return')
                self.indicator.StateReset()
            else:
                char_processed = False 
            pass

        elif oper == 'change':
            if self.visual_mode: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change word':
            if not self.visual_mode:
                KeyPress('left shift')
                KeyPress('left ctrl')
                KeyStroke('right')
                KeyRelease('left ctrl')
                KeyRelease('left shift')
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change word back': #visual or not visual 
            if not self.visual_mode:
                KeyPress('left shift')
                KeyPress('left ctrl')
                KeyStroke('left')
                KeyRelease('left ctrl')
                KeyRelease('left shift')
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change line':
            if not self.visual_mode:
                KeyStroke('home')
                KeyStroke('home')
                KeyPress('left shift')
                KeyStroke('end')
                for i in range(oper_number()-1 ): KeyStroke( 'down' )
                KeyStroke('left')
                KeyStroke('end')
                KeyRelease('left shift')
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change begin':
            if not self.visual_mode:
                KeyPress('left shift')
                KeyStroke('home')
                KeyStroke('home')
                KeyRelease('left shift')
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()
            pass
        elif oper == 'change end':
            if not self.visual_mode:
                KeyPress('left shift')
                KeyStroke('end')
                KeyRelease('left shift')
            else: self.quit_visual_mode_state()
            KeyStroke('delete')
            self.insert_mode = True
            self.indicator.StateReset()

            pass
        elif oper == 'visual mode':
            #log.log('visual mode')
            if not self.visual_mode:
                KeyPress('left shift')
                self.geekey.state_on_shift = False
                self.visual_mode = True
            else:
                self.quit_visual_mode()
                pass
            self.indicator.StateReset()
            return False
        ##########################
        ### copy part
        elif oper == 'copy' :
            #log.log('process copy')
            if self.visual_mode:
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False,)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                char_processed = False 
            pass
        elif oper == 'copy word':
            if self.visual_mode:
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False,)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                KeyPress('left ctrl')
                KeyStroke('right')
                KeyRelease('left ctrl')
                KeyRelease('left shift')

                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                KeyStroke('left')
                self.setRegister(False, False,)

            pass
        elif oper == 'copy word back':
            if self.visual_mode:
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False,)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                KeyPress('left ctrl')
                KeyStroke('left')
                KeyRelease('left ctrl')
                KeyRelease('left shift')

                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister(False,False,)

                KeyStroke('right')
            pass
        elif oper == 'copy line' : # no visual mode will be here
            if self.visual_mode: # the same as copy 
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False,)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                #log.log('process copy')
                for i in range( oper_number() -1 ): KeyStroke('down')
                KeyStroke('end')
                KeyPress('left shift')
                KeyStroke('home')
                for i in range( oper_number() -1 ): KeyStroke('up')
                KeyStroke('home')
                KeyRelease('left shift')

                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')

                self.setRegister('0',True)
                KeyStroke('left')
                pass
            pass
        elif oper == 'copy begin':
            if self.visual_mode: # the same as copy 
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                KeyStroke('home')
                KeyStroke('home')
                KeyRelease('left shift')

                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False)

                KeyStroke('right')
                pass

            pass
        elif oper == 'copy end':
            if self.visual_mode: # the same as copy 
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False)

                self.quit_visual_mode_move()
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                KeyStroke('end')
                KeyRelease('left shift')

                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('0',False)

                KeyStroke('left')
                pass
            pass

        elif oper == 'x cut' :
            #log.log('process cut')
            if self.visual_mode:
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('x')
                KeyRelease('left ctrl')
                self.setRegister('1',False)

                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                for i in range(oper_number() ):
                    KeyStroke('right')
                    pass
                KeyRelease('left shift')
                KeyPress('left ctrl')
                KeyStroke('x')
                KeyRelease('left ctrl')
                self.setRegister(False,False)
                pass

        elif oper == 'x cut previous' :
            #log.log('process cut')
            if self.visual_mode:
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('x')
                KeyRelease('left ctrl')
                self.setRegister('1',False)

                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                for i in range(oper_number() ):
                    KeyStroke('left')
                    pass
                KeyRelease('left shift')
                KeyPress('left ctrl')
                KeyStroke('x')
                KeyRelease('left ctrl')
                self.setRegister(False,False)

                pass

        elif oper == 'cut':
            #log.log('process cut')
            if self.visual_mode:
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('x')
                KeyRelease('left ctrl')
                self.setRegister('1',False)

                self.indicator.StateReset()
                pass
            else:
                char_processed = False 

        elif oper == 'cut line':
            if self.visual_mode: # the same as d cut
                ## extra shift will make ctrl-c not working
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyRelease('left ctrl')
                self.setRegister('1',False)

                KeyStroke('delete')
                self.indicator.StateReset()
                pass
            else: #normal cut line

                for i in range( oper_number() -1 ): KeyStroke('down')
                KeyStroke('end')
                KeyPress('left shift')
                KeyStroke('home')
                for i in range( oper_number() -1 ): KeyStroke('up')
                KeyStroke('home')
                KeyStroke('delete')
                KeyRelease('left shift')

                self.setRegister('1',True)
                pass
            pass
        elif oper == 'cut begin': 
            KeyPress('left shift')
            KeyStroke('home')
            KeyStroke('home')
            KeyStroke('delete')
            KeyRelease('left shift')

            self.setRegister('1',False)

            pass
        elif oper == 'cut end': 
            KeyPress('left shift')
            KeyStroke('end')
            KeyStroke('delete')
            KeyRelease('left shift')

            self.setRegister('1',False)

            pass
        elif oper == 'cut word': 
            KeyPress('left shift')
            KeyPress('left ctrl')
            KeyStroke('right')
            KeyRelease('left ctrl')
            KeyStroke('delete')
            KeyRelease('left shift')

            self.setRegister(False,False)

            pass
        elif oper == 'cut word back':
            KeyPress('left shift')
            KeyPress('left ctrl')
            KeyStroke('left')
            KeyRelease('left ctrl')
            KeyStroke('delete')
            KeyRelease('left shift')

            self.setRegister(False,False)

            pass
        #######################
        # paste part
        elif oper == 'paste' :
            #log.log('process paste')
            if self.getRegister():
                if self.line_cut: # paste to a single line
                    for i in range(oper_number() ):
                        KeyStroke('end')
                        KeyStroke('return')
                        KeyStroke('home')

                        KeyPress('left ctrl')
                        KeyStroke('v')
                        KeyRelease('left ctrl')
                    pass
                else:
                    KeyPress('left ctrl')
                    for i in range(oper_number() ): KeyStroke('v')
                    KeyRelease('left ctrl')
                pass

        elif oper == 'paste prev':
            #log.log('process paste')
            if self.getRegister():
                if self.line_cut: # paste to a single line
                    for i in range(oper_number() ):
                        KeyStroke('home')
                        KeyStroke('home')
                        KeyStroke('up')
                        KeyPress('left ctrl')
                        KeyStroke('v')
                        KeyRelease('left ctrl')
                        pass
                else:
                    KeyPress('left ctrl')
                    for i in range(oper_number() ): KeyStroke('v')
                    KeyRelease('left ctrl')
                pass
        elif oper == 'undo' :
            KeyPress('left ctrl')
            KeyStroke('z')
            KeyRelease('left ctrl')
            pass
        elif oper == 'redo' :
            KeyPress('left ctrl')
            KeyStroke('y')
            KeyRelease('left ctrl')
            pass
        elif oper == 'merge line':
            KeyStroke('end')
            KeyStroke('delete')
            pass
        elif oper == 'find' :
            if self.visual_mode: # the same as d cut
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyStroke('f')
                KeyStroke('v')
                KeyRelease('left ctrl')
                self.insert_mode = True
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left ctrl')
                KeyStroke('f')
                KeyRelease('left ctrl')

                self.insert_mode = True
                self.indicator.StateReset()
                pass
            pass
        elif oper == 'find current':
            if self.visual_mode: # the same as d cut
                self.quit_visual_mode_state() 
                KeyPress('left ctrl')
                KeyStroke('c')
                KeyStroke('f')
                KeyStroke('v')
                KeyRelease('left ctrl')
                self.insert_mode = True
                self.indicator.StateReset()
                pass
            else:
                KeyPress('left shift')
                KeyPress('left ctrl')
                KeyStroke('right')
                KeyRelease('left shift')

                KeyStroke('c')
                KeyStroke('f')
                KeyStroke('v')
                KeyRelease('left ctrl')

                self.insert_mode = True
                self.indicator.StateReset()
                pass
            pass
        elif oper in ('jump head','jump tail') :
            if self.number == '': # jump to buffer end
                KeyPress('left ctrl')
                if oper == 'jump head': KeyStroke('home')
                else: KeyStroke('end')
                KeyRelease('left ctrl')
                pass
            else:
                KeyPress('left ctrl')
                KeyStroke('home')
                KeyRelease('left ctrl')
                for i in range(oper_number()-1 ):
                    KeyStroke('down')
                pass
            pass
        elif oper == 'save':
            KeyPress('left ctrl')
            KeyStroke('s')
            KeyRelease('left ctrl')
            pass

        ###########################################
        ##### vim oper end
        ###########################################
        else: #others 
            if not self.visual_mode:
                #log.log('try test vim map for',ckey)
                #log.log(mapvalue)
                if oper:
                    mapvalue = oper.split(':')

                    if len(mapvalue)>=3:
                        try:
                            #log.log( lt('cmd "{0}" processed by self-defined macro',ckey) )
                            name = mapvalue[0]
                            oper = name
                            ratio = toFloat(mapvalue[1],1.0 )
                            mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                            sequence =  list(mapvalue) * oper_number()
                            #log.log('macro sequence is',sequence)
                            self.number = ''
                            self.geekey.Replay(ratio, sequence)
                            return False
                        except Exception as e:
                            self.geekey.Log("self-defined command {0} failed for: {1}".format(oper,e) )
                            self.indicator.StateReset( lt('command {0} failed',oper) )
                            if DEBUG: raise e
                            pass
                        pass
                    else:
                        self.geekey.Log("Command {0} not processed".format(oper) )
                        self.indicator.StateReset( lt('Command not processed')+": "+oper )
                    pass
                else:
                    char_processed = False 
                    pass
            else:
                #log.log('key {0} oper {1} not processed'.format(ckey, oper) )
                char_processed = False 

        if not self.visual_mode: geeKeyboard.recoverKey('shift')

        ### record unprocessed Key for 
        #log.log('after process',char_processed, double_key, self.unprocessed_char, self.number)
        if char_processed: # processed
            if not keep_number:
                self.number = ''
                self.indicator.StateReset()
            return False

        # what left are all unprocessed ckey
        if double_key:
            ### not find cmd
            self.indicator.StateReset(lt("command {0} not found.",ckey ),' ')
            log.log( lt('command {0} not found. You can bind your own operation to vim_map_{0}:: item in globalvim.ini',ckey) )
            self.number = ''
            pass
        else:
            if Key in FunctionKeys or self.geekey.state_on_ctrl or self.geekey.state_on_alt or self.geekey.state_on_windows:
                ### pass on current keyboard event to system or current application
                self.unprocessed_char = ''
                self.number = ''
                return True 
            self.unprocessed_char = ckey
            pass

        return False

    # n == 0: current to end
    # n == -N: current to end - n 
    # n > 0:  current to someplace
    def do_replace(self,pattern,string,flags): #
        ori_txt = getCbText()
        #print('do replace with',pattern,string,flags,'to',['>>>',ori_txt,'<<<'] )
        flag = re.M|re.S|re.U
        count = 0
        if not 'g' in flags: count = 1
        if 'i' in flags: flag = flag|re.I
        #print('ori txt =',ori_txt)
        if count:
            strings = ori_txt.split('\n')
            #print('do seperate to',strings)
            new_txt='\n'.join([re.sub(pattern,string,s,count=count,flags=flag)for s in strings])
            pass
        else:
            new_txt = re.sub(pattern,string,ori_txt,count=count,flags=flag)
            pass
        #print('new txt >>>',[new_txt,'<<<'])
        #print(ori_txt == new_txt)
        setCbText(new_txt)
        KeyPress('left ctrl')
        KeyStroke('v')
        KeyRelease('left ctrl')
        self.indicator.StateReset( lt('substitution done') )
        return 
        
    def ProcessCommand(self,command):
        command = command.strip()
        if not command: return
        # check if substitute command s/

        items = re.split(r'(?<!\\)#',command)
        if not( len(items) == 4 and items[0][-1] == 's'): items = re.split(r'(?<!\\)/',command)
        if len(items) == 4 and items[0][-1] == 's': # a sub command 'xxs/xx/yy/zz'
            #print('try do substitute')
            try:
                pattern = items[1]
                string = items[2]
                flags = items[3] # only support 'gi' or empty
                if 'c' in flags:  raise Exception(("flag 'c' is not supported"))

                if self.visual_mode:
                    KeyPress('right shift')
                    KeyStroke('delete')
                    KeyRelease('right shift')
                    self.quit_visual_mode_state()
                    pass
                else:
                    scope = items[0][:-1]
                    if scope == '%':
                        start = [1,0]
                        end = ['$',0] 
                    elif scope == '':
                        start = ['.',0]
                        end = ['.',0]
                    else:
                        ss = scope.split(',')
                        if len(ss) > 2:
                            raise Exception(lt("Invalid search scope {0}",scope))
                        start = vim_search_scope(ss[0] )
                        if not start: raise Exception(("Invalid search scope {0}",scope))
                        if len( ss ) == 1: end = start
                        else: end = vim_search_scope(ss[1] )
                        if not end: raise Exception(("Invalid search scope {0}",scope))
                        #print(start,end)
                        if start[0] == '': start[0] = '.'
                        if end[0] == '': end[0] = '.'
                        pass
                    #print(start,end)

                    # step 1 get range txt
                    #SetKeyDelay( 0 )
                    if type(start[0])  == int and type(end[0]) == int:
                        s = start[0] + start[1]
                        e = end[0] + end[1]
                        #print('both number',s,e)
                        if s>e: raise Exception(("Invalid search scope {0}",scope))
                        KeyPress('left ctrl')
                        KeyStroke('home')
                        KeyRelease('left ctrl')
                        for i in range(e-1): KeyStroke('down')
                        KeyStroke('end')
                        # KeyStroke('space')
                        # KeyStroke('left')

                        KeyPress('left shift')
                        KeyStroke('home')
                        for i in range(e-s): KeyStroke('up')
                        KeyStroke('home')
                        KeyStroke('delete')
                        KeyRelease('left shift')

                    elif type(start[0])  == int and end[0] == '$':
                        #print('replace all')
                        KeyPress('left ctrl')
                        KeyStroke('end')
                        KeyRelease('left ctrl')
                        for i in range(-end[1]): KeyStroke('up')
                        KeyStroke('end')
                        # KeyStroke('space')
                        # KeyStroke('left')

                        KeyPress('left shift')

                        KeyPress('left ctrl')
                        KeyStroke('home')
                        KeyRelease('left ctrl')
                        s = start[0]+start[1]
                        for i in range(s-1): KeyStroke('down')
                        KeyStroke('home')
                        KeyStroke('delete')
                        KeyRelease('left shift')

                    elif type(start[0]) == int and end[0] == '.':
                        #print('top to current')
                        for i in range( -end[1] ): KeyStroke('up')
                        for i in range( end[1] ): KeyStroke('down')
                        KeyStroke('end')
                        # KeyStroke('space')
                        # KeyStroke('left')

                        KeyPress('left shift')
                        KeyPress('left ctrl')
                        KeyStroke('home')
                        KeyRelease('left ctrl')
                        s = start[0]+start[1]
                        for i in range(s-1): KeyStroke('down')
                        KeyStroke('home')
                        KeyStroke('delete')
                        KeyRelease('left shift')

                    elif start[0] == '.' and end[0] == '$':
                        #print('current to tail')
                        for i in range( -start[1] ): KeyStroke('up')
                        for i in range( start[1] ): KeyStroke('down')
                        KeyStroke('home')
                        KeyStroke('home')
                        KeyPress('left shift')
                        KeyPress('left ctrl')
                        KeyStroke('end')
                        KeyRelease('left ctrl')
                        KeyStroke('left')
                        for i in range(-end[1]): KeyStroke('up')
                        if end[1]<0: KeyStroke('end')
                        KeyStroke('delete')
                        KeyRelease('left shift')
                        # KeyStroke('space')
                        # KeyStroke('left')
                    elif start[0] == '.' and type(end[0]) == int:
                        #print('current to tail')
                        for i in range( -start[1] ): KeyStroke('up')
                        for i in range( start[1] ): KeyStroke('down')
                        KeyStroke('home')
                        KeyStroke('home')
                        KeyPress('left shift')
                        KeyPress('left ctrl')
                        KeyStroke('home')
                        KeyRelease('left ctrl')
                        e = end[0]+end[1]
                        for i in range(e-1): KeyStroke('down')
                        KeyStroke('end')
                        KeyStroke('delete')
                        KeyRelease('left shift')
                        # KeyStroke('space')
                        # KeyStroke('left')
                    elif start[0] == '.' and end[0] == '.':
                        #print('around to current')
                        if start[1] > end[1]: raise Exception(("Invalid search scope {0}",scope))
                        KeyPress('home')
                        for i in range( -end[1] ): KeyStroke('up')
                        for i in range( end[1] ): KeyStroke('down')
                        KeyStroke('end')
                        # KeyStroke('space')
                        # KeyStroke('left')
                        KeyPress('left shift')
                        n = end[1] - start[1] + 1
                        for i in range(n-1): KeyStroke('up')
                        KeyStroke('home')
                        KeyStroke('delete')
                        KeyRelease('left shift')
                        pass
                    #SetKeyDelay( 0 )
                    pass
                WxCallLater(0.1,self.do_replace,pattern,string,flags) 
            except Exception as e:
                self.indicator.StateReset(lt('substitude failed for: {0}',e))
                if DEBUG: raise e
                pass
            return False

        cmds = command.split()
        if cmds[0] == 'reg' or cmds[0] == 'register': 
            cont = "--"+lt('Registers')+"--\n\n"
            cont += "\"{0}    {1}\n".format('"',escape(getCbText()[:55] ) )
            for (key,value) in sorted( GlobalMaps['vim_register'].items() ) :
                #print(key,value)
                if key and value:
                    cont += "\"{0}    {1}\n".format(key, escape(value[:55])  )
                    pass
                pass
            self.indicator.StateReset(cont)
            pass
        elif cmds[0] == 'w':
            KeyPress('left ctrl')
            KeyStroke('s')
            KeyRelease('left ctrl')
            self.indicator.StateReset(lt('save done'))
            pass
        else:
            cont = GetMap('vim_cmd',command )
            if cont: 
                mapvalue = cont.split(':') # :0:_x~0.1:x~0.2
                if len(mapvalue)>=3:
                    try:
                        ratio = toFloat(mapvalue[1],-1)
                        if ratio < 0: return False
                        mapvalue = map(lambda v: v.split('~'), mapvalue[2:] )  
                        oper_number = lambda : 1 if self.number  == '' else int(self.number)
                        sequence =  list(mapvalue) * oper_number()
                        self.number = ''
                        self.geekey.Replay(ratio, sequence)
                        self.indicator.StateReset(lt('{0} done',command ))

                    except Exception as e:
                        self.geekey.Log("command {0} failed for: {1}".format(command ,e ) )
                        self.indicator.StateReset( lt('execute {0} failed',command ))
                        if DEBUG: raise e
                        pass
                    pass
                pass
            else:
                self.indicator.StateReset(lt("command {0} not found.",command ) )
                log.log(lt("command {0} not found. You can bind your own operation to vim_cmd_map_{0} item in globalvim.ini",command) )
                pass
            return False

        return False
    pass


