#!/bin/bash

{% if cloudless_test_framework_ssh_key %}
adduser "{{ cloudless_test_framework_ssh_username }}" --disabled-password --gecos "Cloudless Test User"
echo "{{ cloudless_test_framework_ssh_username }} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
mkdir /home/{{ cloudless_test_framework_ssh_username }}/.ssh/
echo "{{ cloudless_test_framework_ssh_key }}" >> /home/{{ cloudless_test_framework_ssh_username }}/.ssh/authorized_keys
{% endif %}

apt-get update
apt-get -y install postgresql postgresql-contrib
{% if cloudless_test_framework_ssh_key %}
# Creating a test DB but only if we are in the cloudless test framework.
update-rc.d postgresql enable
cat <<EOF >> /etc/postgresql/9.5/main/postgresql.conf
listen_addresses = '*'
EOF
sudo -u postgres createuser test
sudo -u postgres createdb test
cat <<EOF >> /etc/postgresql/9.5/main/pg_hba.conf
host    test             test             0.0.0.0/0            trust
EOF
{% endif %}
sudo service postgresql restart
