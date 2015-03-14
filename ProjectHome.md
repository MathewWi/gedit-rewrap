## Description ##
This gedit plugin will re-wrap selected lines of text, e.g. comments,
(not code) based on the right margin set in gedit Preferences.

![http://gedit-rewrap.googlecode.com/files/gedit_margin_setting.png](http://gedit-rewrap.googlecode.com/files/gedit_margin_setting.png)

It will maintain
the indentation and any leading comment characters based on the first
line in the selection.

## Installation ##
  1. Download [Rewrap-1.1.0.tar.gz](http://gedit-rewrap.googlecode.com/files/Rewrap-1.1.0.tar.gz).
  1. Extract the files into your `~/.gnome2/gedit/plugins` directory:
    * ![http://gedit-rewrap.googlecode.com/files/plugins_folder.png](http://gedit-rewrap.googlecode.com/files/plugins_folder.png)
  1. Restart gedit.
  1. Activate the plugin in gedit Edit > Preferences > Plugins.

## Usage ##
Select the lines of text to be reformatted and then either
select the menu item (Edit > Rewrap) or press its accelerator keys.

The selection can be made from anywhere on the first and last lines and
will automatically expand to include the full lines.  If no text
selected, the current line will be selected and re-wrapped.

![http://gedit-rewrap.googlecode.com/files/Rewrap_Edit_menu.png](http://gedit-rewrap.googlecode.com/files/Rewrap_Edit_menu.png)

## Screencast ##
http://gedit-rewrap.googlecode.com/files/rewrap.ogg

## Configuration window ##
![http://gedit-rewrap.googlecode.com/files/Screenshot-Rewrap%20plugin%20settings.png](http://gedit-rewrap.googlecode.com/files/Screenshot-Rewrap%20plugin%20settings.png)

The indentation (if any) of the first line will be used for all lines,
and all other spaces and tabs will be ignored.

### Multiple paragraphs ###
If you reformat multiple paragraphs, i.e. blocks of text separated by
blank lines, one blank line will be maintained between them.  If the "Indent empty lines" option is checked, the blank lines will include the indentation and comment markers.

### Sentence spacing ###
Two spaces will be placed between a period and a capitalized word to
separate sentences, but this could also put extra spaces where they don't
belong, e.g. between an abbreviation's period and a proper noun's
capital.

### Really long words ###
If a word (any string of non-whitespace characters) is longer than the
maximum line length, it will not be broken, and it will extend beyond
the maximum line length.  In those cases, you can manually break the
word where you want and then re-wrap as needed.

### Tab characters ###
When re-wrapping text indented with hard tabs, the tab width set in
gedit Preferences is taken into account.

### Trailing comments ###
For example:
```

void bar (int i) {
i = i + 1; // This is a very very very very very very very very very very very very very very very long comment.
}```
Position the cursor just left of the `//`, press Shift+Ctrl+W, and the comment will be re-wrapped like this:
```

void bar (int i) {
i = i + 1; // This is a very very very very very very very very very
// very very very very very very long comment.
}```

### Un-wrapping ###
This is the same process but with an unlimited line length.