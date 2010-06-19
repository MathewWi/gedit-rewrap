#!/usr/bin/env python
# -*- coding: utf8 -*-
#
#  Rewrap plugin for Gedit
#
#  Copyright (C) 2010 Derek Veit
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
2010-06-18  Version 1.0.0

This module provides the plugin object that Gedit interacts with.

See __init__.py for the description of the plugin.

Classes:
RewrapPlugin -- object is loaded once by an instance of Gedit
RewrapWindowHelper -- object is constructed for each Gedit window

Each time the same Gedit instance makes a new window, Gedit calls the
plugin's activate Emethod.  Each time RewrapPlugin is so activated, it
constructs a RewrapWindowHelper Eobject to handle the new window.

Settings common to all Gedit windows are attributes of RewrapPlugin.
Settings specific to one window are attributes of RewrapWindowHelper.

"""

INDENT_CHARS = ' \t#/;*!-'
"""
The characters in INDENT_CHARS will be treated as part of indentation at
the start of each line.  This allows for comment blocks in various
languages to be re-wrapped.

Leading indentation characters on the first selected line will be used
for indentation of all re-wrapped lines.

Leading indentation characters on all other selected lines will be
discarded.

Indentation characters that occur after the first non-indentation
character will not be handled specially.
"""

ACCELERATOR = '<Shift><Control><Alt>w'
"""
This string can be edited to change the accelerator keys used to
activate the plugin.
"""

import re

import gconf
import gedit
import gtk

from .logger import Logger
LOGGER = Logger(level=('DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL')[2])

class RewrapPlugin(gedit.Plugin):
    
    """
    An object of this class is loaded once by a Gedit instance.
    
    It creates a RewrapWindowHelper object for each Gedit main window.
    
    Public methods:
    activate -- Gedit calls this to start the plugin.
    deactivate -- Gedit calls this to stop the plugin.
    update_ui -- Gedit calls this at certain times when the ui changes.
    is_configurable -- Gedit calls this to check if the plugin is configurable.
    
    """
    
    def __init__(self):
        """Establish the settings shared by all Rewrap instances."""
        LOGGER.log()
        
        gedit.Plugin.__init__(self)
        
        self._instances = {}
        """Each Gedit window will get a RewrapWindowHelper instance."""
    
    def activate(self, window):
        """Start a RewrapWindowHelper instance for this Gedit window."""
        LOGGER.log()
        self._instances[window] = RewrapWindowHelper(self, window)
        self._instances[window].activate()
    
    def deactivate(self, window):
        """End the RewrapWindowHelper instance for this Gedit window."""
        LOGGER.log()
        self._instances[window].deactivate()
        del self._instances[window]
    
    def update_ui(self, window):
        """Forward Gedit's update_ui command for this window."""
        LOGGER.log()
        self._instances[window].update_ui(window)
    
    def is_configurable(self):
        """Identify for Gedit that Rewrap is not configurable."""
        LOGGER.log()
        return False
    
