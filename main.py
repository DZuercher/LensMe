# First things, first. Import the wxPython package.
import wx
import cv2
import sys
import numpy as np
from lens import nfw_halo_lens
import matplotlib.pyplot as plt
from PIL import Image


class FloatSlider(wx.Slider):
    # def __init__(self, *args, **kw):
    #     super(FloatSlider, self).__init__(*args, **kw)
    def GetValue(self):
        return (float(wx.Slider.GetValue(self)))/self.GetMax()

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

        # and a status bar
        self.CreateStatusBar()
        self.SetStatusText("LensMe Status: Initializing")

        # init master panel
        self.master_panel = wx.Panel(self)
        self.master_panel.SetBackgroundColour("gray")

        # sizer
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # viedo title 
        videotitle_panel = wx.Panel(self.master_panel)
        videotitle = wx.StaticText(videotitle_panel, label='Lensed webcam steam')
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        videotitle.SetFont(font)
        self.vbox.Add(videotitle_panel, flag=wx.ALL, border=10)

        # initialize video capture
        capture = VideoInput()
        self.capture = capture

        # setup lens
        self.SetStatusText("LensMe Status: Calculating deflection field. Please wait...")

        # defaults
        self.M_halo=200.
        self.c_halo=3.
        self.z_halo=0.5
        self.z_source=1.
        self.frac_pos_x=0.5 
        self.frac_pos_y=0.5
        self.lens = nfw_halo_lens(200., 3., 0.5, 1.0, 480, 480, 0.5, 0.5)    
        self.SetStatusText("LensMe Status: Ready")

        # init videopanel
        self.videopanel = wx.Panel(self.master_panel)
        self.vbox.Add(self.videopanel, flag=wx.ALL, border=10)

        # init with single shot image
        frame = self.capture()
        frame = self.lens(frame)
        self.height, self.width = frame.shape[:2]
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = wx.Image(self.width, self.height, frame)
        self.imageCtrl = wx.StaticBitmap(self.videopanel, wx.ID_ANY, 
                                         wx.Bitmap(img))

        # controls
        self.add_slider('set_M_halo', 'Halo Mass in 10^15 solar masses', 1., 200., 1000.)
        self.add_slider('set_c_halo', 'Halo concentration', 0.1, 3, 10.)
        self.add_slider('set_z_halo', 'Halo redshift', 0., 0.5, 1.)
        self.add_slider('set_frac_pos_x', 'Halo position, x-axis', 0., 0.5, 1.)
        self.add_slider('set_frac_pos_y', 'Halo position, y-axis', 0., 0.5, 1.)

        # add buttons
        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(self.master_panel, label='Recompute', size=(100, 30))
        btn1.Bind(wx.EVT_BUTTON, self.recompute)
        buttonbox.Add(btn1)
        btn2 = wx.Button(self.master_panel, label='Reset Defaults', size=(180, 30))
        btn2.Bind(wx.EVT_BUTTON, self.reset)
        buttonbox.Add(btn2, flag=wx.LEFT|wx.BOTTOM, border=5)
        self.vbox.Add(buttonbox, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=10)

        # set up periodic screen capture
        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.NextFrame, self.timer)
        self.fps = 1 # unfortunately performance is not great 
        self.timer.Start(int(1000/self.fps))

        self.master_panel.SetSizer(self.vbox)

    def add_slider(self, attribute, label, min, default, max):
        # title

        min *= 100
        max *= 100
        default *= 100
        min = int(min)
        max = int(max)
        default = int(default)

        title_panel = wx.Panel(self.master_panel)
        title = wx.StaticText(title_panel, label=label)
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        title.SetFont(font)
        self.vbox.Add(title_panel, flag=wx.ALL, border=10)
        # slider box
        sliderbox = wx.BoxSizer(wx.HORIZONTAL)
        sld = wx.Slider(self.master_panel, value=default, minValue=min, maxValue=max,
                        style=wx.SL_HORIZONTAL)
        sld.Bind(wx.EVT_SCROLL, getattr(self, attribute))
        sliderbox.Add(sld, flag=wx.LEFT|wx.EXPAND, border=25, proportion=5)
        default = float(default) / 100.
        setattr(self, f'{attribute}_label', wx.StaticText(self.master_panel, label=str(default)))
        sliderbox.Add(getattr(self, f'{attribute}_label'), flag=wx.RIGHT, border=25, proportion=1)
        self.vbox.Add(sliderbox, flag=wx.ALL|wx.EXPAND, border=10)

    def set_M_halo(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()
        val = float(val) / 100.
        self.M_halo = float(val)
        self.set_M_halo_label.SetLabel(str(val)) 

    def set_c_halo(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()
        val = float(val) / 100.
        self.c_halo = float(val)
        self.set_c_halo_label.SetLabel(str(val)) 

    def set_z_halo(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()
        val = float(val) / 100.
        self.z_halo = float(val)
        self.set_z_halo_label.SetLabel(str(val)) 

    def set_frac_pos_x(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()
        val = float(val) / 100.
        self.frac_pos_x = float(val)
        self.set_frac_pos_x_label.SetLabel(str(val)) 

    def set_frac_pos_y(self, event):
        obj = event.GetEventObject()
        val = obj.GetValue()
        val = float(val) / 100.
        self.frac_pos_y = float(val)
        self.set_frac_pos_y_label.SetLabel(str(val)) 

    def recompute(self, event):
        self.SetStatusText("LensMe Status: Calculating deflection field. Please wait...")
        self.timer.Stop() 
        self.lens = nfw_halo_lens(self.M_halo, self.c_halo, self.z_halo, self.z_source, 480, 480, self.frac_pos_x, self.frac_pos_y)    
        self.timer.Start(int(1000/self.fps)) 
        self.SetStatusText("LensMe Status: Ready")

    def reset(self, event):
        self.SetStatusText("LensMe Status: Calculating deflection field. Please wait...")
        self.timer.Stop() 
        self.lens = nfw_halo_lens(200., 3., 0.5, 1.0, 480, 480, 0.5, 0.5)    
        self.timer.Start(int(1000/self.fps)) 
        self.SetStatusText("LensMe Status: Ready")

    def NextFrame(self, event):
        frame = self.capture()
        frame = self.lens(frame)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = wx.Image(self.width, self.height, frame)
        self.imageCtrl.SetBitmap(wx.Bitmap(img))
        self.videopanel.Refresh()

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