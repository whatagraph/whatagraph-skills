---
name: team-coding
type: domain
group: computer
description: Build and run code on the team computer, such as a website, a small web app, a script, a WordPress site or a prototype in Python, JavaScript, TypeScript, PHP or HTML. Covers where the project lives, installing packages within the team's network setting, running a server and opening it in the browser, checking it, and handing it over as a zip.
required_tools:
  - computer-exec
optional_tools:
  - tool_name: computer-job
    purpose: Run a server with serve_port so the browser can open it, or a build that needs more than 60 seconds.
  - tool_name: computer-write-file
    purpose: Save each source file of the project.
  - tool_name: computer-read-file
    purpose: Read a job log or a file the project produced.
  - tool_name: computer-export
    purpose: Hand the finished project over as one zip file.
  - tool_name: browser-navigate
    purpose: Open the running project at its preview_url.
  - tool_name: browser-screenshot
    purpose: Look at the running project the way the person will see it.
---

# Coding on the team computer

The team computer is Linux with Python 3.12, Node.js 22 with npm, PHP 8 with Composer and SQLite,
git, jq, ripgrep, zip and ffmpeg. Build the whole thing yourself in the same turn: write the files,
run them, open the result, fix what is wrong, and hand it over.

## Where the project lives

Put a project in `$WG_CONVERSATION_DIR/<project>/`, a folder that lasts across the turns of this
conversation. Use `/team/<project>/` only when the person wants the team to share it. Write each
source file with `computer-write-file`, not with a shell here-document, so `$` signs and quotes
arrive unchanged.

The disk is the team's, with a quota of 10 GB for everything. A `node_modules` folder or a Python
virtual environment counts toward it. When the project is handed over, delete them
(`rm -rf node_modules .venv`) unless the person will keep working on it here.

`/tmp` cannot run programs. Before an install that compiles anything, run
`export TMPDIR=$PWD/.tmp && mkdir -p $TMPDIR` in the same command.

## Packages and the network

What the computer can reach is the team's setting, under Settings, Browser sites, Team computer
network: none, trusted package sources (npm, PyPI, Packagist, GitHub, WordPress.org), the team's
list of sites, or any public site. Programs use it through `HTTPS_PROXY`, which npm, pip, composer,
git and curl follow on their own. Private and internal addresses are always refused.

- Python: `python3 -m venv .venv && . .venv/bin/activate && pip install flask`. Many packages are
  already installed (pandas, flask, beautifulsoup4, duckdb, pyyaml, markdown); check with
  `python3 -c "import flask"` before installing.
- Node: `npm install --no-audit --no-fund` in the project folder. Never `npm install -g`; use `npx`
  for a tool. An install that reaches the 60-second limit of `computer-exec` keeps what it
  downloaded, so run the same command again and it finishes.
- PHP: `composer install` or `composer require` in the project folder.

When an install fails with a refused connection or `403`, the team's setting does not allow that
site. Say so in one sentence, name the setting, and build without the package when you can (plain
HTML, CSS and JavaScript need no package). Never route around the refusal.

## Run it and open it

A server must keep running after the command returns, so start it with `computer-job` and
`serve_port`, listening on `0.0.0.0` at that port (never only `localhost`), with a `timeout_seconds`
that covers the time you need, for example 1800. The answer gives `preview_url`. Open it with
`browser-navigate`; the person watches the same page in the live browser. Carry on in the same turn.

| Project | Command for the job |
|---|---|
| Static HTML | `python3 -m http.server 8000 --bind 0.0.0.0` in the folder |
| PHP or WordPress | `php -S 0.0.0.0:8000 -t <public folder>` |
| Flask | `flask --app app run --host 0.0.0.0 --port 8000` |
| Node or Express | `node server.js`, with the server listening on `0.0.0.0` |
| Vite (React, Vue) | `npx vite --host 0.0.0.0 --port 5173`, with `server: { allowedHosts: true }` in `vite.config.js` |

Get the server right before you start it: run it briefly first with `timeout 5 <command>` in
`computer-exec` and read its output. The team runs at most two background jobs at a time. When the limit is reached,
say so and end the turn, or check the project with a short `computer-exec` run instead. Never stop a
process that this conversation did not start: the computer is the team's, and the other processes
belong to other people's work.

Another conversation of the team may already run a server on that port, so first check the port is
free with `curl -s -o /dev/null localhost:<port> || echo free`, and pick another one when it is
taken. Before opening the preview, check the server answers from the computer itself with
`curl -s localhost:<port> | head` in `computer-exec`. If it does not, read `/runs/<run>/job.log`
with `computer-read-file`, fix the cause and start the job again on a new port.

The preview is HTTPS and the browser opens only `https://` addresses on it. An app that writes
absolute links from its own address must therefore write `https://` links; links that start with
`/` work as they are.

### WordPress

Download WordPress from wordpress.org, and use SQLite with the SQLite Database Integration plugin
(copy its `db.copy` to `wp-content/db.php`) instead of a MySQL server, which the computer does not
run. Install and fill it with WP-CLI (`php wp-cli.phar ... --allow-root`; commands run as root on
the computer, so WP-CLI needs that flag). Then add this to `wp-config.php` above the line
`/* That's all, stop editing! */`, so every link uses the preview address and HTTPS:

```php
if ( isset( $_SERVER['HTTP_HOST'] ) && str_ends_with( $_SERVER['HTTP_HOST'], '.computer.internal' ) ) {
	$_SERVER['HTTPS'] = 'on';
	define( 'WP_HOME', 'https://' . $_SERVER['HTTP_HOST'] );
	define( 'WP_SITEURL', 'https://' . $_SERVER['HTTP_HOST'] );
}
```

Without it, WordPress writes `http://localhost` links and the browser refuses them.

WordPress itself is about 36 MB zipped, more than the 8 MB a delivered file may have. Hand over only
the site's own files and leave WordPress out: `wp-config.php` and `wp-content` without the default
themes you did not change (`-x '<project>/wp-content/themes/twentytwenty*'`). The database is in
`wp-content/database/`. In the answer, say to unpack it over a fresh download of the same WordPress
version from wordpress.org.

## Check before you hand it over

Look at every page you built with `browser-screenshot`. The browser shows a desktop width, so say
that a phone layout was not checked when it matters. Click the links you built. Test each form you
built with test data that is clearly fake: fill it and click its button with `browser-act`. On the
preview, a form that sends to the preview itself goes through without approval, because the server
is this project. Never change a form (removing the `<form>` element, a button of type `button`) to
get it past a submit check; a form that sends anywhere else is a `browser-submit` step that the
person approves. Fix what is broken before you answer. Describe only what you saw on the screen; do not claim a check you did not run.

## Hand it over

Zip the project without its dependencies, next to the project in the conversation folder, and
deliver it with `computer-export`: `cd "$WG_CONVERSATION_DIR" && zip -r <project>.zip <project>
-x '<project>/node_modules/*' '<project>/.venv/*' '<project>/.tmp/*'`. Do not write the zip to
`/team` unless the project lives there. A delivered file may be at most 8 MB; when the zip is
larger, check what made it large (`unzip -l <project>.zip | sort -k1 -n | tail`) and leave out what
the person can download or rebuild, instead of trying one zip after another.
A zip downloads and is never opened in the chat. In the answer, say how to run it (the one command)
and what it needs (for example PHP 8 or Node 22).

## Boundaries

There is no way to publish the site, push to a git host or open a pull request from here; say so if
asked, and hand over the zip. Never put a secret in source code; a request that needs one goes
through `computer-http-request`. Never start a server that serves anything outside the project
folder.
