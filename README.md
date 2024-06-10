# Monkey Tools for Social Media

[![Release Notes](https://img.shields.io/github/release/inf-monkeys/monkey-tools-social-media)](https://github.com/inf-monkeys/monkey-tools-social-media/releases)
[![GitHub star chart](https://img.shields.io/github/stars/inf-monkeys/monkey-tools-social-media?style=social)](https://star-history.com/#inf-monkeys/monkey-tools-social-media)
[![GitHub fork](https://img.shields.io/github/forks/inf-monkeys/monkey-tools-social-media?style=social)](https://github.com/inf-monkeys/monkey-tools-social-media/fork)


English | [中文](./README-ZH.md)

### Generate RSA Key pair

Generate RSA Key pair:

> We use a 8192 length private key to support longer data.

```bash
# Private key
openssl genpkey -algorithm RSA -out private_key.pem -pkeyopt rsa_keygen_bits:8192

# Public Key
openssl rsa -pubout -in private_key.pem -out public_key.pem
```

The public key will send to Monkeys Server to store the encrypted credentials, the private key will be used to decrpt.


### Configuration

Create a `config.yaml` in the source root directory: 

```sh
cp config.yaml.example config.yaml
```

Be sure to replace rsa public key and private key in `config.yaml`.

## Setup

### 🐳 Docker

We provide docker image on [docker hub](https://hub.docker.com/r/infmonkeys/monkey-tools-social-media):

```sh
# Use docker image from docker hub
docker pull infmonkeys/monkey-tools-social-media:latest
# Or build docker image by your own
# docker build . -t infmonkeys/monkey-tools-social-media:latest
docker run --name monkey-tools-social-media -d -p 8891:8891 -v ./config.yaml:/app/config.yaml infmonkeys/monkey-tools-social-media:latest
```

Or you can build your own using the Dockerfile:

```sh
docker build . -t monkey-tools-social-media
```

### 👨‍💻 Developers

1. Clone the repository

    ```sh
    git clone https://github.com/inf-monkeys/monkey-tools-social-media
    ```

2. Go into repository folder

    ```sh
    cd monkey-tools-social-media
    ```

3. Install python dependencies:

    ```sh
    python -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

4. Install playwright dependencies

    ```bash
    playwright install
    playwright install-deps
    ```


6. Create `config.yaml`:

    ```bash
    cp config.yaml.example config.yaml
    ```

    And replace your RSA public key and private key.

7. Start the API Server:

    ```bash
    python app.py
    ```

    You can now access the app on [http://localhost:8891](http://localhost:8891)
