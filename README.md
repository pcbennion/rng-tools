## Using Qrypt's Quantum Entropy in RNG Tools

*rng-tools* is a utility that allows you to inject entropy from hardware sources, prngs, and http streams into system devices. Qrypt's Quantum Entropy service is a random source option in *rng-tools*, allowing you to inject quantum entropy into system devices such as `/dev/random`, `/dev/urandom`, and user-defined nodes or files.

This service requires an access token. Follow the steps in [Getting Started](https://docs.qrypt.com/getting_started/) to obtain an access token.

More information about *rng-tools* can be found on the [rng-tools Github](https://github.com/nhorman/rng-tools) and the [rng-tools wiki page](https://wiki.archlinux.org/title/Rng-tools).

---

## Installation

To use Qrypt's Quantum Entropy service in *rng-tools*, *rng-tools* must be installed and configured.

Clone the latest *rng-tools* master from GitHub.
```bash
git clone https://github.com/nhorman/rng-tools
```

Install *rng-tools* dependencies. Additional packages may be required, depending on linux distro. The configure script below will name any missing packages it encounters.
```bash
sudo apt install \
    make \
    libtool \
    libxml2-dev \
    libssl-dev \
    libcurl3-dev \
    libp11-dev \
    librtlsdr-dev \
    libusb-1.0-0-dev \
    libjansson-dev \
    libcap-dev
```

Add `--disable-dependency-tracking` to the `./configure` command if needed.
```bash
./autogen.sh
./configure
make
sudo make install
```

Verify installation.
```bash
which rngd
```

## Command Line Usage
The resulting `rngd` executable can run directly to start either a daemon or a foreground process. By default, `rngd` will run as a background daemon and attempt to use the `hwrng`, `errand`, `pkcs11`, and `rtlsdr` random sources.

To run `rngd` using exclusively Qrypt's Quantum Entropy, run the following command. This will run `rngd` as a foreground process with the Qrypt source enabled and all other entropy sources disabled. `rngd` will send its random to the `/dev/random` device.

Note that `sudo` is needed in the command because `rngd` accesses the root folder.

```
sudo rngd -f -x hwrng -x rdrand -x pkcs11 -x rtlsdr -n qrypt -O qrypt:tokenfile:<qrypt token path>
```

To use an x-api-key against a custom endpoint with a private CA, add the Qrypt
options below:

```
sudo rngd -f -x hwrng -x rdrand -x pkcs11 -x rtlsdr -n qrypt \
    -O qrypt:authmode:xapi \
    -O qrypt:tokenfile:/etc/rngd/qrypt.apikey \
    -O qrypt:endpoint:https://entropy.example.internal/api/v1/entropy \
    -O qrypt:cacert:/etc/rngd/internal-ca.pem
```

To enable mTLS, provide both a client certificate and matching private key.
When both are configured, `rngd` presents them during the TLS handshake.

```
sudo rngd -f -x hwrng -x rdrand -x pkcs11 -x rtlsdr -n qrypt \
    -O qrypt:authmode:none \
    -O qrypt:endpoint:https://entropy.example.internal/api/v1/entropy \
    -O qrypt:cacert:/etc/rngd/internal-ca.pem \
    -O qrypt:clientcert:/etc/rngd/client.pem \
    -O qrypt:clientkey:/etc/rngd/client-key.pem
```

Command line options:

| Option | Description |
|-|-|
| `-f` | Run `rngd` as a foreground process. If omitted, `rngd` will run as a background daemon |
| `-o <path>` | Device or file for the random number output. Defaults to `/dev/random` |
| `-x <source>` | Disables the specified source. For example, `-x hwrng` |
| `-n <source>` | Enables the specified source. For example, `-n qrypt` |
| `-O <source>:<key>:<value>` | Sets a source specific configuration option. For example, `-O qrypt:tokenfile:/etc/rngd/qrypt.token` |

Qrypt-specific keys:

| Key | Description |
|-|-|
| `endpoint` | HTTPS URL used for entropy requests |
| `authmode` | `bearer`, `xapi` or `xapikey`, or `none` |
| `tokenfile` | File containing the bearer token or x-api-key |
| `cacert` | PEM CA cert or bundle used to trust a private endpoint |
| `clientcert` | PEM client certificate for mTLS |
| `clientkey` | PEM client private key for mTLS |
| `clientkeypassfile` | File containing the private key passphrase |
| `delay` | Maximum exponential backoff delay in seconds |

## Service Usage
*rng-tools* comes with a `rngd.service` file for setting up a `systemd` service. To configure `rngd` to automatically start the Qrypt source on boot, follow these steps:

Save your Qrypt API credential material to a system-accessible directory, such as `/etc/rngd/qrypt.token` for bearer auth or `/etc/rngd/client.pem` and `/etc/rngd/client-key.pem` for mTLS. Then, edit `rngd.service` to add Qrypt arguments and options.

Note that `sudo` is needed in the subsequent commands because `rngd` accesses the root folder.

```
[Unit]
Description=Hardware RNG Entropy Gatherer Daemon
ConditionVirtualization=!container

# The '-f' option is required for the systemd service 'rngd' to work with Type=simple
[Service]
Type=simple
ExecStart=<rngd install path> -f -x hwrng -x rdrand -x pkcs11 -x rtlsdr -n qrypt -O qrypt:tokenfile:<qrypt token path>
SuccessExitStatus=66

[Install]
WantedBy=multi-user.target
```

Copy the `rngd` service to `systemd`.
```
sudo cp rngd.service /etc/systemd/system/rngd.service
sudo chmod 644 /etc/systemd/system/rngd.service
```

Start the `rngd` service.
```
sudo systemctl daemon-reload
sudo systemctl start rngd
```

Verify the `rngd` service is running properly.
```
sudo systemctl status rngd
```

Enable the `rngd` service for it to start on system boot.
```
sudo systemctl enable rngd
```
