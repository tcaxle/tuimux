#!/usr/bin/env python

from asciimatics.widgets import Frame, ListBox, Layout, Divider, Text, Button, TextBox, Widget, PopUpDialog
from asciimatics.scene import Scene
from asciimatics.event import KeyboardEvent
from asciimatics.screen import Screen, ManagedScreen
from asciimatics.exceptions import ResizeScreenError, NextScene, StopApplication
import os
import sys
import subprocess
import libtmux as tm
from random_words import RandomNicknames
import psutil

rn = RandomNicknames()

def list_sessions():
    sessions = []
    for session in tm.Server().sessions:
        attached = session['session_attached'] == '1'
        if attached:
            attached = "(*)"
        else:
            attached = "( )"
        windows = int(session['session_windows'])
        sessions.append(("{} {} [{}]".format(attached, session.name, windows), session.name))
    return sessions

class ListView(Frame):
    def __init__(self, screen):
        super(ListView, self).__init__(
            screen,
            screen.height * 2 // 3,
            screen.width * 2 // 3,
            on_load=self._reload_list,
            hover_focus=True,
            title="Session List"
        )

        # Create the form for displaying the list of sessions.
        self._session_list = ListBox(
            Widget.FILL_FRAME,
            list_sessions(),
            name="Sessions",
            on_select=self._attach,
        )

        layout = Layout([100], fill_frame=True)
        self.add_layout(layout)
        layout.add_widget(Divider())
        self._new_button = Button("[N]ew Session", self._new)
        layout.add_widget(self._new_button, 0)
        layout.add_widget(Divider())
        layout.add_widget(self._session_list)
        layout.add_widget(Divider())

        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        self._attach_button = Button("[A]ttach", self._attach)
        self._delete_button = Button("[D]elete", self._delete)
        self._quit_button = Button("[Q]uit", self._quit)
        layout2.add_widget(self._attach_button, 0)
        layout2.add_widget(self._delete_button, 1)
        layout2.add_widget(self._quit_button, 2)

        self.fix()

    def _reload_list(self):
        self._session_list.options = list_sessions()

    def _new(self):
        raise NextScene("New")

    def _delete(self):
        subprocess.run([
            "tmux",
            "kill-session",
            "-t",
            self._session_list.value,
        ])
        self._reload_list()

    def _attach(self):
        subprocess.run([
            "tmux",
            "attach-session",
            "-t",
            self._session_list.value,
        ])
        subprocess.run([
            "tmux",
            "switch-client",
            "-t",
            self._session_list.value,
        ])
        raise StopApplication("User attached to a new session")

    @staticmethod
    def _quit():
        raise StopApplication("User pressed quit")

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code in [ord('q'), ord('Q'), Screen.ctrl("c")]:
                raise StopApplication("User quit")
            if event.key_code in [ord('a'), ord('A')]:
                self._attach()
            if event.key_code in [ord('d'), ord('D')]:
                self._delete()
            if event.key_code in [ord('n'), ord('N')]:
                self._new()

        # Now pass on to lower levels for normal handling of the event.
        return super(ListView, self).process_event(event)


class NewView(Frame):
    def __init__(self, screen):
        super(NewView, self).__init__(
            screen,
            5,
            screen.width * 2 // 3,
            hover_focus=True,
            title="New Session",
        )

        self.data["name"] = rn.random_nick(gender = "u")

        layout = Layout([100])
        self.add_layout(layout)
        layout.add_widget(Text("Name:", "name"))
        layout.add_widget(Divider())

        layout2 = Layout([1, 1, 1])
        self.add_layout(layout2)
        layout2.add_widget(Button("[A]ttach", self._attach), 0)
        layout2.add_widget(Button("[B]ackground", self._background), 1)
        layout2.add_widget(Button("[C]ancel", self._cancel), 2)

        self.fix()

    @staticmethod
    def _cancel():
        raise NextScene("Main")

    def _create_session(self):
        self.save()
        subprocess.run([
            "tmux",
            "new",
            "-d",
            "-s",
            self.data["name"],
        ])

    def _background(self):
        self._create_session()
        self._cancel()

    def _attach(self):
        self._create_session()
        subprocess.run([
            "tmux",
            "attach-session",
            "-t",
            self.data["name"],
        ])
        subprocess.run([
            "tmux",
            "switch-client",
            "-t",
            self.data["name"],
        ])
        raise StopApplication("User attached to a new session")

    def process_event(self, event):
        # Do the key handling for this Frame.
        if isinstance(event, KeyboardEvent):
            if event.key_code in [Screen.ctrl("c")]:
                raise StopApplication("User quit")

        # Now pass on to lower levels for normal handling of the event.
        return super(NewView, self).process_event(event)

def demo(screen, scene):
    scenes = [
        Scene([ListView(screen)], -1, name="Main"),
        Scene([NewView(screen)], -1, name="New"),
    ]

    screen.play(scenes, stop_on_resize=True, start_scene=scene, allow_int=True)

def check_tmux_running():
    for proc in psutil.process_iter():
        pname = proc.as_dict(attrs=["name"])["name"].lower()
        if pname == "tmux: server":
            return True
    return False

last_scene = None
if check_tmux_running():
    while True:
        try:
            Screen.wrapper(demo, catch_interrupt=True, arguments=[last_scene])
            sys.exit(0)
        except ResizeScreenError as e:
            last_scene = e.scene
else:
    subprocess.run([
        "tmux",
        "new",
        "-s",
        rn.random_nick(gender = "u"),
    ])
