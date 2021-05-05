function passedClickThreshold(lastMouse, event) {
    if (!lastMouse || !event)
        return false;

    return (
        Math.abs(lastMouse.x - event.screenX) > clickThreshold ||
        Math.abs(lastMouse.y - event.screenY) > clickThreshold
    );
}
