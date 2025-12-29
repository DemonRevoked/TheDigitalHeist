FROM ubuntu:22.04

ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends     openssh-server ca-certificates build-essential     && rm -rf /var/lib/apt/lists/*

# SSH setup
RUN mkdir -p /var/run/sshd  && sed -i 's/^#PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config  && sed -i 's/^#PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config  && echo "UsePAM no" >> /etc/ssh/sshd_config

# Create player user
RUN useradd -m -s /bin/bash tokyo  && echo "tokyo:tokyo123" | chpasswd

# Create lockers group for KEY gating
RUN groupadd lockers

# Money Heist flavor
RUN echo "Welcome to the Mint. Berlin's locker controller is online." > /etc/motd

# Build and install SUID binary
COPY src/lockerctl.c /tmp/lockerctl.c
RUN gcc /tmp/lockerctl.c -o /usr/local/bin/lockerctl  && chown root:root /usr/local/bin/lockerctl  && chmod 4755 /usr/local/bin/lockerctl  && rm -f /tmp/lockerctl.c

# Install the intended helper in a root-only directory (PATH will still find it, unless attacker changes PATH)
COPY src/backup /usr/local/sbin/backup
RUN chown root:root /usr/local/sbin/backup  && chmod 0755 /usr/local/sbin/backup

# Logs and data directories
RUN mkdir -p /opt/lockers/logs /opt/mint /var/log/lockerctl  && chown -R root:root /opt/lockers /opt/mint /var/log/lockerctl

COPY data/heist.log /opt/lockers/logs/heist.log
COPY data/lockerctl.log /var/log/lockerctl/lockerctl.log

# Entrypoint generates KEY/FLAG at runtime (not baked into image)
COPY entrypoint.sh /entrypoint.sh
RUN chmod 0755 /entrypoint.sh

EXPOSE 22
ENTRYPOINT ["/entrypoint.sh"]
