
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
            wx.MessageBox( lt("Another GlobalVim instance is running"),lt('Error') )
            return False

        
        geeKeyFrame = GeeKeyFrame(None,-1)
        # if geeKeyFrame.getConfig('runasadmin') == 'True':
        #     ret = runAsAdmin()
        #     if ret is None:
        #         #print 'elevating to admin privileges'
        #         geeKeyFrame.OnExit(None)
        #         return False

        #     elif ret is False:

        #         #print 'failed to elevating to admin privileges'
        #         style = wx.OK|wx.TE_MULTILINE
        #         dlg = wx.MessageDialog(self, lt('_not_run_as_admin'), lt('_warning'),style = style)
        #         dlg.ShowModal()
        #         dlg.Destroy()
        #         self.payImage.SetFocus()
        #         pass
        #     else: # True, which is running in admin privileges
        #         pass
        #     pass

        self.SetTopWindow(geeKeyFrame)
        geeKeyFrame.Show(True)
        geeKeyFrame.RaiseShow()
        #if geeKeyFrame.getConfig('startshow') == 'True':
        #    geeKeyFrame.Show(True)
        #    pass
        return True
    pass

if __name__ == '__main__':
    app = LocalApp()
    app.MainLoop()
    wx.Exit()
    log_out.close()

