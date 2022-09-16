# LSP-Metals

![lsp-metals](https://i.imgur.com/vJKP0T3.gif)

`LSP-metals` is the recommended [Sublime LSP](https://packagecontrol.io/packages/LSP) extension for [Metals](https://scalameta.org/metals/), the Scala language server. `LSP-metals` offers automated Metals installation, easy configuration, Metals-specific commands and many other small features.

<p>
    <a href="https://discord.gg/qSWW6khxjD">
        <img alt="Discord" src="https://img.shields.io/discord/632642981228314653">
    </a>
</p>

## Table of Contents
  - [Requirements](#requirements)
  - [Installing LSP-metals](#installing-lsp-metals)
  - [Importing a build](#importing-a-build)
    - [Speeding up import](#speeding-up-import)
    - [Importing changes](#importing-changes)
  - [Configuration](#configuration)
    - [Java version](#java-version)
    - [Server version](#server-version)
  - [Workplace Diagnostic](#workplace-diagnostic)
  - [Run doctor](#run-doctor)
  - [All Available Commands](#all-available-commands)
  - [Show document symbols](#show-document-symbols)
  - [Formatting on save](#formatting-on-save)
  - [Organize imports on save](#organize-imports-on-save)
  - [Decoration protocol](#decoration-protocol)
  - [Status Bar](#status-bar)
  - [Troubleshooting](#troubleshooting)



### Requirements

- Sublime Text (build 4000 or later)
- [LSP](https://github.com/tomv564/LSP) package: `Command Palette (Cmd + Shift + P) > Install package > LSP`
- Java 8 or 11 provided by OpenJDK or Oracle. Eclipse OpenJ9 is not supported,
    please make sure the JAVA_HOME environment variable points to a valid Java 8 or
    11 installation.

### Installing LSP-metals

Once you have `LSP` installed, you can then install Metals via

- Automatically via package control: `Command Palette (Cmd + Shift + P) > Install package > LSP-metals`

- manually: run `git clone https://github.com/scalameta/metals-sublime.git LSP-metals` in your sublime packages directory 

### Importing a build

The first time you open Metals in a new workspace it prompts you to import the
build. Click "Import build" to start the installation step.

![Build Import](https://i.imgur.com/eUk30Zy.png)

- "Not now" disables this prompt for 2 minutes.
- "Don't show again" disables this prompt forever, use rm -rf .metals/ to
    re-enable the prompt.
- Run `lsp toggle server panel` in the command palette to watch the build import progress. You can optionally add a key binding for this command.
- Behind the scenes, Metals uses Bloop to import sbt builds, but you don't need
    Bloop installed on your machine to run this step.

Once the import step completes, compilation starts for your open *.scala files.

Once the sources have compiled successfully, you can navigate the codebase with
goto definition.

#### Speeding up import

The "Import build" step can take a long time, especially the first time you run
it in a new build.  The exact time depends on the complexity of the build and if
library dependencies need to be downloaded. For example, this step can take
everything from 10 seconds in small cached builds up to 10-15 minutes in large
uncached builds.

Consult the Bloop [documentation](https://scalacenter.github.io/bloop/docs/what-is-bloop) to learn how to speed up build import.

#### Importing changes

When you change build.sbt or sources under project/, you will be prompted to
re-import the build.

### Configuration

You can edit the package settings by running `LSP-metals Settings` in the sublime palette or accessing `Preferences > Package Settings > LSP > Servers > LSP-metals`.

![config](https://i.imgur.com/WFSJKV0.png)

#### Java version
The `LSP-metals` extension by default uses the `JAVA_HOME` environment variable
(via [`environ`](https://docs.python.org/3/library/os.html#os.environ)). Otherwise, it uses [which](https://docs.python.org/3/library/shutil.html#shutil.which) to locate the `java` executable.

If no `JAVA_HOME` is detected you can then open Settings by following the
instructions in the displayed error message.

![No Java Home](https://i.imgur.com/yLrqzGP.png)


#### Server version

In order to install the latest snapshot of metals you can explicitly set the snapshot version for `server_version`. Alternatively, you can also just default to the latest snapshot by setting `server_version` to `latest-snapshot`.
The same can be done for the latest stable release by setting the value to `latest-stable`, If no version is set, it defaults to the latest stable release as well.

The new release check in done each time sublime text is started.

### Workplace Diagnostic

To see all compilation errors and warnings in the workspace, run the following command `Toggle Diagnostics Panel` Or use the default mapping `super+shift+M` / `ctr+alt+M`

To cycle through the diagnostic use the default mapping Next `F4` / Previous `shift+F4` 

![diagnostic](https://i.imgur.com/uRSLJJ0.gif)

### Run doctor

To troubleshoot problems with your build workspace, run `Doctor run` in the command pallet. This command opens a browser window.

![Run Doctor Command](https://i.imgur.com/yelm0jd.png)


### All Available Commands

The following commands can be invoked simply via the sublime command palette.

  - [Build Import](https://scalameta.org/metals/docs/editors/new-editor.html#import-build)
  - [Build Connect](https://scalameta.org/metals/docs/editors/new-editor.html#connect-to-build-server)
  - [compile Cascade](https://scalameta.org/metals/docs/editors/new-editor.html#cascade-compile)
  - [Compile Cancel](https://scalameta.org/metals/docs/editors/new-editor.html#cancel-compilation)
  - [Doctor Run](https://scalameta.org/metals/docs/editors/new-editor.html#run-doctor)
  - [New Scala File](https://scalameta.org/metals/docs/editors/new-editor.html#create-new-scala-file): Also available in the side bar context menu. ![Peek 2020-07-19 16-48](https://user-images.githubusercontent.com/1632384/87877673-e5e37300-c9df-11ea-9516-6fccb221e3f6.gif) 


### Show document symbols

Run the `Document Symbols` command to show a symbol outline for the current file. You can also set a key binding for the `lsp_document_symbols` command

![Document Symbols](https://i.imgur.com/z5mqk8D.gif)

### Formatting on save

If you'd like to have `LSP-metals` format your file on document save then make sure to add this setting to your Sublime settings, Syntax-specific settings and/or in Project files. 

```
"lsp_format_on_save": true,
...
```

### Organize imports on save

If you'd like to have `LSP-metals` organize your imports on document save then make sure to add this to your `LSP` settings.

```
"lsp_code_actions_on_save":{
  "source.organizeImports": true
},
...
```

### Decoration protocol

This plugin implements the [Decoration protocol](https://scalameta.org/metals/docs/editors/decoration-protocol.html) (only for ST4) which allows showing worksheet evaluations (instead of comments), as well as inferred types and other info as Sublime Phantom.

To enable this feature enable the following `LSP-metals` settings:

```
"settings": {
  "metals": {
    ...
    "showInferredType": true,
    "showImplicitArguments": true,
    "showImplicitConversionsAndClasses": true
  }
}

```
### Status Bar

Information about your workspace build like compilation errors count, build status, etc. are displayed by Metals in the sublime status bar.

![Status bar info](https://i.imgur.com/0mIi6XB.gif)

### Troubleshooting

If you have any questions or issues with LSP-metals, please submit an
[issue](https://github.com/scalameta/metals-sublime/issues) in this repository if it is related to the extension. 

If the issue is general to Metals, please submit it
in the [Metals issue repo](https://github.com/scalameta/metals/issues). 

If you have any feature requests, we also have a feature request [issue
repo](https://github.com/scalameta/metals-feature-requests). 
