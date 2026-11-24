# Print the PIDs running a guest program in the selected slot.
pids_of() {
    local pid entry tag
    for pid in $(pgrep -f -- "$1"); do
        [ "$pid" != "$$" ] || continue
        grep -zExq -- "$1" "/proc/$pid/cmdline" 2>/dev/null || continue
        local -a environment
        mapfile -d '' -t environment 2>/dev/null < "/proc/$pid/environ" || continue
        tag=
        for entry in "${environment[@]}"; do
            case "$entry" in DJSDEV_TAG=*) tag=${entry#*=}; break ;; esac
        done
        [ "$tag" != "${DJSDEV_TAG:-}" ] || echo "$pid"
    done
}

# A boot menu can own the screen before the official app is running.
guest_init_unit() {
    local pid seen=
    for pid in $(pids_of /opt/djsemu/init.sh); do
        seen=1
        if grep -zFxq DJSDEV_UNIT=sp16 "/proc/$pid/environ" "/proc/$pid/cmdline" 2>/dev/null; then
            echo sp16
            return
        fi
    done
    [ -z "$seen" ] || echo djs1000
}
