FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends     openssh-server cron ca-certificates     && rm -rf /var/lib/apt/lists/*

# SSH setup
RUN mkdir -p /var/run/sshd  && sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config  && sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config  && echo "UsePAM no" >> /etc/ssh/sshd_config

# Create users: tokyo (player) and rio (service account)
RUN useradd -m -s /bin/bash tokyo  && echo "tokyo:tokyo123" | chpasswd  && useradd -m -s /bin/bash rio  && echo "rio:rio123" | chpasswd

RUN echo "Rio's relay node is online. The Mint rotates keys on schedule." > /etc/motd

# Directories + logs
RUN mkdir -p /opt/relay /opt/rotation /var/log/relay  && chown -R root:root /opt/relay /opt/rotation /var/log/relay

COPY data/relay.log /var/log/relay/relay.log

# Misconfigured secret leak (stage 1 progression)
COPY data/relay.env /opt/relay/relay.env
RUN chmod 0644 /opt/relay/relay.env

# Root automation: cron job running rotate.sh
COPY src/rotate.sh /opt/rotation/rotate.sh
COPY src/rotation.env /opt/rotation/rotation.env
RUN chown root:root /opt/rotation/rotate.sh  && chmod 0755 /opt/rotation/rotate.sh  && chown root:rio /opt/rotation/rotation.env  && chmod 0664 /opt/rotation/rotation.env

# Cron schedule
COPY src/mint-rotation-cron /etc/cron.d/mint-rotation
RUN chmod 0644 /etc/cron.d/mint-rotation  && crontab /etc/cron.d/mint-rotation

# Entrypoint
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
