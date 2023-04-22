#!/bin/sh

if [ "$(echo $@)" = "server" ]; then
  entry=help
else
  entry="$1"
  shift
fi

case "$entry" in
  test)
    entry=unittest
    ;;
  *help)
    cat >&2 <<EOF
Usage: samsara <command> [options]

Commands:
  get     Perform a single request, writing the response to stdout
  server  Start an HTTP server on port 2420 and serve forever
  spider  Spider a site, writing static files to the specified directory
  test    Run the bundled unit tests

EOF
    exit
esac

. /venv/bin/activate

exec "$entry" "$@"
