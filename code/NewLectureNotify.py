#-*- coding:utf-8 -*-
import os
import json
import requests
import webbrowser
import win32api
import win32con
import win32gui


def get_new_lecture():
    try:
        user_agent = {'user-agent': 'Mozilla/5.0'}
        url = "http://www.cqupt.edu.cn/getPublicPage.do?ffmodel=notic&&nc_mode=news&page=1&rows=20"
        response = requests.get(url, headers=user_agent, timeout=10)
        response.raise_for_status()
        webdata = response.text.encode('utf-8')

        decodejson = json.loads(webdata)
        lecture_id = decodejson['rows'][0]['id'].encode('utf-8')
        title = decodejson['rows'][0]['nc_title'].encode('utf-8')
        time = decodejson['rows'][0]['puser_time'].encode('utf-8')
        dept_name = decodejson['rows'][0]['dept_name'].encode('utf-8')

        with open("../res/new_lecture_id.txt", "rb") as f:
            old_lecture_id = f.read()
        if int(lecture_id) > int(old_lecture_id):
            with open("../res/new_lecture_id.txt", "wb") as f:
                f.write(lecture_id)
            return title, time, lecture_id, dept_name
    except BaseException:
        return None


class Taskbar:
    def __init__(self, title="Notification", msg="message", lecture_id=0, icon_path=None):
        self.title = title
        self.msg = msg
        self.lecture_id = lecture_id
        self.visible = 0
        message_map = {
            win32con.WM_DESTROY: self.onDestroy,
            win32con.WM_USER + 20: self.onTaskbarNotify,
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "PythonTaskbarDemo"
        wc.style = win32con.CS_VREDRAW | win32con.CS_HREDRAW
        wc.hCursor = win32gui.LoadCursor(0, win32con.IDC_ARROW)
        wc.hbrBackground = win32con.COLOR_WINDOW
        wc.lpfnWndProc = message_map  # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(
            classAtom,
            "Taskbar Demo",
            style,
            0,
            0,
            win32con.CW_USEDEFAULT,
            win32con.CW_USEDEFAULT,
            0,
            0,
            hinst,
            None)
        win32gui.UpdateWindow(self.hwnd)

        # icon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        # self.setIcon(icon)
        # self.show()

        if icon_path is not None:
            icon_path = os.path.realpath(icon_path)
        else:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            hicon = win32gui.LoadImage(hinst, icon_path,
                              win32con.IMAGE_ICON, 0, 0, icon_flags)
        except:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)

        self.setIcon(hicon)
        self.show()


    def setIcon(self, hicon, tooltip=None):
        self.hicon = hicon
        self.tooltip = tooltip

    def show(self):
        """Display the taskbar icon"""
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE
        if self.tooltip is not None:
            flags |= win32gui.NIF_TIP
            nid = (
                self.hwnd,
                0,
                flags,
                win32con.WM_USER +
                20,
                self.hicon,
                self.tooltip)
        else:
            nid = (self.hwnd, 0, flags, win32con.WM_USER + 20, self.hicon)
        if self.visible:
            self.hide()
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        self.visible = 1

    def hide(self):
        """Hide the taskbar icon"""
        if self.visible:
            nid = (self.hwnd, 0)
            win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        self.visible = 0

    def onDestroy(self, hwnd, msg, wparam, lparam):
        self.hide()
        win32gui.PostQuitMessage(0)  # Terminate the app.

    def onTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONUP:
            self.onClick()
        elif lparam == win32con.WM_LBUTTONDBLCLK:
            self.onDoubleClick()
        elif lparam == win32con.WM_RBUTTONUP:
            self.onRightClick()
        return 1

    def onClick(self):
        self.detail(self.lecture_id)

    def onDoubleClick(self):
        win32gui.PostQuitMessage(0)

    def onRightClick(self):
        pass


    def showToast(self):
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_INFO
        nid = (
            self.hwnd,
            0,
            flags,
            win32con.WM_USER +
            20,
            self.hicon,
            "",
            self.msg,
            10,
            self.title
        )

        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, nid)

    def detail(self, lecture_id):
        morelink = 'http://www.cqupt.edu.cn/getPublicNotic.do?id=%s' % lecture_id
        webbrowser.open(morelink)


if __name__ == "__main__":
    result = get_new_lecture()
    if result is not None:
        title, time, lecture_id, dept_name = result
        t = Taskbar(title=time.decode('utf-8'),
                    msg=title.decode('utf-8'),
                    lecture_id=lecture_id,
                    icon_path="../img/python.ico")
        t.showToast()
        win32gui.PumpMessages()
    else:
        pass
