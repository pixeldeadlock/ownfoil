#!/bin/bash

# Get root_dir from env, defaults to /games
root_dir="${ROOT_DIR:-/games}"

gid=${PGID:-1000}
uid=${PUID:-1000}

gt_group=$(getent group $gid | cut -d: -f1)
gt_user=$(getent passwd $uid | cut -d: -f1)

# Setup non root user
if [[ -z $gt_group ]]; then
    echo "Creating group app with GID ${gid}"
    addgroup -g ${gid} -S app
    gt_group=app
fi

if [[ -z $gt_user ]]; then
    echo "Creating user app with UID ${uid}"
    adduser -u ${uid} -S app -G ${gt_group}
    gt_user=app
fi

chown -R ${uid}:${gid} /app

# Check and copy the nginx.conf if it does not already exist in /config
if [[ -f /config/nginx.conf ]]; then
    echo "nginx.conf already exists in /config, skipping copy."
else
    echo "Copying nginx.conf to /config."
    cp /app/conf/nginx.conf /config/nginx.conf
fi

# Check and copy the shop config and template if they do not already exist in /config
if [[ -f /config/shop_config.toml ]]; then
    echo "shop_config.toml already exists in /config, skipping copy."
else
    echo "Copying shop_config.toml to /config."
    cp /app/shop_config.toml /config/shop_config.toml
fi

if [[ -f /config/shop_template.toml ]]; then
    echo "shop_template.toml already exists in /config, skipping copy."
else
    echo "Copying shop_template.toml to /config."
    cp /app/shop_template.toml /config/shop_template.toml
fi

# Setup nginx basic auth if needed
if [[ ! -z $USERNAME && ! -z $PASSWORD ]]; then
    echo "Setting up authentification for user $USERNAME."
    htpasswd -c -b /etc/nginx/.htpasswd $USERNAME $PASSWORD
    sed -i 's/# auth_basic/auth_basic/g' /etc/nginx/http.d/default.conf
else
    echo "USERNAME and PASSWORD environment variables not set, skipping authentification setup."
fi

# Start nginx and app
echo "Starting ownfoil"
nginx -c /config/nginx.conf -g "daemon off;" &
sudo -u $gt_user python /app/app.py $root_dir/shop_config.toml
