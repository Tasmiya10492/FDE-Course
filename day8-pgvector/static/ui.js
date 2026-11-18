/**
 * Configure HTMX response handling.
 *
 * Normally HTMX does not swap 4xx responses.
 * We allow the 403 response to be swapped so that
 * the user can see the CSRF error message.
 */
// Prevent HTMX from injecting inline indicator styles.
// Loading indicator appearance is controlled by our own CSS.
htmx.config.includeIndicatorStyles = false;

htmx.config.responseHandling = [
    { code: "204", swap: false },
    { code: "403", swap: true, error: true },
    { code: "[23]..", swap: true },
    { code: "[45]..", swap: false, error: true },
    { code: "...", swap: true }
];
