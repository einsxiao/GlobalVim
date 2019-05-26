#!/usr/bin/env python
# -*- coding: utf-8 -*-

from res import *
from sortedcontainers import SortedList

class AutoComplete(wx.Frame):
    def __init__(self,parent, mainFrame, dictfile=None):
        self.geekey = mainFrame 
        wx.Frame.__init__(self,parent,wx.NewId(),"Popup",
                          style=wx.STAY_ON_TOP| wx.FRAME_NO_TASKBAR|wx.NO_BORDER|
                          wx.FRAME_TOOL_WINDOW
        )
        self.MaxNum = 9
        self.ShowBitNum = 3
        self.fontsize = 12
        ###################
        font = wx.Font(self.fontsize, wx.DEFAULT, wx.NORMAL, wx.NORMAL)
        self.lists = wx.ListBox(self,)
        self.lists.SetFont( font )
        self.lists.Bind( wx.EVT_LISTBOX, self.OnLists )
        ###################
        self.min_width = 100
        self.max_width = 1666# change to the longest candidates length
        self.item_num = self.MaxNum
        #self.char_width,self.char_height = (8,16)
        self.char_width,self.char_height = self.lists.GetTextExtent('O')
        self.switch_force_on = False
        self.auto_complete_on = False 
        #log.log 'char width,height =',self.char_width,self.char_height
        ################### read word list in from file
        self.word_list = SortedList()
        
        self.StateReset()

        ###################
        #get self hw
        self.ui = GUITHREADINFO(cbSize=sizeof(GUITHREADINFO))
        self.hw = self.GetTopWindow()
        #log.log("current hw is %s"%self.hw)
        self.Show(False);
        self.Raise()
        self.Move((-200,-200) )
        self.popup_hw =  self.GetTopWindow()
        win32gui.SetForegroundWindow(self.hw)
        #self.ui = None

        ####################
        #load dict
        self.dictfile = dictfile
        if os.path.exists( dictfile ):
            f = open( dictfile, 'r' )
            cont = f.read()
            f.close()
            for row in cont.split('\n'):
                items = row.split()
                if len(items) == 0: continue
                word = items[0]
                freq = 1
                if len(items) > 1: freq = toFloat( items[1], freq)
                self.UpdateWord( word, freq * 0.9 )
                pass
            pass
        ####
        self.height = 0
        self.width = 0
        self.start_pos = (0,0)
        pass

    def FindWord(self,word):
        ind = self.word_list.bisect_left( [word.lower(),word,-1] )
        if ind >= len( self.word_list ): return False,ind
        if self.word_list[ ind ][1] != word: return False,ind
        return True,ind

    def FindSection(self,prefix):
        left_ind = self.word_list.bisect_left( [prefix.lower(),prefix.upper(),-1] )
        right_ind = self.word_list.bisect_right( [prefix.lower()+"~",prefix.lower()+"~",-1] )
        return (left_ind,right_ind)

    def UpdateWord(self,word,freq = 1):
        if freq <= 0: return
        res,ind = self.FindWord(word)
        #log.log("update list of len %s with word %s"%(len(self.word_list),self.word) )
        if res:
            self.word_list[ind][2]+=freq
        else:
            self.word_list.add( [word.lower(),word,freq] )
            pass
        pass

    def DeleteWord(self,word):
        res,ind = self.FindWord(word)
        if res:
            del self.word_list[ind]
            pass
        pass

    def PopupActive(self):
        return ( self.GetTopWindow() == self.popup_hw )
        
    def GetInput(self,evtType,key,geekey,shift,ctrl,alt):
        ###
        if self.geekey.getConfig('geekeyenabled') == 'False': return True
        if not self.auto_complete_on: return True
        
        #log.log("get into get input")
        self.state_on_geekey = geekey
        self.state_on_shift = shift
        self.state_on_ctrl = ctrl
        self.state_on_alt = alt
        is_active = ( self.GetTopWindow() == self.popup_hw )

        # # esc to cancel candinate selection
        # if is_active and key == 'esc':
        #     if is_active:
        #         log.log('cancel auto complete by esc')
        #         self.StateReset()
        #     return False

        if key == 'tab':
            #log.log("tab here in tab dealing")
            #log.log("prepare to deal with tab without geekey state_is_on = %s"%self.state_is_on)
            if self.state_is_on: #candidate is shown on the screen
                if evtType == 'key up': return False
                #log.log("is active = %s  wtop = %s wpop = %s"%(is_active,self.GetTopWindow(),self.popup_hw ) )
                if is_active: #the same as self.state_is_selection
                    #pop up current selection
                    #log.log("the popup window is focused.")
                    select = self.lists.GetSelection()
                    select_word = self.lists.GetString( select )
                    win32gui.SetForegroundWindow(self.hw)
                    log.log("update candidate %s with %s"%(select_word,self.word) )
                    self.UpdateTabCandidate( select_word, self.word )
                    self.StateReset()
                elif self.state_is_selection: #on screen current selection
                    pass
                elif self.state_is_tab_selection: #move to next candidate in tab selection mode
                    #log.log("already in tab selection mode, move to the the next one candidate")
                    direction = 'down' if not shift else 'up'
                    word = self.MoveCandidateSelection( direction )
                    #log.log("update candidate %s with %s"%(self.word,word ) )
                    self.UpdateTabCandidate(word,self.word)
                    self.word = word
                    pass
                else: #still in input mode, enter the tab selection mode
                    #log.log("start the tab selection mode")
                    #choose the first one to be on screen 
                    self.state_is_tab_selection = True
                    select = self.lists.GetSelection()
                    reset = True
                    if select == wx.NOT_FOUND:
                        self.lists.SetSelection( 0 ) 
                        select = 0
                        reset = False
                        pass
                    new_word = self.lists.GetString(select)
                    #log.log("update candidate %s on %s"%(new_word,self.word) )
                    self.UpdateTabCandidate( new_word, self.word )
                    self.word = new_word
                    if reset or self.item_num == 1: self.StateReset()
                    pass
                #log.log("get out tab when is selection")
                return False
            else: pass # normal tab, do nothing, and return True to pass the tab by
            #log.log("get out normal tab")
            return True

        if key == 'Packet': return True
        if key == '': return True

        if self.state_is_on and key == 'return':
            if evtType == 'key up': return False
            select = self.lists.GetSelection()
            if select < 0:
                self.StateReset()
                return True
            select_word = self.lists.GetString( select )
            self.UpdateTabCandidate( select_word, self.word )
            self.StateReset()
            return False

        if self.state_is_on and key == 'delete':
            if evtType == 'key up': return False
            select = self.lists.GetSelection()
            select_word = self.lists.GetString( select )
            if select_word != '': self.DeleteWord( select_word )
            self.StateReset();
            return False

        if key in ('up','down'):
            if self.state_is_on: ##get into selection mode
                if evtType == 'key up': return False
                #log.log("get in up down")
                self.MoveCandidateSelection( key )
                self.state_is_tab_selection = False
                #self.StateReset()
                #log.log("get out up down")
                return False 
            #else
            return True

        if key in ('page up','page down'):
            if self.state_is_on: ##get into selection mode
                if evtType == 'key up': return False
                #log.log("get in page up down")
                incr = self.item_num if key == 'page down' else -self.item_num
                self.MoveCandidateSelection( incr )
                #self.StateReset()
                self.state_is_tab_selection = False
                #log.log("get out page up down")
                return False 
            #else
            return True

        if is_active: return False

        if evtType == 'key up':
            #log.log("get out key up")
            return True

        pos  = self.GetCaretPosition()
        #log.log(pos)
        old_pos = self.last_pos
        self.last_pos = pos
        #log.log('pos = %s old_pos = %s'%(pos,old_pos) )
        if ( old_pos and ( pos[0] - old_pos[0] < -8 or
                           pos[1] - old_pos[1] > 16  or
                           pos[1] - old_pos[1] < -16 ) ):
            #log.log("position condition not meet. StateReset")
            self.StateReset()
            return True
 
        #log.log 'with key = %s'%(key)

        ### combo key with ctrl or alt encoutered, rest
        if ctrl or alt or not key in StringKeys:
            #log.log("non-string key encountered")
            if key == 'backspace': 
                if len( self.section_list ) >= 1: del self.section_list[-1]
                if self.word: self.word = self.word[:-1]
                self.ShowSelection()
                #log.log("get out up backspace")
                return True
            else: #record the word to word_list
                #log.log("try update %s to word_list %s"%(self.word,self.word_list) )
                #log.log len(self.word), self.ShowBitNum 
                #remove  last SpecKeys
                while len(self.word)>1 and self.word[-1] in SpecKeys: self.word = self.word[:-1]
                if len(self.word)>=self.ShowBitNum+2 and min(self.word)!=max(self.word):
                    #log.log("update word %s"%self.word)
                    #check if word is consist of a single char ignore
                    self.UpdateWord( self.word )
                    #log.log("after word_list = %s"%(self.word_list) )
                    pass
                else:
                    #log.log("word content condition not meet to updateword")
                    #log.log("word = %s min %s max %s"%(self.word,min(self.word),max(self.word)))
                    pass
                self.StateReset()
                #log.log("get out up backspace")
                return True
            pass

        ### normal char dealing
        #log.log("normal char dealing key = %s shift = %s"%(key,shift) )
        ### add key to word
        if shift: self.word += ( UpperKeys[ key  ] if key in UpperKeys else key.upper() )
        else: self.word += key

        #log.log("word expanded to %s"%self.word)
        ###
        if len(self.word)>2 and self.word[0] == self.word[1]:
            self.StateReset()
            return True
        if not self.auto_complete_on:
            return True
        #log.log self.word
        wordlen = len( self.word )
       
        if wordlen == 1:
            self.start_pos = pos
            return True

        if wordlen < self.ShowBitNum: return True

        if wordlen == self.ShowBitNum: ### show selection window at starting pos
            #candidate will be at least MaxNum+2 bits
            lind,rind = self.FindSection( self.word )
            self.section_list.append( (lind,rind) ) ## may append (0,0) if not find
            self.ShowSelection(True)
            return True

        if wordlen > self.ShowBitNum: ### update selection window
            lind,rind = self.FindSection( self.word )
            self.section_list.append( (lind,rind) )
            self.ShowSelection()
            return True

        ### won't come here
        return True

    def ShowSelection(self,initshow=False):
        lind,rind = (0,0)
        if len( self.section_list ) > 0: lind,rind = self.section_list[-1]
        #log.log lind,rind
        if lind == rind:
            self.state_is_on = False
            self.state_no_candidate = True
            self.Show(False)
            return False
        #log.log "section = %s lind = %s rind = %s"%(self.section_list,lind,rind)
        #log.log "section list now ",self.word_list[ lind:rind ]
        #find out the max width
        self.state_is_on = True
        self.width = self.min_width
        self.width = min(self.max_width,
                         max( list(map( lambda x:len(x[1])*self.char_width,
                                   self.word_list[ lind:rind ] ) ) ) + 40 )
        self.item_num = min( rind-lind, self.MaxNum )
        #log.log 'show list with item_num = ',self.item_num
        self.old_height = self.height
        self.height = (self.char_height ) * self.item_num + 6
        self.SetSize( (self.width, self.height) )
        self.Move( (self.start_pos[0],self.start_pos[1]-self.height) )

        word_list = list(map(lambda x:x[1], self.word_list[ lind:rind ]))
        self.lists.Set( word_list )
        self.Show( True )
        win32gui.SetForegroundWindow(self.hw)
        pass

    def HideSelection(self):
        self.Show( False )
        

    def StateReset(self):
        self.Show(False)
        self.section_list = []
        self.word = ''
        self.start_pos = None
        self.state_is_on = False
        self.state_is_selection = False
        self.state_is_tab_selection = False
        self.state_no_candidate = False
        self.tab_selection_word = ''
        self.last_pos = None
        pass

    def UpdateTabCandidate(self,new_word,old_word):
        #log.log("get into update cadidate")
        for i in range( len(old_word) ):
            geeKeyboard.keyPress('backspace')
            geeKeyboard.keyRelease('backspace')
            pass
        for ch in new_word:
            upper = False
            if ch in LowerKeys:
                upper = True
                ch = LowerKeys[ ch ]
            elif ch.isupper():
                upper = True
                ch = ch.lower()
                pass
            #log.log("deal char %s with upper = %s and shift = %s"%(ch,upper,self.state_on_shift) )
            if self.state_on_shift:
                shift_key = 'left shift' if keyboard.is_pressed('left shift') else 'right shift'
                if upper:
                    #log.log"case 1" #shift is on and a upper char
                    geeKeyboard.keyPress(ch)
                    geeKeyboard.keyRelease(ch)
                else:
                    #log.log"case 2" #not upper char, but the shift key is on
                    geeKeyboard.keyRelease(shift_key)
                    geeKeyboard.keyPress(ch)
                    geeKeyboard.keyRelease(ch)
                    geeKeyboard.keyPress(shift_key)
                    pass
                pass
            else: # not on shift
                if upper:
                    #log.log"case 3" #not on shift and A upper char
                    geeKeyboard.keyPress('left shift')
                    geeKeyboard.keyPress(ch)
                    geeKeyboard.keyRelease(ch)
                    geeKeyboard.keyRelease('left shift')
                else: 
                    #log.log"case 4"  #not shift and not upper
                    geeKeyboard.keyPress(ch)
                    geeKeyboard.keyRelease(ch)
                    pass
                pass
            pass
        #log.log("get out of update cadidate")
        pass

    def MoveCandidateSelection(self,direction='down'):
        if direction == 'down': incr = 1
        elif direction == 'up': incr = -1
        else: incr = direction
        new_item = self.lists.GetSelection() + incr
        if new_item < 0: new_item = 0
        elif new_item >= self.lists.GetCount(): new_item = self.lists.GetCount() - 1 
        else:pass
        word = self.lists.GetString( new_item )
        self.lists.SetSelection( new_item )
        self.lists.EnsureVisible( new_item )
        return word
   
    def GetTopWindow(self):
        fhwnd =  win32gui.GetFocus()
        user32.GetGUIThreadInfo(0, byref(self.ui) )
        return self.ui.hwndFocus
        
    def GetCaretPosition(self):
        fhwnd =  win32gui.GetFocus()
        user32.GetGUIThreadInfo(None, byref(self.ui) ) # None/0 for foreground thread
        if self.ui.hwndFocus != self.popup_hw: self.hw = self.ui.hwndFocus
        return win32gui.ClientToScreen(self.ui.hwndFocus,
                                       (self.ui.rcCaret.left, self.ui.rcCaret.top )
        ) 

    def OnLists(self,evt):
        #log.log("selection = %s "%(self.lists.GetSelection() ) )
        pass
        
    def Destroy(self):
        ### save lists to dictfile
        cont = ''
        for item in self.word_list:
            if item[2] <= 0: continue
            cont += "%s %s\n"%(item[1],item[2])
            pass
        f = open( self.dictfile, 'w' )
        f.write( cont )
        f.close()
        
        super(AutoComplete,self).Destroy()
        pass

    def SwitchState(self,state=None):
        #log.log("geekey+tab to switch the auto complete state")
        if not state: self.auto_complete_on = not self.auto_complete_on
        else: self.auto_complete_on = True if state in ('True', 'on') else False

        if not self.auto_complete_on: #turn off
            self.StateReset()
            self.geekey.vim.indicator.StateReset( lt('_autocomplete'),lt('_autocomplete_off'))
            pass
        else: #turn on
            self.geekey.vim.indicator.StateReset( lt('_autocomplete'),lt('_autocomplete_on'))
            pass

        pass

            

        


    pass
