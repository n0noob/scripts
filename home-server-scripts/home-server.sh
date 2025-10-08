#!/bin/bash

start_server() {
    echo "Starting home server..."
    media-mount mount
    pushd ~/.containers/home-server
    podman-compose down >/dev/null 2>&1 || true
    podman-compose up -d
    popd
}

stop_server() {
    echo "Stopping home server..."
    media-mount unmount
    pushd ~/.containers/home-server
    podman-compose down
    popd
}

print_help() {
    echo "Usage: $0 {start|stop|help}"
    echo "Commands:"
    echo "  start   Start the home server"
    echo "  stop    Stop the home server"
    echo "  help    Display this help message"
}

main() {
    case "$1" in
        start)
            start_server
            ;;
        stop)
            stop_server
            ;;
        help|--help|-h|"")
            print_help
            ;;
        *)
            echo "Error: Unknown command '$1'"
            print_help
            exit 1
            ;;
    esac
}

main "$@"