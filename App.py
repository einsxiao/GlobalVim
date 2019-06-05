
from GeeKey import *
from res import runAsAdmin
import wx

class LocalApp(wx.App):
    def OnInit(self):
        #mySplash = LocalSplashScreen()
        #mySplash.Show()
        ###################### other way without splash
        self.name = "SingleApp-%s"% wx.GetUserId()

        self.instance = wx.SingleInstanceChecker(self.name)

        if self.instance.IsAnotherRunning():
            wx.MessageBox(lt("Another GlobalVim instance is running"),lt('Error') )
            return False

        
        INFO['GEEKEY'] = GeeKeyFrame(None,-1)

        self.SetTopWindow(INFO['GEEKEY'])
        INFO['GEEKEY'].Show(True)
        INFO['GEEKEY'].RaiseShow()
        return True
    pass

if __name__ == '__main__':
    INFO['PID'] = os.getpid()
    INFO['APP'] = LocalApp()
    INFO['LISTENER'] = Listener()

    INFO['APP'].MainLoop()

    wx.Exit()

