FROM debian:bookworm-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential openssh-server apache2 libapache2-mod-php && \
    rm -rf /var/lib/apt/lists/*

# Prepare sshd
RUN mkdir -p /var/run/sshd

COPY src/ /app/src/

# Build arg for embedding the challenge key at compile time
ARG CHALLENGE_KEY_BUILD=offline-session-key

# Compile with maximum obfuscation: stripped, no debug info, no symbols
# Makes binary unreadable with basic tools, requires RE tools like Ghidra
RUN gcc -O2 -s -fno-stack-protector -fno-ident \
    -fno-asynchronous-unwind-tables -fno-unwind-tables \
    -ffunction-sections -fdata-sections \
    -Wl,--build-id=none -Wl,--gc-sections \
    -DCHALLENGE_KEY_BUILD=\"${CHALLENGE_KEY_BUILD}\" \
    /app/src/confession_app.c -o /app/confession_app && \
    strip --strip-all /app/confession_app

COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Configure Apache to listen only on localhost:31337
RUN echo "ServerName localhost" >> /etc/apache2/apache2.conf && \
    sed -i 's/Listen 80/Listen 127.0.0.1:31337/' /etc/apache2/ports.conf

# Enable PHP module - find and enable the installed PHP module
RUN for mod in php8.2 php8.1 php7.4 php; do \
        if [ -f "/etc/apache2/mods-available/${mod}.load" ]; then \
            a2enmod "${mod}" && break; \
        fi; \
    done || true

# Configure VirtualHost
RUN echo '<VirtualHost 127.0.0.1:31337>' > /etc/apache2/sites-available/000-default.conf && \
    echo '    ServerAdmin webmaster@localhost' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    DocumentRoot /var/www/html' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    <Directory /var/www/html>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        Options -Indexes +FollowSymLinks' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        AllowOverride None' >> /etc/apache2/sites-available/000-default.conf && \
    echo '        Require all granted' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    </Directory>' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    ErrorLog ${APACHE_LOG_DIR}/error.log' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    CustomLog ${APACHE_LOG_DIR}/access.log combined' >> /etc/apache2/sites-available/000-default.conf && \
    echo '    PassEnv CHALLENGE_FLAG' >> /etc/apache2/sites-available/000-default.conf && \
    echo '</VirtualHost>' >> /etc/apache2/sites-available/000-default.conf

# Copy Apache content
COPY apache-content/ /var/www/html/
RUN chown -R www-data:www-data /var/www/html

# Create default basics.txt (will be moved to /root/.flag_storage by entrypoint)
# This file is only accessible by root, not by SSH user
RUN echo "TDHCTF{confession_gateway_phrase}" > /app/basics.txt && \
    chmod 600 /app/basics.txt

CMD ["/app/entrypoint.sh"]

