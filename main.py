# First things, first. Import the wxPython package.
import wx
import cv2
import sys
import numpy as np
from lens import nfw_halo_lens
import matplotlib.pyplot as plt
from PIL import Image

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

        ##########
        # General setup of the main application
        ##########

        # center main frame on screen
        self.Centre()

        # create a menu bar
        self.makeMenuBar()

        # init master panel
        self.panel = wx.Panel(self)
        self.panel.SetBackgroundColour("gray")

        # initialize video capture
        capture = VideoInput()
        self.capture = capture

        # setup lens
        self.lens = nfw_halo_lens(nx=480, ny=480)    

        #self.input_frame = wx.Bitmap(frame)
        #self.videopanel = wx.StaticBitmap(self.panel, wx.ID_ANY, self.input_frame)        
        #self.videopanel.SetPosition((20, 20))

        # init with single shot image
        frame = self.capture()
        frame = self.lens(frame)
        self.height, self.width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = wx.Image(self.width, self.height, frame)
        self.imageCtrl = wx.StaticBitmap(self.panel, wx.ID_ANY, 
                                         wx.Bitmap(img))


        # # set up periodic screen capture
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.NextFrame, self.timer)
        fps = 3 
        self.timer.Start(int(1000/fps))


        """


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
        frame = self.lens(frame)
        self.height, self.width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # plt.imsave('example_lensed.jpg', frame.astype('uint8'))
        self.videopanel = wx.Panel(self.pnl, wx.ID_ANY, (0,0), (self.width, self.height))
        self.videopanel.bitmap = wx.Bitmap.FromBuffer(self.height, self.width, frame)

        # set up periodic screen capture
        #self.timer = wx.Timer(self)
        #self.Bind(wx.EVT_TIMER, self.NextFrame, self.timer)


        # and a status bar
        #self.CreateStatusBar()
        #self.SetStatusText("LensMe Status: Ready")

        fps = 5 
        #self.timer.Start(int(1000/fps))
        """

    def NextFrame(self, event):
        frame = self.capture()
        frame = self.lens(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = wx.Image(self.width, self.height, frame)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.panel.Refresh()

    def makeMenuBar(self):
        menubar = wx.MenuBar()

        # File menu
        fileMenu = wx.Menu()
        exitItem = fileMenu.Append(wx.ID_EXIT, 'Quit', 'Quit application')
        self.Bind(wx.EVT_MENU, self.OnExit,  exitItem)
        menubar.Append(fileMenu, '&File')

        aboutMenu = wx.Menu()
        aboutItem = aboutMenu.Append(wx.ID_ABOUT)
        self.Bind(wx.EVT_MENU, self.OnAbout, aboutItem)
        menubar.Append(aboutMenu, "&About")

        self.SetMenuBar(menubar)


    def OnExit(self, event):
        """Close the frame, terminating the application."""
        self.Close(True)

    def OnAbout(self, event):
        """Display an About Dialog"""
        wx.MessageBox("Some LensMe blabla")
        

if __name__== '__main__':
    app = wx.App()
    frm = MainFrame(None, title='LensMe')
    frm.Show()
    app.MainLoop()