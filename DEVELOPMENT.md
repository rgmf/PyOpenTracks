# Install Dependencies
In Debian:
sudo apt install libcairo2-dev
sudo apt install libgirepository1.0-dev

# Virtual Environment
pipenv --three
pipenv shell
pipenv install

# Build
meson --internal regenerate buildir --backend ninja