class RewrapWindowHelper(object):
    
    """
    RewrapPlugin creates a RewrapWindowHelper object for each Gedit
    window.
    
    Public methods:
    deactivate -- RewrapPlugin calls this when Gedit calls deactivate for
                  this window.
    update_ui -- RewrapPlugin calls this when Gedit calls update_ui for
                 this window.  It activates the menu for the Gedit window and
                 connects the mouse event handler to the current View.
                 Also, RewrapWindowHelper.__init__ calls this.
    
    """
    
    def __init__(self, plugin, window):
        """Initialize attributes for this Back Button instance."""
        LOGGER.log()
        
        self._window = window
        """The window this RewrapWindowHelper runs on."""
        
        self._menu_ui_id = None
        """The menu's UI identity, saved for removal."""
        self._action_group = None
        """The menu's action group, saved for removal."""
        
        self._start_iter = None
        """The start the text selection."""
        self._end_iter = None
        """The end of the text selection."""
    
    # Public methods
    
    def activate(self):
        """Start this instance of Rewrap."""
        LOGGER.log()
        self._insert_menu()
        self.update_ui(self._window)
        LOGGER.log('Rewrap started for %s' % self._window)
    
    def deactivate(self):
        """End this instance of Rewrap."""
        LOGGER.log()
        self._remove_menu()
        LOGGER.log('Rewrap stopped for %s' % self._window)
        self._window = None
    
    def update_ui(self, window):
        """Make sure the menu is set sensitive."""
        LOGGER.log()
        document = window.get_active_document()
        view = window.get_active_view()
        if document and view and view.get_editable():
            self._action_group.set_sensitive(True)
    
    # Menu
    
    def _insert_menu(self):
        """Create the custom menu item under the Edit menu."""
        LOGGER.log()
        
        manager = self._window.get_ui_manager()
        
        actions = []
        
        name = 'Rewrap'
        stock_id = None
        label = 'Rewrap'
        accelerator = ACCELERATOR
        tooltip = 'Re-wrap selected lines.'
        callback = lambda action: self._rewrap_selection()
        actions.append((name, stock_id, label, accelerator, tooltip, callback))
        
        self._action_group = gtk.ActionGroup("RewrapPluginActions")
        self._action_group.add_actions(actions)
        manager.insert_action_group(self._action_group, -1)
        
        ui_str = """
            <ui>
              <menubar name="MenuBar">
                <menu name="EditMenu" action="Edit">
                  <placeholder name="EditOps_6">
                    <placeholder name="Rewrap">
                      <menuitem action="Rewrap"/>
                    </placeholder>
                  </placeholder>
                </menu>
              </menubar>
            </ui>
            """
        self._menu_ui_id = manager.add_ui_from_string(ui_str)
        LOGGER.log('Menu added for %s' % self._window)
    
    def _remove_menu(self):
        """Remove the custom menu item."""
        LOGGER.log()
        manager = self._window.get_ui_manager()
        manager.remove_ui(self._menu_ui_id)
        manager.remove_action_group(self._action_group)
        self._action_group = None
        manager.ensure_update()
        LOGGER.log('Menu removed for %s' % self._window)
    
    # Text functions
    
    def _rewrap_selection(self):
        """Re-wrap the currently selected text."""
        LOGGER.log()
        text = self._get_text_selection()
        if not text:
            return
        text += '\n'
        max_line_length = self._get_gedit_margin()
        tab_width = self._get_gedit_tab_width()
        
        # Get the indent and calculate its width
        indent = re.match('[%s]*' % INDENT_CHARS, text).group(0)
        indent_width = len(indent) + indent.count('\t') * (tab_width - 1)
        
        # Remove any pre-existing indentation
        text = '\n'.join(line.lstrip(INDENT_CHARS) for
                            line in text.splitlines())
        
        def format_paragraph(paragraph):
            """Re-wrap the text of one paragraph."""
            LOGGER.log()
            new_paragraph = ''
            offset = 0
            # Get a list of the words in the paragraph
            words = re.findall('\S+', paragraph)
            for word in words:
                # Add a successive word in a line
                if offset != 0:
                    # Determine space between words or sentences
                    is_after_period = new_paragraph[-1] == '.'
                    is_before_capital = word[0] in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    is_between_sentences = is_after_period and is_before_capital
                    space = '  ' if is_between_sentences else ' '
                    # Add the word or start a new line
                    potential_offset = offset + len(space) + len(word)
                    if potential_offset <= max_line_length:
                        new_paragraph = space.join([new_paragraph, word])
                        offset = potential_offset
                    else:
                        new_paragraph += '\n'
                        offset = 0
                # Indent and add the first word in a line
                if offset == 0:
                    new_paragraph = indent.join([new_paragraph, word])
                    offset = indent_width + len(word)
            new_paragraph += '\n'
            return new_paragraph
        
        # Get a list of the paragraphs
        word_re = r'[ \t]*\S+'
        line_re = r'^(?:' + word_re + r')+\n'
        paragraph_re = r'(?:' + line_re + ')+'
        paragraphs = re.findall(paragraph_re, text, re.MULTILINE)
        
        # Re-wrap the paragraphs
        new_paragraphs = (format_paragraph(paragraph) for
                            paragraph in paragraphs)
        
        # Combine the paragraphs
        blank_line = indent + '\n'
        output = blank_line.join(new_paragraphs)
        
        # Replace the selected text with the reformatted text
        self._replace_text_selection(output)
    
    def _get_text_selection(self):
        """Return the currently selected text."""
        LOGGER.log()
        document = self._window.get_active_document()
        if document.get_has_selection():
            self._start_iter, self._end_iter = \
                document.get_selection_bounds()
        else:
            # With no selection, the current line will become the selection
            insert_mark = document.get_insert()
            self._start_iter = document.get_iter_at_mark(insert_mark)
            self._end_iter = self._start_iter.copy()
        
        # Capture the beginning of the first line
        if not self._start_iter.starts_line():
            self._start_iter.set_line_offset(0)
        
        # Capture the end of the last line
        if not self._end_iter.starts_line():
            self._end_iter.forward_line()
        
        selected_text = document.get_text(self._start_iter,
                                          self._end_iter)
        
        return selected_text
    
    def _get_gedit_margin(self):
        """Return the the preference setting for the right margin, e.g. 80."""
        LOGGER.log()
        gconf_client = gconf.client_get_default()
        margin = gconf_client.get_int('/apps/gedit-2/preferences/editor/'
                                      'right_margin/right_margin_position')
        return margin
    
    def _get_gedit_tab_width(self):
        """Return the the preference setting for the tab width, e.g. 4."""
        LOGGER.log()
        gconf_client = gconf.client_get_default()
        tab_width = gconf_client.get_int('/apps/gedit-2/preferences/editor/'
                                      'tabs/tabs_size')
        return tab_width
    
    def _replace_text_selection(self, text):
        """Replace the currently selected text."""
        LOGGER.log()
        document = self._window.get_active_document()
        
        # Delete the old text
        document.delete(self._start_iter, self._end_iter)
        
        # Mark where the selection starts
        start_mark = document.create_mark(
            mark_name=None,
            where=self._start_iter,
            left_gravity=True)
        
        # Insert the new text
        document.insert(self._start_iter, text)
        
        # Move the selection bound to the start location
        # (The insert is already at the new end.)
        new_start_iter = document.get_iter_at_mark(start_mark)
        document.move_mark_by_name("selection_bound", new_start_iter)
        

