#!/usr/bin/env python3
from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
import locale
from math import nan
import random
import re
import serial
from serial.tools import list_ports
from time import time
from tkinter import *  # pyright: ignore (this is tkinter style)
from tkinter import font
from tkinter import ttk
import tomllib
from typing import List
import winsound


@dataclass
class Delay:
    min = 5.0
    max = 10.0


@dataclass
class Config:
    locale = 'it_IT'
    """Locale for formatting numbers in CSV output"""
    scents = ['Undefined 1', 'Undefined 2']
    """Scents available to choose in the window"""
    delay = Delay()
    """Random delay for `TIME_*` stages"""
    balanced_count = 5
    """Number of each ordering in a balanced batch"""


class ControlWindow:
    def __init__(self, root: Tk, config: Config):
        self.root = root
        self.config = config
        self.olfactory_state = (None, None)  # type: ignore
        root.title("Olfactory reaction experiment")

        self.com_port = StringVar()

        padding = "6 6 12 12"
        # Resizing frame to fully cover window
        mainframe = ttk.Frame(root, padding=padding)
        mainframe.grid(column=0, row=0, sticky='nwes')
        root.columnconfigure(0, weight=1)
        root.rowconfigure(0, weight=1)

        hardframe = ttk.Labelframe(
            mainframe, text='Hardware:', padding=padding)
        hardframe.grid(column=0, row=0, sticky='we')
        ttk.Label(hardframe, text='Choose serial port').grid(
            column=0, row=0, sticky='e')
        self.ports_box = ttk.Combobox(
            hardframe, textvariable=self.com_port, state='readonly', width=30)
        self.ports_box.grid(column=1, row=0, columnspan=2)
        self.ports_box.bind('<<ComboboxSelected>>', self.update_active)

        ttk.Button(hardframe, text='Refresh',
                   command=self.refresh_ports).grid(column=3, row=0)
        self.refresh_ports()

        self.serial: serial.Serial = None  # type: ignore
        self.experiment_window = None
        self.connect_btn = ttk.Button(
            hardframe, text='Connect', command=self.connect)
        self.connect_btn.grid(column=0, row=1)
        self.disconnect_btn = ttk.Button(
            hardframe, text='Disconnect', command=self.disconnect)
        self.disconnect_btn.grid(column=1, row=1)

        self.ch1_btn = ttk.Button(
            hardframe, text='Channel 1', command=lambda: self.set_olfactory(True, False))
        self.ch1_btn.grid(column=0, row=2)
        self.ch2_btn = ttk.Button(
            hardframe, text='Channel 2', command=lambda: self.set_olfactory(False, True))
        self.ch2_btn.grid(column=1, row=2)
        self.both_btn = ttk.Button(
            hardframe, text='Both', command=lambda: self.set_olfactory(True, True))
        self.both_btn.grid(column=2, row=2)
        self.none_btn = ttk.Button(
            hardframe, text='None', command=lambda: self.set_olfactory(False, False))
        self.none_btn.grid(column=3, row=2)

        expframe = ttk.Labelframe(
            mainframe, text='Experiment:', padding=padding)
        expframe.grid(column=0, row=1, sticky='we')
        expframe.columnconfigure(0, weight=1)
        expframe.columnconfigure(1, weight=1)

        self.ch1_scent = StringVar()
        self.ch2_scent = StringVar()
        ttk.Label(expframe, text='Select scent for each channel:').grid(
            column=0, row=0, sticky='w')
        self.radio1 = []
        self.radio2 = []
        for col, (scent, radio) in enumerate([(self.ch1_scent, self.radio1), (self.ch2_scent, self.radio2)]):
            frame = ttk.Frame(expframe)
            frame.grid(column=col, row=1, sticky='w')
            for i, name in enumerate(self.config.scents):
                radio.append(ttk.Radiobutton(
                    frame, text=name, variable=scent, value=name, command=self.update_active))
                radio[-1].grid(column=0, row=i, sticky='w')

        partframe = ttk.Labelframe(
            mainframe, text='Participant:', padding=padding)
        partframe.grid(column=0, row=2, sticky='we')
        partframe.columnconfigure(1, weight=1)
        ttk.Label(partframe, text='Identifier:').grid(
            column=0, row=0, sticky='e')
        self.participant_name = StringVar()
        participant_entry = ttk.Entry(
            partframe, textvariable=self.participant_name)
        participant_entry.grid(column=1, row=0, sticky='w')
        participant_entry.bind('<KeyRelease>', self.update_name)
        ttk.Label(partframe, text='(three first letters of name and surname)').grid(
            column=0, row=2, columnspan=2, sticky='w')
        ttk.Label(partframe, text='Gender:').grid(column=0, row=3, sticky='e')
        self.participant_gender = StringVar()
        gender_box = ttk.Combobox(partframe, textvariable=self.participant_gender, state='readonly',
                                  values=['Female', 'Male', 'Other', 'Prefer not to answer'])
        gender_box.grid(column=1, row=3, sticky='w')
        gender_box.bind('<<ComboboxSelected>>', self.update_active)
        ttk.Label(partframe, text='Age:').grid(column=0, row=4, sticky='e')
        self.participant_age = StringVar()
        age_entry = ttk.Entry(partframe, textvariable=self.participant_age)
        age_entry.grid(column=1, row=4, sticky='w')
        age_entry.bind('<KeyRelease>', self.update_age)
        self.participant_smokes = StringVar()
        ttk.Label(partframe, text='Smoking tobacco:').grid(
            column=0, row=5, sticky='e')
        smokes_box = ttk.Combobox(partframe, textvariable=self.participant_smokes, state='readonly',
                                  values=['Smokes', 'Doesn\'t smoke', 'Prefer not to answer'])
        smokes_box.grid(column=1, row=5, sticky='w')
        smokes_box.bind('<<ComboboxSelected>>', self.update_active)

        self.error_text = StringVar()
        ttk.Label(mainframe, textvariable=self.error_text,
                  foreground='red').grid(column=0, row=9)
        self.experiment_btn = ttk.Button(
            mainframe, text='Start experiment', command=self.show_experiment_window)
        self.experiment_btn.grid(column=0, row=10)

        self.update_active()

    def update_age(self, *args):
        self.participant_age.set(
            re.sub(r'[^\d]', '', self.participant_age.get()))
        self.update_active()

    def refresh_ports(self, *args):
        ports = list_ports.comports()
        text_list = [f'{p[0]} - {p[1]}' for p in ports]
        self.ports_box['values'] = tuple(text_list)

    def connect(self, *args):
        self.serial = serial.Serial(
            self.com_port.get().split(' - ')[0], 115200,
            timeout=None,        # blocking mode, wait until requested number of bytes
            write_timeout=None)  # blocking mode, infinite timeout; setting to 0 would fail silently
        self.update_active()

    def disconnect(self, *args):
        self.serial.close()
        self.serial = None  # type: ignore
        self.update_active()

    def update_name(self, *args):
        self.participant_name.set(
            re.sub(r'[^a-z]', '', self.participant_name.get().lower()))
        self.update_active()

    def update_active(self, *args) -> bool:
        self.ports_box['state'] = 'normal' if (
            self.serial is None) else 'disabled'
        self.connect_btn['state'] = 'normal' \
            if (self.serial is None and self.com_port.get() != '') else 'disabled'
        for button in [self.disconnect_btn, self.ch1_btn, self.ch2_btn, self.both_btn, self.none_btn]:
            button['state'] = 'normal' if self.serial is not None else 'disabled'

        self.experiment_btn['state'] = 'disabled'
        if self.serial is None:
            self.error_text.set('Connect the olfactory device')
            return False
        if (self.ch1_scent.get() == '') or (self.ch2_scent.get() == ''):
            self.error_text.set('Choose scent for each channel')
            return False
        if self.ch1_scent.get() == self.ch2_scent.get():
            self.error_text.set('The scent must be different for each channel')
            return False
        if self.participant_name.get() == '':
            self.error_text.set('Enter participant identifier')
            return False
        if len(self.participant_name.get()) != 6:
            self.error_text.set(
                'Identifier should be three first letters of name and surname')
            return False
        if self.participant_gender.get() == '':
            self.error_text.set('Select participant gender')
            return False
        if self.participant_age.get() == '':
            self.error_text.set('Enter participant age')
            return False
        try:
            age = int(self.participant_age.get())
            if age <= 0:
                self.error_text.set('Age must be a positive number')
                return False
        except ValueError:
            self.error_text.set('Age must be a valid number')
            return False
        if self.participant_smokes.get() == '':
            self.error_text.set('Select if participant smokes')
            return False

        self.error_text.set('')
        self.experiment_btn['state'] = 'normal'
        return True

    def set_olfactory(self, ch1: bool, ch2: bool):
        """Send olfactory command over serial"""
        command = '0'
        if ch1:
            command = command + '1'
        if ch2:
            command = command + '2'

        if self.serial is not None:
            # TODO: Handle serial error better: indicate in GUI, save experiment data
            self.serial.write(command.encode('ascii'))
            self.olfactory_state = (ch1, ch2)
            self.serial.read_all()  # empty the OS buffer

    def show_experiment_window(self, *args):
        if self.update_active():
            self.experiment_window = ExperimentWindow(self.root, self)


