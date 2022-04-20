# First things, first. Import the wxPython package.
import wx
import cv2
import sys
import numpy as np

class VideoInput():
    def __init__(self):
        # define a video capture object
        self.video = cv2.VideoCapture(0)

    def __call__(self):
        ret, frame = self.video.read()
        return frame

class MainFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
        # ensure the parent's __init__ is called
        super(MainFrame, self).__init__(*args, **kw)

        # create the main panel in the frame
        self.pnl = wx.Panel(self)

        # put some text with a larger bold font on it
        # st = wx.StaticText(pnl, label="Hello World!")
        # font = st.GetFont()
        # font.PointSize += 10
        # font = font.Bold()
        # st.SetFont(font)

        # and create a sizer to manage the layout of child widgets
        sizer = wx.BoxSizer(wx.VERTICAL)
        # sizer.Add(st, wx.SizerFlags().Border(wx.TOP|wx.LEFT, 25))
        self.pnl.SetSizer(sizer)

        # initialize video capture
        capture = VideoInput()

        self.capture = capture
        frame = self.capture()
        self.height, self.width = frame.shape[:2]
        self.videopanel = wx.Panel(self.pnl, wx.ID_ANY, (0,0), (self.width, self.height))
        self.videopanel.bitmap = wx.Bitmap.FromBuffer(self.height, self.width, frame)

        # set up periodic screen capture
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.NextFrame, self.timer)

        # create a menu bar
        self.makeMenuBar()

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("LensMe Status: Ready")

        self.Show()
        fps = 30
        self.timer.Start(int(1000/fps))

    def NextFrame(self, event):
        frame = self.capture()
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        theBitmap = wx.Bitmap.FromBuffer(self.width, self.height, frame)
        self.videopanel.bitmap = wx.StaticBitmap(self, bitmap=theBitmap)

    def makeMenuBar(self):
        # Make a file menu with Hello and Exit items
        fileMenu = wx.Menu()
        # The "\t..." syntax defines an accelerator key that also triggers
        # the same event
        helloItem = fileMenu.Append(-1, "&Hello...\tCtrl-H",
                "Help string shown in status bar for this menu item")
        fileMenu.AppendSeparator()
        # When using a stock ID we don't need to specify the menu item's
        # label
        exitItem = fileMenu.Append(wx.ID_EXIT)

        # Now a help menu for the about item
        helpMenu = wx.Menu()
        aboutItem = helpMenu.Append(wx.ID_ABOUT)

        # Make the menu bar and add the two menus to it. The '&' defines
        # that the next letter is the "mnemonic" for the menu item. On the
        # platforms that support it those letters are underlined and can be
        # triggered from the keyboard.
        menuBar = wx.MenuBar()
        menuBar.Append(fileMenu, "&File")
        menuBar.Append(helpMenu, "&Help")

        # Give the menu bar to the frame
        self.SetMenuBar(menuBar)

        # Finally, associate a handler function with the EVT_MENU event for
        # each of the menu items. That means that when that menu item is
        # activated then the associated handler function will be called.
        self.Bind(wx.EVT_MENU, self.OnHello, helloItem)
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)


    def OnHello(self, event):
        """Say hello to the user."""
        wx.MessageBox("Hello again from wxPython")


    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("This is a wxPython Hello World sample",
                      "About Hello World 2",
                      wx.OK|wx.ICON_INFORMATION)
        

if __name__== '__main__':
    app = wx.App()
    frm = MainFrame(None, title='LensMe')
    app.MainLoop()