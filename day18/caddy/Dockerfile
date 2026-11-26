FROM caddy:2.11.9-alpine@sha256:003a97808e781aa9f7e75cc2f43d34d461099031faf5e20faefb9f61126836f0

# Apply available Alpine security and package updates.
# Remove the binary's file capability because the container
# runs with all Linux capabilities dropped.
RUN apk upgrade --no-cache \
    && setcap -r /usr/bin/caddy

# Create a dedicated non-root user.
RUN addgroup -S -g 10001 caddy \
    && adduser -S -D -H -u 10001 -G caddy caddy \
    && mkdir -p /data /config \
    && chown -R caddy:caddy /data /config

COPY Caddyfile /etc/caddy/Caddyfile

USER caddy

EXPOSE 8080 8443

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD ["caddy", "validate", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]

CMD ["caddy", "run", "--config", "/etc/caddy/Caddyfile", "--adapter", "caddyfile"]