class Stage(Enum):
    INIT = auto(),
    """Experiment initialised"""
    START = auto(),
    """Ready to start next cycle"""
    TIME_ON = auto(),
    """Waiting for emitter to turn on"""
    ACK_ON = auto(),
    """Waiting for user to notice emitter is on"""
    TIME_SW = auto(),
    """Waiting for emitters to switch"""
    ACK_SW = auto(),
    """Waiting for user to acknowledge the switch"""
    TIME_OFF = auto(),
    """Waiting for emitter 2 to turn off"""
    ACK_OFF = auto(),
    """Waiting for user to notice turn off"""


@dataclass
class Cycle:
    """Data saved from one experiment run"""
    start_date: datetime
    """Experiment start time"""
    participant_name: str
    """Anonymised name of test participant"""
    gender: str
    """Participant gender"""
    age: int
    """Participant age"""
    smokes: str
    """Participant smoking tobacco"""
    scent1: str
    """Scent turned on first"""
    scent2: str
    """Scent turned on second"""
    on_wait: float = nan
    """Random time until emitter 1 turned on"""
    on_reaction: float = nan
    """Time until user noticed the change, -1 if before"""
    sw_wait: float = nan
    """Random time until emitters switched"""
    sw_reaction: float = nan
    """Time until user noticed the change, -1 if before"""
    off_wait: float = nan
    """Random time until emitter 2 turned off"""
    off_reaction: float = nan
    """Time until user noticed the change, -1 if before"""

    @staticmethod
    def csv_header() -> str:
        return '"cycle start [ISO 8601]";"participant anonymous name";"participant gender";"participant age";"participant smokes";"scent 1";"scent 2";' + \
            '"turn on 1 [s]";"on reaction [s]";"switch [s]";"switch reaction [s]";"turn off [s]";"turn off reaction [s]"\n'

    def to_csv(self) -> str:
        start = f'{self.start_date.isoformat()};"{self.participant_name}";"{self.gender}";' + \
                f'{self.age};"{self.smokes}";"{self.scent1}";"{self.scent2}";'
        times = [locale.format_string('%.3f', t) for t in [self.on_wait, self.on_reaction,
                                                           self.sw_wait, self.sw_reaction,
                                                           self.off_wait, self.off_reaction]]
        return start + ';'.join(times) + '\n'


