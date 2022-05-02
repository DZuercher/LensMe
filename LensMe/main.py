import wx
from LensMe.lens import nfw_halo_lens
import cv2
import _thread 
import numpy as np

class StreamPanel(wx.Panel):
    def __init__(self, video=None, lens=None, *args, **kw):
        # ensure the parent's __init__ is called
        super(StreamPanel, self).__init__(*args, **kw)

        self.SetDoubleBuffered(True)

        self.fps = 4

        self.video = video
        self.lens = lens

        frame = np.zeros((480, 480, 3))
        img = wx.Image(480, 480, frame)
        self.bmp = img.ConvertToBitmap()

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.timer.Start(int(1000/self.fps))
        self.Show()


    def UpdateFrame(self):
        ret, frame = self.video.read()
        if ret:
            frame = self.lens.reshape_image(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = wx.Image(480, 480, frame)
            self.bmp = img.ConvertToBitmap()

    def OnTimer(self, event):
        _thread.start_new_thread(self.UpdateFrame, ())
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

class LensPanel(wx.Panel):
    def __init__(self, *args, **kw):
        super(LensPanel, self).__init__(*args, **kw)

        self.SetDoubleBuffered(True)

        frame = np.zeros((480, 480, 3))
        img = wx.Image(480, 480, frame)
        self.bmp = img.ConvertToBitmap()

        self.fps = 4

        self.video = cv2.VideoCapture(0)

        self.lens = nfw_halo_lens(200., 3., 0.5, 1.0, 480, 480, 0.5, 0.5)    

        self.timer = wx.Timer(self)
        self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
        self.Bind(wx.EVT_PAINT, self.OnPaint)
        self.timer.Start(int(1000/self.fps))
        self.Show()


    def UpdateFrame(self):
        ret, frame = self.video.read()
        if ret:
            frame = self.lens(frame)
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = wx.Image(480, 480, frame)
            self.bmp = img.ConvertToBitmap()

    def OnTimer(self, event):
        _thread.start_new_thread(self.UpdateFrame, ())
        self.Refresh()

    def OnPaint(self, event):
        dc = wx.PaintDC(self)
        dc.DrawBitmap(self.bmp, 0, 0)

class MainFrame(wx.Frame):
    """
    A Frame that says Hello World
    """

    def __init__(self, *args, **kw):
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

        # defaults
        self.M_halo=200.
        self.c_halo=3.
        self.z_halo=0.5
        self.z_source=1.
        self.frac_pos_x=0.5 
        self.frac_pos_y=0.5

        # sizer
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # viedo title 
        videotitle_panel = wx.Panel(self.master_panel)
        videotitle = wx.StaticText(videotitle_panel, label='Lensed webcam stream')
        font = wx.SystemSettings.GetFont(wx.SYS_SYSTEM_FONT)
        videotitle.SetFont(font)
        self.vbox.Add(videotitle_panel, flag=wx.ALL, border=10)

        self.SetStatusText("LensMe Status: Calculating deflection field. Please wait...")

        self.SetStatusText("LensMe Status: Ready")

        # init videopanel
        videobox = wx.BoxSizer(wx.HORIZONTAL)
        self.videopanel = LensPanel(self.master_panel, size=(480, 480))
        self.streampanel = StreamPanel(video=self.videopanel.video, lens=self.videopanel.lens, parent=self.master_panel, size=(480, 480))
        videobox.Add(self.videopanel)
        videobox.Add(self.streampanel, flag=wx.LEFT|wx.BOTTOM, border=5)
        self.vbox.Add(videobox, flag=wx.ALIGN_LEFT|wx.RIGHT, border=10)

        # controls
        self.add_slider('set_M_halo', 'Halo Mass in 10^15 solar masses', 1., 200., 1000.)
        self.add_slider('set_c_halo', 'Halo concentration', 0.1, 3, 10.)
        self.add_slider('set_z_halo', 'Halo redshift', 0., 0.5, 1.)
        self.add_slider('set_frac_pos_x', 'Halo position, x-axis', 0., 0.5, 1.)
        self.add_slider('set_frac_pos_y', 'Halo position, y-axis', 0., 0.5, 1.)

        # add buttons
        buttonbox = wx.BoxSizer(wx.HORIZONTAL)
        btn1 = wx.Button(self.master_panel, label='Recompute', size=(100, 50))
        btn1.Bind(wx.EVT_BUTTON, self.recompute)
        buttonbox.Add(btn1)
        btn2 = wx.Button(self.master_panel, label='Reset Defaults', size=(180, 50))
        btn2.Bind(wx.EVT_BUTTON, self.reset)
        buttonbox.Add(btn2, flag=wx.LEFT|wx.BOTTOM, border=5)
        self.vbox.Add(buttonbox, flag=wx.ALIGN_RIGHT|wx.RIGHT, border=5)

        self.master_panel.SetSizer(self.vbox)

        # Fullscreen (improves performance)
        self.Maximize(True)

    def add_slider(self, attribute, label, min, default, max):
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
        self.vbox.Add(title_panel, flag=wx.ALL, border=5)
        # slider box
        sliderbox = wx.BoxSizer(wx.HORIZONTAL)
        sld = wx.Slider(self.master_panel, value=default, minValue=min, maxValue=max,
                        style=wx.SL_HORIZONTAL)
        sld.Bind(wx.EVT_SCROLL, getattr(self, attribute))
        sliderbox.Add(sld, flag=wx.LEFT|wx.EXPAND, proportion=5)
        setattr(self, f'{attribute}_slider', sld)
        default = float(default) / 100.
        setattr(self, f'{attribute}_label', wx.StaticText(self.master_panel, label=str(default)))
        sliderbox.Add(getattr(self, f'{attribute}_label'), flag=wx.RIGHT, proportion=1)
        self.vbox.Add(sliderbox, flag=wx.ALL|wx.EXPAND, border=5)

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
        self.videopanel.lens = nfw_halo_lens(self.M_halo, self.c_halo, self.z_halo, self.z_source, 480, 480, self.frac_pos_x, self.frac_pos_y)    
        self.SetStatusText("LensMe Status: Ready")

    def reset(self, event):
        self.SetStatusText("LensMe Status: Calculating deflection field. Please wait...")
        self.videopanel.lens = nfw_halo_lens(200., 3., 0.5, 1.0, 480, 480, 0.5, 0.5)    

        # reset sliders
        self.set_M_halo_slider.SetValue(int(200. * 100.))
        self.set_c_halo_slider.SetValue(int(3. * 100.))
        self.set_z_halo_slider.SetValue(int(0.5 * 100.))
        self.set_frac_pos_x_slider.SetValue(int(0.5* 100.))
        self.set_frac_pos_y_slider.SetValue(int(0.5 * 100.))
        self.set_M_halo_label.SetLabel('200.0')
        self.set_c_halo_label.SetLabel('3.0')
        self.set_z_halo_label.SetLabel('0.5')
        self.set_frac_pos_x_label.SetLabel('0.5')
        self.set_frac_pos_x_label.SetLabel('0.5')

        self.SetStatusText("LensMe Status: Ready")

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
        wx.MessageBox("BLAAA")
        
def main():
    app = wx.App()
    frm = MainFrame(None, title='LensMe')
    frm.Show()
    app.MainLoop()

if __name__== '__main__':
    main()
