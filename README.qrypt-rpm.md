# rng-tools Qrypt RPM Setup

This RPM installs rngd configured to use only the qrypt entropy source.

## Defaults Installed by the Package

- Endpoint: `https://eaas-aws.qrypt.com/api/v1/entropy`
- Auth mode: `xapi`
- Token path: `/etc/rngd/qrypt.token`
- Optional override file: `/etc/sysconfig/rngd-qrypt`

## Install Steps

1. Install the RPM.
2. Create the token directory and file:

   ```bash
   sudo install -d -m 0700 /etc/rngd
   sudo install -m 0600 -o root -g root /dev/null /etc/rngd/qrypt.token
   sudo sh -c 'cat > /etc/rngd/qrypt.token' <<'EOF'
   YOUR_QRYPT_API_KEY_OR_BEARER_TOKEN
   EOF
   ```

3. Start and enable rngd:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now rngd
   ```

4. Validate logs:

   ```bash
   sudo journalctl -u rngd --since "10 min ago" --no-pager -o cat \
     | grep -Ei 'qrypt|Initialized|Initialization Failed'
   ```

## SELinux

On SELinux-enforcing systems, `rngd` may be denied outbound HTTPS access even
when the same qrypt request works from an interactive root shell. A typical
symptom is a journal message like `Failed to send curl: Could not connect to
server` together with an AVC denial for `rngd_t` connecting to port 443.

To confirm:

```bash
sudo ausearch -m avc -c rngd -ts recent
```

To install a local policy module permitting this access:

```bash
sudo dnf install -y policycoreutils-python-utils checkpolicy
sudo ausearch -m avc -c rngd --raw | audit2allow -M rngd_qrypt
sudo semodule -i rngd_qrypt.pp
sudo systemctl restart rngd
```

This creates a host-local SELinux policy module from the observed denials and
applies it without disabling SELinux globally.

## Optional Overrides

To change endpoint, auth mode, or token path, edit `/etc/sysconfig/rngd-qrypt`:

```bash
QRYPT_ENDPOINT=https://eaas-aws.qrypt.com/api/v1/entropy
QRYPT_AUTH_MODE=xapi
QRYPT_TOKEN_FILE=/etc/rngd/qrypt.token
```

Then restart the service:

```bash
sudo systemctl restart rngd
```

## Security Notes

- Do not embed tokens in RPMs.
- Keep token files root-owned and mode 0600.
- Avoid passing tokens on command lines to prevent shell history leakage.