class ExperimentWindow(Toplevel):
    def __init__(self, root, control: ControlWindow):
        super().__init__(root)
        self.control = control

        self._stage = Stage.INIT
        """Current experiment stage"""
        self._entered_stage = time()
        """Time when entered current stage"""
        self._after_reference = ''
        """Reference from `after()` method to cancel"""
        self.complete_cycles: List[Cycle] = []
        self.current_cycle: Cycle = None  # type: ignore
        self.balanced_reverses = []
        self.reversed_cycle = False

        winsound.PlaySound('White_noise.wav',
                           winsound.SND_ASYNC | winsound.SND_LOOP)

        self.title('Experiment')
        self.geometry('1920x1080')
        self.attributes('-fullscreen', True)

        self.bind('<ButtonPress-1>', self.acknowledge)  # LMB
        # self.bind('<MouseWheel>', self.acknowledge)  # HACK: Scroll for testing
        self.bind('<ButtonPress-3>', self.quit)  # RMB
        # when window is closed by system
        self.protocol('WM_DELETE_WINDOW', self.quit)

        self.mainframe = ttk.Frame(self, padding='6 6 24 24')
        self.mainframe.grid(column=0, row=0, sticky='nwes')
        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

        family = font.nametofont('TkTextFont').actual()['family']
        bigFont = font.Font(family=family, size=50, weight='normal')
        self.statustext = StringVar()
        ttk.Label(self.mainframe, textvariable=self.statustext,
                  font=bigFont).grid(column=1, row=1, sticky='nw')
        self.mainframe.rowconfigure(1, weight=1)
        ttk.Label(
            self.mainframe, text='Click right mouse button to end', font=bigFont).grid(column=1, row=2, sticky='sw')
        self.cycletext = StringVar()
        self.cycletext.set(
            f'(participant "{self.control.participant_name.get()}")')
        ttk.Label(self.mainframe, textvariable=self.cycletext,
                  font=bigFont).grid(column=1, row=3, sticky='sw')

        self.advance()

    def change_stage(self, new_stage):
        """Setter for `self._stage`, handles all state that is related only to the stage"""
        print(f'Changing from {self._stage} to {new_stage}', end='')
        time_in_stage = time() - self._entered_stage
        match self._stage:
            case Stage.TIME_ON:
                self.current_cycle.on_wait = time_in_stage
            case Stage.ACK_ON:
                self.current_cycle.on_reaction = time_in_stage
            case Stage.TIME_SW:
                self.current_cycle.sw_wait = time_in_stage
            case Stage.ACK_SW:
                self.current_cycle.sw_reaction = time_in_stage
            case Stage.TIME_OFF:
                self.current_cycle.off_wait = time_in_stage
            case Stage.ACK_OFF:
                self.current_cycle.off_reaction = time_in_stage
        if new_stage in [Stage.TIME_ON, Stage.TIME_SW, Stage.TIME_OFF]:
            delay = int(1000 * random.uniform(self.control.config.delay.min,
                        self.control.config.delay.max))  # delay in milliseconds
            self._after_reference = self.after(delay, self.stage_elapsed)
        self._stage = new_stage
        self._entered_stage = time()

        # Set displayed text
        match self._stage:
            case Stage.START:
                self.statustext.set('Click to start next cycle')
            case Stage.TIME_ON | Stage.ACK_ON:
                self.statustext.set('Click when you feel the scent')
            case Stage.TIME_SW | Stage.ACK_SW:
                self.statustext.set('Click when you feel the change')
            case Stage.TIME_OFF | Stage.ACK_OFF:
                self.statustext.set("Click when you don't feel the scent")

        # Set olfactory device
        match self._stage:
            case Stage.START | Stage.TIME_ON | Stage.ACK_OFF:
                self.control.set_olfactory(False, False)
            case Stage.ACK_ON | Stage.TIME_SW:
                self.control.set_olfactory(
                    not self.reversed_cycle, self.reversed_cycle)
            case Stage.ACK_SW | Stage.TIME_OFF:
                self.control.set_olfactory(
                    self.reversed_cycle, not self.reversed_cycle)
        print(f', olfactory state: {self.control.olfactory_state}')

    def stage_elapsed(self):
        self.advance()

    def acknowledge(self, *args):
        """Click by the user to advance"""
        try:
            self.after_cancel(self._after_reference)
        except:
            pass
        match self._stage:
            # was clicked prematurely
            case Stage.TIME_ON:
                self.current_cycle.on_reaction = -1
            case Stage.TIME_SW:
                self.current_cycle.sw_reaction = -1
            case Stage.TIME_OFF:
                self.current_cycle.off_reaction = -1
        self.advance(False)

    def advance(self, timed=True):
        """Choose next stage in the sequence, handle starting cycle"""
        next_stage = {
            Stage.INIT: Stage.START,
            Stage.START: Stage.TIME_ON,
            Stage.TIME_ON: Stage.ACK_ON if timed else Stage.TIME_SW,
            Stage.ACK_ON: Stage.TIME_SW,
            Stage.TIME_SW: Stage.ACK_SW if timed else Stage.TIME_OFF,
            Stage.ACK_SW: Stage.TIME_OFF,
            Stage.TIME_OFF: Stage.ACK_OFF if timed else Stage.START,
            Stage.ACK_OFF: Stage.START,
        }
        self.change_stage(next_stage[self._stage])
        if self._stage == Stage.START:
            # save the completed cycle
            if self.current_cycle is not None:
                self.complete_cycles.append(self.current_cycle)
                self.cycletext.set(f'(participant "{self.control.participant_name.get()}",' +
                                   f'completed cycles: {len(self.complete_cycles)}/{self.control.config.balanced_count * 2})')

            # create a new balanced list if just starting or completed all
            if len(self.balanced_reverses) == 0:
                count = self.control.config.balanced_count
                self.balanced_reverses.extend([True for _ in range(count)])
                self.balanced_reverses.extend([False for _ in range(count)])
                random.shuffle(self.balanced_reverses)

            # choose if this cycle will be in normal or reversed order
            self.reversed_cycle = self.balanced_reverses.pop()

            self.current_cycle = Cycle(
                datetime.now(),
                self.control.participant_name.get(),
                self.control.participant_gender.get(),
                int(self.control.participant_age.get()),
                self.control.participant_smokes.get(),
                (self.control.ch1_scent.get() if (not self.reversed_cycle)
                 else self.control.ch2_scent.get()),
                (self.control.ch2_scent.get() if (not self.reversed_cycle)
                 else self.control.ch1_scent.get()),
            )

    def quit(self, *args):
        """Save gathered data and close"""
        if len(self.complete_cycles) > 0:
            csvdata = Cycle.csv_header() + \
                ''.join([c.to_csv() for c in self.complete_cycles])
            print()
            print(csvdata)
            filename = datetime.now().strftime('%Y%m%dT%H%M%S') + \
                f'_{self.complete_cycles[0].participant_name}.csv'
            with open(filename, 'w') as outfile:
                outfile.write(csvdata)
            print(f'Saved {len(self.complete_cycles)} cycles to {filename}')

        winsound.PlaySound(None, 0)  # stop sound
        self.control.set_olfactory(False, False)
        self.control.root.focus_force()
        self.control.experiment_window = None
        self.destroy()


if __name__ == '__main__':
    config = Config()
    try:
        with open('config.toml', 'rb') as config_file:
            data: dict = tomllib.load(config_file)
            for key, value in data.items():
                if type(value) is dict:
                    for innerkey, innervalue in value.items():
                        setattr(getattr(config, key), innerkey, innervalue)
                else:
                    setattr(config, key, value)
    except Exception as e:
        print('Error loading config:')
        print(e)

    locale.setlocale(locale.LC_ALL, config.locale)
    root = Tk()
    control_window = ControlWindow(root, config)
    try:
        root.mainloop()
    except Exception as e:
        print(e)

    winsound.PlaySound(None, 0)  # stop sound

    if control_window.serial is not None:
        control_window.serial.close()
