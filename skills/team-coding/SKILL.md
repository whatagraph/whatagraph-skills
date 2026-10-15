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
    purpose: Hand the finished project over as one zip file, or as an app card when it runs as a site.
  - tool_name: browser-navigate
    purpose: Open the running project at its preview_url.
  - tool_name: browser-screenshot
    purpose: Look at the running project the way the person will see it.
---

# Coding on the team computer

The team computer is Linux with Python 3.12, Node.js 22 with npm, PHP 8.4 with Composer and SQLite
(with the intl and bcmath extensions that Laravel and Filament need), git, jq, ripgrep, zip and
ffmpeg. Build the whole thing yourself in the same turn: write the files,
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
- PHP: `composer install` or `composer require` in the project folder. Installing a framework
  (`composer create-project laravel/laravel <project>`, or adding Filament) takes longer than the
  60 seconds of `computer-exec`, so run it with `computer-job` (no `serve_port`) and continue when
  it wakes the conversation. Do not run it again in `computer-exec` after a timeout; a cut-off
  Composer run leaves the project half installed.

When an install fails with a refused connection or `403`, the team's setting does not allow that
site. Say so in one sentence, name the setting, and build without the package when you can (plain
HTML, CSS and JavaScript need no package). Never route around the refusal.

## Run it and open it

A server must keep running after the command returns, so start it with `computer-job` and
`serve_port`, listening on `0.0.0.0` at that port (never only `localhost`), with a `timeout_seconds`
that also leaves the person time to try the site after you answer, for example 3600. The answer
gives `preview_url`. Open it with `browser-navigate`; the person watches the same page in the live
browser. Carry on in the same turn.

| Project | Command for the job |
|---|---|
| Static HTML | `python3 -m http.server 8000 --bind 0.0.0.0` in the folder |
| PHP or WordPress | `php -S 0.0.0.0:8000 -t <public folder>` |
| Laravel | `php artisan serve --host=0.0.0.0 --port=8000` in the project folder |
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

### Laravel and Filament

Use SQLite: in `.env` set `DB_CONNECTION=sqlite` and remove the other `DB_` lines, then
`touch database/database.sqlite && php artisan migrate --seed --force`. Sample rows go in a seeder,
so the person gets them again with the same command.

The preview reaches Laravel over HTTP behind its HTTPS address, so Laravel writes `http://` links
for its pages, styles and scripts, and the browser refuses them. Add this to the `boot` method of
`app/Providers/AppServiceProvider.php` (with `use Illuminate\Support\Facades\URL;`):

```php
if (str_ends_with(request()->getHost(), '.computer.internal')) {
    URL::forceScheme('https');
}
```

Build on the current releases. Run `composer create-project laravel/laravel <project>` and
`composer require filament/filament` without a version, so Composer picks the newest ones that fit
PHP 8.4. Never pin an older major version from memory, and never take an older Laravel to fit a
package: an old pin is what makes a package refuse the current Laravel. When Composer refuses, read
its message and drop the pin that causes it. Name the versions you got in the answer.

For an admin panel, install Filament with `composer require filament/filament` and
`php artisan filament:install --panels --no-interaction` (both in one `computer-job`). Create the
login without prompts: `php artisan make:filament-user --name="..." --email="..." --password="..."`.
Make up a password, and give the email and password in the answer: they are for this test copy,
and the person changes them. Open `/admin` on the preview, sign in with `browser-act`, and check
each resource's list and create form.

Hand over the project without `vendor` and `node_modules` (`-x '<project>/vendor/*'`), and keep
`database/database.sqlite` so the sample data comes with it. In the answer, say to run
`composer install`, then `php artisan serve`.

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
When the project runs as a site, pass the `run_id` of the `computer-job` that serves it as
`app_run_id`. The person then gets an app card: Open starts the site again in their browser, at any
later time, and Download gives the zip. Without `app_run_id` the zip is only a download.
In the answer, say how to run it (the one command) and what it needs (for example PHP 8 or Node 22).

The person cannot open `preview_url` themselves; they see the site only in your browser. So the last
page you open before you answer is the site's start page on the preview. In the answer, tell them to
open the app card, or your browser with the globe button at the top of the conversation, to try the
site. Both start the site again by themselves when its server has stopped, so they can come back to
it later without asking you.

Write the answer about the site, not about the computer: what was built, how it was checked, the
zip, and how to try it. Leave out run ids, exit codes, signals, process ids and durations.

## Boundaries

There is no way to publish the site, push to a git host or open a pull request from here; say so if
asked, and hand over the zip. Never put a secret in source code; a request that needs one goes
through `computer-http-request`. Never start a server that serves anything outside the project
folder.
